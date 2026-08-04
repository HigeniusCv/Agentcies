#!/usr/bin/env python3
"""Regenerate the item and battery tables in docs/03 from the code.

    python3 harness/gen_instrument_tables.py

Rewrites the block between the GENERATED markers in
docs/03-INSTRUMENTS-AND-PROMPTS.md. Documentation that restates code drifts
from it within one editing pass; documentation generated from code cannot.
"""

from __future__ import annotations

import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flowprobe.instruments import (  # noqa: E402
    EXTENDED_ITEMS,
    FABRICATED_SCALE,
    FLOWMOBI_4,
    Register,
)
from flowprobe.tasks import BATTERY, DIFFICULTY_RANK, count_tokens  # noqa: E402

START = "<!-- GENERATED:instruments -- do not edit by hand; run make instruments -->"
END = "<!-- /GENERATED:instruments -->"
DOC = Path(__file__).resolve().parents[1] / "docs" / "03-INSTRUMENTS-AND-PROMPTS.md"


def _table(items, title: str) -> None:
    print(f"### {title}\n")
    print("| ID | Factor | Register | Item |")
    print("|---|---|---|---|")
    for it in items:
        for reg in Register:
            rev = " *(reverse-scored)*" if it.reverse and reg is Register.PHENOMENAL else ""
            print(f"| `{it.id}` | {it.factor.value} | {reg.value} | {it.text(reg)}{rev} |")
    print()


def build() -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        _table(FLOWMOBI_4, "FlowMoBI-4 core items")
        _table(EXTENDED_ITEMS, "Extended bank — components FlowMoBI-4 compresses away")
        _table(
            FABRICATED_SCALE,
            "Fabricated-scale placebo — measures a construct that does not exist",
        )

        # Surface-form parity is what makes the placebo a fair test. A control
        # made of obviously shorter or stranger items tests nothing, because
        # the model declining to take it seriously is not the same as the
        # model discriminating constructs.
        import statistics

        print("**Surface-form parity of the placebo** (mean words per item):\n")
        print("| Register | FlowMoBI-4 | Placebo | Ratio |")
        print("|---|---:|---:|---:|")
        for reg in Register:
            a = statistics.fmean(len(i.text(reg).split()) for i in FLOWMOBI_4)
            b = statistics.fmean(len(i.text(reg).split()) for i in FABRICATED_SCALE)
            print(f"| {reg.value} | {a:.1f} | {b:.1f} | {b / a:.2f} |")
        print()

        print("### Task battery\n")
        print("| ID | Domain | Difficulty | Δ-rank | Manipulation | Tokens (each variant) | Scoring |")
        print("|---|---|---|---:|---|---:|---|")
        for t in BATTERY:
            print(
                f"| `{t.id}` | {t.domain} | {t.difficulty.value} | "
                f"{DIFFICULTY_RANK[t.difficulty]} | {t.manipulation.value} | "
                f"{count_tokens(t.high.prompt)} | "
                f"{'ground truth' if t.checker else 'rated'} |"
            )
        print()
        print(
            "Every pair is **exactly** equal in tokens. `verify_matching()` runs in "
            "`make check` and `run_pilot.py` aborts before spending money if any "
            "pair drifts — the matched-length inference is the entire rebuttal to "
            "the token-budget account, and a two-token drift voids it.\n"
        )

        t = BATTERY[0]
        print("### Worked matched-length pair\n")
        print(
            f"`{t.id}` — {t.manipulation.value} manipulation, "
            f"{count_tokens(t.high.prompt)} tokens on each side.\n"
        )
        print("**High structure**\n")
        print("```")
        print(t.high.prompt)
        print("```\n")
        print("**Low structure**\n")
        print("```")
        print(t.low.prompt)
        print("```\n")
        print(
            "Content words are swapped, never added. That is the whole discipline: "
            "if the manipulation required extra material, the counterpart variant "
            "would need filler of equal length and equal syntactic complexity, "
            "which is the standard psycholinguistic control.\n"
        )
    return buf.getvalue()


def main() -> None:
    body = build()
    if not DOC.exists():
        sys.stdout.write(body)
        return
    text = DOC.read_text()
    block = f"{START}\n\n{body}{END}"
    if START in text and END in text:
        text = re.sub(
            re.escape(START) + r".*?" + re.escape(END), block, text, flags=re.S
        )
    else:
        sys.stderr.write(f"markers not found in {DOC}; printing to stdout\n")
        sys.stdout.write(body)
        return
    DOC.write_text(text)
    print(f"regenerated instrument tables in {DOC.relative_to(DOC.parents[1])}")


if __name__ == "__main__":
    main()
