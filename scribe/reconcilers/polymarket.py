#!/usr/bin/env python3
"""
Polymarket Reconciler — polls market resolutions and emits OutcomeObserved events.

Reads spine for ActionExecuted events with tool=polymarket_trade,
checks if the market has resolved, and backfills the outcome.
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "spine", "writer"))
from spine_write import outcome, load_events if hasattr(__import__("spine_write", fromlist=["load_events"]), "load_events") else None

SPINE_DIR = os.environ.get("SPINE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "spine", "events"))
GAMMA_API = "https://gamma-api.polymarket.com"


def get_market_status(condition_id: str) -> dict:
    """Check if a Polymarket market has resolved."""
    url = f"{GAMMA_API}/markets/{condition_id}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def reconcile(spine_path: str = None):
    """
    Scan spine for unresolved trades and check for outcomes.

    For each DecisionProposed with chosen_action=place_trade that has
    an ActionExecuted but no OutcomeObserved, check if the market resolved.
    """
    if spine_path is None:
        spine_path = os.path.join(SPINE_DIR, "spine.jsonl")

    if not os.path.exists(spine_path):
        print("No spine events found.")
        return

    with open(spine_path) as f:
        events = [json.loads(line) for line in f if line.strip()]

    # Group by decision_id
    decisions = {}
    for e in events:
        did = e["decision_id"]
        if did not in decisions:
            decisions[did] = []
        decisions[did].append(e)

    # Find decisions with execution but no outcome
    unresolved = []
    for did, evts in decisions.items():
        types = {e["event_type"] for e in evts}
        if "ActionExecuted" in types and "OutcomeObserved" not in types:
            proposal = next((e for e in evts if e["event_type"] == "DecisionProposed"), None)
            if proposal and proposal["payload"].get("chosen_action") == "place_trade":
                unresolved.append((did, proposal))

    print(f"Found {len(unresolved)} unresolved trade decisions")

    for did, proposal in unresolved:
        market_id = proposal["payload"].get("parameters", {}).get("condition_id")
        if not market_id:
            print(f"  {did[:8]}: no condition_id, skipping")
            continue

        status = get_market_status(market_id)
        if "error" in status:
            print(f"  {did[:8]}: API error: {status['error']}")
            continue

        resolved = status.get("resolved", False)
        if not resolved:
            print(f"  {did[:8]}: market still open")
            continue

        # Market resolved — emit outcome
        resolution = status.get("outcome", "unknown")
        side = proposal["payload"]["parameters"].get("side", "YES")
        size = proposal["payload"]["parameters"].get("size", 0)
        price = proposal["payload"]["parameters"].get("price", 0)

        hypothesis_correct = (resolution.upper() == side.upper())
        pnl = (size * (1 - price)) if hypothesis_correct else (-size * price)

        outcome(
            decision_id=did,
            resolution=f"{resolution} (side was {side})",
            hypothesis_correct=hypothesis_correct,
            pnl=round(pnl, 2),
            resolution_source="polymarket_api",
        )
        print(f"  {did[:8]}: RESOLVED {resolution} | correct={hypothesis_correct} | pnl=${pnl:+.2f}")


if __name__ == "__main__":
    reconcile()
