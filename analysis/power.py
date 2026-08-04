"""Power and MDES for LLM-subject designs.

The single most consequential fact in this whole project:

    Effects manipulated WITHIN a (model, task) cell -- the matched-length
    structural manipulations, token budget, item register -- gain precision
    from replicates. Effects that vary BETWEEN tasks or BETWEEN models --
    challenge-skill ratio, model family, difficulty -- do not. Their standard
    error is floored by the cluster-level variance component, so buying more
    API calls buys nothing at all past a few dozen per cell.

That asymmetry is why "we ran 100,000 completions" is not a power argument,
and why the binding constraints on this study are the number of TASKS and the
number of MODELS. It is also the cheapest possible mistake to avoid, since
recognising it moves budget from replicates (useless past saturation) to task
authoring (the actual bottleneck).

Formulae used, for a balanced design with `k` clusters and `m` replicates per
condition per cluster:

    within-cluster contrast:   SE = sqrt( s2_slope/k + 2*s2_resid/(k*m) )
                               -> floor sqrt(s2_slope/k)     as m -> inf
    between-cluster predictor: SE = sqrt( (s2_cluster + s2_resid/m) / (k*Vx) )
                               -> floor sqrt(s2_cluster/(k*Vx))

MDES is then t_crit * SE with t = 1.96 + 0.84 for 80% power (two-sided .05).
`validate_by_simulation` checks these closed forms against Monte Carlo.
"""

from __future__ import annotations

import argparse
import math

import numpy as np
import pandas as pd
from scipy import stats

from simulate import Params

Z_ALPHA = 1.959964
Z_POWER = 0.8416212  # 80%


def mdes_within(
    k_cells: int,
    m_reps: int,
    *,
    sd_resid: float,
    sd_slope: float,
    power: float = 0.80,
) -> float:
    """MDES for a manipulation applied within each (model, task) cell."""
    z_pow = stats.norm.ppf(power)
    se = math.sqrt(sd_slope**2 / k_cells + 2 * sd_resid**2 / (k_cells * m_reps))
    return (Z_ALPHA + z_pow) * se


def mdes_between(
    k_clusters: int,
    m_reps: int,
    *,
    sd_resid: float,
    sd_cluster: float,
    var_x: float = 1.0,
    power: float = 0.80,
) -> float:
    """MDES for a predictor that varies only between clusters (tasks/models)."""
    z_pow = stats.norm.ppf(power)
    se = math.sqrt((sd_cluster**2 + sd_resid**2 / m_reps) / (k_clusters * var_x))
    return (Z_ALPHA + z_pow) * se


def saturation_point(
    k_cells: int, *, sd_resid: float, sd_slope: float, tol: float = 0.05
) -> int:
    """Replicates past which MDES improves by less than `tol` of its floor."""
    floor = math.sqrt(sd_slope**2 / k_cells)
    if floor <= 0:
        return 10**6
    for m in range(1, 10001):
        se = math.sqrt(sd_slope**2 / k_cells + 2 * sd_resid**2 / (k_cells * m))
        if (se - floor) / floor < tol:
            return m
    return 10000


def mdes_grid(params: Params, powers: float = 0.80) -> pd.DataFrame:
    """MDES table over the design grid, in FlowMoBI index points."""
    rows = []
    for n_models in (3, 5, 8, 12, 20):
        for n_tasks in (6, 12, 24, 48):
            k = n_models * n_tasks
            for m in (1, 4, 8, 16, 32):
                within = mdes_within(
                    k, m, sd_resid=params.sd_residual,
                    sd_slope=params.sd_model_slope_csr, power=powers,
                )
                between_task = mdes_between(
                    n_tasks, m * n_models,
                    sd_resid=params.sd_residual, sd_cluster=params.sd_task,
                    var_x=2.0, power=powers,
                )
                between_model = mdes_between(
                    n_models, m * n_tasks,
                    sd_resid=params.sd_residual, sd_cluster=params.sd_model_intercept,
                    var_x=1.0, power=powers,
                )
                rows.append(
                    {
                        "n_models": n_models,
                        "n_tasks": n_tasks,
                        "n_replicates": m,
                        "n_calls": k * m * 2 * 3,  # x2 levels, x3 budgets
                        "mdes_within_structure": round(within, 2),
                        "mdes_between_task_csr": round(between_task, 2),
                        "mdes_between_model": round(between_model, 2),
                    }
                )
    return pd.DataFrame(rows)


def validate_by_simulation(
    params: Params, *, k_cells: int = 96, m_reps: int = 8, n_sims: int = 400,
    true_effect: float = 6.0, seed: int = 7,
) -> dict:
    """Monte-Carlo check that the closed-form MDES is not fantasy."""
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sims):
        cell_slope = rng.normal(0, params.sd_model_slope_csr, k_cells)
        hi = true_effect + cell_slope[:, None] + rng.normal(
            0, params.sd_residual, (k_cells, m_reps)
        )
        lo = rng.normal(0, params.sd_residual, (k_cells, m_reps))
        contrasts = hi.mean(axis=1) - lo.mean(axis=1)
        t, p = stats.ttest_1samp(contrasts, 0)
        hits += int(p < 0.05)
    empirical = hits / n_sims
    predicted = mdes_within(
        k_cells, m_reps, sd_resid=params.sd_residual, sd_slope=params.sd_model_slope_csr
    )
    return {
        "true_effect": true_effect,
        "empirical_power": empirical,
        "mdes_at_80pct": round(predicted, 2),
        "closed_form_consistent": bool(
            (true_effect >= predicted and empirical >= 0.75)
            or (true_effect < predicted and empirical < 0.85)
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/mdes_grid.csv")
    args = ap.parse_args()
    p = Params()

    grid = mdes_grid(p)
    grid.to_csv(args.out, index=False)

    print("=" * 84)
    print("MDES (FlowMoBI index points) at 80% power, alpha=.05 two-sided")
    print("=" * 84)
    head = grid[grid.n_replicates.isin([1, 8, 32])].copy()
    key = head[head.n_models.isin([3, 8, 20]) & head.n_tasks.isin([6, 12, 48])]
    print(key.to_string(index=False))

    print("\n" + "=" * 84)
    print("REPLICATE SATURATION -- where extra API calls stop buying precision")
    print("=" * 84)
    print(f"{'n_models':>9} {'n_tasks':>8} {'cells':>7} {'sat_reps':>9} "
          f"{'MDES@sat':>9} {'MDES@inf':>9}")
    for n_models in (3, 5, 8, 12, 20):
        for n_tasks in (6, 12, 24):
            k = n_models * n_tasks
            sat = saturation_point(k, sd_resid=p.sd_residual, sd_slope=p.sd_model_slope_csr)
            at_sat = mdes_within(k, sat, sd_resid=p.sd_residual, sd_slope=p.sd_model_slope_csr)
            at_inf = (Z_ALPHA + Z_POWER) * math.sqrt(p.sd_model_slope_csr**2 / k)
            print(f"{n_models:>9} {n_tasks:>8} {k:>7} {sat:>9} {at_sat:>9.2f} {at_inf:>9.2f}")

    print("\n" + "=" * 84)
    print("BETWEEN-TASK PREDICTORS DO NOT BENEFIT FROM REPLICATES")
    print("=" * 84)
    print(f"{'n_tasks':>8} {'reps=1':>9} {'reps=8':>9} {'reps=64':>9} {'reps=inf':>9}")
    for n_tasks in (6, 12, 24, 48, 96):
        vals = [
            mdes_between(n_tasks, m, sd_resid=p.sd_residual,
                         sd_cluster=p.sd_task, var_x=2.0)
            for m in (1, 8, 64)
        ]
        floor = (Z_ALPHA + Z_POWER) * math.sqrt(p.sd_task**2 / (n_tasks * 2.0))
        print(f"{n_tasks:>8} {vals[0]:>9.2f} {vals[1]:>9.2f} {vals[2]:>9.2f} {floor:>9.2f}")
    print("\nRead the last two columns: going from 8 to 64 replicates -- an 8x cost")
    print("increase -- moves the between-task MDES by a rounding error. Spend the")
    print("money on more tasks instead.")

    print("\n" + "=" * 84)
    print("MONTE-CARLO VALIDATION OF THE CLOSED FORM")
    print("=" * 84)
    for eff in (2.0, 4.0, 6.0):
        r = validate_by_simulation(p, true_effect=eff)
        print(f"  true effect {eff:>4.1f} pts -> empirical power {r['empirical_power']:.3f}  "
              f"(MDES at 80% = {r['mdes_at_80pct']} pts)  consistent={r['closed_form_consistent']}")

    print(f"\nGrid written to {args.out} ({len(grid)} rows)")


if __name__ == "__main__":
    main()
