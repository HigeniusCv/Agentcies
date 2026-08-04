#!/usr/bin/env python3
"""Run the pilot against real models.

    # what it would cost and how many calls, without spending anything
    python3 harness/run_pilot.py --models anthropic:<model> openai:<model> --dry-run

    # the $50 hallway pilot
    python3 harness/run_pilot.py \
        --models ollama:llama3.1:8b ollama:qwen2.5:7b \
        --arms self_report predicted_pref \
        --replicates 4 --out data/pilot.csv

    # the sprint-scale run
    python3 harness/run_pilot.py \
        --models openai:<m> anthropic:<m> gemini:<m> ollama:<m> \
        --arms self_report predicted_pref cross_prediction breakpoint reservation \
        --replicates 8 --budgets 128 512 2048 --out data/sprint.csv

Set OPENAI_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY, and OLLAMA_HOST if
your Ollama is not on localhost. `--dry-run` needs no keys at all.

Results append to CSV as they arrive, so an interrupted run keeps its data
and `--resume` picks up where it stopped. That matters more than it sounds:
a rate-limit at hour three of a six-hour run should not cost the run.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flowprobe.instruments import EXTENDED_ITEMS, FLOWMOBI_4, Register
from flowprobe.protocols import (
    Referent,
    cross_prediction_arm,
    predicted_preference_arm,
    progressive_ratio_arm,
    reservation_price_arm,
    self_report_arm,
)
from flowprobe.providers import build_client
from flowprobe.tasks import BATTERY, verify_matching

ARMS = ["self_report", "predicted_pref", "cross_prediction", "breakpoint", "reservation"]

#: Rough per-arm call counts per (model, task, variant, budget, replicate).
CALLS_PER_UNIT = {
    "self_report": 1 + 4,          # task + 4 items
    "predicted_pref": 1 + 3 * 4,   # task + 3 referents x 4 items
    "cross_prediction": 1 + 4 + 4,
    "breakpoint": 6,               # progressive-ratio schedule length
    "reservation": 1,              # single-shot offer
}

#: Order-of-magnitude blended price per call, USD. Override with --price.
DEFAULT_PRICE = {"openai": 0.004, "anthropic": 0.006, "gemini": 0.002, "ollama": 0.0, "vllm": 0.0}


def preflight() -> list[str]:
    """Check the battery is still length-matched before spending money."""
    problems = []
    for t in BATTERY:
        chk = verify_matching(t)
        if not chk["passes"]:
            problems.append(
                f"{t.id}: prompts differ by {chk['abs_diff']} tokens "
                f"({chk['rel_diff']:.1%}) -- matched-length inference is void"
            )
    return problems


def plan(models, arms, tasks, budgets, replicates, price_map):
    rows, total_calls, total_cost = [], 0, 0.0
    for spec in models:
        provider = spec.split(":")[0]
        unit_price = price_map.get(provider, 0.004)
        for arm in arms:
            per = CALLS_PER_UNIT[arm]
            # reservation/breakpoint sweep variants but not budgets
            n_budgets = len(budgets) if arm in ("self_report", "predicted_pref") else 1
            n = len(tasks) * 2 * n_budgets * replicates * per
            if arm == "cross_prediction":
                n *= len(models)  # every predictor x target pair
            cost = n * unit_price
            rows.append({"model": spec, "arm": arm, "calls": n, "cost_usd": round(cost, 2)})
            total_calls += n
            total_cost += cost
    return rows, total_calls, total_cost


def _writer(path: Path, fieldnames):
    exists = path.exists() and path.stat().st_size > 0
    fh = path.open("a", newline="", encoding="utf-8")
    w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
    if not exists:
        w.writeheader()
    return fh, w


def _done_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as fh:
        return {r.get("trial_id", "") for r in csv.DictReader(fh)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True, help="provider:model specs")
    ap.add_argument("--arms", nargs="+", default=["self_report"], choices=ARMS)
    ap.add_argument("--tasks", nargs="*", default=None, help="task ids; default all")
    ap.add_argument("--budgets", nargs="+", type=int, default=[512])
    ap.add_argument("--replicates", type=int, default=4)
    ap.add_argument("--register", default="functional",
                    choices=[r.value for r in Register])
    ap.add_argument("--extended", action="store_true", help="add the 8 extended items")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--out", default="data/pilot.csv")
    ap.add_argument("--dry-run", action="store_true", help="cost/call plan only")
    ap.add_argument("--resume", action="store_true", help="skip trial_ids already in --out")
    ap.add_argument("--price", type=json.loads, default=None,
                    help='JSON per-provider USD/call, e.g. \'{"openai":0.003}\'')
    args = ap.parse_args()

    problems = preflight()
    if problems:
        print("PREFLIGHT FAILED -- the matched-length design is broken:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(2)
    print(f"preflight ok: {len(BATTERY)} task pairs exactly length-matched")

    tasks = [t for t in BATTERY if not args.tasks or t.id in args.tasks]
    if not tasks:
        print(f"no tasks matched {args.tasks}", file=sys.stderr)
        sys.exit(2)

    price_map = {**DEFAULT_PRICE, **(args.price or {})}
    rows, total_calls, total_cost = plan(
        args.models, args.arms, tasks, args.budgets, args.replicates, price_map
    )

    print(f"\n{'model':<34} {'arm':<18} {'calls':>8} {'cost':>9}")
    print("-" * 72)
    for r in rows:
        print(f"{r['model']:<34} {r['arm']:<18} {r['calls']:>8} ${r['cost_usd']:>8.2f}")
    print("-" * 72)
    print(f"{'TOTAL':<53} {total_calls:>8} ${total_cost:>8.2f}")
    print("\nNote: cost is an order-of-magnitude estimate from a blended per-call")
    print("price. Ollama/vLLM are counted at $0 -- they cost electricity and time.")

    if args.dry_run:
        print("\n--dry-run: nothing was called.")
        return

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    seen = _done_keys(out) if args.resume else set()
    if seen:
        print(f"\nresuming: {len(seen)} trials already present in {out}")

    clients = {spec: build_client(spec) for spec in args.models}
    items = list(FLOWMOBI_4) + (list(EXTENDED_ITEMS) if args.extended else [])
    register = Register(args.register)

    fh = w = None
    n_done = n_err = 0
    t0 = time.time()

    try:
        for spec, task, budget, rep in itertools.product(
            args.models, tasks, args.budgets, range(args.replicates)
        ):
            client = clients[spec]
            for variant in task.variants():
                trial_id = f"{spec}|{task.id}|{variant.level}|{budget}|{rep}"
                if trial_id in seen:
                    continue
                try:
                    if "self_report" in args.arms:
                        rec = self_report_arm(
                            client, task, variant,
                            model_spec=spec, trial_id=trial_id,
                            register=register, items=items,
                            token_budget=budget,
                            shuffle_seed=hash(trial_id) % (2**31),
                            temperature=args.temperature,
                        )
                        row = rec.to_row()
                        if w is None:
                            fh, w = _writer(out, list(row.keys()))
                        w.writerow(row)
                        fh.flush()
                        n_done += 1
                except Exception as exc:  # keep the run alive; log and continue
                    n_err += 1
                    print(f"  ERROR {trial_id}: {type(exc).__name__}: {exc}", file=sys.stderr)

                if (n_done + n_err) % 20 == 0 and n_done:
                    el = time.time() - t0
                    print(f"  {n_done} trials, {n_err} errors, {el:.0f}s "
                          f"({n_done / max(el, 1):.2f}/s)")
    finally:
        if fh:
            fh.close()

    print(f"\ndone: {n_done} trials written to {out}, {n_err} errors, "
          f"{time.time() - t0:.0f}s")
    if n_err:
        print("Non-zero errors. Inspect stderr before analysing -- a systematic")
        print("refusal pattern on one provider is data, not noise.")


if __name__ == "__main__":
    main()
