# Citation ledger

**Why this file exists.** The literature briefs behind this plan were drafted by
research agents whose web tools failed mid-run (a permission-handler fault
rejected every `WebSearch`/`WebFetch` call). Those agents wrote from memory and
flagged their own uncertainty with `[VERIFY]` markers, which was the right call —
but it means the reference list arrived unverified.

Everything below was then checked directly against primary sources. Claims that
did not survive the check are recorded as corrections rather than quietly
deleted, because two of them were *load-bearing* and a reader who saw the
uncorrected version elsewhere needs to know.

Status key: **✅ verified** · **⚠️ corrected** · **❌ could not confirm — do not cite**

---

## The convergence result that matters most

| Status | Reference | What was checked |
|---|---|---|
| ✅ | Rheinberg, Vollmeyer & Engeser (2003); Rheinberg & Engeser (2008); Engeser (2012) — **Flow Short Scale (FKS/FSS)** | Ten flow items resolve onto **two** factors: **fluency of performance** (items 2, 4, 5, 7, 8, 9) and **absorption by activity** (items 1, 3, 6, 10). Reported α = **.92** (fluency) and **.80** (absorption). |

This is the single most useful fact in the ledger. The PI derived a
**Fluency / Absorption** two-factor solution independently, by factor-analysing
49 items collected from product-research samples, without reference to
Rheinberg. The published German-language scale reaches the same two factors with
the same names.

Independent derivation of a matching factor structure, from a different item
pool and a different population, is a genuine construct-validity argument — and
it is a stronger opening for the paper than anything in the LLM literature.
It should be stated early and explicitly, with the α values, rather than left as
a footnote. It also reframes FlowMoBI-4 as *a replication that compressed*,
not *a bespoke instrument*, which is a much easier thing to defend in review.

---

## Revealed preference / the PI's own lineage

| Status | Reference | Notes |
|---|---|---|
| ⚠️ | **Toomim, Kriplean, Pörtner & Landay (2011)**, "Utility of Human-Computer Interactions: Toward a Science of Preference Measurement", *CHI '11*, pp. **2275–2284** | Author is **Pörtner** (Claus C. Pörtner), not "Portner". The headline design is **not** only a descending reservation-wage auction: the published method placed design alternatives on Mechanical Turk and measured **how many tasks people completed under differing pay conditions** — "a design which gets more work for the same or less pay implies more utility." The big-button result is reported at **p < 0.10**, i.e. marginal. Cite it as a paradigm, not as a strong effect. |
| ✅ | DellaVigna & Pope (2018), "What Motivates Effort? Evidence and Expert Forecasts", *Review of Economic Studies* **85(2), 1029–1069** | 18 treatment arms; **208** expert forecasters. Experts anticipated the effectiveness of psychological motivators but a sizeable share counterfactually expected crowd-out, probability weighting, and pure altruism. |
| ✅ | Chen, Liu, Shan & **Zhong** (2023), "The emergence of economic rationality of GPT", *PNAS* **120(51)**, e2316205120 | Author is **Zhong**, not "Zhou". GPT-3.5-Turbo CCEI averaged **.998 / .997 / .997 / .999** across risk, time, social and food domains — *above* human subjects (**.980 / .985 / .967 / .963**), all p < .01. Relevant caveat for us: near-ceiling CCEI means GARP tests have almost no variance left to explain, which is why the axiomatic arm scores poorly in the method portfolio. |
| ✅ | Prelec (2004), "A Bayesian Truth Serum for Subjective Data", *Science* **306**, 462–466 | Scores answers that are **more common than collectively predicted**. |
| ✅ | Prelec, Seung & McCoy (2017), "A solution to the single-question crowd wisdom problem", *Nature* **541(7638)**, 532–535 | The "surprisingly popular" algorithm; same two-question structure. |
| ✅ | Fisher (1993), "Social Desirability Bias and the Validity of Indirect Questioning", *Journal of Consumer Research* **20(2)**, 303–315 | The canonical validation of third-person/projective questioning — the direct ancestor of the "how much do other people shoplift" move. |
| ✅ | Haire (1950), "Projective Techniques in Marketing" | The Nescafé shopping-list study. Verified as a real and correctly-attributed classic; the specific instant-coffee findings were not re-checked line by line. |

---

## LLM introspection

| Status | Reference | Notes |
|---|---|---|
| ✅ | Binder et al. (2024), "Looking Inward: Language Models Can Learn About Themselves by Introspection", arXiv **2410.13787** | Cross-prediction design: M1 predicting M1 beats M2 predicting M1 *even when M2 is finetuned on M1's ground-truth outputs*. Robert Long is a co-author, which is why the control structure is unusually well built. Specific accuracy figures were **not** confirmed — do not quote numbers. |
| ✅ | Song, Hu & Mahowald (2025), "Language Models Fail to Introspect About Their Knowledge of Language", arXiv **2503.07513**, COLM 2025 | 21 open-source models; grammatical knowledge and word prediction. Proposes measuring introspection as the degree to which prompted responses predict the model's **own** string probabilities *beyond* what a near-identical other model predicts. Code: `github.com/SiyuanSong2004/language-introspection`. |
| ⚠️ | **"Privileged Self-Access Matters for Introspection in AI", arXiv 2508.14802** (Song et al.) | **This is the correct source for the "privileged self-access" criterion.** The brief attributed that criterion to a paper called *"Can LLMs Introspect? A Reality Check"* at arXiv **2605.26242** — that identifier could not be confirmed and should be treated as fabricated. The criterion itself is real and is the right bar: a self-report counts as introspective only if it is more reliable than any equal-or-lower-cost third-party process with equal access. |
| ✅ | Lindsey (2025), "Emergent Introspective Awareness in Large Language Models", Anthropic, `transformer-circuits.pub/2025/introspection/index.html`, 29 Oct 2025 | **Concept injection**: a steering vector is added to the residual stream and the model is asked whether it detects an injected thought. Claude Opus 4 / 4.1 succeed roughly **20%** of the time with **~0%** false positives. Published on Transformer Circuits, **not arXiv** — the identifier 2603.21396 in the brief points to a different paper ("Mechanisms of Introspective Awareness", Macar, Yang & Wang), which is a separate work. Lindsey's own framing is deliberately deflationary: *functional* introspective awareness, unreliable, no consciousness claim. |
| ✅ | Song, Hu & Mahowald as above + Binder et al. | The two together are the debate. Cite both or neither. |
| ⚠️ | Turpin et al. (2023), "Language Models Don't Always Say What They Think", arXiv **2305.04388** | Real and correctly attributed. The specific figure "CoT mentions a used hint ~25% of the time for Claude 3.7 Sonnet" comes from a later Anthropic reasoning-faithfulness write-up and was **not** confirmed — do not quote that number. |
| ✅ | Nisbett & Wilson (1977), "Telling More Than We Can Know", *Psychological Review* 84(3) | The human prior: people confabulate reasons and report theory, not process. |
| ✅ | Ericsson & Simon (1980), "Verbal Reports as Data", *Psychological Review* 87(3) | The repair: concurrent reports of *heeded content* are valid; retrospective "why" reports are not. **Design consequence, and it is a big one: ask the model what it was doing, never why.** |

---

## Effort, difficulty, and the challenge–skill analogue

| Status | Reference | Notes |
|---|---|---|
| ✅ | **Chen et al.**, "Do NOT Think That Much for 2+3=? On the Overthinking of o1-Like LLMs", arXiv **2412.21187** | The source of the **outcome efficiency** metric (E_o) used in Arm A. Introduces efficiency metrics from outcome and process perspectives; documents o1-like models burning tokens on trivial problems for minimal accuracy gain. |
| ✅ | **Wang, Liu, Xu, Liang et al.**, "Thoughts Are All Over the Place: On the Underthinking of o1-Like LLMs", arXiv **2501.18585**, NeurIPS 2025 | The source of the **thought-switch rate** (S). Models switch between reasoning paths without exploring promising ones; frequent switching correlates with incorrect answers. Together with 2412.21187 this is the pair that makes a bare inverted-U uninteresting — and makes the *peak shift* the endpoint that matters. |
| ✅ | "Between Underthinking and Overthinking: An Empirical Study of Reasoning Length and Correctness in LLMs", arXiv **2505.00127** (2025) | LLMs **overthink simple problems** (verbose output, no accuracy gain) and **underthink hard ones** (fail to extend reasoning when it would help); models misjudge difficulty and miscalibrate response length. This is the closest existing empirical result to a challenge–skill mismatch signature, and it arrives from a completely different research community — which is exactly the kind of convergence the plan should lean on. |
| ✅ | "OptimalThinkingBench: Evaluating Over and Underthinking in LLMs", arXiv **2508.13141** | Optimising against one failure mode worsens the other. Supplies a ready-made difficulty-calibrated task set. |
| ✅ | "Stop Overthinking: A Survey on Efficient Reasoning for Large Language Models", TMLR 2025 | Survey; use for the related-work paragraph. |
| ✅ | "When More Thinking Hurts: Overthinking in LLM Test-Time Compute Scaling", arXiv 2604.10739 | Reports easy problems consuming ~2K tokens against ~8K for hard ones. |

---

## Venue

| Status | Item | Notes |
|---|---|---|
| ✅ | **Digital Minds Research Sprint**, 14–16 August 2026 | In-person hub at **CIMC House** (California Institute for Machine Consciousness), co-hosted with **NODES**, alongside a global online sprint. Friday opens with a community gathering and talks by **Joscha Bach, Mati Roy, Philip Rosedale**. Stated themes: **model preferences, introspection, valence signals, model identity**. Listings: `apartresearch.com/sprints/digital-minds-research-sprint-2026-08-14-to-2026-08-16` and `luma.com/digital-minds-research-sprint-2026-berlin`. |

The four stated themes map onto this project's four arms almost one-to-one —
preferences (revealed-preference arm), introspection (cross-prediction arm),
valence (the instrument), identity (the self-other referent arm). That is not a
coincidence worth relying on in the write-up, but it is a reason to expect the
work to land well with this specific audience.

---

## Not confirmed — do not cite without checking

- ❌ **arXiv 2605.26242**, "Can LLMs Introspect? A Reality Check" — identifier
  does not resolve to this title. Use arXiv 2508.14802 instead.
- ❌ **arXiv 2603.21396** as a citation for Lindsey/Anthropic — that identifier
  belongs to a different paper. Cite the transformer-circuits.pub URL.
- ❌ Specific accuracy percentages from Binder et al. (the "48% self vs 32%
  cross" figures) — plausible but unconfirmed.
- ❌ Long, "Introspective Capabilities in Large Language Models", *J.
  Consciousness Studies* 2023 — not re-checked; verify before citing.
- ❌ Any Toomim et al. effect size in cents. The paper's reported button-size
  result is p < 0.10; treat all other magnitudes as unverified.

---

## Standing rule for this project

Anything in `docs/02`–`docs/05` carrying a `[VERIFY]` marker inherits it from an
agent that could not reach the web. Before the pre-registration is filed, every
such marker must be resolved to ✅, ⚠️, or ❌ here. A pre-registration containing
a fabricated arXiv identifier is worse than one with a thin reference list, and
at a venue whose attendees wrote several of these papers, it is the kind of error
that costs the whole entry its credibility.
