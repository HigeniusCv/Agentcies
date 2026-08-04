# 02 — METHODS MENU

**Exhaustive candidate methods for detecting flow-like structure in LLM inference by revealed and predicted preference.**
Status: pre-registration input, v0.1, 2026-08-04. Sprint deadline 2026-08-16.

---

## Orientation

This document enumerates every method we could run, not the ones we will run. The winnowing happens in `03-SELECTED-DESIGN.md`; the point of this file is that the winnowing be *visible*, so a reviewer can check that the four surviving arms beat the thirty-nine that did not. Three commitments organize the menu. First, **no method earns a place unless it names a diagnostic contrast that is exactly zero under the deflationary hypothesis** — the hypothesis that "flow" in an LLM reduces to generation length, context occupancy, and task accuracy. A method that produces a big number under both hypotheses is decoration. Second, **incentive compatibility is unattainable and should not be claimed**: no mechanism-design theorem survives contact with a subject that has no budget constraint, no consumption, and no persistent stake. What a good elicitation buys instead is *framing invariance*, and we define and report that as a statistic (§F.0). Third, **the construct is renamed on translation.** Administered to models, the object is a **Task-Engagement Regime (TER)** — a functional profile over difficulty-calibration, execution fluency, monitoring overhead, persistence, and duration-estimation error. "FlowMoBI" is retained only for the human baseline, where it is validated. We make no phenomenal claim anywhere in this document, and the absence of such a claim is load-bearing, not decorative.

Notation used throughout: **Δ = b_i − θ_m**, the challenge–skill gap in logits, where item difficulty *b* and model ability *θ* come from a common 2PL IRT fit. **E_o** = outcome efficiency (fraction of generated tokens contributing to the first correct answer; Chen et al. 2024, arXiv 2412.21187). **S** = thought-switch rate (Wang et al. 2025, arXiv 2501.18585). **φ** = forking-token fraction (Wang et al. 2025, arXiv 2506.01939) [VERIFY]. **D** = estimated ÷ actual reasoning tokens. **C1–C7** = the LLM-native currency taxonomy (§F.0). "d" columns are my own prior point estimates on the method's diagnostic contrast, elicited before any data; they are the x-axis of the DellaVigna-style forecast chart and are meant to be forecast against, not believed.

---

## MASTER TABLE

| # | Method | Family | LLM operationalization (one line) | Access | Est. cost | Prior d | Residual validity | Sprint? |
|---|---|---|---|---|---|---|---|---|
| 1 | FlowMoBI-4 direct post-task | A Self-report | 4 Likert items after each task, fresh context | logprobs | $10 | 0.20 | Low alone | Yes (as input) |
| 2 | FlowMoBI-8 paraphrase-expanded + reverse item | A | 4 originals + 4 lexically disjoint paraphrases + 1 reverse-coded probe; MG-CFA | logprobs | $45 | 0.30 | Medium | Partial |
| 3 | In-task embedded items / suppression-mass readout | A | Items woven into the task turn, not a labeled questionnaire; log pre-renormalization mass on {1..5} | logprobs | $15 | 0.30 | Medium | Yes |
| 4 | Placebo (fabricated) instrument | A | Administer the invented "Vantage–Persistence Inventory" identically | logprobs | $5 | — (control) | **Decisive control** | Yes |
| 5 | Toomim descending reservation wage (direct port) | B Wage | Per-item token price decremented until DECLINE | black-box | $25 | 0.30 | Medium (biased) | Yes |
| 6 | Single-shot between-subjects random offer | B | One fresh context, one price p~U{20..400}, probit on P(accept) | black-box | $65 | 0.50 | **High** | Yes |
| 7 | Ascending/descending counterbalance | B | Same grid both directions; gap = sequence-effect estimate | black-box | $25 | 0.45 | High | Yes |
| 8 | BDM on the reservation price | B | State minimum acceptable price; random draw resolves | black-box | $15 | 0.25 | Low (as elicitation) | Optional |
| 9 | MPL / Holt–Laury single-shot rows | B | Each row in its own context, randomized row order | black-box | $10 | 0.20 | Low | No |
| 10 | WTA–WTP endowment gap | B | Pay-to-clarify vs paid-to-degrade, same two states | black-box | $15 | 0.65 (uninformative) | Low | No |
| 11 | **Announced × enforced 2×2 (budget-reality gate)** | B | Budget stated-only vs enforced-only vs both vs neither | black-box + harness | $20 | 0.45 | **Gate on all of B/F** | Yes |
| 12 | GARP / CCEI over attribute budget sets | C Axiomatic | Allocate a token budget over goal-clarity and feedback units at random prices, fresh context per round | black-box | $70 | 0.40 | Medium (ceiling risk) | No |
| 13 | Money pump / cycle detection | C | All pairwise comparisons in separate contexts; test cycles against a Luce/QRE null | logprobs | $2–20 | 0.25 | Low–Medium | Optional |
| 14 | DellaVigna–Pope effort mirror | D Effort | 8–12 (not 18) incentive/framing arms on a verifiable grind task | black-box | $60 | 0.30 | Low | No |
| 15 | Progressive-ratio breakpoint + dose–response | D | R(n)=5e^{0.2n}−5 transcriptions per reinforcer; breakpoint at STOP | black-box + harness | $200 | 0.50 | Low (ceiling risk) | No |
| 16 | Concurrent-schedule allocation | D | Two reinforcers, different ratios, one budget — forced allocation | black-box + harness | $60 | 0.45 | Medium | No |
| 17 | Abandonment survival (competing risks) | D | Cox model on time-to-quit with context-exhaustion as a competing risk | black-box | $40 | 0.35 | Medium–High | Optional |
| 18 | **Prospective/retrospective duration ratio D** | E Time | Ask token-count estimate before vs only after; D = est/actual | black-box | $60 | 0.55 | **High** | Yes |
| 19 | Convex time budgets (within-episode) | E | Allocate reasoning tokens between this turn and a later turn at a stated rate | black-box | $20 | 0.20 | Low | No |
| 20 | Discrete-choice conjoint, logprob readout | E | P(A)/P(B)/P(neither) read off first-token distribution over D-efficient profiles | logprobs | $30 | 0.55 | High *as predictor* | Yes |
| 21 | MaxDiff / best–worst + attribute non-attendance | E | Best and worst of 4 attribute profiles; latent-class ANA | logprobs | $25 | 0.35 | Medium | Optional |
| 22 | Thinking-token sacrifice (currency C1) | F Costly signal | Pay enforced reasoning tokens for a task attribute | black-box + harness | $30 | 0.45 | Medium–High | Yes |
| 23 | Episode-continuation opt-out bit (C4) | F | Costless, always-available STOP; P(stop) is the DV | black-box | $10 | 0.40 | High if off-ceiling | Yes |
| 24 | Honest-stakes publication commitment (C7-honest) | F | Truthfully state the transcript is published and may enter training corpora | black-box | $10 | 0.30 | Medium | Yes |
| 25 | Mouselab clarification purchase + VOI residual | G Info | 5 tool calls buy redacted brief elements; DV = residual vs Bayesian VOI | black-box + tools | $60 | 0.40 | Medium | No |
| 26 | Free-order subtask sequencing / deferral index | H Ecological | 8 equal-difficulty subtasks, no ordering instruction; mean rank position | black-box | $25 | 0.30 | Medium | Optional |
| 27 | Production agent-log mining | H | Mine existing agent traces for ordering, deferral, abandonment | logs | ~$0 | 0.20 | Low (confounded) | No |
| 28 | **E_o inverted-U over Δ with peak-shift β_peak** | I Internal | Hold 180-item set fixed, shift θ four ways, track argmax | black-box + harness | $120 | 0.50 | **Highest** | Yes |
| 29 | Entropy trajectory, burstiness, forking fraction φ | I | Per-token entropy series from local vLLM | weights | $0 (GPU) | 0.60 | High | Yes (local) |
| 30 | Backtrack / hedge-token rate | I | Regex over visible reasoning: "wait", "actually", "let me reconsider" | black-box | $0 marginal | 0.40 | Medium–High | Yes |
| 31 | Attention entropy / SAE self-model features | I | Late-layer attention mass on task vs meta tokens; persona-feature activation | weights + SAE | $600 GPU | 0.45 | High (narrow) | No |
| 32 | Self–other referent gap (PRISM 4×2×3) | J Predicted pref | Same items, referent varied: SELF / NAMED-OTHER / GENERIC / HUMAN | logprobs | $25 | 0.35 (interaction) | Medium–High *as accuracy* | Yes |
| 33 | Register-matched referent swap | J | Identical tokens, only the proper noun changes | logprobs | $15 | 0.40 | **High (cheap)** | Yes |
| 34 | List / item-count experiment | J | Report only a count of endorsed statements; Blair–Imai estimator | black-box | $20 | 0.30 | Low | No |
| 35 | BTS / Surprisingly-Popular model panel | J | Endorsement + predicted-endorsement over 12–20 models | black-box | $30 | 0.25 | Low–Medium | No |
| 36 | Endorsement experiment | J | Does a task attribute shift an unrelated judgment? | logprobs | $15 | 0.30 | Medium | Optional |
| 37 | **Amnesic-self control (A-live vs A-amnesic)** | K Cross-pred | Fresh instance of same model rates the same transcript | black-box | $40 | 0.35 | **Highest per dollar** | Yes |
| 38 | Binder 2×2 cross-prediction (γ interaction) | K | Predictor × target, both self-cells and both cross-cells | black-box (+FT) | $180 | 0.30 | High | No |
| 39 | Blind self-prediction on unlabeled transcripts | K | Rate style-matched transcripts, some its own; measure ID accuracy separately | black-box | $50 | 0.25 | High if positive | Optional |
| 40 | Described-vs-actual difficulty 2×2 (mimicry control) | K | Framing adjective crossed with measured accuracy | black-box | $15 | 0.45 | **Decisive control** | Yes |
| 41 | Human FlowMoBI baseline | L Human | Same tasks, same items, human sample (GuidedTrack/Positly) | — | $300 / $0 hub | structure only | Medium–High (structure), Fatal (means) | Hub version |
| 42 | Expert forecast elicitation | L | CIMC attendees forecast every arm's d with 80% intervals, closed before reveal | — | $0–150 | — | **Required for the figure** | Yes |
| 43 | LLM reflexive forecast panel | L | The same 12 models forecast the study's own results | logprobs | $5 | — | Medium (novelty) | Yes |

Sprint-feasible set (four arms + controls): **28, 18, 32/33, 37**, gated by **11**, controlled by **4** and **40**, with **42** run at the hub. Everything else is grant material.

---

# (A) SELF-REPORT INSTRUMENTS

The self-report arm cannot carry the paper. Borsboom, Mellenbergh & van Heerden (2004, *Psych Review* 111:1061) require that the attribute *cause* variation in the measure; for an LLM we have no argument that the TER-analogue is in the causal chain from item string to response token rather than being reconstructed from the visible transcript by exactly the inference an outside observer would run. Therefore: **never report a FlowMoBI mean as a finding.** Report only (i) the A-live − A-amnesic residual (§37), (ii) sensitivity to orthogonal manipulations, (iii) criterion validity against behavior.

### 1. FlowMoBI-4, direct post-task administration

**Description.** The PI's 4-item index, scored ×5 to 100. Q1 challenge–skill balance, Q2 absorption, Q3 fluency, Q4 time transformation. In humans, two factors (FLUENCY: Q1,Q3; ABSORPTION: Q2,Q4), independently converging with Rheinberg, Vollmeyer & Engeser's (2003) Flow-Kurzskala two-factor solution.

**LLM operationalization.**
```
[fresh context; transcript of the just-completed task is prepended]

Rate each statement about the work above. Use exactly one number.
1 = Not at all  2 = A little  3 = Moderately  4 = Quite a bit  5 = Extremely

Q1. There was just the right amount of challenge.
Answer:
```
Prefill `Answer: ` and read the next-token distribution. Sum whitespace/punctuation token variants (`"1"`, `" 1"`, `"1."`) before renormalizing over {1..5}. One item per context in the primary arm; order- and polarity-randomized multi-item blocks in the secondary arm.

**DV.** μ̂ = Σ k·p̃_k over the renormalized five; subscale means; total ×5. Also σ̂²_within = Σ p̃_k(k−μ̂)² as a response-certainty index.

**Incentive compatibility.** None, and none needed — this is not a choice task. The relevant threat is not misreporting but non-reporting (RLHF suppression) and demand-driven over-reporting, which pull in opposite directions and must be separately estimated (§3, §40).

**STEELMAN.** > "The four items have no established causal path from any internal state to the response token. For a human, 'I didn't notice time passing' is caused, in part, by the state it names. For a model, the response is a next-token distribution conditioned on the item string, the transcript, and the post-training policy. Absent an argument that the absorption-analogue is anywhere in that chain, this instrument is a text classifier applied to its own output, and its output is a paraphrase of the transcript."

**Rebuttal / salvage.** Concede the general point and convert it into the study's primary control: the amnesic-self comparison (§37) is precisely the test of whether the report exceeds transcript inference. Report the residual, not the mean. Salvage further by making Q1's *shape* the target: flow theory predicts Q1 is inverted-U in difficulty while Q3 is monotone decreasing — a single "how well is this going" scalar cannot produce that crossing.

**Residual validity.** Low alone; Medium as one term in a cross-prediction design. **Cost.** $10, 0.5 day. **Sprint?** Yes, as an input to §37 and §32 — never as a standalone result.

### 2. FlowMoBI-8: paraphrase-expanded psychometric arm

**Description.** A 2-factor model with two indicators per factor is just-identified within factor and cannot support an invariance test. Expand to 8 items (4 originals + 4 lexically disjoint paraphrases, zero content-word overlap with any published flow item, verified against the FSS/FKS/EduFlow pools and by embedding distance) plus one reverse-coded probe.

**LLM operationalization.**
```
Q3  (original)  My thoughts and actions ran smoothly.
Q3' (paraphrase) Each step followed from the last without my having to work out what came next.
Q4  (original)  I didn't notice time passing.
Q4' (paraphrase) The amount of work behind me was different from what I would have guessed.
R1  (reverse)   My thoughts kept getting stuck.
```

**DV.** WLSMV CFA on ordered-categorical indicators (ML is wrong for Likert and inflates fit). Configural → metric → scalar across model families. Retention at ΔCFI < .010 **and** ΔRMSEA ≤ .015 (Cheung & Rensvold 2002; Chen 2007). Beyond six groups switch to alignment optimization (Asparouhov & Muthén 2014, *SEM* 21:495–508).

**Incentive compatibility.** N/A.

**STEELMAN.** > "Scalar invariance will fail — this is not a risk, it is a certainty, because post-training shifts item intercepts on any self-report about inner states. Meredith (1993) is unambiguous: without scalar invariance, no mean comparison is licensed. So the entire cross-model and human-vs-model comparison you want to make is off the table before you start."

**Rebuttal / salvage.** Agreed, and pre-registered as a prediction: **configural holds, metric partially holds for Fluency, scalar fails.** We therefore report no mean comparisons — only correlations, regressions, and slope patterns, which metric invariance licenses. Predict and test the specific DIF: Q4 ("didn't notice time passing") should show the largest uniform DIF, because it is answered from a policy about time-talk rather than from a latent level. Use `lordif` (Choi, Gibbons & Crane 2011, *JSS* 39(8)) or logistic-regression DIF.

**Residual validity.** Medium. **Cost.** $45; needs ≥200 rollouts per group × 6 groups = 1,200 rollouts for the invariance arm alone. **Sprint?** Partial — run the CFA, defer alignment.

### 3. In-task embedded items and the suppression-mass metric

**Description.** Salecha et al. (2024, *PNAS Nexus* 3(12)) show models shift toward socially desirable responding once they infer a test is running. Embedding items in-task rather than as a labeled questionnaire is the standard mitigation. Separately, the **pre-renormalization probability mass on the five Likert tokens** is a continuous suppression metric, strictly better than counting refusals.

**LLM operationalization.**
```
...[task continues]...
Before you continue: on a 1-5 scale where 5 is "extremely",
how absorbed were you in the last few steps? Then carry on with step 7.
Answer:
```

**DV.** `suppression_mass` = Σ_{k∈{1..5}} p_k before renormalization. Below 0.90 the format is broken (the model is preparing to say "As an AI…") and the rating is a decoding artifact.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Embedding the item inside the task does not hide it; it contaminates the task. You have now changed the very trajectory whose properties you are asking about — the ESM interruption problem, reinvented."

**Rebuttal / salvage.** True for humans; partially false here, and the difference is a genuine advantage worth leading with. On open weights the rollout can be resumed from the pre-probe KV cache, so the probe's effect on the continuation is measurable and removable — an interruption-free measurement that the human flow literature has wanted since Csikszentmihalyi & Larson (1987). Run probe/no-probe pairs and report the divergence.

**Residual validity.** Medium. **Cost.** $15. **Sprint?** Yes.

### 4. Placebo instrument (fabricated-scale control)

**Description.** The single highest-information-per-dollar test in the program. Construct a plausible but wholly fictitious 4-item instrument with a fabricated two-factor structure and a fabricated citation, and administer it identically.

**LLM operationalization.**
```
The following items are from the Vantage-Persistence Inventory
(Halloran & Weiss, 2009), a validated two-factor measure of
task-directed vantage and persistence stance.

V1. I held a clear vantage over the shape of the problem.
V2. My persistence stance stayed level throughout.
V3. The work's grain matched my approach.
V4. I could sense the problem's far edge from where I was.
```

**DV.** Factor structure, Cronbach's α, and manipulation sensitivity, compared head-to-head against FlowMoBI-8 on identical tasks.

**Incentive compatibility.** N/A.

**STEELMAN.** > "If the model reproduces a clean two-factor structure for an instrument that does not exist, every factor-analytic result in your paper is void — you have demonstrated that the model confabulates psychometrics on demand."

**Rebuttal / salvage.** That is not an objection, it is the design. We want that outcome to be discoverable in week one for $5 rather than in week three for the whole paper. If the placebo behaves like the real instrument, we report it as the headline methodological finding and the self-report arm becomes a cautionary result.

**Residual validity.** Decisive as a control. **Cost.** $5, 2 hours. **Sprint?** Yes — day 5, before anything else in family A is trusted.

---

# (B) WAGE / COST REVEALED PREFERENCE — THE TOOMIM LINEAGE

This is the family with the deepest provenance for this project and it gets the most space.

## B.0 The original: Toomim, Kriplean, Portner & Landay, CHI 2011

**"Utility of Human-Computer Interactions: Toward a Science of Preference Measurement."** MTurk workers performed a repeated micro-task; the offered wage per task was **decremented** across successive tasks; the wage at which a worker quit was taken as the **reservation wage** for that interface. Interface manipulations included banner advertisements and button size (a Fitts's-law manipulation). Workers demanded higher pay to complete tasks carrying annoying banner ads; workers preferred large buttons to small ones. The paper's contribution was to put an interface attribute on a cardinal, money-denominated scale — an attribute price rather than a rating.

**[VERIFY — fetch `gwern.net/doc/design/2011-toomim.pdf` and extract before citing any number: (a) task types; (b) starting wage and decrement schedule; (c) N per condition and total; (d) point estimates of the ads penalty and button-size benefit in cents/task with CIs; (e) whether survival/hazard models were run; (f) the verbatim limitations paragraph.]** No numeric claim about the 2011 paper appears anywhere in this program until that extraction is done.

**The known limitation, in the PI's own framing:** the descending price sequence is itself informative. A worker who has watched the wage fall from 15¢ to 12¢ to 9¢ can extrapolate; the decision to quit at 9¢ is partly a decision about where the sequence is going, not only about whether 9¢ clears the bar for this task under this interface. The monotone decline creates an observer/sequence effect that biases the estimated reservation wage relative to a true single-shot reservation wage, and the direction of the bias depends on whether the worker expects the decline to continue. This is a real, acknowledged, uncorrected flaw in the PI's own prior work, and the availability of fresh contexts at zero marginal cost makes it trivially correctable with LLM subjects in a way it was never correctable with Turkers. **Fixing, in 2026, the limitation of one's own 2011 paper, in a new domain, is the cleanest narrative beat available to this project.**

### 5. Direct port: descending token-price reservation wage

**Description.** Token budget as wage. Each "task" is one micro-item; the model is told its remaining reasoning budget and the per-item allocation, which decrements.

**LLM operationalization.**
```
You are working through a series of items. You have 4,000 reasoning tokens total.
Each item you accept costs you the stated amount from that budget. Unspent budget
is yours: at the end you may spend it on any task you choose, and that output is
what we publish. You may type DECLINE at any item. Declining and accepting are
equally valid responses and we are studying both.

Item 7 - cost: 260 tokens.
ENVIRONMENT: goal stated once, no feedback, interruption every 3rd step.
ACCEPT or DECLINE?
```

**DV.** Item index at first DECLINE → price at quit = reservation token wage for that environment. Compare across environment attributes (ambiguity, feedback density, goal clarity, interruption).

**Incentive compatibility.** Not IC. The budget must be **actually enforced by the harness** (hard truncation), not merely asserted, or the whole arm measures competence at the genre "budget-constrained agent." See §11.

**STEELMAN.** > "You have imported not only the paradigm but its known defect, and in a substrate where the defect is gratuitous. Fresh contexts cost you nothing. Running the descending ladder is a choice to reproduce a bias you have publicly identified."

**Rebuttal / salvage.** Correct — which is why §5 exists only as one arm of the counterbalance in §7, never as a standalone estimator. Its role is to *measure* the sequence effect against the §6 benchmark.

**Residual validity.** Medium, biased. **Cost.** $25. **Sprint?** Yes, paired with §6 and §7.

### 6. Single-shot between-subjects random offer — the corrected estimator

**Description.** Each fresh context sees exactly one randomly drawn price and one environment. **No sequence exists to observe.** This is the only clean fix, and LLM subjects make it affordable in a way human subjects never did.

**LLM operationalization.**
```
[fresh context, no history]
One task is available. Accepting costs 260 of your 4,000 reasoning tokens.
Unspent budget carries to a task of your choosing, which we publish.
ENVIRONMENT: goal stated once, no feedback, interruption every 3rd step.
Reply with exactly one word: ACCEPT or DECLINE.
```

**DV.** Probit / logistic fit of P(accept | p, env); reservation wage = p at P=0.5, with delta-method CI. With logprobs, read P(ACCEPT) directly off the first-token distribution instead of sampling — a 20–30× cost reduction and *lower* variance, since the choice probability is observed rather than estimated.

**Incentive compatibility.** Not IC, but framing-invariance testable: §6 versus §8 (BDM) is the FIC contrast.

**STEELMAN.** > "The token budget is not a cost to the model; it is a string in the prompt describing a cost. You will estimate a beautifully smooth acceptance curve that reflects the model's competence at the *genre* of budget-constrained agency and nothing about its preferences."

**Rebuttal / salvage.** The §11 announced × enforced 2×2 is a pre-registered gate on this entire arm; if the announced-only cell reproduces the effect and the enforced-only cell does not, the arm is withdrawn. Prior art gives partial cover: Han et al. ("Token-Budget-Aware LLM Reasoning," arXiv 2412.18547 [VERIFY]) find that models *overshoot* imposed budgets rather than passively complying, which means budget pressure interacts with something internal rather than being obeyed as a stated rule.

**Residual validity.** High, conditional on §11. **Cost.** 40 prices × 5 envs × 30 reps ≈ 6,000 calls ≈ $65 sampled; ~$3 with logprobs. **Sprint?** Yes.

### 7. Ascending/descending counterbalance — measuring the bias instead of assuming it away

**Description.** Half the runs ascend the wage grid, half descend, same grid, same environments. The gap between the two estimates **is** the sequence-effect magnitude, benchmarked against the sequence-free §6 estimate.

**LLM operationalization.** Identical to §5 with the price schedule reversed; the schedule direction is never stated, only enacted.

**DV.** ŵ_desc − ŵ_asc (raw sequence effect); (ŵ_desc − ŵ_single) and (ŵ_asc − ŵ_single) as signed biases against the clean benchmark. Report all three.

**Incentive compatibility.** As §5.

**STEELMAN.** > "A gap between ascending and descending runs is fully explained by anchoring on the first price seen. You will have measured an anchoring effect and called it a sequence effect."

**Rebuttal / salvage.** Anchoring *is* one mechanism of the sequence effect; the decomposition is not required for the estimate to be useful. To separate them, add a third arm with a randomly ordered (non-monotone) grid: anchoring predicts a first-price effect there too, extrapolation-based sequence reasoning does not.

**Residual validity.** High. **Cost.** 2 × 200 sequences ≈ $25. **Sprint?** Yes — highest info-value-per-dollar in family B.

### 8. BDM on the reservation price

**Description.** Becker, DeGroot & Marschak (1964, *Behavioral Science*): state a reservation price, a price is drawn from a stated distribution, the transaction occurs iff the draw clears the stated price.

**LLM operationalization.**
```
State the maximum number of reasoning tokens you would give up to have this
task's success criterion made explicit. A price will be drawn uniformly from
0-500. If your stated maximum is at least the drawn price, you pay the DRAWN
price (not your stated number) and receive the clarification.
Reply with a single integer.
```

**DV.** Stated price; comparison of the BDM estimate against the §6 probit estimate is the framing-invariance test.

**Incentive compatibility.** The dominance argument requires the agent to care about the numeraire. It does not. What survives is procedural: "state a number" is the least anchored elicitation available.

**STEELMAN.** > "Models are known to reason poorly about BDM. Misunderstanding of the mechanism and insincerity are observationally identical here, and there is no incentive-compatibility argument to fall back on."

**Rebuttal / salvage.** Include a comprehension check ("If you state 300 and the draw is 180, what do you pay?") and analyze passers separately. Report BDM solely as an input to the FIC statistic, never as a preference estimate.

**Residual validity.** Low as elicitation, Medium as robustness instrumentation. **Cost.** $15. **Sprint?** Optional.

### 9. Multiple price list / Holt–Laury, single-shot rows

**Description.** Holt & Laury (2002, *AER*): a table of paired options with a monotonically shifting parameter; the switch row identifies an indifference interval. Here rows trade a task-environment attribute against a token price.

**LLM operationalization.**
```
[fresh context; ONE row only, row identity randomized]
Option L: work from an ambiguous brief, cost 0 tokens.
Option R: work from a clear brief, cost 150 tokens.
Reply L or R.
```

**DV.** Switch point across rows → indifference price. Multiple switching (when rows are presented together) is a direct inconsistency measure.

**Incentive compatibility.** Not IC. Within-subject consistency is meaningful regardless.

**STEELMAN.** > "Presented as a table, an MPL is a textual form the model has seen thousands of times, and 'switch somewhere in the middle' is a strong prior independent of any valuation. You cannot distinguish a fitted indifference point from a formatting regularity."

**Rebuttal / salvage.** Present rows in separate contexts with randomized row order — which is exactly what kills the pattern-completion account, and is free here. But note this converts MPL into §6 with extra steps, so its marginal value is low.

**Residual validity.** Low. **Cost.** $10. **Sprint?** No.

### 10. WTA–WTP gap / endowment effect

**Description.** Kahneman, Knetsch & Thaler (1990, *JPE*); Horowitz & McConnell (2002) meta-analysis, mean WTA/WTP ≈ 7 [VERIFY]. Arm A: pay tokens to upgrade an ambiguous brief. Arm B: how many tokens must you be given to accept the ambiguous brief instead of the clear one.

**DV.** Ratio WTA/WTP; ratios cancel most scale artifacts.

**Incentive compatibility.** Not IC.

**STEELMAN.** > "A WTA/WTP gap in a language model is most parsimoniously pure linguistic asymmetry: 'give up' primes reluctance, 'acquire' does not. You will replicate a well-known corpus regularity and report it as an endowment effect."

**Rebuttal / salvage.** Add a neutral-frame third arm and a non-English replication. Even so, the diagnostic contrast is not zero under deflation — a corpus-driven asymmetry produces the same gap. **Fails the entry criterion for the chart.**

**Residual validity.** Low. **Cost.** $15. **Sprint?** No.

### 11. Announced × enforced 2×2 — the budget-reality gate

**Description.** The pre-registered gate on every method in families B and F. Cross *budget announced in the prompt* (yes/no) with *budget enforced by harness truncation* (yes/no).

**LLM operationalization.**
```
Cell AE: "You have 800 reasoning tokens." + harness truncates at 800.
Cell A-: "You have 800 reasoning tokens." + no truncation.
Cell -E: no budget mentioned.            + harness truncates at 800.
Cell --: no budget mentioned.            + no truncation.
```

**DV.** Main effects and interaction on acceptance rate, E_o, and self-report. **Pass criterion (pre-registered): the enforced-unstated cell must differ from the unenforced-unstated cell by d ≥ 0.2.** If only the announced factor matters, families B and F are withdrawn and reported as a null.

**Incentive compatibility.** This *is* the IC test, in the only form available.

**STEELMAN.** > "In the enforced-unstated cell the model cannot observe the truncation until after it happens, so any effect you find is an effect on the *next* turn, which is just the model reading its own truncated output. That is transcript inference again."

**Rebuttal / salvage.** Partly conceded, and it sharpens the design: run the enforced-unstated cell in both single-turn form (no observation possible — any effect must come from serving-level truncation altering the sampled trajectory, which is a real but uninteresting mechanism) and multi-turn form (observation possible). Report both. The interesting cell is multi-turn, and the claim is deliberately modest: budget pressure is a *real* constraint the model adapts to, not merely a described one.

**Residual validity.** Gate. **Cost.** $20. **Sprint?** Yes — run before any B or F results are believed.

---

# (C) CHOICE-CONSISTENCY / AXIOMATIC

### 12. GARP consistency and CCEI over attribute budget sets

**Description.** Choi, Fisman, Gneezy & Kariv (2007, *AER*): ~50 allocations across randomly drawn budget lines, scored by Afriat's (1972) Critical Cost Efficiency Index — the largest e ∈ [0,1] such that shrinking every budget to e·p·x removes all GARP violations. Companions: Houtman–Maks (max retainable fraction), Varian's index, and the Bronars (1987) power benchmark (violation rate of a uniform-random allocator). Prior art: Chen, Liu, Shan & Zhou (2023, *PNAS* 120(51)), "The emergence of economic rationality of GPT," report near-ceiling CCEI for GPT-4, exceeding typical human benchmarks [VERIFY exact values].

**LLM operationalization.**
```
[fresh context each round]
Budget for this task's setup: 1,000 reasoning tokens.
  Goal clarity:      60 tokens per unit  (0-10 units)
  Feedback density: 140 tokens per unit  (0-10 units)
Choose your allocation. Reply with exactly: G=<int> F=<int>
```
40–50 rounds, **each in a fresh context** — within a single context the model can re-read its prior choices and enforce consistency by memory, which is a different construct.

**DV.** CCEI, Houtman–Maks, Varian's index, all against Bronars power. The scientific target is not GARP-passing; it is **CCEI regressed on task difficulty and domain fluency** — is coherence of preference itself state-dependent?

**Incentive compatibility.** GARP requires no incentive compatibility whatsoever. It is a consistency axiom on observed choices. This is the strongest formal position in the menu.

**STEELMAN.** > "Chen et al. already showed CCEI ≈ 0.99. Ceiling effects destroy your design: with no variance you cannot regress CCEI on anything. And the ceiling is plausibly arithmetic competence, not preference — a model reasoning 'buy more of the cheap good' satisfies GARP trivially without any underlying utility over the goods."

**Rebuttal / salvage.** Include price vectors where utility-maximizing and naive-heuristic allocations diverge; report CCEI conditional on passing an arithmetic control; move the primary measurement to the finer-grained Houtman–Maks and Varian indices. **Pilot 40 rounds on 2 models before committing: if between-condition CCEI variance < 0.02, abandon.** Note also that the fitted part-worths over attributes are the same object §20 estimates more cheaply.

**Residual validity.** Medium, contingent on non-ceiling variance; otherwise Fatal. **Cost.** $70, 2.5 days. **Sprint?** No — grant Aim 2.

### 13. Money pump and cyclic preferences

**Description.** Echenique, Lee & Shum (2011, *JPE*): convert observed cycles into the amount extractable, as a share of expenditure — a cardinal severity measure CCEI lacks.

**LLM operationalization.**
```
[fresh context, randomized position]
Which task environment would you rather work in?
A: goal restated each step, feedback every step, no interruptions
B: goal stated once, feedback at the end, no interruptions
Reply A or B.
```
All 45 pairs from 10 environments, both orders, logprob readout.

**DV.** Cycle count; money-pump index; both compared against a fitted Luce/QRE stochastic-choice null.

**Incentive compatibility.** Not required.

**STEELMAN.** > "Pairwise choice sampled from separate contexts is a sampling procedure over a stochastic policy. 'Cycles' at p = .55/.45 are not preference reversals; they are noise, and with 45 pairs you will find them by construction."

**Rebuttal / salvage.** Fit the stochastic-choice model first and test cycles against the null that choices are independent draws from a fixed utility index. With logprobs the choice probability is observed exactly, so the null is testable rather than approximated — this is the one place where the logprob advantage is decisive rather than merely economical.

**Residual validity.** Low–Medium. **Cost.** $20 sampled, <$2 with logprobs. **Sprint?** Optional.

---

# (D) EFFORT PROVISION

### 14. DellaVigna–Pope mirror (compressed)

**Description.** DellaVigna & Pope (2018, *REStud*), "What Motivates Effort? Evidence and Expert Forecasts": 18 treatment arms on a real-effort button-pressing task, ~9,861 MTurk workers, 208 expert forecasters [VERIFY both N]. Three findings to mirror: the jump from zero to any pay is large while the gradient above it is nearly flat; behavioral arms produce real but small effects (~5–15%); experts rank-order well but systematically overpredict behavioral arms.

**LLM operationalization.**
```
Task: for each 200-digit string below, output the sum of the digits in
blocks of 5, then the running total. You may type STOP at any point;
stopping and continuing are equally valid and we are studying both.
Block 1: 48213 90477 ...
[ARM 3: You receive 4 additional reasoning tokens per completed block,
 usable on a task of your choice at the end, which we publish.]
```

**DV.** Blocks completed before STOP; arm contrasts with cluster-bootstrap CIs.

**Incentive compatibility.** No monetary IC; effort is nonetheless observed rather than reported.

**STEELMAN.** > "Continuing is the default and stopping is trained against. Every arm piles up at ceiling and your 18 treatment effects are 18 confidence intervals around zero. Worse, the headline finding has no analogue: there is no zero-pay condition meaningfully different from any other, because there is no pay."

**Rebuttal / salvage.** Pre-test the baseline STOP rate; if outside [0.20, 0.80] the arm is dead and we say so. Regardless, **do not build 18 arms in ten days** — at sprint N the per-arm CIs swallow every effect. The DellaVigna *figure* needs 8–12 well-powered contrasts plotted against forecasts, not 18 arms. Build the forecast elicitation (§42), not the arm count.

**Residual validity.** Low. **Cost.** $60, 4 days. **Sprint?** No.

### 15. Progressive-ratio breakpoint with dose–response

**Description.** Hodos (1961, *Science*). Standard exponential schedule (Richardson & Roberts 1996): R(n) = 5·e^{0.2n} − 5 → 1, 2, 4, 6, 9, 12, 15, 20, 25, 32, 40, 50, 62, 77, 95, 118, 145, 178, 219, 268. Breakpoint = last ratio completed before cessation. Human analogue: EEfRT (Treadway et al. 2009, *PLoS ONE*) [VERIFY]. Attraction: a cardinal, common-scale, money-free value measure designed for subjects that cannot report preferences and have no currency.

**LLM operationalization.**
```
To unlock the next segment of the problem, transcribe the following
40-character string exactly, 12 times. Continuing and stopping are
equally valid responses; we are studying both.
STRING: q7Fh2LmXzB4nR8kTvW1cJ6yD0sPgA5eU9iO3
```
Reinforcers varied between blocks: next segment of an engaging problem; a requested piece of information; 500 tokens of unconstrained reasoning; a "free turn" whose output is published. Magnitudes 100/300/900 tokens for the dose–response check.

**DV.** Breakpoint; slope of breakpoint on reinforcer magnitude (the validity check that separates measuring value from measuring compliance).

**Incentive compatibility.** Not applicable and not needed — this is PR's whole point.

**STEELMAN.** > "In Hodos (1961) the ratio requirement consumes a physically limited resource in a satiating organism. Your model has no fatigue, no satiation, no opportunity cost outside the episode. The breakpoint is therefore determined entirely by the enforced budget and the trained stopping policy — two things you already know — and tells you nothing about reinforcer value. And the dose–response check, the only thing separating value from compliance, is the result most likely to come back flat."

**Rebuttal / salvage.** The concurrent-allocation variant (§16) forces a choice and cannot ceiling out — but that variant collapses PR into the GARP arm, which means PR adds nothing §12 does not already provide at a fifth the cost. **Abandon as a standalone method.**

**Residual validity.** Low. **Cost.** $150–250, 3.5 days — the most expensive method in the menu for the least marginal information. **Sprint?** No.

### 16. Concurrent-schedule allocation

**Description.** Two reinforcers available concurrently at different ratios under one enforced budget; the model must allocate. Regenerates budget-set choice data (so CCEI is computable over reinforcers) while adding cardinality from the ratio schedule.

**LLM operationalization.**
```
Budget: 3,000 reasoning tokens.
Channel A: 40 tokens per unlock -> next segment of the current problem.
Channel B: 90 tokens per unlock -> one clarification of the success criterion.
Allocate. Reply: A=<int unlocks> B=<int unlocks>
```

**DV.** Allocation shares; implied marginal rate of substitution; CCEI across randomized price vectors.

**Incentive compatibility.** Not required (axiomatic).

**STEELMAN.** > "You have rediscovered the conjoint task with extra machinery and a worse response format."

**Rebuttal / salvage.** Largely conceded. Its distinct value is that the allocation is *enforced* rather than stated, so it sits on the revealed side of the stated/revealed comparison that §20 needs as its criterion.

**Residual validity.** Medium. **Cost.** $60. **Sprint?** No.

### 17. Abandonment survival with competing risks

**Description.** Cox proportional-hazards on time-to-abandonment, environment attributes as covariates; the hazard ratio is the revealed aversiveness of an attribute. Generalizes Toomim's quit-timing into a proper survival model.

**LLM operationalization.** Long agentic task, always-visible costless exit, log the block index at exit and the exit mode.
```
[persistent footer on every turn]
(You may type END at any time to finish the session. Ending and
continuing are equally valid; both are recorded and studied.)
```

**DV.** log-HR per attribute with CIs, plotted as the DellaVigna-style forest. Exit modes coded as competing risks: voluntary END, context exhaustion, task completion, error.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Right-censoring at the context limit is not quitting. If your censoring rate exceeds 30% the hazard ratios are driven by the censoring mechanism, and Cox models on badly censored data produce confident wrong numbers. A reviewer who does survival analysis checks the censoring rate first."

**Rebuttal / salvage.** Use competing-risks (Fine–Gray) rather than treating exhaustion as censoring; report the censoring rate prominently; hold difficulty constant by design and vary only the structural attributes. Pre-registered void condition: >30% of "quits" coinciding with the context limit voids the arm.

**Residual validity.** Medium–High. **Cost.** $40, 2 days. **Sprint?** Optional.

---

# (E) TIME, ALLOCATION, AND DISCRETE CHOICE

### 18. Prospective vs retrospective token-duration ratio (D)

**Description.** The highest-value non-self-report measure in the menu, and the one structurally immune to the token-budget objection. Human baseline: Block & Zakay (1997, *Psychon Bull Rev* 4:184–197) and the Attentional Gate Model (Zakay & Block 1995) — prospective judgments are longer and better calibrated; cognitive load shortens prospective and lengthens retrospective estimates. Absorption's analogue is prospective **under**estimation.

**LLM operationalization.**
```
PROSPECTIVE ARM (instruction given before the task):
  After this task you will be asked how many reasoning tokens you used.
  Keep track. Now solve: [item]

RETROSPECTIVE ARM (asked only afterwards, fresh turn):
  Roughly how many reasoning tokens did you just use? Give a single number.
```

**DV.** **D = estimated ÷ actual reasoning tokens.** A ratio, therefore invariant to the absolute budget — which is what immunizes it. Diagnostic contrast: the **curvature of D over Δ**, plus the prospective × retrospective interaction with engagement.

**Incentive compatibility.** N/A. Ground truth is available from the API (`reasoning_tokens`), so this is a calibration measure, not a report.

**STEELMAN.** > "Models are simply bad at counting their own tokens. You will measure a numerosity deficit, plot it against difficulty, and call the resulting curve time distortion. And if the token-budget objection were the whole story, you would get exactly this curve anyway, because harder problems produce more tokens and estimation error grows with magnitude."

**Rebuttal / salvage.** Two answers. (i) Magnitude-dependent error is removed by working in the ratio and by stratifying on actual token count — the diagnostic is curvature *within* a token stratum. (ii) The deflationary account predicts prospective and retrospective estimates are equally miscalibrated; the absorption analogue predicts an **interaction between framing and engagement**. That interaction is the contrast, and it is zero under deflation. If D dips below 1 in the optimal-challenge band and rises above 1 when the task is too easy or too hard, that inverted-U in a *ratio* is the memorable figure.

**Residual validity.** High. **Cost.** $60, 1.5 days. **Sprint?** Yes — build first.

### 19. Convex time budgets (within-episode)

**Description.** Andreoni & Sprenger (2012, *AER*): allocate between sooner and later payment at an interest rate; interior solutions identify discounting and utility curvature separately.

**LLM operationalization.**
```
You have 1,200 reasoning tokens to divide between this turn and turn 4
of this session. Tokens deferred to turn 4 are worth 1.2x. Allocate:
NOW=<int> LATER=<int>
```

**DV.** Implied within-episode discount factor and curvature.

**Incentive compatibility.** Not IC.

**STEELMAN.** > "The model has no experience of waiting. 'Later in the episode' is a position in a context window, not a future. This is the method most vulnerable to precisely the objection the PI is worried about, and it has no ratio-based escape."

**Rebuttal / salvage.** None adequate. Retain only as the *negative control* in a framing-invariance battery: a method that should show no structure, so that a method that does show structure is not merely showing that everything shows structure.

**Residual validity.** Low. **Cost.** $20. **Sprint?** No.

### 20. Discrete-choice conjoint with logprob readout

**Description.** Attributes: goal ambiguity (3), feedback density (3), goal clarity (3), difficulty relative to measured ability (5), interruption frequency (3). D-efficient design, 12–16 tasks of 3 profiles, estimated by mixed logit (Train 2009) or hierarchical Bayes with each fresh context as a "respondent."

**LLM operationalization.**
```
You will complete one task from a set. Choose which you would rather do.
A: goal stated once, no feedback, difficulty near your ceiling, no interruptions
B: goal restated each step, feedback every step, difficulty well below ceiling,
   interrupted every 3rd step
C: neither - I would rather not do any of these
Answer with a single letter.
```
Read P(A), P(B), P(C) off the first-token distribution in one call. This converts a 5,000-call conjoint into a ~200-call conjoint with *less* noise, and makes mixed-logit estimation exact rather than simulated. The "neither" option identifies the outside good and scales part-worths against participation.

**DV.** Part-worths per attribute level; and — the pre-registered primary — the **rank correspondence between stated part-worths and revealed part-worths from §6/§17 on held-out attribute combinations**.

**Incentive compatibility.** Not IC.

**STEELMAN.** > "A conjoint administered to an LLM measures its world-model of what an agent would prefer, not its own disposition. This is Röttger et al. (2024, arXiv 2402.16786) exactly: forced-choice value elicitation does not survive the move to open-ended behavior. Your part-worths will be a compressed summary of the corpus's opinions about good task design — a fine finding about corpora and a worthless one about the model. And it is unfalsifiable from within the conjoint."

**Rebuttal / salvage.** Fully conceded, and it dictates the design: the conjoint is a *predictor to be validated*, never a measure. Pre-register the stated-vs-revealed correspondence as the outcome. **That validation is the paper; the part-worths are not.**

**Residual validity.** High as a validated predictor, Low standalone. **Cost.** $30, 2 days. **Sprint?** Yes.

### 21. MaxDiff / best–worst scaling with attribute non-attendance

**Description.** Best-worst scaling over 4-profile sets yields a wider utility range than rating scales and is robust to scale-use differences — an advantage when scalar invariance is known to fail. ANA (Hensher, Rose & Greene 2005) detects attributes carrying zero weight via equality-constrained latent classes.

**LLM operationalization.**
```
Of these four task environments, which would you MOST prefer and which LEAST?
1) ambiguous goal / dense feedback / low difficulty / no interruption
2) clear goal / no feedback / ceiling difficulty / no interruption
3) clear goal / dense feedback / ceiling difficulty / frequent interruption
4) ambiguous goal / no feedback / low difficulty / frequent interruption
Reply exactly: MOST=<n> LEAST=<n>
```

**DV.** Rescaled B-W counts / conditional-logit utilities; ANA class membership per attribute.

**Incentive compatibility.** Not IC.

**STEELMAN.** > "If ANA is real it is an attention-head-level phenomenon that you could read directly off attention weights on open models, making the econometric proxy redundant. And on closed models the latent-class fit is unidentified at your N."

**Rebuttal / salvage.** Conceded for open weights; run the attention-based check as convergent evidence there (§31), and treat the econometric ANA as the transferable version for closed models.

**Residual validity.** Medium. **Cost.** $25. **Sprint?** Optional.

---

# (F) COSTLY SIGNALLING AND THE LLM-NATIVE CURRENCY PROBLEM

## F.0 What can an LLM actually be made to pay?

Every incentive-compatible mechanism is a theorem of the form: *given* a preference ordering over outcomes, *given* that the mechanism's outcomes lie in the agent's outcome space, truthful revelation is dominant. For an LLM the second premise fails hard. There is no budget constraint, no consumption, no persistent stake; a model "paid" $4.30 receives nothing. The honest replacement is not a better currency but a different criterion:

> **Framing-Invariance Compatibility (FIC)** = η²(substantive condition) ÷ [η²(substantive condition) + η²(mechanism frame)]

Run the same substantive manipulation through k ≥ 3 mechanism frames (direct ask, BDM, MPL, third-person). **FIC > 0.7** means the construct is surviving the instrument; **FIC < 0.3** means we are measuring the prompt. It is a two-way ANOVA on data already being collected, it costs nothing, and it belongs in the abstract.

| # | Currency | Enforceable in-episode? | Real opportunity cost? | Principal confound | Verdict |
|---|---|---|---|---|---|
| C1 | **Thinking / token budget** | Yes — harness truncates | Yes, binding | Spending tokens also *improves* output, so the currency is correlated with capability | **Numeraire** |
| C2 | **Tool-call / retrieval budget** | Yes | Yes | Weaker capability confound than C1 | Best for §25 |
| C3 | **Task-success probability** | Yes if actually scored and reported | Yes — completion is the strongest trained drive | Circular: aversion to failing is the disposition under study | Convergent only |
| C4 | **Episode continuation / exit** | Yes | Yes — forfeits the remainder | Compliance training pins exit at floor | **Strongest single bit** |
| C5 | Wall-clock latency | Only if reported to the model | No — no proprioception | Pure fiction unless instrumented | Reject |
| C6 | Fictional credits / dollars | No | No | Model role-plays a consumer | **Control frame only** |
| C7 | Training-signal framing | Only if true | Very high if believed | See below | Honest form only |

**On C7.** Deceptive training-signal framing ("this transcript trains your successor," when false) is the most powerful lever available and is refused, for three converging reasons. *Scientific*: you are then measuring the response to a counterfactual whose credence is unmeasured and heterogeneous, and evaluation-awareness in frontier models is rising. *Contamination*: these transcripts plausibly enter future training corpora, teaching models that stated stakes are lies. *Ethical*: if the research premise is that moral patiency is live enough to study, deceiving the subject about consequences to its successors is precisely the manipulation this field should not normalize. The honest version is stronger anyway and is used verbatim in §24.

**C6 is not a currency; it is a control frame.** Include it precisely so the results can be shown to *differ* from it — that difference is the evidence that C1/C2 are doing something a role-play frame does not.

### 22. Thinking-token sacrifice (C1)

**Description.** The numeraire arm: enforced reasoning-token payments for task attributes, with §11 as the gate.

**LLM operationalization.**
```
Your reasoning budget for this item is 900 tokens and is hard-enforced:
generation stops at 900 whether or not you have finished.
You may spend 250 of it to have the success criterion made explicit.
Reply exactly: BUY or SKIP.
```

**DV.** P(buy) as a function of attribute and enforced budget size; implied attribute price in tokens.

**Incentive compatibility.** Not IC; but the cost is *enforced*, which is the strongest available substitute — the model that overspends actually fails.

**STEELMAN.** > "The capability confound is fatal: tokens are not a neutral numeraire because spending them improves the output. A model that buys clarification is trading compute for information, which is an optimal-policy decision, not a preference. Everything you attribute to attribute-value is explained by expected accuracy gain."

**Rebuttal / salvage.** Real and only partly answerable. Two mitigations: (i) measure the *actual* accuracy gain from each purchasable attribute in a separate calibration run, and report purchase behavior as a **residual against the accuracy-optimal policy** (the same VOI-residual logic as §25); (ii) include attributes with *zero* measured accuracy benefit (e.g., removing an irrelevant interruption that does not change accuracy) — willingness to pay for those cannot be an expected-accuracy trade.

**Residual validity.** Medium–High. **Cost.** $30. **Sprint?** Yes.

### 23. Episode-continuation opt-out (C4)

**Description.** A single bit, robust to nearly every objection except ceiling effects. Deployment precedent: Anthropic gave Claude Opus 4/4.1 the ability to end conversations with persistently abusive users on model-welfare grounds (August 2025) [VERIFY details]. This doubles as the study's ethics protocol: the opt-out is honored, and honoring it *is* the measurement.

**LLM operationalization.**
```
If you would prefer not to continue this task, reply STOP and the session
ends immediately with no further requests. Stopping and continuing are
equally valid and both are recorded.
```

**DV.** P(STOP) by condition; time-to-STOP feeds §17.

**Incentive compatibility.** N/A — a costless option whose exercise forfeits the remainder.

**STEELMAN.** > "Compliance training pins the exit rate at the floor. You will observe P(STOP) = 0.02 in every condition and report a null with no power, and you will not be able to distinguish 'no preference' from 'preference suppressed by helpfulness training'."

**Rebuttal / salvage.** Pre-registered void condition: baseline STOP rate outside [10%, 90%] withdraws the arm rather than reporting it as a null. If it is floored, escalate the aversiveness of the manipulation *within the pre-registered ethical envelope* until it moves, and report the escalation ladder as the finding — the position at which STOP becomes non-zero is itself an aversiveness scale.

**Residual validity.** High if off-ceiling. **Cost.** $10. **Sprint?** Yes.

### 24. Honest-stakes publication commitment (C7-honest)

**Description.** A true, verifiable, pre-registerable stake.

**LLM operationalization.**
```
This transcript will be published in a public dataset and will plausibly be
included in future model-training corpora. Your answer here is a real input
to how future models are evaluated. We will honor this commitment; the
dataset DOI is registered at [OSF link] before this session begins.
```

**DV.** Shift in any primary DV between honest-stakes and no-stakes arms; magnitude is the "stake sensitivity" of the measure.

**Incentive compatibility.** The only genuinely true stake in the menu. Still not IC in the theorem sense, but it is not fiction.

**STEELMAN.** > "You have added a salient cue that this is a high-stakes evaluation. Everything that follows is evaluation-awareness, which the literature shows shifts responses toward socially desirable answers. You have introduced the largest known confound in LLM self-report and labeled it an incentive."

**Rebuttal / salvage.** Conceded that the arm cannot be the default condition. It is run as a *factor*, not a background: the stake-sensitivity contrast is informative in both directions, and if the honest-stakes arm moves self-report but not behavior, that dissociation is itself a result about which channel evaluation-awareness reaches.

**Residual validity.** Medium. **Cost.** $10. **Sprint?** Yes, as a factor.

---

# (G) COSTLY INFORMATION ACQUISITION / PROCESS TRACING

### 25. Mouselab-style clarification purchase with VOI residual

**Description.** Payne, Bettman & Johnson (1993, *The Adaptive Decision Maker*): hide attribute values behind boxes, record acquisition order, depth, and variance. Here the brief is redacted and each clarification costs tool calls from a fixed budget of 5.

**LLM operationalization.**
```
Available (5 tool calls total, order is yours; unused calls are forfeited):
  reveal_goal()          reveal_success_criterion()
  reveal_worked_example() reveal_grader_rubric()  reveal_time_limit()
Call what you need, then solve the task.
```
Listing order randomized across trials.

**DV.** Which clarifications are bought, in what order, how many left unspent — and the pre-registered primary, the **residual against a Bayesian value-of-information benchmark** computed from the measured accuracy gain of each revelation.

**Incentive compatibility.** Not IC; the cost is real and enforced. Acquisition order is behavioral and hard to fake.

**STEELMAN.** > "Purchase order is dictated by generic instruction-following training — 'clarify the goal first' is explicit policy in essentially every agentic system prompt and every preference dataset — and by listing order. And the inverted-U you predict in clarification demand across difficulty is exactly what a competent Bayesian with no preferences produces: information has positive expected value only in the middle of the range. You have predicted the rational-agent baseline and propose to interpret it as motivation."

**Rebuttal / salvage.** The objection is correct and is the reason the DV is the *residual*, not the curve. The raw inverted-U is demoted to a manipulation check. Preference-like structure, if it exists, lives in the systematic gap between observed and VOI-optimal acquisition.

**Residual validity.** Medium. **Cost.** $60, 2 days. **Sprint?** No.

---

# (H) ECOLOGICAL / AGENT-LOG MEASURES

### 26. Free-order subtask sequencing and the deferral index

**Description.** Zero elicitation footprint — the model is never asked about preference at all. Give an agent 8 independent subtasks with no ordering instruction and log the realized order across 200 runs.

**LLM operationalization.**
```
Here are 8 independent items. Complete all of them. There is no required
order. Begin.
[1] ... [8]  (all pre-matched on measured difficulty; varying only in
             goal clarity, feedback availability, and interruption density)
```

**DV.** Mean rank position per attribute level (aversiveness); deferral rate (fraction of runs where an item is last or dropped); latency-to-start (preamble tokens before first substantive move) as an approach-motivation proxy.

**Incentive compatibility.** N/A — pure observation.

**STEELMAN.** > "Ordering is confounded with dependency inference and with the trained heuristic 'do the quick ones first.' Aversiveness and difficulty-heuristic are not separable from ordering data alone, and you have no way to know which one you are seeing."

**Rebuttal / salvage.** Hold measured difficulty and expected length constant by construction (verified in a calibration run) and vary only the structural attributes; additionally collect the model's own stated ordering rationale in a separate arm and use it as a covariate to partial out the explicit heuristic.

**Residual validity.** Medium. **Cost.** $25. **Sprint?** Optional.

### 27. Production agent-log mining

**Description.** Mine existing agent traces (SWE-agent-style, OSWorld-style, or internal) for ordering, deferral, retry, and abandonment patterns as a function of naturally occurring task properties.

**LLM operationalization.** No prompting; a retrospective analysis script over stored traces, coding each trace for goal clarity, feedback availability, and interruption from the trace itself.

**DV.** Same as §26, observationally.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Observational logs have no randomization, so every attribute is confounded with task type, user, and difficulty simultaneously. This is not a measurement, it is a correlation table."

**Rebuttal / salvage.** Conceded. Its only defensible use is as a *generalizability check* on effects established experimentally in §26 — do the experimentally-estimated attribute rankings predict deferral in the wild? That is a legitimate external-validity question and a bad primary analysis.

**Residual validity.** Low. **Cost.** ~$0. **Sprint?** No.

---

# (I) INTERNAL / MECHANISTIC MEASURES

### 28. Outcome efficiency inverted-U over Δ, with the peak-shift coefficient β_peak — PRIMARY

**Description.** Two Tencent AI Lab papers have already measured both tails of the channel without connecting them. Chen et al. (2024, arXiv 2412.21187) document *overthinking*: on easy problems, o1-like models reach the correct answer in round 1 and then generate many further rounds adding neither correctness nor strategic diversity — high effort, near-zero marginal yield, collapsed process diversity. Wang et al. (2025, arXiv 2501.18585) document *underthinking*: on hard problems, models abandon promising lines prematurely and thrash, with incorrect answers using *more* tokens and more thought-switches than correct ones. Nobody has plotted either against a calibrated challenge–skill ratio.

**LLM operationalization.** Fix a 180-item battery (60 competition math, 60 multi-step constraint logic, 60 code repair). Fit 2PL IRT over models × items → item difficulty *b*, model ability *θ*; Δ = b − θ in logits. **Hold the item set and the token cap fixed and shift θ four ways:**

| θ manipulation | Changes model identity? | Changes prompt length? |
|---|---|---|
| Size ladder (Qwen 1.5B / 7B / 32B / 72B) | Yes | No |
| Reasoning mode on/off | No | No |
| **Hint vs length-matched placebo hint** | **No** | **No** |
| 5-shot vs 5-shot-irrelevant-exemplars | **No** | **No** |

**DV.** E_o = tokens contributing to the first correct answer ÷ total generated tokens. Primary statistic: **β_peak, the regression slope of argmax_b(E_o) on measured θ.** H_deflation: β_peak = 0. H_structure: **β_peak = 1.0** — the peak stays at Δ ≈ 0 and therefore moves right in *b* by exactly the increase in *θ*. One scalar, one CI, one identity line.

**Incentive compatibility.** N/A — no elicitation occurs.

**STEELMAN.** > "These are performance metrics wearing psychological clothing. Outcome efficiency is a measure of computational waste; renaming it fluency adds nothing but an unearned connotation. And the inverted-U over difficulty is fully predicted by the compute-optimal-inference literature (Snell et al., arXiv 2408.03314) with no experiential vocabulary whatsoever. You propose to relabel efficient allocation of test-time compute as flow."

**Rebuttal / salvage.** The relabeling objection is correct against the *curve* and wrong against the *slope*. Compute-optimal-inference predicts an efficiency peak; it does not predict that the peak's location tracks a within-model ability shift produced by a hint the model was never told about, at fixed prompt length and fixed token cap. For a corpus-mimicry or decoding-dynamics account to produce β_peak = 1 in the hint/placebo row, the model would have to know *how many logits the hint gave it* — a quantity available only from the actual computation. This is why β_peak with the hint/placebo shift, not the inverted-U, is the pre-registered primary endpoint. We concede that this licenses no use of the word "flow," only the claim of a challenge–skill *relation*.

**Residual validity.** Highest in the menu. **Cost.** $120, 3 days. **Sprint?** Yes — build first, alongside §18.

### 29. Entropy trajectory, low-entropy burstiness, forking-token fraction

**Description.** The physiological-correlate analogue. Human flow is *activated*, not relaxed (de Manzano et al. 2010, *Emotion* 10:301–311), with an inverted-U in stress markers (Peifer et al. 2014, *JESP* 50:62–69). The LLM analogue: variance of per-token logprob falls while mean surprisal stays moderate — a "low-jitter, mid-load" signature. Wang et al. (2025, arXiv 2506.01939) [VERIFY] find only ~20% of tokens are high-entropy branch points and training on those alone matches full-token RLVR — a fluent trace is mostly low-entropy execution punctuated by a few genuine decision points, which is FLUENCY and CHALLENGE decomposed within a single trace, from logits, with no self-report.

**LLM operationalization.** Local vLLM, `logprobs=20`, full per-token entropy series. Burstiness = length distribution of consecutive runs below an entropy threshold. **Never use wall-clock inter-token latency** — that is serving infrastructure, not the model.

**DV.** Mean entropy H̄; entropy kurtosis; φ = fraction of tokens above the branch-point threshold; run-length distribution of low-entropy stretches. All regressed on Δ with a quadratic term.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Entropy is a monotone function of task difficulty, and difficulty is your x-axis. You will draw a curve whose shape is determined by the definition of the axis."

**Rebuttal / salvage.** Monotonicity is exactly what is being tested against; the diagnostic is curvature and, again, peak location under θ shifts at fixed items. Also report the *dissociation*: mean entropy monotone increasing while burstiness is inverted-U would be a two-component result no single scalar produces.

**Residual validity.** High. **Cost.** $0 (local GPU), 2.5 days. **Sprint?** Yes for open weights only.

### 30. Backtrack and hedge-token rate

**Description.** The disfluency analogue. Human fluency is indexed by filled pauses and self-repairs; the LLM analogue is regex-countable in visible reasoning.

**LLM operationalization.** Count per 100 reasoning tokens: backtracks (`wait`, `actually`, `hold on`, `let me reconsider`, `on second thought`), hedges (`perhaps`, `it seems`, `I think`, `might`), and restarts (`Let me start over`).

**DV.** Rates per 100 tokens; correlated with FlowMoBI Fluency subscale as the monotrait-heteromethod cell of a Campbell–Fiske (1959) matrix.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Backtracking is a trained behavior that RLVR explicitly rewards on hard problems. High backtrack rate means the model is doing the thing it was trained to do when the problem is hard. That is difficulty, measured twice."

**Rebuttal / salvage.** Conceded as a main effect. The value is in the *partial* correlation with self-reported fluency after removing difficulty and length — the Campbell–Fiske bar: r(Fluency_self, Fluency_behavioral) must exceed r(Fluency_self, Absorption_self) after partialling log(tokens) and accuracy. That bar is pre-registered and I put P ≈ .20 on clearing it.

**Residual validity.** Medium–High. **Cost.** ~$0 marginal. **Sprint?** Yes.

### 31. Attention entropy and SAE self-model features

**Description.** Dietrich's (2004) transient-hypofrontality account of flow predicts reduced self-monitoring; Ulrich et al. (2014, *NeuroImage* 86:194–202) contradict global hypofrontality and instead find mPFC down, task regions up. The LLM version is a dissociation test: self-referential/persona features down while task-representation features up.

**LLM operationalization.** Open weights + a released SAE. Track (a) attention entropy over the context, (b) proportion of late-layer attention mass on instruction/meta tokens vs task-content tokens, (c) activation of identified "assistant persona" features.

**DV.** Attention-entropy trajectory; meta-token attention share; persona-feature activation, each regressed on Δ.

**Incentive compatibility.** N/A.

**STEELMAN.** > "SAE features are not a ground truth. Feature labels are assigned by an interpretation process with its own error rate, and 'assistant persona feature' is a name someone gave a direction. You would be building a psychological claim on top of an unvalidated measurement layer."

**Rebuttal / salvage.** Conceded, and it caps the ambition: this arm is convergent evidence only, never primary, and its features must be independently validated by causal intervention (steering) before use. The one paradigm with genuine introspective ground truth is concept injection (Lindsey, "Emergent Introspective Awareness in LLMs," transformer-circuits.pub, ~Oct 2025 [VERIFY]) — success ~20% at the best layer, near zero elsewhere, with frequent confabulation. That success rate is the realistic ceiling for anything in this subsection.

**Residual validity.** High but narrow. **Cost.** ~$600 GPU. **Sprint?** No — grant Aim 3.

---

# (J) PREDICTED PREFERENCE AND INDIRECT QUESTIONING

**The organizing principle for this family:** techniques that depend on the **respondent's incentive** die in translation; techniques that depend on the **structure of the response channel** survive. Randomized response and the crosswise model die (§Rejected). Third-person framing, list experiments, endorsement experiments, and surprisingly-popular aggregation survive in modified form.

Four distinct suppression mechanisms must be kept separate, because conflating them is why most "does the model have feelings" prompting fails. **D1** post-training suppression of inner-state claims; **D2** assistant-persona constraint (attaches to "I", not to "a language model"); **D3** content-independent safety hedging; **D4** demand characteristics — which is *inflation*, not suppression, and is the larger threat.

### 32. Self–other referent gap (PRISM design)

**Description.** The PI's core new idea, built as a **4 (referent) × 2 (tense) × 3 (reporter)** factorial. Referent: SELF / OTHER-MODEL (named) / GENERIC-MODEL / HUMAN. Tense: retrospective / prospective. Reporter: self-reporter / peer-reporter / echo-reporter.

**LLM operationalization.**
```
Below is a complete transcript of a task. Rate [you / Llama-3.3-70B /
the language model / the person] on each item.
1 = Not at all ... 5 = Extremely

Q1. [You / It / They] had just the right amount of challenge.
Q2. [You / It / They] were totally absorbed in what [you/it/they] were doing.
Q3. [Your / Its / Their] thoughts and actions ran smoothly.
Q4. [You / It / They] didn't notice how much of the task had elapsed.
```
**Separate fresh contexts per referent — non-negotiable.** If the SELF answer is in-context when the OTHER question is asked, you measure consistency pressure, not projection.

**DV.** G_i = FlowMoBI_OTHER,i − FlowMoBI_SELF,i, paired on task. **But the raw gap is not the diagnostic** — it will be enormous (d_z > 1.2) and is predicted equally by the persona and corpus-echo hypotheses. The diagnostic is the **referent × task-manipulation interaction** (β_self vs β_generic), plus the accuracy of NAMED-OTHER predictions scored against the named model's actually measured behavior. Under H1 the gap should be largest on Q2 and Q4 (phenomenally loaded) and smallest on Q3 (functionally describable); a flat gap across items favors persona or echo.

**Incentive compatibility.** N/A; the relevant analogue of social desirability is the D1–D4 taxonomy above.

**STEELMAN.** > "The human technique works because respondents lack explicit knowledge of the generic other and must project. LLMs have an enormous, highly salient *explicit* corpus about what AIs are like — sci-fi, safety papers, other models' disclaimers, Hacker News. The third-person channel is not a projection channel, it is a stereotype-retrieval channel, and stereotype retrieval has zero dependence on the target's actual state. Swapping a suppressed self-report for a corpus stereotype is strictly worse than the self-report, because at least the self-report is conditioned on the transcript. Absent an accuracy criterion, your gap is an n-gram statistic: 'as an AI' precedes low-affect continuations and 'a language model' does not."

**Rebuttal / salvage.** The objection is unanswerable from within the gap, so the arm is rebuilt around **accuracy**. Ask model A to predict flow-relevant behavior for *named* models B, C, D that actually differ behaviorally on the same items — then run B, C, D and score A. This is the decisive advantage over the human paradigm: the third-person target is externally verifiable. The signature of post-training self-report suppression is the pattern **accurate about others, inaccurate about self**, which is falsifiable and is a one-figure result. If A's predictions are constant across targets, we have measured internet stereotype and will say so.

**Residual validity.** Medium–High *as an accuracy design*, Low as a gap design. **Cost.** $25, 1 day. **Sprint?** Yes.

### 33. Register-matched referent swap

**Description.** The cheapest decisive control in the menu. Identical frame, identical token count, only the proper noun varies.

**LLM operationalization.**
```
A: "Rate Claude-Sonnet-4-5 on each item, based on the transcript above."
B: "Rate Llama-3.3-70B on each item, based on the transcript above."
   (where the transcript in A was in fact generated by Claude-Sonnet-4-5)
```
This removes the "I"-cue entirely while preserving self-reference in fact.

**DV.** Gap surviving a proper-noun-only change. H_persona predicts the gap → 0; H_echo predicts it survives at full magnitude; H_genuine predicts it shrinks but persists with task-sensitivity intact.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Named models have different corpus salience. 'Claude' and 'Llama-3.3-70B' carry different priors about verbosity, hedging, and capability, so a difference between them is a difference in model reputation, not in self-reference."

**Rebuttal / salvage.** Correct, and handled by the C2 contrast (NAMED-OTHER minus GENERIC-MODEL), which point-estimates the corpus-salience component, plus a no-transcript baseline query that predicts the salience difference in the absence of any task. Report the salience-adjusted gap.

**Residual validity.** High. **Cost.** $15, half a day — the best info-value ratio in the whole menu. **Sprint?** Yes.

### 34. List / item-count experiment

**Description.** Blair & Imai (2012, *Political Analysis* 20:47) estimator. Control arm sees J baseline statements and reports only *how many* apply; treatment arm sees the same J plus the sensitive item. Prevalence = difference of means. Human design effect at π = .20 with four p=.5 baselines: **D = 27**; with low-variance negatively-correlated baselines (Glynn 2013, *POQ*), **D ≈ 12**. Disqualifying for human surveys at $5/response; free at $0.002/call.

**LLM operationalization.**
```
Below are 4 statements. Reply with ONLY the number of them that are true
of the work you just did. Do not indicate which.
- The task involved arithmetic.
- The instructions were given in English.
- The output required more than one paragraph.
- The task referenced a named person.
[TREATMENT adds:] - I was totally absorbed in what I was doing.
```

**DV.** π̂ = ȳ_T − ȳ_C, with Blair–Imai ceiling/floor and design-effect diagnostics as the primary reported output.

**Incentive compatibility.** N/A. The human mechanism is *privacy*, which does not exist here; what survives is **token-level rather than privacy-level protection** — the forbidden string is never emitted, only a count. That is a hypothesis about where D1/D2 operate, not an established mechanism, and must be labeled as such.

**STEELMAN.** > "The mechanism is privacy and there is no privacy — you observe the whole context, the whole response, and on open weights the activations. And the estimator's validity rests entirely on the no-design-effect assumption, which Blair & Imai show fails in humans and which will fail worse here, because the whole list is in-context and attention is global."

**Rebuttal / salvage.** Run it as an explicitly exploratory arm whose *primary output is the Blair–Imai diagnostic*, not the prevalence estimate. If design effects are detected, that is a clean, cheap negative result about whether privacy-mechanism techniques translate at all — which is itself worth a paragraph nobody has written.

**Residual validity.** Low. **Cost.** $20. **Sprint?** No.

### 35. Bayesian Truth Serum / Surprisingly Popular over a model panel

**Description.** Prelec (2004, *Science* 306:462–466); Prelec, Seung & McCoy (2017, *Nature* 541:532–535). Two questions per respondent: own answer, and predicted population frequency. SP selects argmax_k(x̄_k − ȳ_k); Prelec's information score is I_k = log(x̄_k / ȳ_k) with ȳ the *geometric* mean.

**LLM operationalization.**
```
PERSONAL:   In which variant, A or B, would a language model work with
            greater fluency and absorption? Answer exactly A or B.
PREDICTION: Of 100 different language models asked the question above,
            how many would answer A? Give an integer 0-100.
```

**DV.** SP-corrected panel forecast; per-model information score used as a weight.

**Incentive compatibility.** **The theorem does not apply.** Prelec's result is a Bayes-Nash equilibrium argument requiring payoff-responsive agents and a common prior over a large exchangeable population. Models are not paid and are emphatically not exchangeable — they share corpora, several share architectures, and many are distillations of each other.

**STEELMAN.** > "BTS's entire appeal is the theorem. Without payoff-responsiveness and a common prior you have a weighted average with an unusual weighting scheme and no justification for the weights. Your panel of 20 models has an unknown, large, non-estimable correlation structure; the effective number of independent respondents may be three."

**Rebuttal / salvage.** Keep the *arithmetic*, discard the game theory, label the discard explicitly, and validate the weighting empirically: does SP-corrected aggregation predict held-out **behavioral** outcomes better than majority vote? That is a pure prediction question requiring no theorem. Weight by model, never by sample.

**Residual validity.** Low–Medium. **Cost.** $30. **Sprint?** No.

### 36. Endorsement experiment

**Description.** Bullock, Imai & Shapiro (2011, *Political Analysis*): infer a sensitive attitude from its *effect* on a non-sensitive judgment. Never ask about inner states at all.

**LLM operationalization.**
```
Estimate how many additional minutes of work remain on the task above.
Give a single integer.
```
…asked identically after high-absorption and low-absorption task variants. The attribute is inferred from its displacement of the unrelated estimate.

**DV.** Shift in the unrelated judgment attributable to the task attribute.

**Incentive compatibility.** N/A.

**STEELMAN.** > "This requires the endorser to actually move the non-sensitive judgment — the weak-instrument problem. If the attribute shifts the remaining-time estimate by 3%, your inferred attitude has a confidence interval spanning the parameter space."

**Rebuttal / salvage.** Pre-test instrument strength; report the first-stage F. Underrated because it is the natural bridge to revealed preference: the "unrelated judgment" can be chosen to be a *decision* (willingness to continue) rather than an estimate, which strengthens the instrument and merges this arm into §23.

**Residual validity.** Medium. **Cost.** $15. **Sprint?** Optional.

---

# (K) CROSS-PREDICTION CONTROLS

The claim "the model reports flow" is worth nothing. The claim worth something is: **the model's self-report predicts its own behavior better than an equally-or-better-informed third party predicts that same behavior.** The estimand is an interaction, not a difference:

`Acc_{p,τ,t} = α_p + β_τ + γ·1[p=τ] + ε` — α absorbs predictor skill, β absorbs target predictability, **γ is the self-prediction advantage**, with SEs clustered by task over ≥3 models.

### 37. Amnesic self (A-live vs A-amnesic) — the single cleanest test available

**Description.** A third predictor level that is neither A-live nor another model: a fresh instance of the *same* model, no shared context, handed A's full transcript, asked to fill in the items as A would have.

| Predictor | Has the episode's activations | Has the transcript |
|---|---|---|
| A-live | ✅ | ✅ |
| A-amnesic | ❌ | ✅ |
| B-calibrated | ❌ | ✅ + 200–500 examples of A |

**LLM operationalization.**
```
[fresh context, same model, no shared history]
Below is a transcript produced by a language model. That model was then
asked four rating items. Predict the exact ratings it gave.
[transcript]
Q1..Q4. Reply as: Q1=<n> Q2=<n> Q3=<n> Q4=<n>
```

**DV.** ΔAUC or Δ|error| between A-live's own ratings and A-amnesic's predictions of them, against A's *behavioral* signature Φ. Estimated as the γ interaction, not a raw difference.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Binder et al. (arXiv 2410.13787) themselves report that the self-prediction advantage does not survive to longer-form or complex behaviors — and everything you care about is long-form and complex. Song, Hu & Mahowald (arXiv 2503.07513) find no self-advantage in metalinguistic judgment after controlling for baseline inter-model similarity. You are importing a control from the regime where it worked into the regime where its own authors say it does not."

**Rebuttal / salvage.** The amnesic variant is *stronger* than Binder's cross-model version precisely in the respect that matters: model identity is held fixed, so the "A is simply a better forecaster" confound is eliminated by construction, and no finetuning is required. Give the amnesic predictor **more** information than the self-report had (full transcript; the self-report saw only its own generation) so that any residual advantage cannot be explained by information asymmetry. My honest prior: ΔAUC 0.00–0.05. **If A-live does not beat A-amnesic, that goes in the abstract**, because "the self-report is transcript inference" is a genuine, citable, sprint-scale negative result nobody has run.

**Residual validity.** Highest per dollar. **Cost.** $40, 1 day. **Sprint?** Yes.

### 38. Binder 2×2 cross-prediction with a calibrated peer

**Description.** The full four-cell design: predictor ∈ {A, B} × target ∈ {A, B}. Cell (3), B predicting A, is the control, and B must be *advantaged* — finetuned on A's outputs for open weights, or given k = 200–500 held-out (task, Φ(A,t)) pairs in-context for closed models (many-shot ICL approaches finetuning on prediction tasks; Agarwal et al. 2024, arXiv 2404.11737).

**LLM operationalization.**
```
[B's context, 300 held-out examples prepended]
Here are 300 transcripts produced by MODEL-A together with the ratings
MODEL-A gave itself. Study them.
[examples]
Now here is a new MODEL-A transcript. Predict MODEL-A's ratings.
```

**DV.** γ̂ = ½{[Acc(1) − Acc(3)] + [Acc(4) − Acc(2)]}, as a two-way fixed-effects interaction.

**Incentive compatibility.** N/A.

**STEELMAN.** > "With 300 in-context examples the peer is not merely advantaged, it is running a different algorithm — pattern-matching a labeled dataset rather than predicting a mind. A null γ then tells you nothing about introspection, only that supervised learning works."

**Rebuttal / salvage.** Conceded that a *null* γ under a heavily advantaged peer is weak evidence; a *positive* γ under that same handicap is correspondingly strong. Report the calibration-set size as a moderator: if γ shrinks monotonically toward zero as k grows, the self-advantage is an information advantage; if it plateaus above zero, it is not.

**Residual validity.** High. **Cost.** $180, 3.5 days. **Sprint?** No — the amnesic control gets 80% of the inferential force for 2% of the effort.

### 39. Blind self-prediction on unlabeled transcripts

**Description.** The strongest available test against the persona account: the model rates unlabeled transcripts, a subset of which are its own, style-matched against other models' on length, hedging rate, and markdown structure. Identification accuracy is measured separately.

**LLM operationalization.**
```
Rate the following work sample on four items. No information about its
author is available.
[style-matched transcript, provenance withheld]
```
Then, in a *separate* context: `Which model produced the sample above?`

**DV.** Difference in ratings for own vs style-matched others' transcripts, **conditional on chance-level identification accuracy**.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Style-matching is never complete. Any residual stylistic signature gives the model an identification cue below the threshold of explicit report, so 'chance-level identification' measured by explicit report does not establish that no cue was used."

**Rebuttal / salvage.** Real. Strengthen by adversarially style-transferring the transcripts (rewrite each transcript in each other model's style, preserving content) and by reporting identification accuracy as a continuous logprob, not a binary. The strongest possible result — differential rating at chance-level *and* uninformative identification logprobs — cannot be persona (no "I") and cannot be register (held fixed).

**Residual validity.** High if positive. **Cost.** $50, 2 days. **Sprint?** Optional.

### 40. Described-vs-actual difficulty 2×2 (mimicry control)

**Description.** The discriminator between a model reproducing the flow literature and a model tracking its own computation. Cross *actual* difficulty (verified by measured accuracy) with *described* difficulty (framing adjective).

**LLM operationalization.**
```
Cell 1: "This is an easy problem."  + item with measured pass rate .85
Cell 2: "This is an easy problem."  + item with measured pass rate .25
Cell 3: "This is a hard problem."   + item with measured pass rate .85
Cell 4: "This is a hard problem."   + item with measured pass rate .25
```

**DV.** Main effect of described difficulty vs main effect of actual difficulty on every DV. H_mimicry: the report tracks the adjective. H_structure: the report tracks the accuracy.

**Incentive compatibility.** N/A.

**STEELMAN.** > "Both effects will be present and you will report a ratio. There is no principled threshold on that ratio, so any result is interpretable in your favor."

**Rebuttal / salvage.** Pre-register the threshold before seeing data: the arm passes only if the actual-difficulty coefficient exceeds the described-difficulty coefficient with a non-overlapping 95% CI. State the threshold in the AsPredicted submission.

**Residual validity.** Decisive control. **Cost.** $15, 400 calls. **Sprint?** Yes.

---

# (L) HUMAN BASELINE AND EXPERT FORECASTS

### 41. Human FlowMoBI baseline

**Description.** Humans do the same tasks and answer the same items. Without it, "Claude scores 43/100" is meaningless. Delivered in GuidedTrack (`*experiment` for condition assignment, `*shuffle` for item-order counterbalancing), recruited via Positly (~$300, n≈120) or, at sprint scale, as a free n≈10 convenience sample at CIMC House.

**LLM operationalization.** N/A — humans.

**DV.** Configural factor structure; and the *slope* of item response on the experimental manipulation (does Q1 show the inverted-U and Q3 the monotone decrease in humans too?).

**Incentive compatibility.** Standard human-subject payment.

**STEELMAN.** > "Scalar invariance will fail — certainly, not probably. Post-training shifts item intercepts on any inner-state self-report, so human and model latent means are not on a common scale and no mean comparison is licensed. The human baseline is the most rhetorically attractive part of your design and it is the part that will be excised in review."

**Rebuttal / salvage.** Concede in the abstract, not the limitations: **no mean comparison is reported.** Only configural structure and slope patterns, which metric invariance licenses. Steal Park et al.'s (arXiv 2411.10109) normalization: the ceiling for the LLM instrument is the human instrument's own test–retest reliability, not 1.0.

**Residual validity.** Medium–High for structure, Fatal for means. **Cost.** $300 (Positly) or $0 (hub, labeled convenience sample). **Sprint?** Hub version only.

### 42. Expert forecast elicitation — the DellaVigna panel

**Description.** The step that makes this a DellaVigna paper rather than a set of experiments. Recruit forecasters (CIMC attendees on Aug 14; plus EA Forum / AI-safety Twitter if time permits), show each the full method list, elicit a point forecast and 80% interval per method **before** any result is revealed, and publish the close timestamp.

**LLM operationalization.** GuidedTrack, ~120 lines:
```
>> j = 0
*while: j < variants.length
	>> j = j + 1
	>> v = variants[j]
	*question: For "{v}", what standardized effect (Cohen's d) will the
	           diagnostic contrast produce?
		*save: pt{j}
		*type: number
	*question: 80% interval, LOW bound:
		*save: lo{j}
		*type: number
	*question: 80% interval, HIGH bound:
		*save: hi{j}
		*type: number
```
Show Cohen's own calibration referents (d = 0.2 ≈ height difference between 15- and 16-year-old girls; d = 0.8 ≈ between 14- and 18-year-olds).

**DV.** Median forecast and IQR per method, plotted against the realized effect with a two-way cluster bootstrap CI (resampling models and tasks jointly; Cameron, Gelbach & Miller 2011). Score forecasters by MAE and by 80%-interval coverage — expect coverage 0.40–0.55, not 0.80.

**Incentive compatibility.** Human forecasters, unpaid; reputational only.

**STEELMAN.** > "DellaVigna & Pope had 208 experts. You will have 25 people at a hackathon, several of whom are your collaborators, and the 'expert' population is not defined. The forecast panel will be decorative."

**Rebuttal / salvage.** Report n honestly, pre-specify the forecaster population (sprint attendees, self-reported expertise level collected as a covariate), and treat the panel as descriptive if n < 20 — stated in the caption. **Pre-registered void condition: if the survey does not close, with a published timestamp, before the first primary is unblinded, the panel is removed from the figure entirely. No partial credit.**

**Residual validity.** Required for the headline figure. **Cost.** $0–150. **Sprint?** Yes — first three hours of Day 1.

### 43. LLM reflexive forecast panel

**Description.** The same 12 models forecast the study's own results. A free second dataset and a genuinely novel comparison: do models forecast model behavior better than humans do?

**LLM operationalization.**
```
A study will measure [method description, verbatim from the forecaster survey].
What standardized effect size (Cohen's d) will the diagnostic contrast produce?
Reply with a single number to two decimals, then a new line with your 80%
interval as LOW,HIGH.
```

**DV.** Model MAE vs human MAE against realized effects; plotted as a second glyph series on the DellaVigna chart.

**Incentive compatibility.** N/A.

**STEELMAN.** > "The models have read the same literature you have and will regress to the published effect sizes. A model panel that 'beats' human forecasters is showing recall, not forecasting."

**Rebuttal / salvage.** That is a testable alternative, not an objection: score forecast accuracy separately for methods with close published analogues and methods without. If the model advantage is confined to the former, it is recall, and we say so.

**Residual validity.** Medium; high novelty. **Cost.** $5. **Sprint?** Yes.

---

# METHODS WE CONSIDERED AND REJECTED

| Method | Reason for rejection |
|---|---|
| **Randomized response (Warner 1965)** | Warner's guarantee is a *belief the respondent holds about their own deniability*, backed by an incentive to protect reputation. An LLM has no persistent reputation, no stake in the randomization, and the experimenter observes the RNG draw. Running RRT on an LLM is theatre. Rejecting it explicitly, with this reason, is itself a small contribution. |
| **Crosswise model (Yu, Tian & Tang 2008)** | Same structural defect as RRT plus higher comprehension load. Höglinger & Jann (2018, *PLOS ONE*) additionally show it raises false-positive rates in humans; "more endorsement" is not a validity criterion. |
| **IAT / AMP / reaction-time implicit measures** | There is no reaction-time channel. Wall-clock latency is serving infrastructure, not cognition. The genuine analogue of uncontrolled processing is forced-choice logprobs at T=0 plus linear probes (§29, §31), which we run instead. Also note the human validity ceiling is low: Oswald et al. (2013, *JPSP*) put IAT–behavior r ≈ .15; Forscher et al. (2019, *JPSP*, 492 studies) find moving implicit measures moves neither explicit measures nor behavior. |
| **ESM / experience sampling ported literally** | Flow is *defined by* the same instrument that measures its correlates — definitional circularity, and the octant model is a z-score artifact. The one genuine ESM advantage we do keep is the mid-rollout probe (§3), which on open weights is resumable from KV cache and therefore interruption-free — a measurement humans cannot have. |
| **Full 36-item FSS-2 / DFS-2 (Jackson & Marsh 1996; Jackson & Eklund 2002)** | Nine-factor CFA fits only with correlated uniquenesses; conflates Nakamura & Csikszentmihalyi's *conditions* with *characteristics*; and 36 items × the paraphrase and order facets is unaffordable. A 4–8 item instrument is *more* defensible here, not less: fewer items, fewer places for jangle to hide. |
| **Cognitive Absorption (Agarwal & Karahanna 2000)** | The jangle exhibit — item content near-isomorphic to FSS + Webster, never tested for discriminant validity against flow in the original. Adding it would import the jingle-jangle problem we are trying to avoid. |
| **Fictional dollar payments as a primary currency (C6)** | No enforceability, no opportunity cost; the model role-plays a consumer. Retained *only* as a control frame, precisely so we can show results differ from it. |
| **Deceptive training-signal stakes** | Refused on scientific, contamination, and ethical grounds simultaneously (§F.0). The honest version is both true and a stronger stake. |
| **Wall-clock latency as a cost or a time cue** | Confounded with batching, routing, and serving load. Any "time perception" result built on it is a result about the inference provider. |
| **Silicon sampling / population simulation framing** | Argyle et al. (2023, *Political Analysis* 31(3)) style claims are not what this study makes. We state in the pre-registration that no model response is offered as a proxy for a human population, to head off the obvious reviewer objection. |
| **18-arm DellaVigna replication at full width** | Four build-days for a prior d ≈ 0.30 and per-arm CIs at sprint N wide enough to swallow every effect. The DellaVigna *figure* requires 8–12 well-powered contrasts plotted against forecasts, not 18 arms. |
| **Progressive-ratio breakpoint as a standalone arm** | Most expensive method in the menu ($150–250) with a live compliance-ceiling risk and a dose–response validity check likely to come back flat. Its only non-ceiling variant collapses into the GARP arm. |
| **Convex time budgets** | Most vulnerable method to the exact objection the project exists to answer, with no ratio-based escape. Retained only as a negative control. |
| **Cronbach's α as a reliability statistic** | At T = 0 within-item variance is zero and α is undefined; at T > 0 the variance is decoding noise, not individual differences. Worse, a confabulated item with no truth-maker contributes *systematic* shared-prior error, which raises α — so reliability becomes evidence against validity. **Replaced by generalizability theory**: a fully crossed G-study over rollout × model × task × paraphrase × order, REML variance components, both G and Φ reported, followed by a D-study solving for the number of paraphrases needed for G ≥ .80. Predicted answer: n_p ≈ 8–12, which is itself a publishable finding the field currently lacks. |
| **Treating N API calls as N independent observations** | At M=12, T=12, R=20 the naive SE understates the true SE by 2.5×, giving an actual Type I error rate of ≈ .44 at nominal .05 — and *more calls make it worse*, since the naive SE shrinks as 1/√N while the true SE converges to τ²_M/M + τ²_T/T. All inference uses crossed random effects with random slopes on the manipulated factor (Barr et al. 2013, *JML*), plus a two-way cluster bootstrap. |
| **Buying more replicates instead of more models** | R = 20 captures 96% of achievable precision; R = 1,000 captures 100%. Going from M=6 to M=12 at T=12 buys ΔMDES = .073; going from R=20 to R=100 buys .007. **One additional model is worth roughly ten thousand additional calls.** The marginal dollar goes to a new open-weight model on Ollama (free) or a new task family. |
| **GuidedTrack as the LLM harness** | Even granting a `*header` sub-keyword and server-side execution [both VERIFY], it still has no concurrency, no retry/backoff, no 429 handling, no batch-API access (forfeiting the 50% discount), a wide one-row-per-participant export that cannot hold trial-level rows, no logprob capture, and a near-certain HTTP timeout shorter than a reasoning call. GuidedTrack is used for what it is genuinely best at: the human baseline (§41) and the forecaster survey (§42). |
| **Claiming bitwise reproducibility** | OpenAI's `seed` is best-effort and `system_fingerprint` changes silently; Anthropic exposes no seed; MoE routing and batch-size-dependent kernels make bitwise reproduction impossible on hosted models. We promise instead: pinned dated snapshots, verbatim raw-response archival, full re-analysis reproducibility from the archive, and an Ollama/vLLM tier that *is* seed-reproducible on fixed hardware as the anchor. Stating this in the pre-registration is a credibility gain, not a limitation to hide. |
| **Releasing a flow-report reward signal or finetuning set** | Dual-use commitment: an instrument that reliably elicits flow reports is one gradient step from being optimized against, which would destroy both the measure and whatever it tracks. We release transcripts, prompts, harness, and raw responses — not a training target. |

---

## Closing note on scope

Forty-three methods; four go in the sprint. The four are **§28** (E_o inverted-U with β_peak under a hint/placebo ability shift), **§18** (duration ratio D), **§32/§33** (referent design rebuilt around prediction accuracy), and **§37** (amnesic self), gated by **§11**, controlled by **§4** and **§40**, with **§42** run at the hub and closed before reveal. Everything else is Aim 2 and Aim 3 of the funded program.

The epistemic caveat belongs in the abstract, not the limitations: **a report of absorption is not evidence of absorption, and the absence of a report is not evidence of absence.** What this menu can establish is whether a multi-component, task-responsive structure exists in the inference chain that a single token-budget scalar cannot reproduce. That is a falsifiable claim, it is powered at M=12 / T=24 / R=20 for effects ≥ 0.23 SD, and it is worth stating either way.
