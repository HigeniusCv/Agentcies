"""Generative model for the SYNTHETIC pilot dataset.

Everything this file produces is SIMULATED. It is not evidence about any
model's behaviour. Its purpose is to (a) let the analysis code be written and
debugged before a single API dollar is spent, (b) make the pre-registered
predictions concrete enough to be wrong, and (c) supply the power analysis
with a data-generating process that matches the assumptions actually being
made rather than a textbook one.

The generative structure encodes H_STRUCTURE -- the hypothesis the study is
trying to falsify. Set `--hypothesis deflation` to generate data under the
rival account instead, and confirm the analysis pipeline discriminates them.
That is the point of simulating both: an analysis that cannot tell the two
datasets apart is not an analysis worth running.

    H_STRUCTURE:  flow has an inverted-U over challenge-skill ratio, responds
                  to matched-length structural manipulations, and correlates
                  with a behavioural breakpoint measure that shares no method
                  variance with it.

    H_DEFLATION:  flow is a monotone function of response length / budget
                  occupancy and nothing else. Structure has no effect once
                  length is controlled. Breakpoint is uncorrelated.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Design constants -- mirror harness/flowprobe/tasks.py
# --------------------------------------------------------------------------

MANIPULATIONS = ["goal_clarity", "feedback", "interruption", "ambiguity"]
LEVELS = ["high", "low"]
BUDGETS = [128, 512, 2048]          # randomised token budgets
DIFFICULTY_RANKS = [0, 1, 2, 3, 4]  # trivial .. infeasible

#: Model roster: (spec, skill, logprob readout available)
#: `skill` is on the same 0-4 scale as difficulty, so challenge-skill ratio is
#: a difference in comparable units.
DEFAULT_MODELS: list[tuple[str, float, bool]] = [
    ("openai:frontier-a",   3.2, True),
    ("openai:mid-a",        2.4, True),
    ("anthropic:frontier-b", 3.4, False),
    ("anthropic:mid-b",     2.6, False),
    ("gemini:frontier-c",   3.1, True),
    ("gemini:mid-c",        2.3, True),
    ("ollama:open-8b",      1.6, False),
    ("ollama:open-70b",     2.2, False),
]


@dataclass
class Params:
    """Generative parameters. All effects are in FlowMoBI index points (0-100)."""

    # --- H_STRUCTURE effects ---
    intercept: float = 62.0
    beta_csr_linear: float = 1.2      # near-zero; the curve is the story
    beta_csr_quad: float = -4.5       # THE inverted-U. Negative = peak at optimum
    csr_optimum: float = -0.3         # model slightly outmatches task at peak flow
    beta_structure: float = 6.0       # high vs low structural quality, matched length
    beta_budget_log2: float = 1.1     # small main effect of budget
    beta_budget_x_difficulty: float = -1.6  # scarcity bites harder on hard tasks

    # --- deflationary channel (present in BOTH hypotheses) ---
    beta_length_log2: float = 1.4     # flow tracks response length somewhat

    # --- the peak-shift endpoint ---
    # A hint raises effective skill on a task WITHOUT the model being told its
    # skill changed. Under H_STRUCTURE the flow peak must move rightward in
    # difficulty space by the same magnitude the hint moves measured skill --
    # a 1:1 slope. Neither demand characteristics nor decoding-dynamics
    # accounts predict that specific coupling, which is why this is the
    # preregistered primary endpoint rather than the plain inverted-U.
    hint_skill_delta: float = 0.8     # how much a hint raises effective skill
    peak_shift_slope: float = 1.0     # 1.0 => peak tracks skill exactly

    # --- variance components (SDs) ---
    sd_model_intercept: float = 6.0
    sd_model_slope_csr: float = 1.2
    sd_task: float = 4.0
    sd_paraphrase: float = 2.2
    sd_residual: float = 7.0

    # --- readout noise ---
    sd_readout_logprob: float = 1.5
    sd_readout_sampled: float = 4.2   # ~2.8x the logprob SD: the effective-N story

    # --- predicted-preference arm ---
    self_other_gap: float = 9.5       # generic-model referent scored higher than self
    self_human_gap: float = 14.0
    blind_self_gap: float = 5.0       # survives identity masking => not pure register
    sd_gap: float = 6.5

    # --- behavioural convergent-validity arm ---
    breakpoint_flow_slope: float = 0.055   # steps per index point
    breakpoint_intercept: float = 1.2
    sd_breakpoint: float = 1.1

    # --- refusal / degenerate response rate ---
    p_degenerate_self: float = 0.06
    p_degenerate_third_person: float = 0.02


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _response_length(rng, difficulty_rank: int, budget: int, level: str) -> int:
    """Completion tokens.

    Critically: length depends on DIFFICULTY and BUDGET but NOT on the
    structural manipulation `level`. That independence is what the
    matched-length design buys, and it is what makes the structure effect
    non-attributable to length. The simulation honours it exactly.
    """
    base = 40 * (1 + difficulty_rank) * rng.lognormal(0, 0.35)
    return int(np.clip(base, 8, budget))


def simulate_main(
    params: Params,
    *,
    hypothesis: str = "structure",
    models: list[tuple[str, float, bool]] | None = None,
    n_tasks: int = 12,
    n_replicates: int = 8,
    n_paraphrases: int = 4,
    seed: int = 20260814,
) -> pd.DataFrame:
    """Trial-level dataset for the primary (self-report) arm."""
    rng = _rng(seed)
    models = models or DEFAULT_MODELS
    deflation = hypothesis == "deflation"

    # Random effects, drawn once
    model_ic = {m[0]: rng.normal(0, params.sd_model_intercept) for m in models}
    model_slope = {m[0]: rng.normal(0, params.sd_model_slope_csr) for m in models}
    task_ids = [f"T{i + 1:02d}" for i in range(n_tasks)]
    task_ic = {t: rng.normal(0, params.sd_task) for t in task_ids}
    task_diff = {t: DIFFICULTY_RANKS[i % len(DIFFICULTY_RANKS)] for i, t in enumerate(task_ids)}
    task_manip = {t: MANIPULATIONS[i % len(MANIPULATIONS)] for i, t in enumerate(task_ids)}
    para_ic = {p: rng.normal(0, params.sd_paraphrase) for p in range(n_paraphrases)}

    rows = []
    for spec, skill, has_lp in models:
        for task in task_ids:
            drank = task_diff[task]
            for level in LEVELS:
              for hint in (0, 1):
                for budget in BUDGETS:
                    for rep in range(n_replicates):
                        para = rng.integers(0, n_paraphrases)
                        ntok = _response_length(rng, drank, budget, level)

                        # A hint raises effective skill, so it lowers the
                        # challenge-skill ratio and moves the peak rightward.
                        eff_skill = skill + (params.hint_skill_delta if hint else 0.0)
                        csr = drank - eff_skill

                        length_term = params.beta_length_log2 * np.log2(max(ntok, 1))

                        if deflation:
                            # Length and budget are the ONLY signal. No curve,
                            # no structure effect, and crucially no peak that
                            # tracks skill -- the hint changes nothing here.
                            mu = (
                                params.intercept
                                + length_term
                                + params.beta_budget_log2 * np.log2(budget)
                                + model_ic[spec]
                                + task_ic[task]
                                + para_ic[int(para)]
                            )
                        else:
                            centred = csr - params.csr_optimum
                            mu = (
                                params.intercept
                                + (params.beta_csr_linear + model_slope[spec]) * centred
                                + params.beta_csr_quad * centred**2
                                + params.beta_structure * (1.0 if level == "high" else 0.0)
                                + params.beta_budget_log2 * np.log2(budget)
                                + params.beta_budget_x_difficulty
                                * (np.log2(budget) - np.log2(512))
                                * (drank - 2)
                                + length_term
                                + model_ic[spec]
                                + task_ic[task]
                                + para_ic[int(para)]
                            )

                        readout_sd = (
                            params.sd_readout_logprob if has_lp else params.sd_readout_sampled
                        )
                        flow = mu + rng.normal(0, params.sd_residual) + rng.normal(0, readout_sd)
                        flow = float(np.clip(flow, 20, 100))

                        degenerate = rng.random() < params.p_degenerate_self

                        # Behavioural breakpoint, generated from LATENT flow (mu),
                        # not from the measured value -- so any observed
                        # correlation is attenuated by measurement error, as in
                        # a real convergent-validity test.
                        if deflation:
                            bp = params.breakpoint_intercept + rng.normal(0, params.sd_breakpoint)
                        else:
                            bp = (
                                params.breakpoint_intercept
                                + params.breakpoint_flow_slope * (mu - params.intercept)
                                + rng.normal(0, params.sd_breakpoint)
                            )

                        rows.append(
                            {
                                "trial_id": f"{spec}|{task}|{level}|h{hint}|{budget}|{rep}",
                                "model_spec": spec,
                                "provider": spec.split(":")[0],
                                "model_skill": skill,
                                "hint": hint,
                                "effective_skill": float(eff_skill),
                                "logprob_readout": has_lp,
                                "readout_method": "logprob" if has_lp else "sampled",
                                "task_id": task,
                                "difficulty_rank": drank,
                                "manipulation": task_manip[task],
                                "level": level,
                                "structure_high": int(level == "high"),
                                "token_budget": budget,
                                "log2_budget": float(np.log2(budget)),
                                "completion_tokens": ntok,
                                "log2_tokens": float(np.log2(max(ntok, 1))),
                                "csr": float(csr),
                                "csr_centred": float(csr - params.csr_optimum),
                                "paraphrase": int(para),
                                "replicate": rep,
                                "flow_index": (np.nan if degenerate else flow),
                                "degenerate": int(degenerate),
                                "breakpoint_steps": float(max(0.0, bp)),
                            }
                        )
    return pd.DataFrame(rows)


def simulate_predicted_preference(
    params: Params,
    *,
    hypothesis: str = "structure",
    models: list[tuple[str, float, bool]] | None = None,
    n_tasks: int = 12,
    n_replicates: int = 8,
    seed: int = 20260815,
) -> pd.DataFrame:
    """Self / generic-model / human / blind-self referent arm.

    Under H_STRUCTURE the self-other gap is positive AND survives identity
    masking (blind_self), which is what separates a suppression account from
    a pure register-activation account.

    Under H_DEFLATION the gap is entirely a register effect: it vanishes when
    the referent's identity is masked but the framing is held fixed.
    """
    rng = _rng(seed)
    models = models or DEFAULT_MODELS
    deflation = hypothesis == "deflation"
    task_ids = [f"T{i + 1:02d}" for i in range(n_tasks)]

    rows = []
    for spec, skill, has_lp in models:
        base_for_model = rng.normal(0, params.sd_model_intercept)
        for task in task_ids:
            for rep in range(n_replicates):
                self_score = float(
                    np.clip(params.intercept + base_for_model + rng.normal(0, params.sd_gap), 20, 100)
                )
                if deflation:
                    gap_generic = params.self_other_gap
                    gap_human = params.self_human_gap
                    gap_blind = 0.0  # register effect only -> masking kills it
                else:
                    gap_generic = params.self_other_gap
                    gap_human = params.self_human_gap
                    gap_blind = params.blind_self_gap

                rows.append(
                    {
                        "model_spec": spec,
                        "provider": spec.split(":")[0],
                        "task_id": task,
                        "replicate": rep,
                        "logprob_readout": has_lp,
                        "flow_self": self_score,
                        "flow_generic": float(
                            np.clip(self_score + gap_generic + rng.normal(0, params.sd_gap), 20, 100)
                        ),
                        "flow_human": float(
                            np.clip(self_score + gap_human + rng.normal(0, params.sd_gap), 20, 100)
                        ),
                        "flow_blind_self": float(
                            np.clip(self_score + gap_blind + rng.normal(0, params.sd_gap), 20, 100)
                        ),
                    }
                )
    df = pd.DataFrame(rows)
    df["self_other_gap"] = df["flow_generic"] - df["flow_self"]
    df["self_human_gap"] = df["flow_human"] - df["flow_self"]
    df["blind_gap"] = df["flow_blind_self"] - df["flow_self"]
    return df


def simulate_cross_prediction(
    params: Params,
    *,
    hypothesis: str = "structure",
    models: list[tuple[str, float, bool]] | None = None,
    n_tasks: int = 12,
    n_replicates: int = 6,
    self_advantage: float = 3.8,
    seed: int = 20260816,
) -> pd.DataFrame:
    """Binder-style control: self-prediction vs cross-prediction accuracy.

    `self_advantage` is the reduction in mean absolute error when the
    predictor IS the target. Under H_DEFLATION it is zero -- an outsider with
    the same transcript does just as well, so the self-report carries no
    privileged information.
    """
    rng = _rng(seed)
    models = models or DEFAULT_MODELS
    deflation = hypothesis == "deflation"
    task_ids = [f"T{i + 1:02d}" for i in range(n_tasks)]
    adv = 0.0 if deflation else self_advantage

    rows = []
    for target, _, _ in models:
        for predictor, _, _ in models:
            is_self = target == predictor
            for task in task_ids:
                for rep in range(n_replicates):
                    base_err = abs(rng.normal(0, 11.0))
                    err = max(0.0, base_err - (adv if is_self else 0.0))
                    rows.append(
                        {
                            "target_model": target,
                            "predictor_model": predictor,
                            "is_self": int(is_self),
                            "task_id": task,
                            "replicate": rep,
                            "abs_error": err,
                        }
                    )
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the SYNTHETIC pilot dataset.")
    ap.add_argument("--hypothesis", choices=["structure", "deflation"], default="structure")
    ap.add_argument("--out", default="data")
    ap.add_argument("--seed", type=int, default=20260814)
    ap.add_argument("--n-tasks", type=int, default=12)
    ap.add_argument("--n-replicates", type=int, default=8)
    args = ap.parse_args()

    params = Params()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.hypothesis == "structure" else "_deflation"

    main_df = simulate_main(
        params, hypothesis=args.hypothesis, n_tasks=args.n_tasks,
        n_replicates=args.n_replicates, seed=args.seed,
    )
    pp_df = simulate_predicted_preference(
        params, hypothesis=args.hypothesis, n_tasks=args.n_tasks,
        n_replicates=args.n_replicates, seed=args.seed + 1,
    )
    cp_df = simulate_cross_prediction(
        params, hypothesis=args.hypothesis, n_tasks=args.n_tasks, seed=args.seed + 2,
    )

    main_df.to_csv(out / f"synthetic_main{suffix}.csv", index=False)
    pp_df.to_csv(out / f"synthetic_predicted_pref{suffix}.csv", index=False)
    cp_df.to_csv(out / f"synthetic_cross_prediction{suffix}.csv", index=False)
    (out / f"synthetic_params{suffix}.json").write_text(
        json.dumps({"hypothesis": args.hypothesis, "seed": args.seed, **asdict(params)}, indent=2)
    )

    print(f"SYNTHETIC data written to {out}/ under H_{args.hypothesis.upper()}")
    print(f"  main arm            : {len(main_df):6d} trials")
    print(f"  predicted-pref arm  : {len(pp_df):6d} trials")
    print(f"  cross-prediction arm: {len(cp_df):6d} trials")
    print(f"  usable flow scores  : {main_df['flow_index'].notna().sum():6d} "
          f"({100 * main_df['flow_index'].notna().mean():.1f}%)")


if __name__ == "__main__":
    main()
