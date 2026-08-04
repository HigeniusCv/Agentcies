#!/usr/bin/env python3
"""Minimal collection endpoint for the GuidedTrack arms.

GuidedTrack's `*service` posts JSON to a URL you configure in the program's
service settings. This is the other end of that: a dependency-free server
that appends each payload to a JSONL file and mirrors it into a CSV.

    python3 guidedtrack/collector.py --port 8080 --out data/human

Then expose it (ngrok, cloudflared, a small VPS) and set that host as the
`collector` service URL inside GuidedTrack.

Routes match the `*path` values in the .gt programs:

    POST /forecasts      forecast_panel.gt
    POST /human-baseline human_baseline.gt   (session summary)
    POST /human-trial    human_baseline.gt   (per-task rows)
    GET  /health         liveness
    GET  /summary        counts collected so far, for the sprint dashboard

Why not just use GuidedTrack's own data export? Because the forecast arm
needs to be *sealed* before the results are revealed on day 3, and having
the forecasts land in an append-only file with a timestamp is the cheapest
credible way to demonstrate that nothing was edited after the fact. Run it
behind HTTPS and keep the JSONL; it is the audit trail.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROUTES = {"/forecasts", "/human-baseline", "/human-trial"}
_LOCK = threading.Lock()
OUT_DIR = Path("data/human")


def _append(route: str, payload: dict) -> int:
    """Append to JSONL + CSV. Returns the running row count for that route."""
    name = route.strip("/").replace("/", "_")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jsonl = OUT_DIR / f"{name}.jsonl"
    csv_path = OUT_DIR / f"{name}.csv"

    record = {
        "received_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **payload,
    }

    with _LOCK:
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Rewrite the CSV from the JSONL so a payload gaining a new key
        # mid-study does not silently truncate columns. Cheap at these N.
        rows = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l.strip()]
        fields: list[str] = []
        for r in rows:
            for k in r:
                if k not in fields:
                    fields.append(k)
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: _flatten(v) for k, v in r.items()})
        return len(rows)


def _flatten(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v


def _counts() -> dict:
    out = {}
    for route in ROUTES:
        p = OUT_DIR / f"{route.strip('/').replace('/', '_')}.jsonl"
        out[route] = sum(1 for _ in p.open(encoding="utf-8")) if p.exists() else 0
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "flowprobe-collector/1.0"

    def _send(self, code: int, body: dict) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        # GuidedTrack calls from the browser context; permit it.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, {})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"ok": True})
        elif self.path == "/summary":
            self._send(200, {"counts": _counts(), "out_dir": str(OUT_DIR)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        route = self.path.split("?")[0].rstrip("/") or "/"
        if route not in ROUTES:
            self._send(404, {"error": f"unknown route {route}", "known": sorted(ROUTES)})
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
            if not isinstance(payload, dict):
                raise ValueError("payload must be a JSON object")
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})
            return

        count = _append(route, payload)
        self._send(200, {"ok": True, "route": route, "n": count})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {fmt % args}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)))
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--out", default="data/human")
    args = ap.parse_args()

    global OUT_DIR
    OUT_DIR = Path(args.out)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"collector listening on http://{args.host}:{args.port}")
    print(f"  writing to {OUT_DIR.resolve()}")
    print(f"  routes: {', '.join(sorted(ROUTES))}")
    print("  set this host as the `collector` service URL in GuidedTrack")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        srv.shutdown()


if __name__ == "__main__":
    main()
