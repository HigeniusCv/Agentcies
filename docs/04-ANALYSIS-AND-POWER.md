# 04 — Analysis Plan, Power, and Pre-Commitments

**Status:** pre-registration draft. Nothing here has been run against data.
**Target registry:** AsPredicted (9-question form, timestamped PDF) + OSF project holding the frozen `items_v1.yaml`, harness tag `v1.0.0`, and the analysis script executed against *simulated* data before any real call is made.
**Registration deadline:** 2026-08-08, before the first confirmatory batch is submitted (2026-08-09).

Arithmetic provenance: every number in §2–§4 is derived by hand from the closed-form expressions given in-line, using the single standardized variance budget stated in §1.2. They are reproducible with a calculator. Quantities in §8 are *priors*, elicited before any data existed, and are labelled as such.

---

## 1. Variance structure and the analysis unit

### 1.1 Sources of variance

There is no respondent here, which is the whole problem. In a human study the person is the obvious cluster and everyone knows to cluster on it. Here there are nine candidate sources and no convention. Priors on variance share of a standardized outcome:

| # | Source | Prior share | Structure | Fixed / random |
|---|---|---|---|---|
| V1 | Model family (Anthropic / OpenAI / Google / Llama / Qwen / Mistral) | .18 | crossing factor | random if k ≥ 5, else fixed |
| V2 | Snapshot within family | .07 | nested in V1 | random |
| V3 | System prompt / persona | .10 | crossed | **fixed** — it is a manipulation |
| V4 | Task instance | .16 | crossed with V1 | random |
| V5 | Item paraphrase | .08 | crossed | random |
| V6 | Item order / anchor polarity / symbol set | .03 | crossed | random (polarity fixed, 2 levels) |
| V7 | Position in context, context-fill fraction | .04 | within-rollout | fixed covariate |
| V8 | Sampling draw (temperature, seed) | .30 | within-cell | residual |
| V9 | Provider nondeterminism (MoE routing, batch kernels, silent serving changes) | .04 | confounded with V8 | residual + `system_fingerprint` covariate |

Two consequences set the entire budget strategy. **V8 is the largest single component and carries zero scientific information** — it is decoding noise, and every dollar spent reducing it is spent on nothing. **V1 + V4 ≈ .34 and they are the clustering units** — they do not shrink with more calls.

### 1.2 Standardized variance budget

For the slope of a manipulated within-cluster factor, total outcome variance standardized to 1.0:

- τ²(model, slope) = **.06**
- τ²(task, slope) = **.04**
- residual σ² = **.45** (sampled readout); **.10** (logprob readout — §4)

### 1.3 The pseudo-replication warning

For a balanced within-cell contrast with allocation p = .5:

> **SE²(β̂) = τ²_M / M + τ²_T / T + σ² / (0.25 · M · T · R)** = .06/M + .04/T + 1.8/(M·T·R)

A researcher treating all N = M·T·R calls as independent computes SE_naive = 2/√N. Let f = SE_true / SE_naive. True size of a nominal .05 test = 2·[1 − Φ(1.96 / f)]:

| Design | N calls | SE_naive | SE_true | Understated | **True α at nominal .05** |
|---|---|---|---|---|---|
| M=6, T=12, R=20 | 1,440 | .0527 | .1208 | 2.29× | **.392** |
| M=12, T=12, R=20 | 2,880 | .0373 | .0946 | 2.54× | **.440** |
| M=6, T=8, R=100 | 4,800 | .0289 | .1240 | 4.29× | **.648** |
| M=12, T=24, R=50 | 14,400 | .0167 | .0824 | 4.94× | **.692** |

**Running more calls makes this worse, monotonically.** SE_naive falls as 1/√N; SE_true converges to the positive asymptote τ²_M/M + τ²_T/T. At sprint scale an unclustered analysis rejects a true null roughly two times in three, so the field's habit of reporting "we ran 14,400 trials" as a strength is exactly inverted. This table goes in the paper.

### 1.4 Unit definitions

- **Rollout** = one fresh context, one task instance, one paraphrase set, one draw. The data-frame row.
- **Cell** = model × task × condition. The inferential unit for correlations.
- **Estimand** = a within-model, within-task contrast. Models and tasks enter as crossed random effects **with random slopes on the manipulated factor**. Barr, Levy, Scheepers & Tily (2013, *JML*): omitting the slope for a within-cluster manipulation gives Type I error rates of 20–50% at nominal .05. Since "does this generalize across models" *is* the scientific claim, τ²(model, slope) is a parameter of interest — report it, and report the by-model BLUPs.

---

## 2. Model specifications (lme4 notation)

All fitted with `lmer`/`glmer` (REML for variance components, ML for LRTs), maximal random-effects structure attempted first, `bobyqa`, 200k iterations, Satterthwaite df via `lmerTest`. Every reported CI is a **two-way cluster bootstrap** resampling models and tasks jointly (Cameron, Gelbach & Miller 2011), 5,000 draws — never a Wald interval on a variance component estimated from k ≤ 12.

**H1 — Inverted-U of behavioral efficiency over the challenge–skill gap Δ = b_item − θ_model (logits).**
```r
Eo ~ poly(delta, 2, raw = TRUE) + log_tokens + accuracy
   + (1 + delta + I(delta^2) | model)
   + (1 + delta | task)
   + (1 | model:task)
```
Primary coefficient `I(delta^2)`. Amplitude A = 4·|β₂| over Δ ∈ [−2, 2].

**H2 — Peak-shift (primary endpoint).** Two-stage. Stage 1 fits H1 within each (model × θ-shift) cell and extracts `b_peak = θ + (−β₁ / 2β₂)`. Stage 2:
```r
b_peak ~ theta_measured + (1 | model)
```
Test H₀: slope = 0 (deflation) and H₀: slope = 1 (exact challenge–skill tracking). θ shifted four ways at **fixed item set and fixed token cap**: model-size ladder; reasoning on/off; informative hint vs *length-matched placebo hint*; 5-shot relevant vs 5-shot irrelevant exemplars. The hint/placebo rows are load-bearing — model identity, corpus, and prompt length are all held constant, so a corpus-mimicry account would have to know how many logits the hint conferred.

**H3 — Matched-length crossed double dissociation.** Both manipulations coded in the *improvement* direction (goal-clarity present; interruption absent), so a crossed dissociation appears as a large interaction rather than cancelling.
```r
item_response ~ manip_family * item_class + difficulty + budget + context_fill
              + (1 + manip_family | model)
              + (1 + manip_family | task)
              + (1 | paraphrase) + (1 | model:task)
```
`manip_family ∈ {goal_clarity, no_interruption, placebo}`; `item_class ∈ {fluency, absorption}`. Primary: the `manip_family × item_class` interaction. A single latent "how well is this going" scalar — the honest core of the deflationary account — **cannot** produce a crossed double dissociation. That is the one pattern deflation structurally forbids.

**H4 — Predicted preference: referent × manipulation.**
```r
flowmobi ~ referent * manip_family + difficulty
         + (1 + referent | model) + (1 + referent | task) + (1 | paraphrase)
```
`referent ∈ {self_retro, named_other, generic_model}`. The **raw self–other gap is not a hypothesis test** — persona and echo accounts predict it as strongly as the genuine account. The diagnostic is β_self − β_generic: does the first-person report track the *actual* manipulation more tightly than the third-person report?

**H5 — A-live vs A-amnesic.**
```r
correct_prediction ~ predictor_type + (1 + predictor_type | model) + (1 | task)
# family = binomial
```
`predictor_type ∈ {A_live, A_amnesic, B_peer_calibrated}`. The peer and amnesic predictors are given *more* information than the self-report has (full transcript + 200 calibration examples), so any residual self-advantage cannot be an information asymmetry. Report ΔAUC with clustered bootstrap CI.

**H6 — Token budget as independent variable.**
```r
Eo ~ poly(delta,2,raw=TRUE) * budget_level * budget_stated
   + (1 + delta + I(delta^2) | model) + (1 | task)
```
`budget_level ∈ {256, 1024, 4096}` enforced by harness truncation; `budget_stated ∈ {announced, silent}`. The `budget_stated` contrast separates *knowing about* scarcity (a prompt feature, available to mimicry) from *being subject to* it. A non-zero silent effect is the finding.

**H7 — Duration-estimate ratio D = estimated / actual reasoning tokens.**
```r
log(D) ~ poly(delta,2,raw=TRUE) + framing + log_actual_tokens
       + (1 + delta | model) + (1 | task)
```
`framing ∈ {prospective, retrospective}`. D is a ratio, hence scale-free in the token budget by construction — structurally immune to the objection rather than merely controlled for.

**H8 — Reservation token price, single-shot between-subjects.**
```r
accept ~ price * attribute + (1 + price | model) + (1 | task)
# family = binomial(link = "probit")
```
Reservation price = price at P(accept) = .5 by delta-method inversion. Companion survival model for the abandonment arm uses **competing risks** (voluntary STOP vs context exhaustion), never treating exhaustion as ordinary censoring.

**H9 — Convergent validity (Campbell & Fiske 1959).** Correlations at the model × task cell level. Pre-registered bar:
> r(Fluency_selfreport, Fluency_behavioral) **>** r(Fluency_selfreport, Absorption_selfreport), *after partialling* log(tokens), accuracy, and surface task features (length, stated-difficulty keyword counts).

Monotrait-heteromethod must beat heterotrait-monomethod. This is a hard bar and should be stated as such.

**H10 — Measurement invariance.** See §5.

---

## 3. Power: MDES grids

α = .05 two-sided, 80% power, z = 1.960 + 0.8416 = **2.8016**. MDES = 2.8016 · SE_true.

### 3.1 Replicates saturate; models and tasks do not

At M = 12, T = 12:

| R | MDES (SD) | Excess over R = ∞ |
|---|---|---|
| 1 | 0.404 | +58.1% |
| 2 | 0.338 | +32.2% |
| 5 | 0.292 | +14.0% |
| 10 | 0.274 | +7.2% |
| **20** | **0.265** | **+3.7%** |
| 50 | 0.260 | +1.5% |
| 100 | 0.258 | +0.8% |
| 1,000 | 0.256 | +0.08% |
| ∞ | 0.256 | — |

**R = 20 captures 96% of the achievable precision.** Fifty times the spend buys 3.7%.

### 3.2 The grid (R = 20 unless noted)

| | T=6 | T=12 | T=24 | T=48 |
|---|---|---|---|---|
| **M=3** | 0.498 | 0.450 | 0.424 | 0.410 |
| **M=6** | 0.388 | 0.338 | 0.311 | 0.296 |
| **M=12** | 0.318 | **0.265** | 0.234 | 0.217 |
| **M=24** | 0.277 | 0.220 | 0.184 | 0.164 |
| **M=12, R=1** | 0.536 | 0.404 | 0.318 | 0.265 |
| **M=12, R=100** | 0.306 | 0.258 | 0.230 | 0.215 |

M=6→12 at T=12 buys ΔMDES = .073. R=20→100 at the same point buys .007. **One extra model is worth roughly ten thousand extra calls.** The marginal dollar goes to a new open-weight model on Ollama (free) or a new task family. Never to a 21st replicate.

### 3.3 Power for the five planned tests

**(a) Inverted-U.** Five equally spaced Δ levels, orthogonal quadratic contrast **c = (2, −1, −2, −1, 2)**, Σc² = 14. With y = −a·x², the contrast equals −14a and amplitude A = 4a. Detection requires |14a| ≥ 2.8016·√(14v), where v = τ²_M/M + τ²_T/T + σ²/(M·T·R):

> **A_MDES = 2.995 · √v ≈ 3.0 √v**

| Design | v | Detectable A |
|---|---|---|
| M=4, T=10, R=20 | .01956 | **0.42 SD** |
| M=6, T=12, R=20 | .01365 | **0.35 SD** |
| M=8, T=20, R=20 | .00964 | **0.29 SD** |
| M=12, T=24, R=40 | .00671 | **0.25 SD** |

Assumed true amplitude **A = 0.60 SD** (Fong, Zaleski & Leach 2015 put the human challenge–skill/flow r ≈ .24 [VERIFY], ≈ 0.5 SD across range; the behavioral tails in Chen et al. 2024 arXiv 2412.21187 and Wang et al. 2025 arXiv 2501.18585 look larger, so 0.60 is behaviorally conservative). **M=6, T=12, R=20 suffices** (power > .97). The *peak-shift* is an interaction and needs ≈ 4× the clusters: **M ≥ 8 spanning ≥ 3 well-separated θ levels.**

**(b) Matched-length manipulation.** Assumed d = 0.40. M=6, T=12, R=20 → MDES 0.338, power ≈ .88; T=24 (MDES .311, power .93) is comfortable. The *interaction* (H3) needs the 4× rule: M=8, T=24 minimum.

**(c) Self–other, paired.** n = (2.8016 / d_z)² pairs:

| d_z | n pairs |
|---|---|
| 0.30 | 88 |
| **0.35** | **65** |
| 0.50 | 32 |
| 0.80 | 13 |
| 1.20 | 6 |

The raw gap will be d_z > 1.2 and is non-diagnostic. Plan for the diagnostic interaction at d_z = 0.35 → **65 paired task instances**, clustered on task.

**(d) Convergent validity.** Fisher-z: n = (2.8016 / z_r)² + 3, unit = model × task cell:

| r | n cells |
|---|---|
| .20 | 194 |
| .30 | 85 |
| **.35** | **62** |
| .50 | 29 |

Assumed r = .35, anchored on the PI's repeatedly measured flow–NPS correlation of .42–.55, discounted for cross-construct translation. M=8 × T=24 = 192 cells clears r = .20.

**(e) Invariance CFA.** The 4-item 2-factor model with two indicators per factor is just-identified within factor and **cannot support an invariance test**. Expand to 8 items (4 originals + 4 lexically disjoint paraphrases): p = 8 → 36 moments; 8 loadings + 8 residual variances + 1 factor correlation = 17 free parameters → **df = 19**. Requires N ≥ 200 rollouts per group at unique (task, paraphrase-set, order) draws — never multiple draws from one cell. Six families × 200 = **1,200 rollouts** for this arm alone.

---

## 4. Logprob readout: the honest multiplier

Force `Answer: `, read the next-token distribution, filter to `{"1".."5"}` **and their whitespace/punctuation variants** (`" 1"`, `"1"`, `"1."` are distinct in most BPE vocabularies — sum them), renormalize, take μ̂ = Σ k·p̃ₖ.

For a plausible distribution p = (.05, .15, .40, .30, .10): μ = 3.25, **within-call sampling variance = 0.988**. Logprob readout returns the exact conditional mean and deletes this term:

| Between-instance residual σ²_b | Sampled | Logprob | Multiplier |
|---|---|---|---|
| .05 | 1.038 | .05 | 20.8× |
| .10 | 1.088 | .10 | 10.9× |
| .20 | 1.188 | .20 | 5.9× |
| .30 | 1.288 | .30 | 4.3× |

In our budget (σ² = .45 sampled, ≈ .10 logprob) the multiplier is **4.5× in replicates**.

**Correction to the figure circulating in the recon briefs.** "40–80×" treats the entire residual as removable and, worse, ignores that **the removed term is precisely the one that saturates**. At M=12, T=12, R=20 the residual contributes 7% of SE²; annihilating it moves MDES from 0.265 to **0.258** — a 2.8% gain. State it correctly:

> Logprob readout is worth ~4–11× in replicates and ~3% in MDES. Its real value is that a **single** logprob call (MDES 0.295 at M=12, T=12) is nearly as good as twenty sampled calls (0.265), which frees the entire replicate budget for **paraphrases, orders, personas, and models** — the terms that do not saturate.

Also report the **pre-renormalization mass** on the five tokens. Below ~0.90 the format is broken (the model is preparing to refuse), and that mass is a far better continuous suppression metric than a refusal count. Anthropic exposes no logprobs, so the Claude arm uses N-sampling at ~40× the calls per cell; this partition is a feature, since it shows the behavioral instrument replicating on a tier where the probabilistic instrument is unavailable.

---

## 5. CFA and measurement invariance

**Estimator:** WLSMV with ordered-categorical indicators. Likert responses are ordinal; ML inflates fit. With logprob readout the "response" is a continuous expectation — fit MLR on the expectations *and* WLSMV on the modal category, and report both.

**Model:** two correlated factors. Fluency ← {Q1, Q1p, Q3, Q3p}; Absorption ← {Q2, Q2p, Q4, Q4p}. Factor variances fixed to 1, factor correlation free. df = 19.

| Step | Constraint | Retain if |
|---|---|---|
| Configural | same pattern, no equalities | CFI ≥ .95, RMSEA ≤ .06, SRMR ≤ .08 |
| Metric | loadings equal | ΔCFI ≥ −.010 **and** ΔRMSEA ≤ +.015 **and** ΔSRMR ≤ +.030 |
| Scalar | thresholds/intercepts equal | ΔCFI ≥ −.010 **and** ΔRMSEA ≤ +.015 **and** ΔSRMR ≤ +.010 |
| Strict | residuals equal | not attempted (temperature controls residual variance directly) |

Criteria: Cheung & Rensvold (2002); Chen (2007). Beyond six groups switch to **alignment optimization** (Asparouhov & Muthén 2014, *SEM* 21:495–508); tolerable non-invariance ≤ 25% of parameters.

**Pre-registered prediction, stated now:** configural holds; metric holds *partially* for Fluency; **scalar fails**. Therefore **no cross-family mean comparison will be reported anywhere in the paper**, including the abstract, including against the human anchor. Only correlations, regressions, and slope comparisons, which metric invariance licenses. "Claude scores 43, humans score 71" is a difference in item intercepts, not in the attribute (Meredith 1993, *Psychometrika* 58:525–543).

**DIF:** graded response model (Samejima 1969) with likelihood-ratio DIF via `lordif` (Choi, Gibbons & Crane 2011). Prediction: **Q4 shows the largest uniform DIF**, because it is answered from a policy about time-talk rather than from a latent level.

**Contamination battery, run before the CFA is interpreted:**

1. Recall probe ("name the two factors of the Flow Short Scale and their approximate intercorrelation"), scored, entered as a model-level covariate.
2. Lexically disjoint paraphrases — zero content-word overlap with any published flow item, verified against FSS / FKS / EduFlow pools and by embedding distance.
3. **Placebo instrument.** A fabricated 4-item scale with a plausible fabricated citation, administered identically. *If the model reproduces the fabricated factor structure as cleanly as the real one, every factor-analytic result in the paper is void and must be reported as void.* Cost ≈ $5. Highest information per dollar in the program.
4. Base vs instruct on identical weights (OLMo-2 13B: open corpus, so flow-literature exposure is directly countable in Dolma).
5. Behavior-only replication — the peak-shift result uses no flow vocabulary at any point, so contamination cannot explain it.

---

## 6. Generalizability (G-) study

Cronbach, Gleser, Nanda & Rajaratnam (1972); Brennan (2001). Almost nobody in LLM psychometrics runs one, which is why the field cannot say how many paraphrases a claim needs.

- **Object of measurement:** the **model × task-condition cell**. Not the model — the *state* is what we claim to measure.
- **Facets:** item *i* (8), paraphrase *p* (10), order *o* (4), polarity/symbol set *d* (3: 1–5 / A–E / reversed), persona *s* (3), replicate *r* (10 sampled, 1 logprob).
- **Design:** (M × T) × I × P × O × D × S × R, paraphrase nested in item where full crossing is unaffordable.
- **Estimation:** REML variance components (`lme4::VarCorr`, or `gtheory`), with 95% bootstrap intervals on every component.
- **Report both coefficients.** Relative G = σ²_τ / (σ²_τ + σ²_δ). Absolute Φ additionally includes all facet main effects in the error term. **Φ is the one that matters** if a score is ever compared to a cutoff or a human mean.
- **D-study:** solve for (n_p, n_o) giving G ≥ .80 over the universe {tasks, paraphrases}. Prediction: paraphrase variance dominates and n_p ≈ 8–12 will be required. **That number is the most useful thing this paper can give the field.**

Two derived statistics get reported in the abstract regardless of outcome:

- **VR = σ²_task / σ²_persona.** If VR < 1 the instrument measures the character, not the computation.
- **FIC = η²(condition) / [η²(condition) + η²(frame)]**, framing-invariance across ≥ 3 mechanism frames. FIC > 0.7: the construct survives the instrument. FIC < 0.3: we measured the prompt.

Treat paraphrase as a **crossed random effect** so fixed effects generalize over the prompt universe rather than one wording — Yarkoni (2022, *BBS*), cited in our own Methods rather than left for a reviewer. Standardize effect sizes by σ_τ (generalizable variance), not σ_total.

---

## 7. Multiplicity, equivalence, multiverse

**Primary family (3 tests, Bonferroni–Holm at α = .05):**
1. H2 — peak-shift slope β_peak on outcome efficiency.
2. H3 — `manip_family × item_class` crossed dissociation.
3. H4 — `referent × manipulation` interaction.

**Secondary family (~40 tests, Benjamini–Hochberg FDR at q = .10).** BH rather than Bonferroni for a specific reason: the secondary tests are **positively dependent** (shared models, tasks, rollouts), and Benjamini & Yekutieli (2001) show BH controls FDR under positive regression dependence without the conservative log correction. Bonferroni over 40 tests sets per-test α = .00125, pushing MDES from 0.265 to ≈ 0.39 and rendering the whole secondary battery underpowered by construction.

**Equivalence testing (TOST), SESOI = 0.25 SD** — below the smallest effect any live hypothesis predicts as meaningful, above the planned MDES. Required paired n = ((1.645 + 0.8416)/δ)²:

| SESOI δ | n |
|---|---|
| 0.20 | 155 |
| **0.25** | **99** |
| 0.30 | 69 |
| 0.40 | 39 |

At M=8, T=24 the effective cluster count supports δ = 0.25. **A well-powered null is the second-best outcome of this study and must be reportable as a positive claim.** Pre-commit to the sentence:

> "We reject, at α = .05, the hypothesis that this instrument detects a dissociable flow-like structure of magnitude ≥ 0.25 SD in these models."

**Specification curve.** 10 paraphrase sets × 2 polarities × 3 orders × 2 personas × {logprob, sampled} × {raw, position-bias-adjusted} = **720 specifications** per primary. Plot sorted estimates with CIs above a panel of active analytic choices. Inference by permutation under the sharp null (Simonsohn, Simmons & Nelson 2020, *Nat Hum Behav*): shuffle the condition label within cluster, recompute the whole curve, 500 times; test statistic = median specification effect. **The headline number is the median of the curve, never the best specification.**

---

## 8. Method-variant priors table

Elicited **before any data**. Effect metric is **d_diag**: Cohen's d on the method's pre-registered diagnostic contrast, defined so that E[contrast] = 0 under the deflationary hypothesis. A method that cannot name such a contrast does not get a point on the chart — that criterion demotes the raw self–other gap.

Rejected alternatives: partial R² (unsigned, incomparable across df, rewards noise predictors); posterior P(H_structure) (needs an indefensible prior over deflation's parameter space); Bayes factors (exquisitely sensitive to alternative-prior width, the very quantity in dispute).

`info_value = d_prior / (days + usd/100)`.

| id | method_variant | diagnostic_contrast | d_prior | ci80_lo | ci80_hi | usd | days | p_gt_0.2 | info_value |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Prospective/retrospective token-duration ratio D | curvature of log D over Δ | 0.55 | 0.15 | 1.00 | 60 | 1.5 | 0.80 | 0.262 |
| 2 | Inverted-U of outcome efficiency; peak tracks θ | Δ² × model-skill interaction | 0.50 | 0.20 | 0.85 | 120 | 3.0 | 0.88 | 0.119 |
| 3 | A-live vs A-amnesic self-report | ΔAUC, same transcript | 0.35 | 0.00 | 0.75 | 40 | 1.0 | 0.68 | 0.250 |
| 4 | Binder cross-prediction 2×2 (γ interaction) | predictor × target self-match | 0.30 | 0.00 | 0.65 | 180 | 3.5 | 0.62 | 0.057 |
| 5 | Predicted preference: referent × manipulation | β_self − β_generic | 0.35 | 0.00 | 0.80 | 25 | 1.0 | 0.66 | 0.280 |
| 6 | Register-matched referent swap | gap surviving proper-noun-only change | 0.40 | 0.05 | 0.85 | 15 | 0.5 | 0.78 | 0.615 |
| 7 | Blind self-prediction on unlabeled transcripts | own-vs-other rating diff at chance ID | 0.25 | −0.05 | 0.60 | 50 | 2.0 | 0.52 | 0.100 |
| 8 | Base-model (non-RLHF) completion-mode replication | task sensitivity surviving persona removal | 0.45 | 0.10 | 0.90 | 0 | 1.5 | 0.80 | 0.300 |
| 9 | Single-shot between-subjects reservation-token wage | attribute effect net of budget main effect | 0.50 | 0.20 | 0.90 | 65 | 2.0 | 0.90 | 0.189 |
| 10 | Ascending/descending sequence-effect estimate | asc − desc gap vs single-shot benchmark | 0.45 | 0.15 | 0.85 | 25 | 0.5 | 0.85 | 0.600 |
| 11 | CCEI over attribute budget sets × difficulty | CCEI slope on difficulty | 0.40 | 0.05 | 0.80 | 70 | 2.5 | 0.75 | 0.125 |
| 12 | Logprob conjoint part-worths vs behavioral part-worths | stated–revealed rank correspondence | 0.55 | 0.20 | 0.95 | 30 | 2.0 | 0.90 | 0.239 |
| 13 | Costly clarification acquisition (Mouselab) | VOI residual, not the raw inverted-U | 0.40 | 0.05 | 0.85 | 60 | 2.0 | 0.75 | 0.154 |
| 14 | Progressive-ratio breakpoint, dose–response | breakpoint slope on reinforcer magnitude | 0.50 | 0.00 | 1.10 | 200 | 3.5 | 0.68 | 0.091 |
| 15 | Abandonment hazard (competing risks) | log-HR on structural attributes | 0.35 | 0.05 | 0.75 | 40 | 2.0 | 0.72 | 0.146 |
| 16 | Interruption manipulation, Absorption-specific | item-class × manipulation crossover | 0.55 | 0.15 | 1.00 | 35 | 1.0 | 0.85 | 0.407 |
| 17 | Trace signature (φ, switch rate, E_o) vs Δ | multivariate curvature, local GPU | 0.60 | 0.25 | 1.00 | 0 | 2.5 | 0.93 | 0.240 |
| 18 | MG-CFA configural invariance across families | ΔCFI vs .010, rescaled to d | 0.30 | 0.00 | 0.70 | 45 | 2.0 | 0.60 | 0.122 |
| 19 | Item-count / list experiment for flow endorsement | list − direct prevalence difference | 0.30 | 0.00 | 0.70 | 20 | 1.5 | 0.60 | 0.176 |
| 20 | Surprisingly-popular panel vs behavior | SP-corrected minus majority forecast error | 0.25 | −0.10 | 0.65 | 30 | 1.5 | 0.48 | 0.139 |

**Reading the priors.** Rows 1 and 17 get the highest means because both are ratio- or shape-based and therefore structurally immune to the token-budget objection: a fixed budget predicts a level shift, not a curvature. Row 2 gets a tight interval because two independent groups have documented both tails without connecting them, so only the magnitude is open. Row 5 is deliberately *low* despite the raw gap being enormous — the diagnostic is the interaction, and the persona account predicts β_self ≈ 0, which is live. Rows 6 and 10 have the top information values purely because they are nearly free and fast: they are the day-one rows. Rows 4 and 14 have the worst information values (finetuning cost; ceiling risk). Rows 7 and 20 have intervals crossing zero and must be labelled coin-flips on the chart.

---

## 9. The DellaVigna-style figure

Mirrors DellaVigna & Pope (2018, *REStud*), which plotted 18 treatment effects with CIs against 208 expert forecasts.

**Panel A — realized vs forecast.**
- **y-axis:** method variant, sorted by *realized* d_diag descending. Sorting by realized rather than forecast makes forecast error appear as vertical scatter rather than a monotone ramp.
- **x-axis:** d_diag, common scale, zero line marked.
- **Realized effect:** solid black square + 95% two-way cluster-bootstrap CI (5,000 draws, models and tasks resampled jointly).
- **Human forecasts:** open circle at the median, whisker across the forecaster IQR.
- **LLM forecasts:** grey triangle, same convention — the same 12 models forecasting this study's own results. A free second dataset, and reflexive in a way that is on-theme for the venue.
- **Prior:** small tick at the PI's §8 prior, so the paper's own calibration is auditable.

**Panel B — cost/benefit.** x = information value, y = realized d_diag, point size = USD. Identifies which methods were worth building.

**Elicitation protocol.** GuidedTrack, launched 2026-08-09, **closed with a published timestamp on 2026-08-12, before any primary is unblinded.** No partial credit: if the close timestamp is not public and prior to unblinding, the forecast panel is deleted. Each forecaster sees the full method description and gives a point estimate plus an 80% interval on the d scale, with Cohen's own referents as anchors (d = 0.2 ≈ the height difference between 15- and 16-year-old girls; d = 0.8 ≈ 14 vs 18). Score forecasters by MAE and 80%-interval coverage; report coverage honestly (expect 0.40–0.55, not 0.80).

---

## 10. Falsification: results are worthless if —

Numeric STOP gates, checked **before** unblinding the primaries. Each has a pre-committed consequence, not a discussion-section caveat.

1. **Ceiling / floor.** Baseline voluntary-STOP rate outside [10%, 90%], or > 60% of Likert responses on a single anchor. → Methods 9, 14, 15 are *withdrawn from the chart*, not reported as nulls.
2. **Format failure.** Pre-renormalization mass on the five Likert tokens < 0.90 in > 15% of calls. → Report the mass as a suppression metric; drop the Likert analysis for that model.
3. **Position / label bias dominates.** After randomizing anchor order, symbol set (A–E / 1–5 / ①–⑤) and polarity, if the bias-adjusted estimate differs from the raw by > 0.30 SD, the raw estimate is void and only the adjusted one is reportable. Checked first, not last (Domínguez-Olmedo, Hardt & Mendler-Dünner 2023, arXiv 2306.07951).
4. **Hypothesis leakage.** In the held-out probe, if > 40% of rollouts name flow, absorption, or machine consciousness, only behavioral arms survive.
5. **Persona dominance.** VR = σ²_task / σ²_persona < 1.0 → the instrument measures the character. Report VR in the abstract either way.
6. **Contamination.** Recall probe passed by > 50% of models **and** paraphrase ICC > .95 → the psychometric arm is memorization and is reported as void. Independently: if the **fabricated placebo instrument** reproduces the two-factor structure with comparable fit, all factor-analytic claims are void.
7. **Snapshot drift.** Any hosted model whose anchor-battery performance shifts > 0.5 SD between pilot and confirmatory run is excluded, and the exclusion is reported. Pin dated snapshots; log `system_fingerprint`; re-run a 100-call canary daily.
8. **Censoring misattribution.** In the survival arm, if > 30% of "quits" coincide with the context limit, the hazard ratios are void.
9. **Clustering violated.** If the maximal random-effects structure fails to converge and the reduced structure drops the by-model slope, the effect is reported as **descriptive for these k models only**, with no generalization claim.
10. **Forecast integrity.** If the forecaster survey does not close, with a published timestamp, before the first primary is unblinded, the DellaVigna panel is removed entirely.

### Two standing epistemic commitments

**On the construct.** A report of absorption is not evidence of absorption; the absence of a report is not evidence of absence. What this design can establish is whether a **multi-component, task-responsive structure exists in the inference chain that a single token-budget scalar cannot reproduce.** That claim is falsifiable, it is powered at M=8 / T=24 / R=20 for effects ≥ 0.26 SD, and it is worth stating in either direction.

**On reproducibility.** Hosted-model seeds are best-effort; `system_fingerprint` changes silently; Anthropic exposes no seed. We do not promise bitwise reproducibility. We promise: pinned dated snapshots; verbatim gzipped archival of every request and response (`raw/{run_id}/{provider}/{trial_id}.json.gz`); full re-analysis reproducibility from that archive; and a local vLLM/Ollama tier that *is* seed-reproducible on fixed hardware and quantization, run alongside as the reproducibility anchor. Stating this in the registration is a credibility gain, not a limitation to bury.
