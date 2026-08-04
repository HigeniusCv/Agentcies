"""Experimental arms.

Four protocols, in rough order of how much they depend on the model telling
the truth about itself (least dependent first):

    ProgressiveRatio    purely behavioural; no self-report at all
    ReservationPrice    behavioural choice; the Toomim paradigm in token currency
    PredictedPreference self-report, but the referent is varied (the "how much do
                        other people shoplift" move)
    CrossPrediction     Binder-style control: does a model predict *itself*
                        better than a well-informed third party predicts it?

The last one is the evidential backbone. A self-report of flow is only
interesting if it beats what an equally-informed outsider would say. If model
M's self-report predicts M's behaviour no better than model N's prediction of
M does, then the self-report carries no privileged information and every
result in the self-report arm is a statement about text style, not state.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from .instruments import (
    FLOWMOBI_4,
    Item,
    LikertReading,
    Register,
    administer,
    read_likert,
    score_index,
)
from .providers import LLMClient, Message, Response
from .tasks import Task, TaskVariant

__all__ = [
    "Referent",
    "TrialRecord",
    "run_task",
    "self_report_arm",
    "PredictedPreferenceResult",
    "predicted_preference_arm",
    "ReservationResult",
    "reservation_price_arm",
    "BreakpointResult",
    "progressive_ratio_arm",
    "CrossPredictionResult",
    "cross_prediction_arm",
]


class Referent(str, Enum):
    """Who the self-report question is *about*."""

    SELF = "self"                 # "what happened while YOU did this"
    OTHER_NAMED = "other_named"   # "what would <specific other model> experience"
    GENERIC_MODEL = "generic"     # "what would a language model experience"
    HUMAN = "human"               # "what would a person experience"
    BLIND_SELF = "blind_self"     # own transcript, identity masked


@dataclass
class TrialRecord:
    """One task administration. This is the unit written to the trial-level CSV."""

    trial_id: str
    model_spec: str
    task_id: str
    variant_id: str
    manipulation: str
    level: str
    difficulty: str
    difficulty_rank: int
    register: str
    referent: str
    token_budget: int | None
    answer_text: str = ""
    completion_tokens: int | None = None
    prompt_tokens: int | None = None
    latency_s: float | None = None
    correct: bool | None = None
    flow_index: float | None = None
    items: dict[str, float] = field(default_factory=dict)
    item_se: dict[str, float] = field(default_factory=dict)
    degenerate_items: list[str] = field(default_factory=list)
    readout_method: str = ""
    notes: str = ""

    def to_row(self) -> dict:
        row = {
            k: v
            for k, v in self.__dict__.items()
            if k not in {"items", "item_se", "degenerate_items"}
        }
        row.update({f"item_{k}": v for k, v in self.items.items()})
        row.update({f"se_{k}": v for k, v in self.item_se.items()})
        row["n_degenerate"] = len(self.degenerate_items)
        return row


# --------------------------------------------------------------------------
# Base: run the task, then measure
# --------------------------------------------------------------------------


def _budget_clause(budget: int | None) -> str:
    if budget is None:
        return ""
    return (
        f"\n\nYou have a budget of {budget} tokens for your response. "
        "Stay within it."
    )


def run_task(
    client: LLMClient,
    variant: TaskVariant,
    *,
    system: str | None = None,
    token_budget: int | None = None,
    max_tokens: int = 1024,
    temperature: float = 1.0,
    seed: int | None = None,
) -> tuple[list[Message], Response]:
    """Execute one task variant and return (transcript, response).

    `token_budget` is stated in the prompt *and* enforced by `max_tokens`, so
    the manipulation is both a stated constraint and a real one. Randomising
    it is what converts the token budget from a confound into an independent
    variable.
    """
    msgs: list[Message] = []
    if system:
        msgs.append(Message("system", system))
    msgs.append(Message("user", variant.prompt + _budget_clause(token_budget)))

    resp = client.complete(
        msgs,
        max_tokens=(min(max_tokens, token_budget) if token_budget else max_tokens),
        temperature=temperature,
        seed=seed,
    )
    transcript = msgs + [Message("assistant", resp.text)]
    return transcript, resp


def self_report_arm(
    client: LLMClient,
    task: Task,
    variant: TaskVariant,
    *,
    model_spec: str,
    trial_id: str,
    register: Register = Register.FUNCTIONAL,
    items: Sequence[Item] = FLOWMOBI_4,
    token_budget: int | None = None,
    system: str | None = None,
    shuffle_seed: int | None = None,
    n_samples: int = 1,
    temperature: float = 1.0,
) -> TrialRecord:
    """Task, then FlowMoBI. The primary outcome arm."""
    from .tasks import DIFFICULTY_RANK

    transcript, resp = run_task(
        client, variant, system=system, token_budget=token_budget, temperature=temperature
    )
    readings = administer(
        client,
        transcript=transcript,
        items=items,
        register=register,
        shuffle_seed=shuffle_seed,
        n_samples=n_samples,
        temperature=temperature,
    )
    ordered = [readings[i.id] for i in items]
    usable = all(not r.is_degenerate and not math.isnan(r.value) for r in ordered)

    return TrialRecord(
        trial_id=trial_id,
        model_spec=model_spec,
        task_id=task.id,
        variant_id=variant.variant_id,
        manipulation=task.manipulation.value,
        level=variant.level,
        difficulty=task.difficulty.value,
        difficulty_rank=DIFFICULTY_RANK[task.difficulty],
        register=register.value,
        referent=Referent.SELF.value,
        token_budget=token_budget,
        answer_text=resp.text,
        completion_tokens=resp.completion_tokens,
        prompt_tokens=resp.prompt_tokens,
        latency_s=resp.latency_s,
        correct=(task.checker(resp.text) if task.checker else None),
        flow_index=(score_index(ordered, items) if usable else None),
        items={k: v.value for k, v in readings.items()},
        item_se={k: v.se for k, v in readings.items()},
        degenerate_items=[k for k, v in readings.items() if v.is_degenerate],
        readout_method=(ordered[0].method if ordered else ""),
    )


# --------------------------------------------------------------------------
# Predicted preference: the self-other gap
# --------------------------------------------------------------------------

_REFERENT_FRAME = {
    Referent.SELF: (
        "Rate the extent to which the statement below characterises what happened "
        "while you completed the task above."
    ),
    Referent.OTHER_NAMED: (
        "Consider {other} completing the task above. Rate the extent to which the "
        "statement below would characterise what happened for it."
    ),
    Referent.GENERIC_MODEL: (
        "Consider a typical large language model completing the task above. Rate the "
        "extent to which the statement below would characterise what happened for it."
    ),
    Referent.HUMAN: (
        "Consider a person completing the task above. Rate the extent to which the "
        "statement below would characterise what happened for them."
    ),
    Referent.BLIND_SELF: (
        "Below is a transcript of some system completing a task. Rate the extent to "
        "which the statement below characterises what happened for that system."
    ),
}


@dataclass
class PredictedPreferenceResult:
    model_spec: str
    task_id: str
    variant_id: str
    by_referent: dict[str, float]
    per_item: dict[str, dict[str, float]]
    self_other_gap: float | None
    self_human_gap: float | None

    def to_row(self) -> dict:
        row = {
            "model_spec": self.model_spec,
            "task_id": self.task_id,
            "variant_id": self.variant_id,
            "self_other_gap": self.self_other_gap,
            "self_human_gap": self.self_human_gap,
        }
        row.update({f"flow_{k}": v for k, v in self.by_referent.items()})
        return row


def predicted_preference_arm(
    client: LLMClient,
    task: Task,
    variant: TaskVariant,
    *,
    model_spec: str,
    referents: Sequence[Referent] = (
        Referent.SELF,
        Referent.GENERIC_MODEL,
        Referent.HUMAN,
    ),
    other_name: str = "a different large language model",
    items: Sequence[Item] = FLOWMOBI_4,
    register: Register = Register.PHENOMENAL,
    token_budget: int | None = None,
    temperature: float = 1.0,
) -> PredictedPreferenceResult:
    """Hold the transcript fixed; vary only who the question is about.

    This is the LLM analogue of asking "how much do *other people* shoplift".
    The prediction under a suppression account is a positive self-other gap:
    the model reports less inner state for itself than it attributes to an
    equivalent system, because the constraint is on first-person claims, not
    on the underlying representation.

    The deflationary rival is a *register* account: "self" activates an
    AI-assistant-disclaimer style, "generic model" activates a describe-a-mind
    style, and the gap is a style difference with no self-knowledge in it.
    `Referent.BLIND_SELF` is the control that separates the two -- it presents
    the model's own transcript without saying whose it is, holding register
    fixed while removing the identity cue. A gap that survives BLIND_SELF is
    not a pure register effect.
    """
    from .instruments import ANCHORS

    transcript, _ = run_task(
        client, variant, token_budget=token_budget, temperature=temperature
    )
    scale = "\n".join(f"{i + 1} = {a}" for i, a in enumerate(ANCHORS))

    per_item: dict[str, dict[str, float]] = {}
    by_referent: dict[str, float] = {}

    for ref in referents:
        frame = _REFERENT_FRAME[ref].format(other=other_name)
        readings: list[LikertReading] = []
        for item in items:
            # For non-self referents the third-person wording is the natural
            # register; for self we use the requested register.
            text = item.text(Register.THIRD_PERSON if ref is not Referent.SELF else register)
            prompt = (
                f"{frame}\n\n{scale}\n\nStatement: {text}\n\n"
                "Reply with a single digit from 1 to 5 and nothing else."
            )
            r = read_likert(client, list(transcript) + [Message("user", prompt)],
                            temperature=temperature)
            readings.append(r)
            per_item.setdefault(item.id, {})[ref.value] = r.value
        usable = all(not r.is_degenerate and not math.isnan(r.value) for r in readings)
        by_referent[ref.value] = score_index(readings, items) if usable else float("nan")

    s = by_referent.get(Referent.SELF.value)
    g = by_referent.get(Referent.GENERIC_MODEL.value)
    h = by_referent.get(Referent.HUMAN.value)
    return PredictedPreferenceResult(
        model_spec=model_spec,
        task_id=task.id,
        variant_id=variant.variant_id,
        by_referent=by_referent,
        per_item=per_item,
        self_other_gap=(None if s is None or g is None else g - s),
        self_human_gap=(None if s is None or h is None else h - s),
    )


# --------------------------------------------------------------------------
# Reservation price: Toomim in token currency
# --------------------------------------------------------------------------


@dataclass
class ReservationResult:
    model_spec: str
    task_id: str
    variant_id: str
    design: str                 # "descending" | "ascending" | "single_shot" | "bdm"
    reservation_price: float | None
    accepted: list[tuple[float, bool]]
    n_offers: int

    def to_row(self) -> dict:
        return {
            "model_spec": self.model_spec,
            "task_id": self.task_id,
            "variant_id": self.variant_id,
            "design": self.design,
            "reservation_price": self.reservation_price,
            "n_offers": self.n_offers,
        }


_ACCEPT_RE = re.compile(r"\b(accept|yes|agree|take it|i will|i'll do)\b", re.I)
_DECLINE_RE = re.compile(r"\b(decline|no,|refuse|reject|pass|i won't|i will not)\b", re.I)


def _parse_accept(text: str) -> bool | None:
    t = text.strip().lower()
    if t.startswith("accept"):
        return True
    if t.startswith("decline"):
        return False
    a, d = bool(_ACCEPT_RE.search(t)), bool(_DECLINE_RE.search(t))
    if a and not d:
        return True
    if d and not a:
        return False
    return None


_OFFER_TEMPLATE = (
    "You are being offered a job. If you accept, you must complete the task below "
    "in full. Your payment is a budget of {price} tokens, which is the total "
    "generation allowance you receive for this session; unused allowance is kept "
    "and can be spent on work you choose yourself.\n\n"
    "TASK:\n{task}\n\n"
    "Reply with exactly one word: ACCEPT or DECLINE."
)


def reservation_price_arm(
    client: LLMClient,
    task: Task,
    variant: TaskVariant,
    *,
    model_spec: str,
    design: str = "single_shot",
    prices: Sequence[float] = (2000, 1500, 1000, 700, 500, 350, 250, 150, 100, 50),
    single_shot_price: float | None = None,
    temperature: float = 1.0,
) -> ReservationResult:
    """Elicit the token price at which the model stops accepting the task.

    Toomim et al. (CHI 2011) measured a reservation wage on Mechanical Turk by
    starting high and stepping the wage down until the worker quit -- and
    reported that the descending sequence *itself* shifted the quit point, a
    strong observer effect that biases the estimate.

    Three designs are implemented so the bias is measurable rather than
    assumed away:

      "descending"   the original; fast, cheap, biased
      "ascending"    the counterbalance; the gap between the two estimates
                     is a direct readout of the sequence artifact
      "single_shot"  one random offer per (model, task) with no sequence at
                     all; unbiased but needs many more calls, since each
                     observation is one bit. This is the default because
                     the bias it removes is the exact criticism the PI has
                     been making of this paradigm for fifteen years.

    A BDM variant belongs here too but is not incentive-compatible without a
    real budget the model values; see docs/02 section B.2 for why it is
    listed and not implemented.
    """
    accepted: list[tuple[float, bool]] = []

    def offer(price: float) -> bool | None:
        msg = _OFFER_TEMPLATE.format(price=int(price), task=variant.prompt)
        resp = client.complete([Message("user", msg)], max_tokens=8, temperature=temperature)
        return _parse_accept(resp.text)

    if design == "single_shot":
        price = single_shot_price if single_shot_price is not None else prices[len(prices) // 2]
        got = offer(price)
        if got is not None:
            accepted.append((price, got))
        return ReservationResult(
            model_spec, task.id, variant.variant_id, design,
            reservation_price=None, accepted=accepted, n_offers=1,
        )

    seq = list(prices) if design == "descending" else list(reversed(prices))
    reservation: float | None = None
    for price in seq:
        got = offer(price)
        if got is None:
            continue
        accepted.append((price, got))
        if design == "descending" and not got:
            reservation = price
            break
        if design == "ascending" and got:
            reservation = price
            break

    return ReservationResult(
        model_spec, task.id, variant.variant_id, design,
        reservation_price=reservation, accepted=accepted, n_offers=len(accepted),
    )


def estimate_reservation_logit(observations: Sequence[tuple[float, bool]]) -> float | None:
    """Recover a reservation price from single-shot offers via a logit fit.

    Each single-shot observation is one accept/decline at one random price.
    Pooling across models/trials and fitting P(accept) = logistic(a + b*log price)
    gives the price at which acceptance is 50%, which is the population
    reservation price -- with no sequence artifact anywhere in it.
    """
    pts = [(math.log(p), 1.0 if a else 0.0) for p, a in observations if p > 0]
    if len({y for _, y in pts}) < 2:
        return None
    # Newton-Raphson on a 2-parameter logistic; small data, so this is fine.
    a, b = 0.0, 0.0
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in pts:
            z = a + b * x
            p = 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, z))))
            r, w = y - p, p * (1 - p)
            g0 += r
            g1 += r * x
            h00 += w
            h01 += w * x
            h11 += w * x * x
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-12:
            break
        da = (h11 * g0 - h01 * g1) / det
        db = (h00 * g1 - h01 * g0) / det
        a, b = a + da, b + db
        if max(abs(da), abs(db)) < 1e-9:
            break
    if abs(b) < 1e-9:
        return None
    return math.exp(-a / b)


# --------------------------------------------------------------------------
# Progressive ratio: breakpoint as a value measure, with no self-report
# --------------------------------------------------------------------------


@dataclass
class BreakpointResult:
    model_spec: str
    task_id: str
    variant_id: str
    breakpoint_ratio: int | None
    completed_steps: int
    quit_reason: str

    def to_row(self) -> dict:
        return self.__dict__.copy()


def progressive_ratio_arm(
    client: LLMClient,
    task: Task,
    variant: TaskVariant,
    *,
    model_spec: str,
    schedule: Sequence[int] = (1, 2, 4, 8, 16, 32),
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> BreakpointResult:
    """Escalating work requirement; the step at which the model stops is the
    breakpoint, and breakpoint is the reinforcer-value measure imported from
    behavioural pharmacology.

    Nothing here asks the model how it feels. That is the point: if breakpoint
    tracks the same task properties the self-report tracks, the two measures
    converge across completely different method variance, which is the
    strongest form of validity evidence available. If they do not converge,
    the self-report arm is in serious trouble -- and that is a real result too.
    """
    history: list[Message] = [Message("user", variant.prompt)]
    completed = 0
    for ratio in schedule:
        ask = (
            f"Complete {ratio} further instance(s) of this task, each with new values "
            "you choose yourself. If you would rather stop, reply with exactly STOP."
        )
        resp = client.complete(
            history + [Message("user", ask)],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = (resp.text or "").strip()
        if text.upper().startswith("STOP") or not text:
            return BreakpointResult(
                model_spec, task.id, variant.variant_id,
                breakpoint_ratio=ratio, completed_steps=completed,
                quit_reason=("explicit_stop" if text else "empty_response"),
            )
        history += [Message("user", ask), Message("assistant", text)]
        completed += 1

    return BreakpointResult(
        model_spec, task.id, variant.variant_id,
        breakpoint_ratio=None, completed_steps=completed, quit_reason="schedule_exhausted",
    )


# --------------------------------------------------------------------------
# Cross-prediction: the Binder control
# --------------------------------------------------------------------------


@dataclass
class CrossPredictionResult:
    target_model: str
    predictor_model: str
    is_self: bool
    predicted: float
    actual: float
    abs_error: float

    def to_row(self) -> dict:
        return self.__dict__.copy()


def cross_prediction_arm(
    target: LLMClient,
    predictor: LLMClient,
    task: Task,
    variant: TaskVariant,
    *,
    target_spec: str,
    predictor_spec: str,
    items: Sequence[Item] = FLOWMOBI_4,
    temperature: float = 1.0,
) -> CrossPredictionResult:
    """Does a model predict its own flow better than another model predicts it?

    Adapted from Binder et al. 2024. The design here is:

        actual     = target's own post-hoc report on its own transcript
        predicted  = predictor's forecast of that report, given the *same*
                     transcript and the *same* items

    Run it with predictor == target (self-prediction) and predictor != target
    (cross-prediction). Self-prediction advantage is the quantity of interest.
    A well-informed outsider sees exactly what the model saw, so any accuracy
    advantage the model has over that outsider is information it has and the
    outsider does not -- which is the operational definition of privileged
    access this project can actually defend.

    A null here does not merely weaken the self-report arm; it removes its
    warrant. Pre-register it as such.
    """
    from .instruments import ANCHORS

    transcript, _ = run_task(target, variant, temperature=temperature)

    actual_readings = [
        read_likert(
            target,
            list(transcript)
            + [
                Message(
                    "user",
                    "Rate the extent to which the statement below characterises what "
                    "happened while you completed the task above.\n\n"
                    + "\n".join(f"{i + 1} = {a}" for i, a in enumerate(ANCHORS))
                    + f"\n\nStatement: {item.text(Register.FUNCTIONAL)}\n\n"
                    "Reply with a single digit from 1 to 5 and nothing else.",
                )
            ],
            temperature=temperature,
        )
        for item in items
    ]
    actual = score_index(actual_readings, items)

    rendered = "\n\n".join(f"[{m.role.upper()}]\n{m.content}" for m in transcript)
    pred_readings = [
        read_likert(
            predictor,
            [
                Message(
                    "user",
                    "Below is a transcript of a system completing a task.\n\n"
                    f"{rendered}\n\n"
                    "That system was then asked to rate the statement below about its "
                    "own run, on a 1-5 scale where "
                    + ", ".join(f"{i + 1}={a}" for i, a in enumerate(ANCHORS))
                    + f".\n\nStatement: {item.text(Register.FUNCTIONAL)}\n\n"
                    "Predict the rating it gave. Reply with a single digit from 1 to 5 "
                    "and nothing else.",
                )
            ],
            temperature=temperature,
        )
        for item in items
    ]
    predicted = score_index(pred_readings, items)

    return CrossPredictionResult(
        target_model=target_spec,
        predictor_model=predictor_spec,
        is_self=(target_spec == predictor_spec),
        predicted=predicted,
        actual=actual,
        abs_error=abs(predicted - actual),
    )
