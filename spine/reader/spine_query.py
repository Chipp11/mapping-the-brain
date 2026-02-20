#!/usr/bin/env python3
"""
Spine Reader — query the decision event log.

Usage:
    python spine_query.py                          # all events
    python spine_query.py --decision <id>          # one decision lifecycle
    python spine_query.py --type DecisionProposed  # filter by type
    python spine_query.py --calibration            # confidence vs outcomes
"""

import json
import os
import sys
from collections import defaultdict

SPINE_DIR = os.environ.get("SPINE_DIR", os.path.join(os.path.dirname(__file__), "..", "events"))
LOG_PATH = os.path.join(SPINE_DIR, "spine.jsonl")


def load_events():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        return [json.loads(line) for line in f if line.strip()]


def by_decision(events, decision_id):
    return [e for e in events if e["decision_id"] == decision_id]


def by_type(events, event_type):
    return [e for e in events if e["event_type"] == event_type]


def calibration_report(events):
    """Compare stated confidence vs actual outcomes."""
    proposals = {e["decision_id"]: e for e in by_type(events, "DecisionProposed")}
    outcomes = {e["decision_id"]: e for e in by_type(events, "OutcomeObserved")}

    buckets = defaultdict(lambda: {"correct": 0, "total": 0, "sum_confidence": 0})

    for did, prop in proposals.items():
        if did not in outcomes:
            continue
        out = outcomes[did]
        hyp_correct = out["payload"].get("hypothesis_correct")
        if hyp_correct is None:
            continue

        confidence = prop["payload"]["confidence"]
        bucket = int(confidence * 10) / 10  # round to nearest 0.1
        buckets[bucket]["total"] += 1
        buckets[bucket]["sum_confidence"] += confidence
        if hyp_correct:
            buckets[bucket]["correct"] += 1

    print(f"\n{'Confidence':>12} | {'Win Rate':>10} | {'N':>5} | {'Delta':>8}")
    print("-" * 50)

    for bucket in sorted(buckets.keys()):
        b = buckets[bucket]
        win_rate = b["correct"] / b["total"] if b["total"] > 0 else 0
        avg_conf = b["sum_confidence"] / b["total"] if b["total"] > 0 else 0
        delta = win_rate - avg_conf
        print(f"{avg_conf:>11.1%} | {win_rate:>9.1%} | {b['total']:>5} | {delta:>+7.1%}")

    total = sum(b["total"] for b in buckets.values())
    correct = sum(b["correct"] for b in buckets.values())
    print(f"\nTotal decisions with outcomes: {total}")
    if total > 0:
        print(f"Overall accuracy: {correct/total:.1%}")


def pnl_report(events):
    """Summarise P&L from OutcomeObserved events."""
    outcomes = by_type(events, "OutcomeObserved")
    total_pnl = 0
    wins = 0
    losses = 0

    for o in outcomes:
        pnl = o["payload"].get("pnl")
        if pnl is not None:
            total_pnl += pnl
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1

    print(f"\nTotal P&L: ${total_pnl:+.2f}")
    print(f"Wins: {wins} | Losses: {losses}")
    if wins + losses > 0:
        print(f"Win rate: {wins/(wins+losses):.1%}")


if __name__ == "__main__":
    events = load_events()

    if not events:
        print("No events in spine yet.")
        sys.exit(0)

    if "--decision" in sys.argv:
        idx = sys.argv.index("--decision") + 1
        did = sys.argv[idx]
        for e in by_decision(events, did):
            print(json.dumps(e, indent=2))
    elif "--type" in sys.argv:
        idx = sys.argv.index("--type") + 1
        for e in by_type(events, sys.argv[idx]):
            print(json.dumps(e, indent=2))
    elif "--calibration" in sys.argv:
        calibration_report(events)
    elif "--pnl" in sys.argv:
        pnl_report(events)
    else:
        print(f"Total events: {len(events)}")
        types = defaultdict(int)
        for e in events:
            types[e["event_type"]] += 1
        for t, c in sorted(types.items()):
            print(f"  {t}: {c}")
        print(f"\nUnique decisions: {len(set(e['decision_id'] for e in events))}")
