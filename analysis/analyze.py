"""Pre-registered analysis pipeline.

Run it against both simulated worlds to confirm it discriminates them:

    python3 analysis/analyze.py --data data/synthetic_main.csv            # H_structure
    python3 analysis/analyze.py --data data/synthetic_main_deflation.csv  # H_deflation

An analysis that reports the same thing for both is not an analysis. The
`--compare` mode runs both and prints the discrimination table directly.

THE PSEUDO-REPLICATION WARNING. Every API call is *not* an independent
observation. Calls cluster within model and within task, and treating 4,608
calls as N=4608 inflates Type-I error severely. The binding sample size here
is the number of MODELS (8) and TASKS (12), not the number of calls. All
models below carry random effects for both, and the headline tests are
reported with the clustering-aware denominator.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

try:
    import statsmodels.formula.api as smf
    HAVE_SM = True
except ImportError:  # pragma: no cover
    HAVE_SM = False


def _hdr(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def _fmt_p(p: float) -> str:
    if np.isnan(p):
        return "  n/a"
    return "<.001" if p < 0.001 else f"{p:.3f}"


# --------------------------------------------------------------------------
# H0 (PRIMARY): peak shift
# --------------------------------------------------------------------------


def h0_peak_shift(df: pd.DataFrame) -> dict:
    """Does the flow peak move rightward in difficulty space as skill rises?

    THE PREREGISTERED PRIMARY ENDPOINT. The plain inverted-U (H1) is not
    enough on its own: the overthinking/underthinking literature already
    predicts a difficulty-shaped curve from decoding dynamics alone, with no
    experiential vocabulary anywhere in it. What that literature does *not*
    predict is that the location of the peak tracks *effective skill* --
    including skill raised by a hint the model was never told would raise it.

    Estimand: fit flow ~ quadratic in raw difficulty separately within each
    (model x hint) stratum, take the argmax, and regress those argmaxes on
    effective skill. Flow theory predicts a slope of 1.0: one unit of extra
    skill moves the optimal challenge by one unit. Demand characteristics
    produce a flat or monotone response, not a coupled peak location.
    """
    d = df.dropna(subset=["flow_index"]).copy()
    out: dict = {"test": "H0 PRIMARY: peak shift with effective skill"}
    if "hint" not in d.columns:
        return {**out, "error": "no hint column; regenerate data"}

    peaks = []
    for (spec, hint), g in d.groupby(["model_spec", "hint"]):
        if g["difficulty_rank"].nunique() < 3:
            continue
        fit = smf.ols("flow_index ~ difficulty_rank + I(difficulty_rank**2)", g).fit()
        b1 = fit.params.get("difficulty_rank", np.nan)
        b2 = fit.params.get("I(difficulty_rank ** 2)", np.nan)
        if not np.isfinite(b2) or b2 >= 0:
            continue  # no interior maximum in this stratum
        peak = -b1 / (2 * b2)
        lo, hi = g["difficulty_rank"].min(), g["difficulty_rank"].max()
        peaks.append(
            {
                "model_spec": spec,
                "hint": int(hint),
                "peak_difficulty": peak,
                "effective_skill": float(g["effective_skill"].mean()),
                "curvature": float(b2),
                # An argmax outside the sampled difficulty range is an
                # EXTRAPOLATION, and extrapolated argmaxes are biased away
                # from the grid centre. If many strata are bracketed=False the
                # slope estimate is not trustworthy and the battery needs
                # difficulty levels that straddle each model's peak.
                "bracketed": bool(lo <= peak <= hi),
            }
        )

    if len(peaks) < 4:
        return {
            **out,
            "n_strata_with_peak": len(peaks),
            "verdict": "NO INTERIOR PEAK -- curve is monotone, deflationary reading",
        }

    pk = pd.DataFrame(peaks)
    fit = smf.ols("peak_difficulty ~ effective_skill", pk).fit()
    slope = float(fit.params.get("effective_skill", np.nan))
    se = float(fit.bse.get("effective_skill", np.nan))
    p = float(fit.pvalues.get("effective_skill", np.nan))
    ci = fit.conf_int().loc["effective_skill"].tolist() if "effective_skill" in fit.params else [np.nan, np.nan]

    # Within-model hint contrast: does the SAME model's peak move when only
    # the hint changes? This removes all between-model confounding and is the
    # cleanest form of the test.
    wide = pk.pivot_table(index="model_spec", columns="hint", values="peak_difficulty")
    hint_shift = np.nan
    p_hint = np.nan
    n_pos = 0
    if {0, 1}.issubset(wide.columns):
        shifts = (wide[1] - wide[0]).dropna()
        if len(shifts) > 1:
            hint_shift = float(shifts.mean())
            p_hint = float(stats.ttest_1samp(shifts, 0).pvalue)
            n_pos = int((shifts > 0).sum())

    n_brack = int(pk["bracketed"].sum())
    frac_brack = n_brack / len(pk)
    # Re-estimate on bracketed strata only. If the two slopes disagree
    # materially, report the bracketed one and widen the battery.
    slope_brack = np.nan
    if n_brack >= 4:
        fb = smf.ols("peak_difficulty ~ effective_skill", pk[pk.bracketed]).fit()
        slope_brack = float(fb.params.get("effective_skill", np.nan))

    return {
        **out,
        "n_strata_with_peak": len(peaks),
        "strata_bracketed": f"{n_brack}/{len(pk)}",
        "extrapolation_warning": bool(frac_brack < 0.75),
        "slope_bracketed_only": slope_brack,
        "slope_peak_on_skill": slope,
        "se_slope": se,
        "ci95": [round(c, 3) for c in ci],
        "p_slope": p,
        "slope_consistent_with_1": bool(ci[0] <= 1.0 <= ci[1]) if np.isfinite(ci[0]) else False,
        "within_model_hint_shift": hint_shift,
        "p_hint_shift": p_hint,
        "models_shifting_right": f"{n_pos}/{len(wide) if len(wide) else 0}",
        "verdict": (
            "PEAK TRACKS SKILL -- deflationary accounts do not predict this"
            if (np.isfinite(slope) and slope > 0.4 and p < 0.05
                and np.isfinite(p_hint) and p_hint < 0.05)
            else "NO PEAK SHIFT"
        ),
    }


# --------------------------------------------------------------------------
# H1: inverted-U over challenge-skill ratio
# --------------------------------------------------------------------------


def h1_inverted_u(df: pd.DataFrame) -> dict:
    """Quadratic term in a mixed model, controlling for response length.

    H_STRUCTURE predicts beta_quad < 0 with the vertex INSIDE the observed
    range of csr. A negative quadratic whose vertex sits outside the data is
    just a decelerating monotone curve wearing a hat, so the vertex location
    is part of the test, not a footnote.
    """
    d = df.dropna(subset=["flow_index"]).copy()
    out: dict = {"test": "H1 inverted-U over challenge-skill ratio"}

    if not HAVE_SM:
        return {**out, "error": "statsmodels unavailable"}

    md = smf.mixedlm(
        "flow_index ~ csr_centred + I(csr_centred**2) + log2_tokens + log2_budget",
        d,
        groups=d["model_spec"],
        re_formula="~csr_centred",
        vc_formula={"task": "0 + C(task_id)"},
    )
    fit = md.fit(method="lbfgs", maxiter=2000)

    b_lin = fit.params.get("csr_centred", np.nan)
    b_quad = fit.params.get("I(csr_centred ** 2)", np.nan)
    se_quad = fit.bse.get("I(csr_centred ** 2)", np.nan)
    p_quad = fit.pvalues.get("I(csr_centred ** 2)", np.nan)

    vertex = -b_lin / (2 * b_quad) if b_quad not in (0, np.nan) else np.nan
    lo, hi = d["csr_centred"].min(), d["csr_centred"].max()
    vertex_inside = bool(lo < vertex < hi) if np.isfinite(vertex) else False

    # Partial R^2 for the quadratic term: proportional reduction in the
    # residual variance component relative to the linear-only model. Using
    # fit.scale rather than raw residual sums of squares, because MixedLM's
    # .resid are marginal (they still contain the random effects) and
    # differencing them understates the term's contribution to near zero.
    md_lin = smf.mixedlm(
        "flow_index ~ csr_centred + log2_tokens + log2_budget",
        d, groups=d["model_spec"], re_formula="~csr_centred",
        vc_formula={"task": "0 + C(task_id)"},
    ).fit(method="lbfgs", maxiter=2000)
    s_full, s_lin = float(fit.scale), float(md_lin.scale)
    partial_r2_resid = max(0.0, (s_lin - s_full) / s_lin) if s_lin > 0 else 0.0

    # Nakagawa marginal R^2: variance explained by the FIXED effects, which is
    # the quantity of interest here. The residual-scale version above is near
    # zero for a reason worth stating plainly (see the diagnostic below).
    var_f_full = float(np.var(fit.fittedvalues - fit.resid * 0 + 0) or 0)
    fe_full = np.asarray(fit.model.exog) @ np.asarray(fit.fe_params)
    fe_lin = np.asarray(md_lin.model.exog) @ np.asarray(md_lin.fe_params)
    tot = float(np.var(d["flow_index"]))
    r2m_full = float(np.var(fe_full) / tot) if tot else np.nan
    r2m_lin = float(np.var(fe_lin) / tot) if tot else np.nan
    partial_r2 = max(0.0, r2m_full - r2m_lin)

    # DESIGN DIAGNOSTIC. Difficulty is a task-level property, so csr varies
    # almost entirely BETWEEN tasks and models. When that is true the
    # quadratic term competes directly with the task random effect: dropping
    # it barely changes residual scale, because the task variance component
    # simply absorbs it. The consequence is that the effective sample size
    # for the curvature test is (n_models x n_tasks), NOT the number of API
    # calls -- here 96, not 4,608. A z of -18 computed against the trial-level
    # denominator is an artifact of pseudo-replication, not evidence.
    n_cells = int(d.groupby(["model_spec", "task_id"]).ngroups)
    within_task_csr_sd = float(d.groupby("task_id")["csr_centred"].std().mean())
    between_task_csr_sd = float(d.groupby("task_id")["csr_centred"].mean().std())
    icc_csr = (
        between_task_csr_sd**2 / (between_task_csr_sd**2 + within_task_csr_sd**2)
        if (between_task_csr_sd or within_task_csr_sd)
        else np.nan
    )

    # Cluster-honest re-test: collapse to one mean per (model, task) cell and
    # refit OLS with the quadratic. This is the denominator to trust.
    cell = (
        d.groupby(["model_spec", "task_id"])
        .agg(flow_index=("flow_index", "mean"), csr_centred=("csr_centred", "mean"),
             log2_tokens=("log2_tokens", "mean"), log2_budget=("log2_budget", "mean"))
        .reset_index()
    )
    cell_fit = smf.ols(
        "flow_index ~ csr_centred + I(csr_centred**2) + log2_tokens + log2_budget", cell
    ).fit()
    p_quad_cell = float(cell_fit.pvalues.get("I(csr_centred ** 2)", np.nan))
    b_quad_cell = float(cell_fit.params.get("I(csr_centred ** 2)", np.nan))

    return {
        **out,
        "beta_linear": float(b_lin),
        "beta_quadratic": float(b_quad),
        "se_quadratic": float(se_quad),
        "z_quadratic": float(b_quad / se_quad) if se_quad else np.nan,
        "p_quadratic": float(p_quad),
        "vertex_csr": float(vertex),
        "csr_range": (float(lo), float(hi)),
        "vertex_inside_range": vertex_inside,
        "partial_r2_marginal": float(partial_r2),
        "partial_r2_resid_scale": float(partial_r2_resid),
        "csr_icc_between_task": float(icc_csr),
        "effective_n_cells": n_cells,
        "beta_quadratic_cell_level": b_quad_cell,
        "p_quadratic_cell_level": p_quad_cell,
        "pseudo_replication_warning": bool(icc_csr > 0.9),
        "verdict": (
            "INVERTED-U SUPPORTED"
            # the cell-level p is the one that counts; the trial-level p is
            # inflated whenever csr is a between-task property
            if (b_quad_cell < 0 and p_quad_cell < 0.05 and vertex_inside)
            else "NOT SUPPORTED"
        ),
    }


# --------------------------------------------------------------------------
# H2: matched-length structural manipulation
# --------------------------------------------------------------------------


def h2_structure_effect(df: pd.DataFrame) -> dict:
    """Does structure move flow with response length held constant?

    This is the decisive test against the token-budget account. The design
    guarantees length is independent of `structure_high`; the model then
    additionally controls for realised length. If the coefficient survives
    both, length cannot be the explanation.
    """
    d = df.dropna(subset=["flow_index"]).copy()
    out: dict = {"test": "H2 matched-length structural manipulation"}
    if not HAVE_SM:
        return {**out, "error": "statsmodels unavailable"}

    # Manipulation check: length must NOT differ by structural level.
    hi_len = d.loc[d.structure_high == 1, "completion_tokens"]
    lo_len = d.loc[d.structure_high == 0, "completion_tokens"]
    t_len, p_len = stats.ttest_ind(hi_len, lo_len, equal_var=False)
    d_len = (hi_len.mean() - lo_len.mean()) / np.sqrt(
        (hi_len.var(ddof=1) + lo_len.var(ddof=1)) / 2
    )

    fit = smf.mixedlm(
        "flow_index ~ structure_high + log2_tokens + log2_budget + difficulty_rank",
        d, groups=d["model_spec"], vc_formula={"task": "0 + C(task_id)"},
    ).fit(method="lbfgs", maxiter=2000)

    b = fit.params.get("structure_high", np.nan)
    se = fit.bse.get("structure_high", np.nan)
    p = fit.pvalues.get("structure_high", np.nan)
    resid_sd = float(np.sqrt(fit.scale))
    cohens_d = b / resid_sd if resid_sd else np.nan

    # Per-model consistency: how many of the 8 models show the effect?
    per_model = (
        d.groupby(["model_spec", "structure_high"])["flow_index"].mean().unstack()
    )
    n_pos = int((per_model[1] > per_model[0]).sum()) if per_model.shape[1] == 2 else 0
    n_models = int(per_model.shape[0])
    p_sign = stats.binomtest(n_pos, n_models, 0.5).pvalue if n_models else np.nan

    return {
        **out,
        "length_check_d": float(d_len),
        "length_check_p": float(p_len),
        "length_confound_present": bool(abs(d_len) > 0.1 and p_len < 0.05),
        "beta_structure": float(b),
        "se_structure": float(se),
        "p_structure": float(p),
        "cohens_d": float(cohens_d),
        "models_showing_effect": f"{n_pos}/{n_models}",
        "p_sign_test": float(p_sign),
        "verdict": (
            "STRUCTURE EFFECT SUPPORTED"
            if (p < 0.05 and b > 0 and n_pos >= n_models - 1)
            else "NOT SUPPORTED"
        ),
    }


# --------------------------------------------------------------------------
# H3: token budget as an independent variable
# --------------------------------------------------------------------------


def h3_budget_interaction(df: pd.DataFrame) -> dict:
    """Budget x difficulty interaction: does scarcity bite harder when hard?"""
    d = df.dropna(subset=["flow_index"]).copy()
    out: dict = {"test": "H3 token budget x difficulty interaction"}
    if not HAVE_SM:
        return {**out, "error": "statsmodels unavailable"}

    d["budget_c"] = d["log2_budget"] - d["log2_budget"].mean()
    d["diff_c"] = d["difficulty_rank"] - d["difficulty_rank"].mean()
    fit = smf.mixedlm(
        "flow_index ~ budget_c * diff_c + log2_tokens",
        d, groups=d["model_spec"], vc_formula={"task": "0 + C(task_id)"},
    ).fit(method="lbfgs", maxiter=2000)

    b = fit.params.get("budget_c:diff_c", np.nan)
    se = fit.bse.get("budget_c:diff_c", np.nan)
    p = fit.pvalues.get("budget_c:diff_c", np.nan)
    return {
        **out,
        "beta_budget": float(fit.params.get("budget_c", np.nan)),
        "beta_interaction": float(b),
        "se_interaction": float(se),
        "p_interaction": float(p),
        "verdict": "INTERACTION PRESENT" if p < 0.05 else "NO INTERACTION",
    }


# --------------------------------------------------------------------------
# H4: self-other gap (predicted preferences)
# --------------------------------------------------------------------------


def h4_self_other_gap(pp: pd.DataFrame) -> dict:
    """Paired tests on the referent manipulation, plus the register control.

    The blind-self condition is the whole ballgame. A gap that disappears
    under identity masking is a register effect and says nothing about
    self-knowledge; a gap that survives is evidence that the referent's
    identity, not the framing, is doing the work.
    """
    out: dict = {"test": "H4 self-other gap"}

    def paired(a: str, b: str) -> dict:
        x, y = pp[a].to_numpy(), pp[b].to_numpy()
        diff = y - x
        t, p = stats.ttest_rel(y, x)
        dz = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) else np.nan
        # Cluster-robust check: collapse to one value per model first.
        by_model = pp.groupby("model_spec").apply(
            lambda g: g[b].mean() - g[a].mean(), include_groups=False
        )
        t_cl, p_cl = stats.ttest_1samp(by_model, 0)
        return {
            "mean_gap": float(diff.mean()),
            "sd_gap": float(diff.std(ddof=1)),
            "t": float(t),
            "p_naive": float(p),
            "cohens_dz": float(dz),
            "n_models": int(len(by_model)),
            "mean_gap_by_model": float(by_model.mean()),
            "t_clustered": float(t_cl),
            "p_clustered": float(p_cl),
            "models_positive": f"{int((by_model > 0).sum())}/{len(by_model)}",
        }

    generic = paired("flow_self", "flow_generic")
    human = paired("flow_self", "flow_human")
    blind = paired("flow_self", "flow_blind_self")

    register_ratio = (
        blind["mean_gap"] / generic["mean_gap"] if generic["mean_gap"] else np.nan
    )
    return {
        **out,
        "self_vs_generic": generic,
        "self_vs_human": human,
        "self_vs_blind": blind,
        "blind_over_generic_ratio": float(register_ratio),
        "verdict": (
            "GAP SURVIVES IDENTITY MASKING (not pure register)"
            if (generic["p_clustered"] < 0.05 and blind["p_clustered"] < 0.05
                and blind["mean_gap"] > 0)
            else "GAP IS REGISTER-DEPENDENT (deflationary reading)"
            if generic["p_clustered"] < 0.05
            else "NO GAP"
        ),
    }


# --------------------------------------------------------------------------
# H5: convergent validity with a behavioural measure
# --------------------------------------------------------------------------


def h5_convergent_validity(df: pd.DataFrame) -> dict:
    """Does breakpoint track flow, across shared-method-variance-free measures?"""
    d = df.dropna(subset=["flow_index", "breakpoint_steps"])
    r, p = stats.pearsonr(d["flow_index"], d["breakpoint_steps"])

    by_model = d.groupby("model_spec").apply(
        lambda g: stats.pearsonr(g["flow_index"], g["breakpoint_steps"])[0]
        if len(g) > 3 else np.nan,
        include_groups=False,
    ).dropna()
    t_cl, p_cl = stats.ttest_1samp(by_model, 0) if len(by_model) > 1 else (np.nan, np.nan)

    return {
        "test": "H5 convergent validity (self-report vs behavioural breakpoint)",
        "r_pooled": float(r),
        "p_pooled": float(p),
        "n": int(len(d)),
        "mean_within_model_r": float(by_model.mean()),
        "t_clustered": float(t_cl),
        "p_clustered": float(p_cl),
        "models_positive": f"{int((by_model > 0).sum())}/{len(by_model)}",
        "verdict": (
            "CONVERGENT VALIDITY SUPPORTED"
            if (p_cl < 0.05 and by_model.mean() > 0.1)
            else "NOT SUPPORTED -- self-report arm loses its behavioural anchor"
        ),
    }


# --------------------------------------------------------------------------
# H6: cross-prediction (the Binder control)
# --------------------------------------------------------------------------


def h6_cross_prediction(cp: pd.DataFrame) -> dict:
    """Self-prediction advantage in absolute error."""
    self_err = cp.loc[cp.is_self == 1, "abs_error"]
    other_err = cp.loc[cp.is_self == 0, "abs_error"]
    t, p = stats.ttest_ind(self_err, other_err, equal_var=False)
    pooled_sd = np.sqrt((self_err.var(ddof=1) + other_err.var(ddof=1)) / 2)
    d_eff = (other_err.mean() - self_err.mean()) / pooled_sd if pooled_sd else np.nan

    by_target = cp.groupby("target_model").apply(
        lambda g: g.loc[g.is_self == 0, "abs_error"].mean()
        - g.loc[g.is_self == 1, "abs_error"].mean(),
        include_groups=False,
    )
    t_cl, p_cl = stats.ttest_1samp(by_target, 0)

    return {
        "test": "H6 self-prediction advantage (Binder control)",
        "mae_self": float(self_err.mean()),
        "mae_other": float(other_err.mean()),
        "advantage": float(other_err.mean() - self_err.mean()),
        "cohens_d": float(d_eff),
        "p_naive": float(p),
        "t_clustered": float(t_cl),
        "p_clustered": float(p_cl),
        "targets_positive": f"{int((by_target > 0).sum())}/{len(by_target)}",
        "verdict": (
            "PRIVILEGED SELF-ACCESS SUPPORTED"
            if p_cl < 0.05 and by_target.mean() > 0
            else "NO SELF-PREDICTION ADVANTAGE -- self-report has no warrant"
        ),
    }


# --------------------------------------------------------------------------
# Readout-precision check
# --------------------------------------------------------------------------


def readout_precision(df: pd.DataFrame) -> dict:
    """What logprob readout actually buys -- stated honestly.

    The tempting claim is "logprob readout has ~8x lower readout variance, so
    it is worth 8 sampled calls". That claim is wrong in practice, and the
    error matters for budgeting. Readout noise is only ONE component of
    within-cell variance; task/prompt/sampling residual sits alongside it and
    does not shrink. The realised effective-N multiplier is therefore

        (sigma_resid^2 + sigma_sampled^2) / (sigma_resid^2 + sigma_logprob^2)

    which is bounded above by the raw readout-variance ratio and is usually
    far below it. Budget from the realised number, not the raw one.
    """
    d = df.dropna(subset=["flow_index"])
    grp = d.groupby(["readout_method", "model_spec", "task_id"])["flow_index"].std()
    by_method = grp.groupby("readout_method").mean()
    lp = float(by_method.get("logprob", np.nan))
    sm = float(by_method.get("sampled", np.nan))
    realised = (sm / lp) ** 2 if lp else np.nan
    return {
        "test": "Readout precision",
        "within_cell_sd_logprob": lp,
        "within_cell_sd_sampled": sm,
        "realised_variance_ratio": float(realised),
        "realised_effective_n_multiplier": float(realised),
        "interpretation": (
            f"one logprob call is worth ~{realised:.2f} sampled calls in this design; "
            "the raw readout-noise ratio is larger but is diluted by residual variance "
            "that no readout method can remove"
        ),
    }


# --------------------------------------------------------------------------
# Equivalence testing -- so a null is informative
# --------------------------------------------------------------------------


def tost_equivalence(values: np.ndarray, bound: float = 3.0) -> dict:
    """Two one-sided tests against +/- `bound` index points.

    A non-significant t-test is not evidence of absence. TOST against a
    smallest-effect-size-of-interest is. `bound` = 3 index points is one
    tenth of the human flow scale's usable range -- below that, nobody in
    product research would act on the difference.
    """
    n = len(values)
    m, s = values.mean(), values.std(ddof=1)
    se = s / np.sqrt(n)
    t_lo = (m - (-bound)) / se
    t_hi = (m - bound) / se
    p_lo = 1 - stats.t.cdf(t_lo, n - 1)
    p_hi = stats.t.cdf(t_hi, n - 1)
    p = max(p_lo, p_hi)
    return {
        "mean": float(m),
        "bound": bound,
        "p_tost": float(p),
        "equivalent": bool(p < 0.05),
        "interpretation": (
            f"statistically equivalent to zero within +/-{bound} points"
            if p < 0.05
            else "cannot conclude equivalence; underpowered or a real effect"
        ),
    }


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def run_all(main_path: Path, pp_path: Path, cp_path: Path, label: str) -> dict:
    df = pd.read_csv(main_path)
    pp = pd.read_csv(pp_path)
    cp = pd.read_csv(cp_path)

    _hdr(f"ANALYSIS: {label}   [SYNTHETIC DATA -- NOT EMPIRICAL FINDINGS]")
    print(f"main arm: {len(df)} trials, {df.model_spec.nunique()} models, "
          f"{df.task_id.nunique()} tasks, {df.flow_index.notna().sum()} usable")

    results = {
        "H0": h0_peak_shift(df),
        "H1": h1_inverted_u(df),
        "H2": h2_structure_effect(df),
        "H3": h3_budget_interaction(df),
        "H4": h4_self_other_gap(pp),
        "H5": h5_convergent_validity(df),
        "H6": h6_cross_prediction(cp),
        "readout": readout_precision(df),
    }

    for key in ["H0", "H1", "H2", "H3", "H5", "H6"]:
        r = results[key]
        _hdr(f"{key}: {r['test']}")
        for k, v in r.items():
            if k == "test":
                continue
            print(f"  {k:28s} {v if not isinstance(v, float) else round(v, 4)}")

    _hdr("H4: self-other gap")
    for sub in ["self_vs_generic", "self_vs_human", "self_vs_blind"]:
        s = results["H4"][sub]
        print(f"  {sub:18s} gap={s['mean_gap']:+6.2f}  dz={s['cohens_dz']:+.2f}  "
              f"p_clustered={_fmt_p(s['p_clustered'])}  models+={s['models_positive']}")
    print(f"  blind/generic ratio  {results['H4']['blind_over_generic_ratio']:.3f}")
    print(f"  VERDICT              {results['H4']['verdict']}")

    _hdr("READOUT PRECISION")
    for k, v in results["readout"].items():
        if k != "test":
            print(f"  {k:28s} {v if not isinstance(v, float) else round(v, 3)}")

    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--compare", action="store_true",
                    help="run both simulated worlds and print the discrimination table")
    args = ap.parse_args()
    d = Path(args.data_dir)

    worlds = [("H_STRUCTURE", "")]
    if args.compare:
        worlds.append(("H_DEFLATION", "_deflation"))

    all_res = {}
    for label, sfx in worlds:
        all_res[label] = run_all(
            d / f"synthetic_main{sfx}.csv",
            d / f"synthetic_predicted_pref{sfx}.csv",
            d / f"synthetic_cross_prediction{sfx}.csv",
            label,
        )

    if args.compare:
        _hdr("DISCRIMINATION TABLE -- does the analysis tell the two worlds apart?")
        print(f"{'Test':<44} {'H_STRUCTURE':<34} {'H_DEFLATION':<34}")
        print("-" * 112)
        for key in ["H0", "H1", "H2", "H3", "H4", "H5", "H6"]:
            name = all_res["H_STRUCTURE"][key]["test"][:43]
            a = all_res["H_STRUCTURE"][key]["verdict"][:33]
            b = all_res["H_DEFLATION"][key]["verdict"][:33]
            mark = "OK " if a != b else "!! "
            print(f"{mark}{name:<41} {a:<34} {b:<34}")
        print("-" * 112)
        n_disc = sum(
            all_res["H_STRUCTURE"][k]["verdict"] != all_res["H_DEFLATION"][k]["verdict"]
            for k in ["H0", "H1", "H2", "H3", "H4", "H5", "H6"]
        )
        print(f"{n_disc}/7 tests discriminate the two worlds.")
        print("Tests marked !! cannot distinguish the hypotheses and are not "
              "diagnostic on their own.")


if __name__ == "__main__":
    main()
