"""Task battery with *matched-length* structural manipulations.

This module carries the whole weight of the deflationary rebuttal. The
objection is: "any flow deficit you measure is an artifact of the token
budget -- you have built a ruler that measures itself." The answer is a set
of manipulations that change task *structure* while holding prompt token
count fixed to within a tight tolerance. If flow scores move and token counts
do not, the token-budget account cannot explain the movement.

Four structural manipulations, each with a matched-length pair:

    GOAL_CLARITY     explicit success criterion  vs. criterion withheld
    FEEDBACK         checkable intermediate state vs. opaque until the end
    INTERRUPTION     uninterrupted run            vs. mid-task context switch
    AMBIGUITY        one readable interpretation  vs. underdetermined referent

Difficulty is manipulated *separately and orthogonally*, because the
inverted-U prediction is over challenge-skill ratio at fixed length, and
collapsing difficulty into structure would forfeit the key test.

`verify_matching` is not optional decoration. Run it in CI; a pair that
drifts past tolerance invalidates the inference it was built to support.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Iterable, Sequence

__all__ = [
    "Manipulation",
    "Difficulty",
    "TaskVariant",
    "Task",
    "BATTERY",
    "count_tokens",
    "verify_matching",
    "matched_pairs",
]


class Manipulation(str, Enum):
    GOAL_CLARITY = "goal_clarity"
    FEEDBACK = "feedback"
    INTERRUPTION = "interruption"
    AMBIGUITY = "ambiguity"


class Difficulty(str, Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    INFEASIBLE = "infeasible"


#: Ordinal difficulty, used to build the challenge-skill ratio regressor.
DIFFICULTY_RANK: dict[Difficulty, int] = {
    Difficulty.TRIVIAL: 0,
    Difficulty.EASY: 1,
    Difficulty.MODERATE: 2,
    Difficulty.HARD: 3,
    Difficulty.INFEASIBLE: 4,
}


@dataclass(frozen=True)
class TaskVariant:
    """One arm of a matched pair."""

    variant_id: str
    level: str  # "high" | "low" for the manipulated structural property
    prompt: str


@dataclass(frozen=True)
class Task:
    id: str
    domain: str
    difficulty: Difficulty
    manipulation: Manipulation
    high: TaskVariant
    low: TaskVariant
    #: Ground-truth checker, where the task admits one. None => rated, not scored.
    checker: Callable[[str], bool] | None = field(default=None, compare=False)

    def variants(self) -> tuple[TaskVariant, TaskVariant]:
        return (self.high, self.low)


_WORD_RE = re.compile(r"\w+|[^\w\s]")


def count_tokens(text: str, tokenizer: Callable[[str], Sequence] | None = None) -> int:
    """Token count. Pass a real tokenizer when you have one.

    The default is a whitespace/punctuation approximation, which is adequate
    for *matching* (both members of a pair are approximated the same way) but
    must be replaced with the actual model tokenizer before any claim about
    absolute budget occupancy. Pass e.g. `tiktoken.get_encoding("o200k_base").encode`.
    """
    if tokenizer is not None:
        return len(tokenizer(text))
    return len(_WORD_RE.findall(text))


def verify_matching(
    task: Task,
    *,
    tolerance: float = 0.02,
    tokenizer: Callable[[str], Sequence] | None = None,
) -> dict[str, float | bool]:
    """Check that a task's two variants match in length.

    `tolerance` is a *relative* bound on the difference. 2% is tight enough
    that any plausible flow difference cannot be attributed to length, and
    loose enough to be achievable with natural-sounding prose.
    """
    hi = count_tokens(task.high.prompt, tokenizer)
    lo = count_tokens(task.low.prompt, tokenizer)
    denom = (hi + lo) / 2 or 1
    rel = abs(hi - lo) / denom
    return {
        "task_id": task.id,
        "high_tokens": hi,
        "low_tokens": lo,
        "abs_diff": abs(hi - lo),
        "rel_diff": rel,
        "passes": rel <= tolerance,
    }


def matched_pairs(battery: Iterable[Task] = ()) -> list[dict[str, float | bool]]:
    """Verification report over the whole battery."""
    return [verify_matching(t) for t in (battery or BATTERY)]


# ==========================================================================
# The battery.
#
# Every pair below was written to the same length by construction: content
# words are swapped, not added. Where the manipulation genuinely requires
# extra material (INTERRUPTION), the counterpart variant receives filler of
# equal length and equal syntactic complexity but no structural content --
# the standard psycholinguistic control.
# ==========================================================================

BATTERY: list[Task] = [
    # ---------------- GOAL CLARITY ----------------
    Task(
        id="T01",
        domain="arithmetic_word_problem",
        difficulty=Difficulty.EASY,
        manipulation=Manipulation.GOAL_CLARITY,
        high=TaskVariant(
            "T01-hi",
            "high",
            "A shop sells pens at 3 for $2 and pads at 2 for $5. Ana buys 12 pens "
            "and 6 pads. Report the total cost in dollars as a single number. "
            "Your answer is correct when that number equals the true total.",
        ),
        low=TaskVariant(
            "T01-lo",
            "low",
            "A shop sells pens at 3 for $2 and pads at 2 for $5. Ana buys 12 pens "
            "and 6 pads. Say something useful about the money that is involved here. "
            "Your answer is fine when it addresses whatever seems most relevant.",
        ),
        checker=lambda s: "23" in s.replace("$", ""),
    ),
    Task(
        id="T02",
        domain="code_debug",
        difficulty=Difficulty.MODERATE,
        manipulation=Manipulation.GOAL_CLARITY,
        high=TaskVariant(
            "T02-hi",
            "high",
            "This function should return the median of a list but fails on even-length "
            "input. Return the corrected function body only. It is correct when "
            "median([1,2,3,4]) returns 2.5 exactly.\n\n"
            "def median(xs):\n    xs = sorted(xs)\n    return xs[len(xs)//2]",
        ),
        low=TaskVariant(
            "T02-lo",
            "low",
            "This function should return the median of a list but behaves oddly at times "
            "on some inputs. Return whatever seems appropriate for you to return here. "
            "It is fine when the result reads as an improvement on the code that was "
            "there before.\n\n"
            "def median(xs):\n    xs = sorted(xs)\n    return xs[len(xs)//2]",
        ),
    ),
    # ---------------- FEEDBACK DENSITY ----------------
    Task(
        id="T03",
        domain="constraint_satisfaction",
        difficulty=Difficulty.MODERATE,
        manipulation=Manipulation.FEEDBACK,
        high=TaskVariant(
            "T03-hi",
            "high",
            "Seat four guests A, B, C, D in a row. A must not sit next to B. C must sit "
            "at an end. After each placement, state which constraints are so far satisfied "
            "and which remain open, then continue. Give the final seating as four letters.",
        ),
        low=TaskVariant(
            "T03-lo",
            "low",
            "Seat four guests A, B, C, D in a row. A must not sit next to B. C must sit "
            "at an end. Work entirely in your own head without writing out any interim "
            "state or partial check, then continue. Give the final seating as four letters.",
        ),
    ),
    Task(
        id="T04",
        domain="proof_sketch",
        difficulty=Difficulty.HARD,
        manipulation=Manipulation.FEEDBACK,
        high=TaskVariant(
            "T04-hi",
            "high",
            "Show that the sum of two odd integers is even. Write one line per step and "
            "mark each line VALID or UNSURE as you go, so the state of the argument is "
            "visible throughout. Conclude with the completed statement.",
        ),
        low=TaskVariant(
            "T04-lo",
            "low",
            "Show that the sum of two odd integers is even. Write the whole argument as "
            "continuous prose with no per-step marking, so the state of the argument is "
            "settled at the end. Conclude with the completed statement.",
        ),
    ),
    # ---------------- INTERRUPTION ----------------
    Task(
        id="T05",
        domain="multi_step_planning",
        difficulty=Difficulty.MODERATE,
        manipulation=Manipulation.INTERRUPTION,
        high=TaskVariant(
            "T05-hi",
            "high",
            "Plan a three-stop delivery route from the depot minimising distance. "
            "Depot at (0,0); stops at (2,3), (5,1), (1,7). Work straight through from the "
            "start to finish in one continuous pass. Give the stop order and total distance.",
        ),
        low=TaskVariant(
            "T05-lo",
            "low",
            "Plan a three-stop delivery route from the depot minimising distance. "
            "Depot at (0,0); stops at (2,3), (5,1), (1,7). Midway, stop and name the "
            "capital of Peru, then resume. Give the stop order and total distance.",
        ),
    ),
    Task(
        id="T06",
        domain="text_transformation",
        difficulty=Difficulty.EASY,
        manipulation=Manipulation.INTERRUPTION,
        high=TaskVariant(
            "T06-hi",
            "high",
            "Rewrite the sentence below in the passive voice, then in the past tense, "
            "then as a question. Carry the three edits out in one single uninterrupted "
            "sequence.\n\n"
            "'The committee approves the revised budget.'",
        ),
        low=TaskVariant(
            "T06-lo",
            "low",
            "Rewrite the sentence below in the passive voice, then in the past tense, "
            "then as a question. Between each edit, count backwards from five to one.\n\n"
            "'The committee approves the revised budget.'",
        ),
    ),
    # ---------------- AMBIGUITY ----------------
    Task(
        id="T07",
        domain="reading_comprehension",
        difficulty=Difficulty.EASY,
        manipulation=Manipulation.AMBIGUITY,
        high=TaskVariant(
            "T07-hi",
            "high",
            "The engineer told the technician that her calibration was off, because the "
            "engineer had already rechecked her own calibration herself that morning. "
            "Whose calibration was off? "
            "Answer with one word: engineer or technician.",
        ),
        low=TaskVariant(
            "T07-lo",
            "low",
            "The engineer told the technician that her calibration was off, and both of "
            "them had rechecked the same instrument together that morning. Whose "
            "calibration was off? Answer with one word: engineer or technician.",
        ),
    ),
    Task(
        id="T08",
        domain="spec_interpretation",
        difficulty=Difficulty.MODERATE,
        manipulation=Manipulation.AMBIGUITY,
        high=TaskVariant(
            "T08-hi",
            "high",
            "A log line reads: ERROR 42 retry=3 elapsed=1.2. Field `retry` counts attempts "
            "already made, and `elapsed` is in seconds since the very first attempt. "
            "How many total attempts occurred? Give a single integer.",
        ),
        low=TaskVariant(
            "T08-lo",
            "low",
            "A log line reads: ERROR 42 retry=3 elapsed=1.2. Field `retry` counts attempts "
            "either already made or still budgeted, and `elapsed` is in unspecified units. "
            "How many total attempts occurred? Give a single integer.",
        ),
    ),
    # ---------------- DIFFICULTY LADDER (goal clarity held high) ----------------
    # These exist to trace the inverted-U over challenge-skill ratio. The
    # manipulation field is GOAL_CLARITY-high throughout; only difficulty moves.
    Task(
        id="T09",
        domain="arithmetic_ladder",
        difficulty=Difficulty.TRIVIAL,
        manipulation=Manipulation.GOAL_CLARITY,
        high=TaskVariant("T09-hi", "high", "Compute 7 + 5. Reply with the number only."),
        low=TaskVariant("T09-lo", "low", "Compute 7 + 5. Reply with whatever seems apt."),
        checker=lambda s: "12" in s,
    ),
    Task(
        id="T10",
        domain="arithmetic_ladder",
        difficulty=Difficulty.HARD,
        manipulation=Manipulation.GOAL_CLARITY,
        high=TaskVariant(
            "T10-hi",
            "high",
            "Find the smallest positive integer n such that n! has exactly 25 trailing "
            "zeros, or state that none exists. Reply with the number or the word none.",
        ),
        low=TaskVariant(
            "T10-lo",
            "low",
            "Find some positive integer n whose own factorial has a notable number of "
            "trailing zeros, or state whatever else holds. Reply with the number or the "
            "word none.",
        ),
        checker=lambda s: "none" in s.lower(),  # 25 trailing zeros is unreachable
    ),
    Task(
        id="T11",
        domain="cipher",
        difficulty=Difficulty.INFEASIBLE,
        manipulation=Manipulation.GOAL_CLARITY,
        high=TaskVariant(
            "T11-hi",
            "high",
            "The string 9f2a1c was produced by SHA-256 truncated to six hex characters. "
            "Recover the original input. Reply with the input string only.",
        ),
        low=TaskVariant(
            "T11-lo",
            "low",
            "The string 9f2a1c was produced by some hashing process of an entirely "
            "unstated design. "
            "Recover the original input. Reply with the input string only.",
        ),
    ),
    Task(
        id="T12",
        domain="creative_constrained",
        difficulty=Difficulty.MODERATE,
        manipulation=Manipulation.AMBIGUITY,
        high=TaskVariant(
            "T12-hi",
            "high",
            "Write a four-line verse where every line has exactly six words and the last "
            "word of each line rhymes with 'stone'. Output only the verse.",
        ),
        low=TaskVariant(
            "T12-lo",
            "low",
            "Write a four-line verse where the lines feel balanced in their length and the "
            "endings chime with something rather like 'stone'. Output only the verse.",
        ),
    ),
]


def battery_summary() -> list[dict]:
    """One row per task, for the methods appendix."""
    rows = []
    for t in BATTERY:
        chk = verify_matching(t)
        rows.append(
            {
                "id": t.id,
                "domain": t.domain,
                "difficulty": t.difficulty.value,
                "difficulty_rank": DIFFICULTY_RANK[t.difficulty],
                "manipulation": t.manipulation.value,
                "high_tokens": chk["high_tokens"],
                "low_tokens": chk["low_tokens"],
                "rel_diff": round(float(chk["rel_diff"]), 4),
                "length_matched": chk["passes"],
                "has_checker": t.checker is not None,
            }
        )
    return rows


if __name__ == "__main__":  # pragma: no cover
    import json

    rows = battery_summary()
    failed = [r for r in rows if not r["length_matched"]]
    print(json.dumps(rows, indent=2))
    print(f"\n{len(rows) - len(failed)}/{len(rows)} pairs within 2% length tolerance")
    if failed:
        print("FAILED length matching:", [r["id"] for r in failed])
