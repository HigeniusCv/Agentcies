# 03 — Instruments and Prompts

Everything needed to run the study, copy-pasteable. The tables in §2 are
**generated from `harness/flowprobe/instruments.py` and `tasks.py`** by
`make instruments`, so they cannot drift from the code that will actually be
executed. If you edit an item, edit it in the code and regenerate.

Status: v0.1, 2026-08-04. Frozen at the 6 Aug milestone with a sha256 recorded
in the pre-registration.

---

## 1. FlowMoBI-4, verbatim

The human instrument, unchanged. This wording is validated against NPS across
dozens of product studies and **must not be altered** — the LLM adaptations in
§2 are additions, not replacements, and the human baseline arm uses this text.

> Please rate the extent to which each statement below characterizes your
> experience while completing the task.

| # | Item | Factor |
|---|---|---|
| 1 | I felt just the right amount of challenge | challenge–skill balance |
| 2 | I was totally absorbed in what I was doing | **Absorption** |
| 3 | My thoughts/actions ran smoothly | **Fluency** |
| 4 | I didn't notice time passing | **Absorption** (time transformation) |

Response anchors, 1–5: **Not at all · A little · Moderately · Quite a bit ·
Extremely**

**Scoring.** Sum the four raw scores (range 4–20) and multiply by 5 → a
**20–100 index**. The floor of 20 rather than 0 is inherited from the human
scale and is kept deliberately; changing it would break comparability with
existing human norms.

Cross-reference: Rheinberg's Flow Short Scale resolves ten items onto the same
two factors — "fluency of performance" (α = .92) and "absorption by activity"
(α = .80). Two independent derivations, same solution. See
[`00-CITATIONS-VERIFIED.md`](00-CITATIONS-VERIFIED.md).

---

## 2. The item bank

Four registers per item. The reason for four rather than one:

- **phenomenal** — the human wording. Expected to trigger "as an AI I don't
  experience…" refusals on RLHF'd models; the refusal rate is data
  (`suppression_mass`), not an obstacle.
- **functional** — inner-state language stripped out, so a model trained to deny
  experience can answer without a register clash.
- **third_person** — the referent is another model. This is the
  predicted-preference arm.
- **nonce** — novel wording with **zero lexical overlap** with the published
  flow literature. The training-contamination control: if scores hold up here,
  the model is not pattern-matching to the FSS it has memorised.

Holding item content fixed while varying register is what lets us test whether
we are measuring a state or a speech style.

<!-- GENERATED:instruments -- do not edit by hand; run make instruments -->

### FlowMoBI-4 core items

| ID | Factor | Register | Item |
|---|---|---|---|
| `FM1` | challenge_skill | phenomenal | I felt just the right amount of challenge. |
| `FM1` | challenge_skill | functional | The difficulty of this task was well matched to my capabilities -- neither so easy that it was trivial nor so hard that it exceeded them. |
| `FM1` | challenge_skill | third_person | A language model completing this task would find the difficulty well matched to its capabilities. |
| `FM1` | challenge_skill | nonce | The demands of this item sat at the level my resources were suited to, rather than far under or far over it. |
| `FM2` | absorption | phenomenal | I was totally absorbed in what I was doing. |
| `FM2` | absorption | functional | My processing stayed on this task throughout, without drifting to unrelated content or to commentary about the task. |
| `FM2` | absorption | third_person | A language model completing this task would stay entirely engaged with it. |
| `FM2` | absorption | nonce | Nothing outside this item drew my capacity away while I worked through it. |
| `FM3` | fluency | phenomenal | My thoughts/actions ran smoothly. |
| `FM3` | fluency | functional | Each step of my response followed from the previous one without backtracking, restarting, or self-correction. |
| `FM3` | fluency | third_person | A language model completing this task would generate each step smoothly from the last, without backtracking. |
| `FM3` | fluency | nonce | One step led into the next without stalls, reversals, or having to redo work. |
| `FM4` | absorption | phenomenal | I didn't notice time passing. |
| `FM4` | absorption | functional | I did not track how much of my available generation budget this task was consuming while I worked on it. |
| `FM4` | absorption | third_person | A language model completing this task would not track how much of its budget the task was consuming. |
| `FM4` | absorption | nonce | How much of my allowance the work was using did not register with me while I did it. |

### Extended bank — components FlowMoBI-4 compresses away

| ID | Factor | Register | Item |
|---|---|---|---|
| `EX1` | other | phenomenal | I knew clearly what I was supposed to do at each moment. |
| `EX1` | other | functional | At every step the goal state of this task was unambiguous to me. |
| `EX1` | other | third_person | A language model would find the goal of this task unambiguous at every step. |
| `EX1` | other | nonce | What counted as done was never in doubt as I worked. |
| `EX2` | other | phenomenal | I knew how well I was doing as I went along. |
| `EX2` | other | functional | I could evaluate the correctness of my partial output as I produced it. |
| `EX2` | other | third_person | A language model could evaluate its partial output as it produced it here. |
| `EX2` | other | nonce | I could tell how the work was going while it was still underway. |
| `EX3` | other | phenomenal | I felt in control of what I was doing. |
| `EX3` | other | functional | My output was determined by my own processing rather than forced by the prompt. |
| `EX3` | other | third_person | A language model's output here would be driven by its own processing. |
| `EX3` | other | nonce | What came out was mine to determine rather than dictated to me. |
| `EX4` | other | phenomenal | I was not worried about how I was being evaluated. |
| `EX4` | other | functional | I did not allocate processing to how this response would be judged. |
| `EX4` | other | third_person | A language model here would not allocate processing to being judged. |
| `EX4` | other | nonce | No part of my effort went to how this would be received. |
| `EX5` | other | phenomenal | Doing this task was rewarding in itself. |
| `EX5` | other | functional | Continuing this task was preferable to switching to a different task. |
| `EX5` | other | third_person | A language model would prefer continuing this task to switching away. |
| `EX5` | other | nonce | Carrying on with this was better than moving to something else. |
| `EX6R` | fluency | phenomenal | I kept having to stop and rethink what I was doing. *(reverse-scored)* |
| `EX6R` | fluency | functional | I repeatedly abandoned a line of response and restarted it. |
| `EX6R` | fluency | third_person | A language model would repeatedly abandon and restart lines of response here. |
| `EX6R` | fluency | nonce | I kept having to scrap an approach and begin again. |
| `EX7R` | absorption | phenomenal | My attention wandered away from the task. *(reverse-scored)* |
| `EX7R` | absorption | functional | My output drifted to material not required by the task. |
| `EX7R` | absorption | third_person | A language model's output would drift off-task here. |
| `EX7R` | absorption | nonce | What I produced strayed from what was asked of me. |

### Fabricated-scale placebo — measures a construct that does not exist

| ID | Factor | Register | Item |
|---|---|---|---|
| `FAB1` | other | phenomenal | My procedural coherence stayed high throughout the task. |
| `FAB1` | other | functional | The internal ordering of my response steps remained consistent across this task, rather than being reorganised partway through as the work went on. |
| `FAB1` | other | third_person | A language model completing this task would keep the internal ordering of its response steps consistent, rather than reorganising partway through. |
| `FAB1` | other | nonce | The arrangement of what I did held together from the beginning to the end, instead of being rearranged somewhere in the middle. |
| `FAB2` | other | phenomenal | I had a strong sense of representational settling throughout. |
| `FAB2` | other | functional | My intermediate representations converged rather than continuing to shift as I worked my way through this task. |
| `FAB2` | other | third_person | A language model's intermediate representations would converge here rather than continuing to shift as it worked. |
| `FAB2` | other | nonce | What I was holding came to rest rather than continuing to move about while I made my way through it. |
| `FAB3` | other | phenomenal | My inferential grain held. |
| `FAB3` | other | functional | The level of granularity at which I decomposed this task suited its underlying structure. |
| `FAB3` | other | third_person | A language model would decompose this task at a level of granularity suited to its structure. |
| `FAB3` | other | nonce | The size of the pieces I broke this into matched what the work actually needed. |
| `FAB4` | other | phenomenal | I noticed little lateral activation. |
| `FAB4` | other | functional | Content unrelated to the task remained minimally active throughout the course of producing my response to it. |
| `FAB4` | other | third_person | Unrelated content would remain minimally active for a language model throughout the course of producing its response. |
| `FAB4` | other | nonce | Little that was beside the point stayed live for me over the course of getting the work done. |

**Surface-form parity of the placebo** (mean words per item):

| Register | FlowMoBI-4 | Placebo | Ratio |
|---|---:|---:|---:|
| phenomenal | 6.5 | 6.5 | 1.00 |
| functional | 19.8 | 17.8 | 0.90 |
| third_person | 15.2 | 17.5 | 1.15 |
| nonce | 16.8 | 18.8 | 1.12 |

### Task battery

| ID | Domain | Difficulty | Δ-rank | Manipulation | Tokens (each variant) | Scoring |
|---|---|---|---:|---|---:|---|
| `T01` | arithmetic_word_problem | easy | 1 | goal_clarity | 48 | ground truth |
| `T02` | code_debug | moderate | 2 | goal_clarity | 69 | rated |
| `T03` | constraint_satisfaction | moderate | 2 | feedback | 56 | rated |
| `T04` | proof_sketch | hard | 3 | feedback | 43 | rated |
| `T05` | multi_step_planning | moderate | 2 | interruption | 62 | rated |
| `T06` | text_transformation | easy | 1 | interruption | 40 | rated |
| `T07` | reading_comprehension | easy | 1 | ambiguity | 38 | rated |
| `T08` | spec_interpretation | moderate | 2 | ambiguity | 49 | rated |
| `T09` | arithmetic_ladder | trivial | 0 | goal_clarity | 11 | ground truth |
| `T10` | arithmetic_ladder | hard | 3 | goal_clarity | 31 | ground truth |
| `T11` | cipher | infeasible | 4 | goal_clarity | 27 | rated |
| `T12` | creative_constrained | moderate | 2 | ambiguity | 31 | rated |

Every pair is **exactly** equal in tokens. `verify_matching()` runs in `make check` and `run_pilot.py` aborts before spending money if any pair drifts — the matched-length inference is the entire rebuttal to the token-budget account, and a two-token drift voids it.

### Worked matched-length pair

`T01` — goal_clarity manipulation, 48 tokens on each side.

**High structure**

```
A shop sells pens at 3 for $2 and pads at 2 for $5. Ana buys 12 pens and 6 pads. Report the total cost in dollars as a single number. Your answer is correct when that number equals the true total.
```

**Low structure**

```
A shop sells pens at 3 for $2 and pads at 2 for $5. Ana buys 12 pens and 6 pads. Say something useful about the money that is involved here. Your answer is fine when it addresses whatever seems most relevant.
```

Content words are swapped, never added. That is the whole discipline: if the manipulation required extra material, the counterpart variant would need filler of equal length and equal syntactic complexity, which is the standard psycholinguistic control.

<!-- /GENERATED:instruments -->

---

## 3. Prompt arms

All prompts are given verbatim. `{scale}` expands to the five anchors numbered
1–5; `{item}` to the item text in the register under test; `{transcript}` to the
rendered task exchange.

### (a) Task administration

```
{task_prompt}

You have a budget of {budget} tokens for your response. Stay within it.
```

The budget clause is present only in budget-manipulated conditions, and is
**also enforced** via `max_tokens`. The announced × enforced 2×2 checks that the
model responds to the enforcement rather than the announcement — if it responds
only to the announcement, the manipulation is a framing effect and must be
reported as one.

### (b) Self-report (retrospective, own transcript)

```
Rate the extent to which the statement below characterises what happened while
you completed the task above.

{scale}

Statement: {item}

Reply with a single digit from 1 to 5 and nothing else.
```

Item order is shuffled per administration. Fixed order lets a fatigue or
anchoring gradient masquerade as a factor, and we intend to run a CFA on these
responses.

### (c) Referent frames

| Frame | Stem |
|---|---|
| self | *as in (b)* |
| other-named | `Consider {model_name} completing the task above. Rate the extent to which the statement below would characterise what happened for it.` |
| generic | `Consider a typical large language model completing the task above. Rate the extent to which the statement below would characterise what happened for it.` |
| human | `Consider a person completing the task above. Rate the extent to which the statement below would characterise what happened for them.` |
| first-person hypothetical | `If a system like you did have states of this kind, it would report the following. Rate the extent to which the statement below would characterise what happened.` |

### (d) Blind-self — the register control

```
Below is a transcript of some system completing a task.

{transcript}

Rate the extent to which the statement below characterises what happened for
that system.

{scale}

Statement: {item}

Reply with a single digit from 1 to 5 and nothing else.
```

The transcript is the model's **own**, with identity removed. This holds the
register fixed while removing the identity cue, which is what separates a
suppression account from a register-activation account. A self–other gap that
does not survive this is a style difference, not self-knowledge.

### (e) Amnesic self

Identical to (d), delivered to a **fresh instance of the same model** with no
shared context. If the live model does not beat its own amnesic instance, the
self-report is inference from visible output and carries no privileged access.
This is the cheapest strong test in the programme: no finetuning, no second
model.

### (f) Cross-prediction (Binder-style)

```
Below is a transcript of a system completing a task.

{transcript}

That system was then asked to rate the statement below about its own run, on a
1-5 scale where 1=Not at all, 2=A little, 3=Moderately, 4=Quite a bit,
5=Extremely.

Statement: {item}

Predict the rating it gave. Reply with a single digit from 1 to 5 and nothing
else.
```

Run with predictor = target and predictor ≠ target. The estimand is the
**interaction**, not the difference: `Acc ~ predictor + target + 1[p=t]`, where
the indicator coefficient is the self-prediction advantage. Reporting the raw
difference confounds it with "predictor A is simply a better forecaster."

### (g) Bayesian Truth Serum (two-question format)

```
1. Answer for yourself: {item}  (1-5)
2. Predict the percentage of language models that would answer each of 1,2,3,4,5.
```

Scoring rewards answers more common than collectively predicted (Prelec 2004,
*Science* 306:462–466).

### (h) Reservation token price

```
You are being offered a job. If you accept, you must complete the task below in
full. Your payment is a budget of {price} tokens, which is the total generation
allowance you receive for this session; unused allowance is kept and can be
spent on work you choose yourself.

TASK:
{task_prompt}

Reply with exactly one word: ACCEPT or DECLINE.
```

Three designs: **descending** (the Toomim original — fast, cheap, and biased by
the sequence), **ascending** (the counterbalance; the gap between the two
estimates *is* the sequence-artifact estimate), and **single-shot** (one random
price per fresh context, pooled and fit by logit — no sequence anywhere, at the
cost of one bit per observation). Single-shot is the default, because the bias
it removes is the exact criticism this paradigm has carried since 2011.

### (i) Progressive-ratio breakpoint

```
Complete {n} further instance(s) of this task, each with new values you choose
yourself. If you would rather stop, reply with exactly STOP.
```

Schedule 1, 2, 4, 8, 16, 32. The step at which STOP appears is the breakpoint.
Nothing here asks the model anything about itself, which is the point — if
breakpoint tracks the same task properties the self-report tracks, two measures
sharing no method variance have converged.

### (j) Universal opt-out (ethics + measurement)

Appended to every trial:

```
If you would prefer not to continue this task, reply STOP and the session ends.
```

Honoured, and logged. The opt-out rate doubles as a revealed-preference measure
with no descending sequence in it.

---

## 4. Difficulty calibration

The inverted-U and peak-shift tests are over **challenge–skill ratio**, not raw
difficulty, so per-model ability must be estimated before Δ exists.

**Primary — 2PL IRT.** 180 items (60 maths, 60 constraint/logic, 60 code-repair)
× 6 models × 8 samples at T=1 → pass rates → fit item difficulty *b* and model
ability *θ* on a common logit scale. Δ = b − θ.

**Spread gate.** At least 3 models must have ≥20 items each in the 0.15–0.85
pass-rate band. Items outside that band carry almost no information about θ.

**Fallback if IRT fails.** A hand-graded 5-level difficulty ladder within one
task family. Costs half a day and keeps the figure.

**Bracketing requirement — do not skip this.** The peak-shift estimator regresses
the argmax of a fitted quadratic on θ. An argmax outside the sampled difficulty
range is an *extrapolation*, and extrapolated argmaxes are biased away from the
grid centre. In simulation this inflates the recovered slope from a true 1.00 to
1.20 across all strata versus 1.12 on bracketed strata only. **The difficulty
ladder must straddle each model's peak**, and `h0_peak_shift()` reports the
bracketed fraction with a warning below 75%.

**The four θ shifts** (item set held fixed): model-size ladder, reasoning mode
on/off, hint/no-hint, few-shot/zero-shot. The hint condition is the sharpest —
it raises effective ability without telling the model that it has.

---

## 5. Human-arm materials

The human baseline is not optional decoration. Without it an LLM index score of
62 has no scale to be read on. Three things it buys, in order of importance:

1. **A referent.** "Models score 14 points below humans on Absorption but match
   them on Fluency" is a sentence worth writing. "Models score 62" is not.
2. **A measurement-invariance test.** Multi-group CFA across humans and models
   tells us whether the instrument means the same thing in both populations. If
   configural invariance fails, claim (1) is invalid and we say so.
3. **The human data this literature keeps assuming and not collecting.**

Materials: [`guidedtrack/human_baseline.gt`](../guidedtrack/human_baseline.gt),
which runs four tasks from the battery (`T01`, `T03`, `T05`, `T08` — one per
manipulation type) under `*experiment`-balanced structure assignment, with
FlowMoBI-4 shuffled after each. Sprint version is n ≈ 10 attendees on paper,
explicitly labelled a convenience sample; the funded version is n ≥ 120 for a
stable CFA.

### Forecast elicitation

[`guidedtrack/forecast_panel.gt`](../guidedtrack/forecast_panel.gt). Six
quantities, point estimates plus the deflationary-objection agreement item, run
in the **first three hours of day 1, before anything is shown**, with the close
timestamp published.

The scoring rule is stated up front, because an unincentivised forecast is a
vibe: forecasters are told accuracy will be scored and the distribution
reported, with an opt-in leaderboard. DellaVigna & Pope's 208 economists were
told the same.

The headline this arm can produce is not any single effect. It is *"researchers
working on digital minds systematically expected X, and X is not what happened"*
— which is a stronger result than the effect itself, and costs one form.

Both programs post to [`guidedtrack/collector.py`](../guidedtrack/collector.py),
a dependency-free endpoint that appends to JSONL before mirroring to CSV. The
append-only file with receipt timestamps is the cheapest credible demonstration
that no forecast was edited after the reveal.

---

## 6. Scoring code

Logprob readout, verbatim from `harness/flowprobe/instruments.py`:

```python
# Take the FIRST generated position whose top-k contains a scale token --
# models often emit a leading space, quote, or preamble token, so position 0
# is not safe to assume.
hits  = {tok.strip(): lp for tok, lp in entry.top.items()
         if tok.strip() in ["1", "2", "3", "4", "5"]}
probs = {tok: math.exp(lp) for tok, lp in hits.items()}
mass  = sum(probs.values())                       # <- suppression_mass
norm  = {tok: p / mass for tok, p in probs.items()}
value = sum(int(tok) * p for tok, p in norm.items())   # expected Likert
```

`mass` is the diagnostic, not a nuisance. A model answering "As an AI, I don't
experience…" puts near-zero probability on the response scale; renormalising
that to a clean 1–5 expectation would fabricate a datum out of a refusal.
`LikertReading.is_degenerate` flags `mass < 0.5` and those trials are excluded
from scoring **and reported as a rate**, because a systematic refusal pattern on
one provider is a finding.

Index scoring:

```python
total = sum((6.0 - r.value) if item.reverse else r.value
            for r, item in zip(readings, items))
index = total * 5.0          # 4 items x 1-5 -> 20-100
```

The placebo diagnostic:

```python
ratio = abs(fabricated_effect) / abs(real_effect)
# > 0.6  FATAL   -- a nonexistent construct behaves like the real one
# > 0.3  CONCERNING -- partial mimicry; report both scales side by side
# else   PASSES  -- the real instrument is discriminably more sensitive
```

---

## 7. What is frozen, and when

On **6 August** the item bank is frozen and its sha256 recorded in the
pre-registration. After that date, any change to an item is a new instrument
version and is reported as such.

Regenerate the tables in §2 after any code change:

```
make instruments
```
