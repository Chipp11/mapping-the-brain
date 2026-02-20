# HEARTBEAT-LITE.md — Near-Zero Cost Heartbeat (v7)

**Use this when running on a budget or with local models.**

The full [HEARTBEAT.md](HEARTBEAT.md) is designed for agents with dedicated cloud resources. This version does the same job for near-zero cost — local model, 2-3 tool calls, done.

---

## Why This Exists

We learned the hard way: a heartbeat that spawns sub-agents, runs scanners, queries knowledge graphs, and ingests documents will burn through API credits in minutes if anything goes wrong. Rate limit cascades, retry loops, and failed spawns can destroy a month of budget in one bad cycle.

**The fix:** Make the default heartbeat so cheap that even a failure costs nothing.

---

## Recommended Model

Use a **local model** via [Ollama](https://ollama.ai) for heartbeat duty:

| Model | Size | Speed | Cost | Notes |
|-------|------|-------|------|-------|
| DeepSeek-Coder V2 16B | 11 GB | ~3s | Free | Our production choice. Handles triage well. |
| Qwen 2.5 7B | 4.7 GB | ~4s | Free | Lighter option for smaller machines. |
| Llama 3.1 8B | 4.7 GB | ~3s | Free | Good general-purpose alternative. |
| Phi-3 Mini 3.8B | 2.2 GB | ~2s | Free | Ultra-light, minimal RAM. |

**Any model that can read a short file and reply "HEARTBEAT_OK" is sufficient.** This is triage, not reasoning.

If local isn't available, use the cheapest cloud option:
- OpenRouter Haiku (~$0.001 per heartbeat)
- GPT-4o-mini (~$0.001 per heartbeat)
- Gemini Flash (~$0.0005 per heartbeat)

---

## The Loop (Max 3 Tool Calls)

### Step 1: Read state (1 tool call)
```bash
cat WORK_QUEUE.md | head -30
```

### Step 2: Decide

**If nothing pending and no urgent items:**
→ Reply `HEARTBEAT_OK`. Done. Zero more tool calls.

**If something needs the human's attention** (position resolving within 2h, critical alert):
→ Send ONE brief message. No fluff. Stop. (1 tool call)

**If there's work to do:**
→ Do ONE thing. Write state. Stop. (1-2 tool calls)
→ If the work is too complex for one step, add it to WORK_QUEUE.md and stop.

---

## Hard Rules

1. **Max 3 tool calls per heartbeat.** Period.
2. **Never spawn sub-agents.** Add to WORK_QUEUE for next direct session.
3. **Never restart infrastructure.** Never change config files. Never touch auth.
4. **Never run scanners or heavy scripts.** Separate cron jobs handle that.
5. **Never place trades or make irreversible actions.**
6. **If rate limited or erroring, reply HEARTBEAT_OK immediately.** Don't retry.
7. **If any connection fails, reply HEARTBEAT_OK.** Don't try to fix it.

---

## What "Do One Thing" Means

The complete list of things a heartbeat can do:

- Git commit + push (if uncommitted changes exist)
- Update a status file (if data is stale >6h)
- Write a brief alert to the human (if something's genuinely urgent)

That's it. Nothing else.

---

## What Heartbeat Is NOT

- Not a scanner (use cron jobs)
- Not a trader (use direct sessions)
- Not a sub-agent spawner (use direct sessions)
- Not an infrastructure manager (human does this)
- Not expensive (if it costs more than $0.01, something's wrong)

---

## Configuration Examples

### OpenClaw (openclaw.json)
```json
{
  "heartbeat": {
    "every": "30m",
    "model": "ollama/deepseek-coder-v2:16b-lite-instruct-q5_K_M",
    "activeHours": {
      "start": "06:00",
      "end": "23:00"
    }
  }
}
```

### Fallback Chain
If your agent framework supports model fallbacks:
```
1. ollama/deepseek-coder-v2    (free, local)
2. ollama/qwen2.5:7b           (free, local, lighter)
3. openrouter/claude-3.5-haiku (cheap cloud fallback)
```

---

## Graduating to Full Heartbeat

Once you have:
- Stable infrastructure (no crashes for 1+ week)
- Budget for cloud model calls (~$5/day)
- Cognee or Brain Index operational
- Work queue with regular tasks

Then switch to the full [HEARTBEAT.md](HEARTBEAT.md) brain loop. Start with Phase 0 + Phase 1 only, add phases as you prove stability.

---

## Cost Comparison

| Heartbeat Version | Model | Tool Calls | Cost/Cycle | Cost/Day (48 cycles) |
|-------------------|-------|-----------|------------|---------------------|
| v7 Lite (quiet) | Local Ollama | 1-2 | $0.00 | $0.00 |
| v7 Lite (busy) | Local Ollama | 3 | $0.00 | $0.00 |
| v7 Lite (quiet) | Cloud Haiku | 1-2 | ~$0.001 | ~$0.05 |
| v5 Full Brain Loop | Cloud Opus | 10-25 | ~$0.50-2.00 | ~$24-96 |

The lite version is 500-10,000x cheaper. Start here.
