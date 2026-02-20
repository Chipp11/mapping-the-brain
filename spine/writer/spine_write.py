#!/usr/bin/env python3
"""
Spine Writer — emit decision events to the append-only log.

Usage:
    from spine_write import propose, dispatched, executed, failed, outcome

    decision_id = propose(
        hypothesis="BTC will close above 95K",
        confidence=0.72,
        chosen_action="place_trade",
        parameters={"market": "btc-95k", "side": "YES", "size": 50},
        pre_mortem="Low volume market, might not fill",
        canon_note_ref="Canon/THINKING/2026-02-19-btc-95k.md"
    )
"""

import json
import uuid
import os
from datetime import datetime, timezone

SPINE_DIR = os.environ.get("SPINE_DIR", os.path.join(os.path.dirname(__file__), "..", "events"))


def _ensure_dir():
    os.makedirs(SPINE_DIR, exist_ok=True)


def _emit(event: dict) -> str:
    """Append event to the spine log. Returns event_id."""
    _ensure_dir()
    log_path = os.path.join(SPINE_DIR, "spine.jsonl")
    with open(log_path, "a") as f:
        f.write(json.dumps(event, default=str) + "\n")
    return event["event_id"]


def _base(decision_id: str, event_type: str, agent: str = "angus") -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "decision_id": decision_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
    }


def propose(
    hypothesis: str,
    confidence: float,
    chosen_action: str,
    parameters: dict = None,
    trigger: str = "heartbeat",
    inputs: list = None,
    alternatives_considered: list = None,
    pre_mortem: str = "",
    canon_note_ref: str = "",
    agent: str = "angus",
) -> str:
    """Emit DecisionProposed. Returns decision_id."""
    decision_id = str(uuid.uuid4())
    event = _base(decision_id, "DecisionProposed", agent)
    event["payload"] = {
        "trigger": trigger,
        "inputs": inputs or [],
        "hypothesis": hypothesis,
        "confidence": confidence,
        "alternatives_considered": alternatives_considered or [],
        "chosen_action": chosen_action,
        "parameters": parameters or {},
        "pre_mortem": pre_mortem,
        "canon_note_ref": canon_note_ref,
    }
    _emit(event)
    return decision_id


def dispatched(decision_id: str, tool: str, parameters: dict, agent: str = "tool_gateway") -> str:
    event = _base(decision_id, "ActionDispatched", agent)
    event["payload"] = {
        "tool": tool,
        "parameters": {k: v for k, v in parameters.items() if k not in ("api_key", "secret", "private_key")},
    }
    return _emit(event)


def executed(decision_id: str, success: bool, result: dict = None, latency_ms: int = 0, agent: str = "tool_gateway") -> str:
    event = _base(decision_id, "ActionExecuted", agent)
    event["payload"] = {
        "success": success,
        "result": result or {},
        "latency_ms": latency_ms,
    }
    return _emit(event)


def failed(decision_id: str, error_type: str, error_detail: str = "", retryable: bool = False, agent: str = "tool_gateway") -> str:
    event = _base(decision_id, "ActionFailed", agent)
    event["payload"] = {
        "error_type": error_type,
        "error_detail": error_detail,
        "retryable": retryable,
        "retry_count": 0,
    }
    return _emit(event)


def outcome(
    decision_id: str,
    resolution: str,
    hypothesis_correct: bool = None,
    pnl: float = None,
    pnl_currency: str = "USDC",
    resolution_source: str = "manual",
    agent: str = "scribe",
) -> str:
    event = _base(decision_id, "OutcomeObserved", agent)
    payload = {
        "resolution": resolution,
        "resolution_source": resolution_source,
        "resolution_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if hypothesis_correct is not None:
        payload["hypothesis_correct"] = hypothesis_correct
    if pnl is not None:
        payload["pnl"] = pnl
        payload["pnl_currency"] = pnl_currency
    event["payload"] = payload
    return _emit(event)


if __name__ == "__main__":
    # Demo: one complete decision lifecycle
    did = propose(
        hypothesis="Demo market will resolve YES",
        confidence=0.85,
        chosen_action="place_trade",
        parameters={"market": "demo-market", "side": "YES", "size": 10},
        pre_mortem="This is a demo, nothing real",
    )
    print(f"DecisionProposed: {did}")

    dispatched(did, "polymarket_trade", {"market": "demo-market", "side": "YES", "amount": 10})
    print("ActionDispatched")

    executed(did, success=True, result={"order_id": "demo-123"}, latency_ms=450)
    print("ActionExecuted")

    outcome(did, resolution="YES", hypothesis_correct=True, pnl=3.50)
    print("OutcomeObserved")

    print(f"\nFull lifecycle written to {SPINE_DIR}/spine.jsonl")
