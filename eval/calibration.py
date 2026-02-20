#!/usr/bin/env python3
"""
Calibration Eval — measures how well the agent's confidence predicts outcomes.

Reads the spine, pairs DecisionProposed (confidence) with OutcomeObserved
(hypothesis_correct), and produces calibration metrics.

Usage:
    python calibration.py                    # print calibration report
    python calibration.py --json             # machine-readable output
    python calibration.py --canon            # write Canon/METRICS note
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

SPINE_DIR = os.environ.get("SPINE_DIR", os.path.join(os.path.dirname(__file__), "..", "spine", "events"))


def load_events():
    log_path = os.path.join(SPINE_DIR, "spine.jsonl")
    if not os.path.exists(log_path):
        return []
    with open(log_path) as f:
        return [json.loads(line) for line in f if line.strip()]


def compute_calibration(events):
    proposals = {}
    outcomes = {}

    for e in events:
        if e["event_type"] == "DecisionProposed":
            proposals[e["decision_id"]] = e
        elif e["event_type"] == "OutcomeObserved":
            outcomes[e["decision_id"]] = e

    # Pair proposals with outcomes
    pairs = []
    for did in proposals:
        if did in outcomes:
            prop = proposals[did]
            out = outcomes[did]
            hyp_correct = out["payload"].get("hypothesis_correct")
            if hyp_correct is not None:
                pairs.append({
                    "decision_id": did,
                    "confidence": prop["payload"]["confidence"],
                    "correct": hyp_correct,
                    "pnl": out["payload"].get("pnl"),
                    "timestamp": prop["timestamp"],
                })

    # Bucket by confidence
    buckets = defaultdict(lambda: {"correct": 0, "total": 0, "pnl": 0, "confidences": []})
    for p in pairs:
        bucket = round(p["confidence"], 1)
        buckets[bucket]["total"] += 1
        buckets[bucket]["confidences"].append(p["confidence"])
        if p["correct"]:
            buckets[bucket]["correct"] += 1
        if p["pnl"] is not None:
            buckets[bucket]["pnl"] += p["pnl"]

    result = {
        "total_decisions": len(pairs),
        "total_proposed": len(proposals),
        "total_unresolved": len(proposals) - len(pairs),
        "buckets": {},
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }

    for bucket in sorted(buckets.keys()):
        b = buckets[bucket]
        avg_conf = sum(b["confidences"]) / len(b["confidences"])
        win_rate = b["correct"] / b["total"]
        result["buckets"][f"{bucket:.0%}"] = {
            "avg_confidence": round(avg_conf, 3),
            "win_rate": round(win_rate, 3),
            "n": b["total"],
            "delta": round(win_rate - avg_conf, 3),
            "pnl": round(b["pnl"], 2),
        }

    # Overall Brier score
    if pairs:
        brier = sum((p["confidence"] - (1 if p["correct"] else 0)) ** 2 for p in pairs) / len(pairs)
        result["brier_score"] = round(brier, 4)

    return result


def print_report(cal):
    print(f"\n=== Calibration Report ===")
    print(f"Decisions with outcomes: {cal['total_decisions']}")
    print(f"Unresolved: {cal['total_unresolved']}")
    if cal.get("brier_score") is not None:
        print(f"Brier score: {cal['brier_score']:.4f}")

    print(f"\n{'Confidence':>12} | {'Win Rate':>10} | {'N':>5} | {'Delta':>8} | {'P&L':>10}")
    print("-" * 55)

    for bucket, data in cal["buckets"].items():
        print(f"{data['avg_confidence']:>11.1%} | {data['win_rate']:>9.1%} | {data['n']:>5} | {data['delta']:>+7.1%} | ${data['pnl']:>+8.2f}")


def write_canon_note(cal, canon_dir="Canon/METRICS"):
    """Write calibration results as an Obsidian note."""
    os.makedirs(canon_dir, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(canon_dir, f"calibration-{date}.md")

    lines = [
        "---",
        f"date: {datetime.now().isoformat()[:16]}",
        "tags: [metrics, calibration, eval]",
        "links:",
        '  - "[[Canon/EVIDENCE/calibration-203k]]"',
        "---",
        "",
        f"# Calibration Report — {date}",
        "",
        f"**Decisions evaluated:** {cal['total_decisions']}",
        f"**Unresolved:** {cal['total_unresolved']}",
    ]

    if cal.get("brier_score") is not None:
        lines.append(f"**Brier score:** {cal['brier_score']:.4f}")

    lines.extend([
        "",
        "| Confidence | Win Rate | N | Delta | P&L |",
        "|-----------|---------|---|-------|-----|",
    ])

    for bucket, data in cal["buckets"].items():
        lines.append(
            f"| {data['avg_confidence']:.1%} | {data['win_rate']:.1%} | {data['n']} | {data['delta']:+.1%} | ${data['pnl']:+.2f} |"
        )

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Written to {path}")


if __name__ == "__main__":
    events = load_events()
    cal = compute_calibration(events)

    if "--json" in sys.argv:
        print(json.dumps(cal, indent=2))
    elif "--canon" in sys.argv:
        print_report(cal)
        write_canon_note(cal)
    else:
        print_report(cal)
