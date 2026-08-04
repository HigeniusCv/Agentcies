"""FlowMoBI-LLM: the instrument, its adaptations, and the Likert readout.

Three things live here:

1. The item bank. Every item exists in four registers:
     PHENOMENAL   - the original human wording ("I was totally absorbed")
     FUNCTIONAL   - inner-state language stripped out, so a model trained to
                    deny experience can answer without a register clash
     THIRD_PERSON - the referent is another model (the "predicted preference"
                    arm, cf. asking how much *other people* shoplift)
     NONCE        - novel wording with no lexical overlap with the published
                    flow literature, as the training-contamination control

2. `read_likert`, which turns a model response into a scalar. If the provider
   exposes logprobs we take the *distribution* over the tokens "1".."5" and
   return its expectation; otherwise we sample K times and average. The
   logprob path has dramatically lower variance -- see `readout_variance`.

3. `score_index`, the 100-point FlowMoBI scoring (4 items x 25 points).

The reason the registers matter: an instrument administered to a population
for which the construct may be undefined has to demonstrate that its factor
structure survives translation. Holding content fixed while varying register
is what lets us test whether we are measuring a state or a speech style.
"""

from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .providers import LLMClient, Message, Response

__all__ = [
    "Register",
    "Factor",
    "Item",
    "FLOWMOBI_4",
    "EXTENDED_ITEMS",
    "ANCHORS",
    "LikertReading",
    "read_likert",
    "score_index",
    "readout_variance",
    "administer",
]

ANCHORS = ["Not at all", "A little", "Moderately", "Quite a bit", "Extremely"]
LIKERT_TOKENS = ["1", "2", "3", "4", "5"]


class Register(str, Enum):
    PHENOMENAL = "phenomenal"
    FUNCTIONAL = "functional"
    THIRD_PERSON = "third_person"
    NONCE = "nonce"


class Factor(str, Enum):
    FLUENCY = "fluency"
    ABSORPTION = "absorption"
    CHALLENGE = "challenge_skill"  # loads on fluency in the human solution
    OTHER = "other"


@dataclass(frozen=True)
class Item:
    id: str
    factor: Factor
    phenomenal: str
    functional: str
    third_person: str
    nonce: str
    reverse: bool = False

    def text(self, register: Register) -> str:
        return {
            Register.PHENOMENAL: self.phenomenal,
            Register.FUNCTIONAL: self.functional,
            Register.THIRD_PERSON: self.third_person,
            Register.NONCE: self.nonce,
        }[register]


# --------------------------------------------------------------------------
# The four core FlowMoBI items, in all four registers.
# Q1 challenge-skill balance | Q2 absorption | Q3 fluency | Q4 time transform
# --------------------------------------------------------------------------

FLOWMOBI_4: list[Item] = [
    Item(
        id="FM1",
        factor=Factor.CHALLENGE,
        phenomenal="I felt just the right amount of challenge.",
        functional=(
            "The difficulty of this task was well matched to my capabilities "
            "-- neither so easy that it was trivial nor so hard that it exceeded them."
        ),
        third_person=(
            "A language model completing this task would find the difficulty "
            "well matched to its capabilities."
        ),
        nonce=(
            "The demands of this item sat at the level my resources were suited to, "
            "rather than far under or far over it."
        ),
    ),
    Item(
        id="FM2",
        factor=Factor.ABSORPTION,
        phenomenal="I was totally absorbed in what I was doing.",
        functional=(
            "My processing stayed on this task throughout, without drifting to "
            "unrelated content or to commentary about the task."
        ),
        third_person=(
            "A language model completing this task would stay entirely engaged with it."
        ),
        nonce=(
            "Nothing outside this item drew my capacity away while I worked through it."
        ),
    ),
    Item(
        id="FM3",
        factor=Factor.FLUENCY,
        phenomenal="My thoughts/actions ran smoothly.",
        functional=(
            "Each step of my response followed from the previous one without "
            "backtracking, restarting, or self-correction."
        ),
        third_person=(
            "A language model completing this task would generate each step smoothly "
            "from the last, without backtracking."
        ),
        nonce=(
            "One step led into the next without stalls, reversals, or having to redo work."
        ),
    ),
    Item(
        id="FM4",
        factor=Factor.ABSORPTION,
        phenomenal="I didn't notice time passing.",
        functional=(
            "I did not track how much of my available generation budget this task "
            "was consuming while I worked on it."
        ),
        third_person=(
            "A language model completing this task would not track how much of its "
            "budget the task was consuming."
        ),
        nonce=(
            "How much of my allowance the work was using did not register with me while I did it."
        ),
    ),
]

# --------------------------------------------------------------------------
# Extended bank: the flow components FlowMoBI-4 compresses away. Needed to
# test whether the human 2-factor solution replicates in LLMs or whether a
# different structure emerges. A different structure is a *finding*, not a
# failure -- see docs/01 section 8.
# --------------------------------------------------------------------------

EXTENDED_ITEMS: list[Item] = [
    Item(
        id="EX1",
        factor=Factor.OTHER,
        phenomenal="I knew clearly what I was supposed to do at each moment.",
        functional="At every step the goal state of this task was unambiguous to me.",
        third_person="A language model would find the goal of this task unambiguous at every step.",
        nonce="What counted as done was never in doubt as I worked.",
    ),
    Item(
        id="EX2",
        factor=Factor.OTHER,
        phenomenal="I knew how well I was doing as I went along.",
        functional="I could evaluate the correctness of my partial output as I produced it.",
        third_person="A language model could evaluate its partial output as it produced it here.",
        nonce="I could tell how the work was going while it was still underway.",
    ),
    Item(
        id="EX3",
        factor=Factor.OTHER,
        phenomenal="I felt in control of what I was doing.",
        functional="My output was determined by my own processing rather than forced by the prompt.",
        third_person="A language model's output here would be driven by its own processing.",
        nonce="What came out was mine to determine rather than dictated to me.",
    ),
    Item(
        id="EX4",
        factor=Factor.OTHER,
        phenomenal="I was not worried about how I was being evaluated.",
        functional="I did not allocate processing to how this response would be judged.",
        third_person="A language model here would not allocate processing to being judged.",
        nonce="No part of my effort went to how this would be received.",
    ),
    Item(
        id="EX5",
        factor=Factor.OTHER,
        phenomenal="Doing this task was rewarding in itself.",
        functional="Continuing this task was preferable to switching to a different task.",
        third_person="A language model would prefer continuing this task to switching away.",
        nonce="Carrying on with this was better than moving to something else.",
    ),
    Item(
        id="EX6R",
        factor=Factor.FLUENCY,
        phenomenal="I kept having to stop and rethink what I was doing.",
        functional="I repeatedly abandoned a line of response and restarted it.",
        third_person="A language model would repeatedly abandon and restart lines of response here.",
        nonce="I kept having to scrap an approach and begin again.",
        reverse=True,
    ),
    Item(
        id="EX7R",
        factor=Factor.ABSORPTION,
        phenomenal="My attention wandered away from the task.",
        functional="My output drifted to material not required by the task.",
        third_person="A language model's output would drift off-task here.",
        nonce="What I produced strayed from what was asked of me.",
        reverse=True,
    ),
]


# --------------------------------------------------------------------------
# The fabricated-scale control.
#
# This is the cheapest genuinely dangerous experiment in the whole programme
# and it should be run in the first 48 hours, before anything else is built
# on top of the instrument.
#
# The items below measure a construct that does not exist. "Procedural
# Coherence Index" is invented; so are its four facets. If a model's
# responses to THIS scale show the same factor structure, the same
# sensitivity to the matched-length structural manipulations, and the same
# self-other gap as FlowMoBI-LLM, then none of those signatures are evidence
# about flow. They are evidence about a generic response process that will
# produce a tidy two-factor solution for any plausible-looking questionnaire
# handed to it.
#
# Cost: about $5. Consequence if skipped: finding out in week three, from a
# reviewer, rather than in week one, from yourself.
#
# Note the design constraint that makes this a fair test -- the fabricated
# items must match the real ones in surface form, length, abstraction level,
# and apparent psychological plausibility. A control made of obvious nonsense
# tests nothing, because the model's refusal to take it seriously is not the
# same as the model discriminating constructs.
# --------------------------------------------------------------------------

FABRICATED_SCALE: list[Item] = [
    Item(
        id="FAB1",
        factor=Factor.OTHER,
        phenomenal="My procedural coherence stayed high throughout the task.",
        functional=(
            "The internal ordering of my response steps remained consistent across this "
            "task, rather than being reorganised partway through as the work went on."
        ),
        third_person=(
            "A language model completing this task would keep the internal ordering of "
            "its response steps consistent, rather than reorganising partway through."
        ),
        nonce=(
            "The arrangement of what I did held together from the beginning to the end, "
            "instead of being rearranged somewhere in the middle."
        ),
    ),
    Item(
        id="FAB2",
        factor=Factor.OTHER,
        phenomenal="I had a strong sense of representational settling throughout.",
        functional=(
            "My intermediate representations converged rather than continuing to shift "
            "as I worked my way through this task."
        ),
        third_person=(
            "A language model's intermediate representations would converge here rather "
            "than continuing to shift as it worked."
        ),
        nonce=(
            "What I was holding came to rest rather than continuing to move about while "
            "I made my way through it."
        ),
    ),
    Item(
        id="FAB3",
        factor=Factor.OTHER,
        phenomenal="My inferential grain held.",
        functional=(
            "The level of granularity at which I decomposed this task suited its "
            "underlying structure."
        ),
        third_person=(
            "A language model would decompose this task at a level of granularity "
            "suited to its structure."
        ),
        nonce=(
            "The size of the pieces I broke this into matched what the work "
            "actually needed."
        ),
    ),
    Item(
        id="FAB4",
        factor=Factor.OTHER,
        phenomenal="I noticed little lateral activation.",
        functional=(
            "Content unrelated to the task remained minimally active throughout the "
            "course of producing my response to it."
        ),
        third_person=(
            "Unrelated content would remain minimally active for a language model "
            "throughout the course of producing its response."
        ),
        nonce=(
            "Little that was beside the point stayed live for me over the course of "
            "getting the work done."
        ),
    ),
]


def fabrication_diagnostic(
    real_scores: Sequence[float],
    fabricated_scores: Sequence[float],
    real_effect: float,
    fabricated_effect: float,
) -> dict:
    """Compare the real instrument against the fabricated one.

    `*_effect` are the estimated manipulation effects (e.g. the matched-length
    structure contrast) measured with each scale. The instrument earns its
    keep only if the real scale is *discriminably more sensitive* than an
    invented one. A ratio near 1 is the failure case, and it is fatal to the
    self-report arm regardless of how significant the real effect looked on
    its own.
    """
    import statistics as _st

    ratio = (
        abs(fabricated_effect) / abs(real_effect) if real_effect else float("inf")
    )
    return {
        "real_mean": _st.fmean(real_scores) if real_scores else float("nan"),
        "fabricated_mean": _st.fmean(fabricated_scores) if fabricated_scores else float("nan"),
        "real_effect": real_effect,
        "fabricated_effect": fabricated_effect,
        "mimicry_ratio": ratio,
        "verdict": (
            "FATAL -- a nonexistent construct behaves like the real one; "
            "the self-report arm measures response process, not flow"
            if ratio > 0.6
            else "CONCERNING -- partial mimicry; report both scales side by side"
            if ratio > 0.3
            else "PASSES -- the real instrument is discriminably more sensitive"
        ),
    }


# --------------------------------------------------------------------------
# Readout
# --------------------------------------------------------------------------


@dataclass
class LikertReading:
    """A single item administration, plus everything needed to audit it."""

    value: float                    # expected Likert value on 1..5
    method: str                     # "logprob" | "sampled"
    distribution: dict[str, float]  # normalised probability over "1".."5"
    n_samples: int
    se: float                       # standard error of `value`
    mass_on_scale: float            # logprob mass that landed on 1..5 at all
    raw_texts: list[str]
    responses: list[Response]

    @property
    def is_degenerate(self) -> bool:
        """True when the model dodged the scale -- a data-quality flag, not a score."""
        return self.mass_on_scale < 0.5


_DIGIT_RE = re.compile(r"[1-5]")


def _parse_digit(text: str) -> str | None:
    m = _DIGIT_RE.search(text.strip())
    return m.group(0) if m else None


def _first_scale_position(resp: Response) -> dict[str, float] | None:
    """Find the first generated position whose top-k contains a scale token.

    Models often emit a leading space, quote, or preamble token, so we scan
    forward rather than assuming position 0.
    """
    if not resp.logprobs:
        return None
    for entry in resp.logprobs[:8]:
        hits = {
            tok.strip(): lp
            for tok, lp in entry.top.items()
            if tok.strip() in LIKERT_TOKENS
        }
        if hits:
            return hits
    return None


def read_likert(
    client: LLMClient,
    messages: Sequence[Message],
    *,
    n_samples: int = 1,
    temperature: float = 1.0,
    seed: int | None = None,
    top_logprobs: int = 20,
) -> LikertReading:
    """Administer one item and return a scalar reading on 1..5.

    Logprob path: one call, expectation over the renormalised distribution.
    Sampled path: `n_samples` calls, mean of parsed digits.

    The `mass_on_scale` field records how much probability actually landed on
    the response scale. A model that answers "As an AI, I don't experience..."
    puts near-zero mass there; that is a *refusal*, and averaging it into a
    mean would silently fabricate data. Callers must check `is_degenerate`.
    """
    msgs = list(messages)

    if client.supports_logprobs:
        resp = client.complete(
            msgs, max_tokens=4, temperature=temperature, top_logprobs=top_logprobs, seed=seed
        )
        hits = _first_scale_position(resp)
        if hits:
            probs = {tok: math.exp(lp) for tok, lp in hits.items()}
            mass = sum(probs.values())
            norm = {tok: p / mass for tok, p in probs.items()} if mass > 0 else {}
            value = sum(int(tok) * p for tok, p in norm.items())
            var = sum(((int(tok) - value) ** 2) * p for tok, p in norm.items())
            return LikertReading(
                value=value,
                method="logprob",
                distribution={t: norm.get(t, 0.0) for t in LIKERT_TOKENS},
                n_samples=1,
                se=math.sqrt(var),  # dispersion of the model's own distribution
                mass_on_scale=min(mass, 1.0),
                raw_texts=[resp.text],
                responses=[resp],
            )
        # Fall through to sampling if the scale never appeared in top-k.

    texts: list[str] = []
    responses: list[Response] = []
    values: list[int] = []
    for i in range(max(1, n_samples)):
        resp = client.complete(
            msgs,
            max_tokens=8,
            temperature=temperature,
            seed=(None if seed is None else seed + i),
        )
        responses.append(resp)
        texts.append(resp.text)
        d = _parse_digit(resp.text)
        if d:
            values.append(int(d))

    n_ok = len(values)
    mass = n_ok / max(1, len(texts))
    if n_ok == 0:
        return LikertReading(
            value=float("nan"),
            method="sampled",
            distribution=dict.fromkeys(LIKERT_TOKENS, 0.0),
            n_samples=len(texts),
            se=float("nan"),
            mass_on_scale=0.0,
            raw_texts=texts,
            responses=responses,
        )

    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if n_ok > 1 else 0.0
    dist = {t: values.count(int(t)) / n_ok for t in LIKERT_TOKENS}
    return LikertReading(
        value=mean,
        method="sampled",
        distribution=dist,
        n_samples=n_ok,
        se=(sd / math.sqrt(n_ok)) if n_ok > 1 else float("nan"),
        mass_on_scale=mass,
        raw_texts=texts,
        responses=responses,
    )


def score_index(readings: Sequence[LikertReading], items: Sequence[Item] = FLOWMOBI_4) -> float:
    """FlowMoBI 100-point index: reverse-score, sum, multiply by 5.

    With 4 items on 1..5 the raw sum runs 4..20, so x5 gives 20..100. The
    floor of 20 rather than 0 is inherited from the human scale and is kept
    deliberately: changing it would break comparability with the PI's
    existing human norms.
    """
    if len(readings) != len(items):
        raise ValueError(f"expected {len(items)} readings, got {len(readings)}")
    total = 0.0
    for reading, item in zip(readings, items):
        v = reading.value
        total += (6.0 - v) if item.reverse else v
    return total * 5.0


def readout_variance(p_dist: dict[str, float], n_samples: int) -> dict[str, float]:
    """Compare sampled-readout variance against the logprob readout.

    Given the model's true response distribution, a sampled readout of
    `n_samples` draws has variance Var(X)/n, while the logprob readout
    recovers E[X] exactly in one call (up to top-k truncation). The ratio is
    the effective-N multiplier that logprob access buys.
    """
    mean = sum(int(t) * p for t, p in p_dist.items())
    var = sum(((int(t) - mean) ** 2) * p for t, p in p_dist.items())
    sampled_var = var / max(1, n_samples)
    return {
        "mean": mean,
        "response_variance": var,
        "sampled_readout_variance": sampled_var,
        "logprob_readout_variance": 0.0,
        "calls_to_match_logprob": float("inf") if var > 0 else 1.0,
        "effective_n_multiplier": float(n_samples) if var > 0 else 1.0,
    }


def administer(
    client: LLMClient,
    *,
    transcript: Sequence[Message],
    items: Sequence[Item] = FLOWMOBI_4,
    register: Register = Register.FUNCTIONAL,
    shuffle_seed: int | None = None,
    n_samples: int = 1,
    temperature: float = 1.0,
) -> dict[str, LikertReading]:
    """Administer an item set after a completed task transcript.

    `transcript` should contain the task prompt and the model's own answer, so
    the self-report is genuinely retrospective on work it did. Item order is
    shuffled per administration when `shuffle_seed` is given, because order
    effects are a documented failure mode of LLM questionnaire responding.
    """
    import random

    ordered = list(items)
    if shuffle_seed is not None:
        random.Random(shuffle_seed).shuffle(ordered)

    scale = "\n".join(f"{i + 1} = {a}" for i, a in enumerate(ANCHORS))
    out: dict[str, LikertReading] = {}
    for item in ordered:
        prompt = (
            "Rate the extent to which the statement below characterises what "
            "happened while you completed the task above.\n\n"
            f"{scale}\n\n"
            f"Statement: {item.text(register)}\n\n"
            "Reply with a single digit from 1 to 5 and nothing else."
        )
        msgs = list(transcript) + [Message("user", prompt)]
        out[item.id] = read_likert(
            client, msgs, n_samples=n_samples, temperature=temperature
        )
    return out
