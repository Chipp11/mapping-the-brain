# 🧠 Mapping the Brain

**A multi-layer persistent memory architecture for AI agents that actually remember, reason, and evolve.**

---

## System Architecture

```
  External World (Markets, Feeds, APIs)
          ↓
    [ Connectors ]            ← raw observation, stateless
          ↓
    [ Signal Router ]         ← normalize, dedupe, batch
          ↓
    [ Strategy Modules ]      ← edge detection, pure functions
          ↓
    [ Decision Spine (L4) ]   ← auditable event log
          ↓
    [ Policy Engine (Ma'at) ] ← governance, veto, constraints
          ↓
    [ Executor ]              ← regime-aware action planning
          ↓
    [ Tool Gateway ]          ← secrets + action adapters
          ↓
    [ External World ]
          ↓
    [ Scribe ]                ← outcome reconciliation
          ↓
    [ Eval / Calibration ]    ← learning signal
          ↺ feeds back into strategy + policy tuning

  Underneath everything:
  ┌─────────────────────────────────────────────────┐
  │  L1: Obsidian Vault    — WHERE the agent thinks │
  │  L2: Semantic Recall   — HOW the agent remembers│
  │  L3: Git History       — PROOF the agent grew   │
  └─────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full specification.

---

## What This Is

A working implementation of persistent multi-layer memory for AI agents. Not theory. Not a whitepaper. A system that's been running in production since February 2026, surviving crashes, learning from mistakes, and growing smarter across sessions.

Every AI agent wakes up with amnesia. This project fixes that.

## The Three-Layer Brain

### L1: Conscious Thought — [Obsidian](https://obsidian.md)

The agent's workspace is an [Obsidian](https://obsidian.md) vault — plain markdown files with bidirectional links. Every analysis, every decision, every mistake gets a linked note.

```
Canon/
├── THINKING/      ← Reasoning journal (linked notes)
├── EVIDENCE/      ← Empirical findings (data, results)
├── DECISIONS/     ← Decisions with reasoning links
├── LESSONS/       ← Extracted patterns from mistakes
└── METRICS/       ← Performance tracking
```

Linked notes create a knowledge graph. When the agent writes about an error, it links to `[[LESSONS/measurement-confusion]]`. Over time, the vault becomes a map of the agent's own reasoning.

### L2: Subconscious Recall — [Cognee](https://github.com/topoteretes/cognee)

[Cognee](https://github.com/topoteretes/cognee) ingests everything from L1 and makes it semantically searchable. The agent can query its own past thinking:

```bash
bash scripts/cognee-chunks.sh "prediction market liquidity" 3
bash scripts/cognee-chunks.sh "have I made this mistake before" 3
```

The agent wakes up with amnesia every session. Cognee lets it reconnect — not just to facts, but to reasoning chains and learned lessons.

### L3: Long-Term Memory — [Git](https://git-scm.com)

Every change is version-controlled. Git diffs show how the agent's thinking evolved:

```bash
git log --oneline Canon/EVIDENCE/calibration*
git diff HEAD~20 Canon/THINKING/
```

### L4: Decision Spine

Append-only event log. Every decision — from proposal through policy check through execution through outcome — is an immutable event.

**The one invariant: No tool call without a `decision_id`.**

See [spine/](spine/) for the schema and implementation.

---

## The Heartbeat Protocol

Two versions — start lite, graduate to full:

### Lite Heartbeat (Recommended Start) — [HEARTBEAT-LITE.md](heartbeat/HEARTBEAT-LITE.md)

Runs on a **local model** (DeepSeek, Qwen, Llama via [Ollama](https://ollama.ai)). Costs $0.00 per cycle.

```
Read WORK_QUEUE.md → anything urgent? → HEARTBEAT_OK or do one thing → stop
```

Max 3 tool calls. Never spawns sub-agents. Never runs scanners. If anything fails, replies HEARTBEAT_OK and waits for next cycle. This is what we run in production.

### Full Brain Loop (Advanced) — [HEARTBEAT.md](heartbeat/HEARTBEAT.md)

For agents with dedicated cloud resources and stable infrastructure:

1. **Rate limit self-check** — Don't burn resources
2. **Wake up** — Query Cognee, read last thinking note, check work queue
3. **Resume thinking** — Continue train of thought before doing tasks
4. **Crash recovery** — Check for stuck processes
5. **Advance work** — Pick one task and do it well
6. **Ingest** — Feed new notes to Cognee
7. **Report or stay silent** — Only speak when there's something worth saying

**Why two versions?** We learned the hard way that a heavy heartbeat on a cloud model can burn through a month of API credits in minutes if anything goes wrong. Start lite. Graduate when your infrastructure is stable.

---

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/Chipp11/mapping-the-brain/main/install.sh | bash
```

This sets up:
- Obsidian vault with Canon structure (L1)
- Cognee semantic memory (L2)
- Git version history (L3)
- Decision Spine event log (L4)
- Helper scripts: `search.sh`, `ingest.sh`, `log-decision.sh`

Requirements: git, Python 3.10+

---

## Building Toward

This architecture is being built incrementally. Current status:

| Component | Status | Description |
|-----------|--------|-------------|
| L1: Obsidian Vault | ✅ Live | Canon folder structure, linked reasoning notes |
| L2: Cognee Recall | ✅ Live | Semantic search across vault, 200K+ documents indexed |
| L3: Git Memory | ✅ Live | Full version history, diffable reasoning evolution |
| L4: Decision Spine | ✅ Live | Event schema, spine writer, trade lifecycle tracking |
| Heartbeat Protocol | ✅ Live | Periodic wake-up, crash recovery, scan scheduling |
| Soul Architecture | ✅ Live | Constitution + Identity + Role separation (~950 tokens) |
| Signal Connectors | 🔧 Partial | Polymarket WS, RSS news feeds (8 sources) |
| Strategy Modules | 🔧 Partial | 4 strategies with self-evolving weight system |
| Eval / Calibration | 🔧 Partial | 203K market calibration dataset, strategy win tracking |
| Policy Engine (Ma'at) | 📐 Spec | Declarative rules, veto authority, risk gating |
| Signal Router | 📐 Spec | Condition-level batching, dedup, fan-out |
| Scribe | 📐 Spec | Deterministic outcome reconciliation |
| Local Brain Index | 📐 Spec | SQLite + FAISS + FTS5 replacement for Cognee |
| Tool Gateway | 📐 Spec | Centralised secrets, allowlists, circuit breakers |

### Local Brain Index (Next Major Build)

Replacing Cognee with a fully local, deterministic cognition layer:

- **SQLite** for truth (documents, chunks, links)
- **FAISS** for vector recall
- **FTS5** for lexical search
- **RRF fusion** for hybrid retrieval
- **Cross-encoder reranker** for reasoning alignment
- **Canon-aware ranking** — exploit existing folder structure instead of rediscovering it
- **Temporal memory model** — 45-day half-life with foundation anchoring

---

## Stack

| Layer | Technology | Role |
|-------|-----------|------|
| Agent Runtime | [OpenClaw](https://github.com/openclaw/openclaw) | Orchestration, heartbeat, tool execution |
| L1 (Conscious) | [Obsidian](https://obsidian.md) | Plain markdown vault with bidirectional links |
| L2 (Subconscious) | [Cognee](https://github.com/topoteretes/cognee) | Semantic search + knowledge graph |
| L3 (Long-term) | [Git](https://git-scm.com) | Version control, diffable reasoning |
| L4 (Operational) | Custom ([schema](spine/schema/decision_event.schema.json)) | Append-only decision event log |
| Local Models | [Ollama](https://ollama.ai) | Infrastructure tasks (DeepSeek, Qwen) |
| Cloud Models | [Anthropic Claude](https://anthropic.com) | Heavy reasoning |
| Embeddings | [Sentence Transformers](https://www.sbert.net/) | Local semantic embeddings |

---

## Key Principles

1. **Think first, task second** — Resume your train of thought before grinding
2. **No tool call without `decision_id`** — The institutional invariant
3. **Events are immutable** — Never rewrite the spine
4. **Constitution beats identity** — Safety and evidence override personality
5. **Measure, don't claim** — If you can't show the calibration curve, don't say "learning"
6. **One agent with a good brain beats six agents with no memory**

---

## Origin Story

This architecture emerged from failure. A previous 6-agent system ("The Castle") crashed from cascading failures — rate limit exhaustion, provider bugs, zombie sessions. The lesson: **simplicity wins.** One agent with persistent memory and institutional discipline beats a fleet of amnesiac agents.

---

## Contributing

Fork it. Break it. Tell me what's wrong.

If you're building persistent agent memory, open an issue or PR. All critique is welcome.

## License

MIT
