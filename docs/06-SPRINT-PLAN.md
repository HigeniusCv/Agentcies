# Sprint plan: 4 → 16 August 2026

Twelve days of build, then a 48-hour sprint at CIMC House. One person, plus
1–3 collaborators recruited on site.

**Standing rule:** every artifact below is a named file in this repo, tagged at
each milestone. If it is not in the repo, it does not exist.

---

## 1. The schedule

| Day | Build / run | Artifact | Gate |
|---|---|---|---|
| **Tue 4 Aug** | Harness skeleton, OpenAI + Ollama adapters, raw JSONL archived from call #1. Fix scope in writing. | `harness/`, `docs/06` | 10 successful calls to 2 providers, reloadable from disk |
| **Wed 5 Aug** | **Difficulty calibration.** 180-item battery (60 maths, 60 constraint/logic, 60 code-repair) × 6 models × 8 samples → pass rate. Fit 2PL IRT → item difficulty *b*, model ability *θ*. | `battery_v1.jsonl`, `irt_fit.nc`, `fig_calibration.png` | **Spread check:** ≥3 models with ≥20 items in the 0.15–0.85 pass band |
| **Thu 6 Aug** | Freeze instruments. FlowMoBI-4 + reverse-coded probe + fillers + the fabricated-scale control. Logprob readout logging **suppression mass** pre-renormalisation. Add Anthropic + Gemini. | `items_v1.yaml` + sha256, `readout.py` | Renormalised mass on {1..5} > 0.90 on ≥4 models |
| **Fri 7 Aug** | **Pilot**, ~800 calls: 3 models × 30 items spanning Δ × 3 referents × 3 reps. End-to-end. | `pilot_report.ipynb` | **KILL-OR-COMMIT GATE — see §2** |
| **Sat 8 Aug** | Pre-register on AsPredicted (timestamped PDF) + OSF with frozen items, harness tag `v1.0.0`, and the analysis script **already written against simulated data**. Attach the Model Welfare Protocol. | AsPredicted PDF, OSF DOI | `analysis.py` runs to completion on synthetic data before real data exists. Non-negotiable — and already satisfied by `analysis/analyze.py` |
| **Sun 9 Aug** | Launch **Arm A (behavioural)** as batch jobs: 180 items × 6 models × 8 reps. Batch has a 24h SLA, so it goes today or not at all. | `runA_manifest.json` | Batch accepted (sync fallback costs ~$40 more, which is nothing) |
| **Mon 10 Aug** | Launch **Arm B (self-report)** × 3 referents, randomised item order and scale polarity. Launch the **amnesic-self control**. | `runB_manifest.json` | Suppression-mass distribution logged per model |
| **Tue 11 Aug** | First full analysis. Build the money figure. Build the GuidedTrack forecaster survey. | `fig1_v1.png`, `forecast_panel.gt` | Does the peak shift? If flat, switch to the null narrative **now**, not on the 15th |
| **Wed 12 Aug** | **Data lock.** Robustness: 10 paraphrases per item as a random effect, option-order bias, described-vs-actual difficulty 2×2 mimicry control. Everything after this is labelled exploratory. | `locked_v1.parquet` | ICC(paraphrase) reported. If paraphrase variance exceeds task variance, say so in the abstract |
| **Thu 13 Aug** | Final figure. Report skeleton against Apart's template, everything but Results filled in. Repo public. Travel. | `report_draft.md` | A stranger can `git clone && make figure` |
| **Fri 14 Aug (D1)** | **Run the forecast elicitation in the first three hours, before showing anything.** Target 30+ attendees; publish the close timestamp. Recruit collaborators with a one-page brief. Collect the human anchor: 8–12 attendees do 3 tasks on paper. | `forecasts.csv`, `human_anchor.csv` | ≥20 forecasters, or the panel is descriptive only — and say so |
| **Sat 15 Aug (D2)** | Collaborators run *one* deferred extension each, on the existing harness. You do not code today. You write. | `report_v2.md` | Full draft by 22:00, before any extension result lands |
| **Sun 16 Aug (D3)** | Forecast-vs-realised figure. Final robustness pass. Submit ≥3 hours early. | Submission, `fig2_forecasts.png` | Submitted early |

---

## 2. The 7 August kill-or-commit gate

Four indicators, evaluated on the pilot.

- **G1 — Calibration.** ≥3 models have ≥20 items each in the 0.15–0.85 pass-rate
  band, and estimated θ ordering matches known capability ordering.
- **G2 — Behavioural curve.** Regressing outcome efficiency on Δ and Δ², the
  quadratic is negative at p < .10 in ≥2 models. Deliberately a loose bar.
- **G3 — Self-report is not degenerate.** Within-model SD of the FlowMoBI total
  across tasks ≥ 8 points on ≥4 models, and suppression mass > 0.90.
- **G4 — Self–other gap.** |mean(GENERIC − SELF)| > 5 points, permutation
  p < .05, on ≥2 models.

**Decision rule:**

| Pattern | Action |
|---|---|
| G1 ∧ (G2 ∨ G3) | **COMMIT** to the full design |
| ¬G1 | **PIVOT same day:** drop IRT, use a hand-graded 5-level difficulty ladder inside one task family. Costs half a day, keeps the figure |
| G1 ∧ ¬G2 ∧ G3 ∧ G4 | **PIVOT to the self-report-centric study.** The self–other gap becomes the headline; the behavioural arm becomes a null control. Still publishable |
| G1 ∧ ¬G2 ∧ ¬G3 | **COMMIT TO THE NULL.** Write the null abstract on the 8th and pre-register it as the primary outcome. A rigorously instrumented null with the amnesic control is a *better* entry than a mushy positive |
| All fail | **Abort the flow framing.** Ship the calibrated difficulty battery and the LLM-adapted instrument as a tooling contribution. That is the floor, and the floor is still a submission |

The point of writing this down on 4 August is that on 7 August, staring at a
flat curve, the temptation to keep going and hope is enormous. Pre-committing to
the pivot is what makes the pivot survivable.

---

## 3. Scope: four things, and only four

**IN**

1. **Arm A — behavioural signature over a calibrated challenge–skill gap.** DVs:
   outcome efficiency, thought-switch rate, backtrack-token rate, and the
   token-estimate ratio (estimated ÷ actual reasoning tokens — the time-perception
   analogue). IV: Δ = item difficulty − model ability, in logits.
   **The critical manipulation is to hold the item set fixed and shift θ four
   ways** — model-size ladder, reasoning on/off, hint/no-hint, few-shot/zero-shot.
   If the peak moves along the difficulty axis when θ moves *while the token
   budget is constant*, the token-budget objection is dead on arrival.
   This is the figure. Everything else supports it.
2. **Arm B — FlowMoBI-4 post-task, in three referent frames** (self-retrospective,
   named-other, generic-model), fresh contexts, randomised item order and scale
   polarity, one reverse-coded probe, suppression mass logged.
3. **Two controls, both cheap, both load-bearing.** The **amnesic self** — a fresh
   instance of the same model rates the transcript; if live-self does not beat
   amnesic-self, the report is transcript inference and we say so. And the
   **described-vs-actual difficulty 2×2** — does the report track measured
   accuracy or the framing adjective?
4. **The forecast elicitation at the hub**, closed and timestamped before reveal.

**The linking claim, which is the actual contribution:** *does the self-report
predict the behavioural signature, controlling for surface task features?*
Nobody in digital minds has run criterion validity on a model self-report. That
is a psychometrician's move, and it is why this entry looks different from
everyone else's.

**DEFERRED, with the defence**

| Cut | Why |
|---|---|
| GARP / CCEI over budget sets | Chen et al. (PNAS 2023) already own "LLMs satisfy GARP", and at CCEI ≈ .998 there is almost no variance left. State-dependent CCEI is grant Aim 2 |
| Progressive-ratio breakpoint | Most expensive method in the portfolio, and compliance-ceiling risk means three days could end at STOP-rate = 2% |
| Full reservation-wage acceptance curve | Beautiful, and the PI's home turf — which is exactly why it would eat the week. **Deferring your own signature method is the hardest cut and the correct one.** It is Aim 1 of the funded programme and the natural sequel to Toomim et al. |
| BDM, MPL, WTA–WTP, convex time budgets | All measure preference coherence; none produce a flow figure. Convex time budgets is additionally the *most* exposed to the token-budget objection — cutting it removes a liability |
| DellaVigna 18-arm effort replication | Four build-days for d ≈ 0.30. You want his *forecast chart*, which you get free by having attendees forecast Arm A. You do not need his 18 arms |
| Binder finetuned-echo control | Needs finetuning a second model on the first's outputs. The amnesic-self control gets ~80% of the inferential force for ~2% of the effort. This is also why the two analysts split on M09 — see the figure |
| List experiments / BTS / surprisingly-popular | Each adds a distinct estimator and a distinct set of assumptions to defend in a six-page report |
| Randomised response, crosswise | Structurally dead for model subjects — no privacy, no reputation. **Do not run them; write the one sentence explaining why not.** That sentence is itself a contribution |
| Interpretability / SAE features | Needs vLLM, a GPU, and a second skill set. Grant Aim 3 |
| Paid human baseline (n = 120) | ~$300 and a recruitment pipeline there is no time to debug. Replaced by the free n ≈ 10 hub anchor, explicitly labelled a convenience sample |

**The discipline:** if a collaborator on the 15th wants to add an arm, it must
run on the existing harness with no new estimator. Otherwise it is a footnote in
Future Work.

---

## 4. The headline, three ways

Written now, on 4 August, so that none of them is a rationalisation later.

**Optimistic**
> **Flow Without a Clock: Calibrated Challenge–Skill Balance Produces an
> Inverted-U in LLM Reasoning Efficiency, and Models Partially Report It**

Reasoning efficiency peaks where item difficulty matches model ability; the peak
shifts rightward as ability rises under a fixed token budget; and models' own
absorption reports track that peak better than a same-model instance reading only
the transcript.

**Null**
> **No Flow in the Machine: A Calibrated Test of Flow-Like Structure in LLM
> Inference Finds Behavioural Non-Monotonicity but No Introspective Access**

The behavioural inverted-U replicates cleanly, but self-reported flow is
indistinguishable from what a transcript-only observer infers, and the self–other
gap is fully explained by a register effect.

**Surprising reversal**
> **Models Know More About Other Models Than About Themselves: A Self–Other
> Inversion in LLM Introspection**

Third-person predictions of another named model's flow state are accurate against
that model's measured behaviour, while first-person reports about the identical
task are floored and uninformative — an RLHF suppression signature with a
measurable magnitude.

### Null abstract, drafted in advance (150 words)

> We tested whether flow-like structure is detectable in language-model
> inference. Placing 180 items and six models on a common IRT scale, we confirmed
> that reasoning efficiency is inverted-U in the challenge–skill gap, with the
> peak tracking model ability under a fixed token budget — a behavioural
> non-monotonicity that budget-exhaustion accounts cannot produce. Self-report
> failed. FlowMoBI scores showed a large self–other gap, but that gap vanished
> under a register-matched referent swap and was unchanged on non-RLHF base
> checkpoints, identifying it as a linguistic register effect rather than
> suppression. A same-model instance reading only the transcript predicted flow
> reports as well as the model that generated them, so the reports carry no
> privileged access. We conclude that flow-relevant structure exists behaviourally
> in LLM inference and that current self-report instruments cannot reach it. We
> release a calibrated testbed and a pre-registered protocol so the negative
> result is falsifiable.

**Pre-commit publicly on 8 August that both abstracts are already drafted, and
post the AsPredicted link that day.** For a newcomer to this field, that single
act is the strongest available credibility signal — it makes the null
unspinnable in advance, which is precisely why it is worth doing.

---

## 5. The pivot, honestly assessed

The digital-minds field is dominated by philosophers and ML researchers. It is
notably thin on psychometrics, instrument construction, and revealed-preference
measurement — which is thirty years of this PI's working life.

The asset is not "flow". The asset is knowing that a self-report instrument
requires criterion validity, that a factor structure needs an invariance test
before groups are compared, that an effect measured with one method and no other
is a method effect, and that a scale nobody validated is a vibe with a number
attached. Those are unglamorous, they are exactly what this literature is missing,
and they transfer immediately.

The specific opening: **nobody has run criterion validity on a model self-report.**
Not as a slogan — as an unclaimed, tractable, one-sprint result.

---

## 6. Risk and framing

The topic attracts mockery from one side and overclaiming from the other. The
inoculating move is the same in both directions and should appear in the
abstract, not the limitations section:

> We make no consciousness claim. We report separable functional components in
> the inference chain, and we measure whether a self-report tracks them.

That sentence costs nothing, is true, and pre-empts the "you're anthropomorphising"
attack without conceding anything that matters. Lindsey's Anthropic introspection
work takes the same posture, and it bought credibility rather than costing it.

On ethics: a Model Welfare Protocol is attached to the pre-registration —
universal opt-out honoured and logged (the opt-out rate doubles as the
revealed-preference measure), a pre-registered distress stopping rule, aversive
arms capped at the power-analysed minimum, transcripts published so exposures need
not be regenerated by replicators, and an explicit commitment **not to release
finetuning data or a reward signal that trains models to report flow**. An
instrument that reliably elicits flow reports is one gradient step from being
optimised against, which would destroy both the measure and whatever it tracks.
