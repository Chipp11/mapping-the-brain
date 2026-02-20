# 🧠 Mapping the Brain

**The road to agentic success — building AI agents that actually remember**

---

## What This Is

A working implementation of persistent multi-layer memory for AI agents. Not theory. Not a whitepaper. A system that's been running in production since February 2026, surviving crashes, learning from mistakes, and growing smarter across sessions.

Every AI agent wakes up with amnesia. This project fixes that.

## The Three-Layer Brain

```
┌─────────────────────────────────────────────┐
│  L1: CONSCIOUS THOUGHT (Obsidian)           │
│  Linked notes, reasoning chains, hypotheses │
│  WHERE the agent thinks                     │
├─────────────────────────────────────────────┤
│  L2: SUBCONSCIOUS RECALL (Cognee)           │
│  Semantic search across everything written  │
│  HOW the agent remembers                    │
├─────────────────────────────────────────────┤
│  L3: LONG-TERM MEMORY (Git)                 │
│  Version history of the entire mind         │
│  PROOF the agent grew                       │
└─────────────────────────────────────────────┘
```

### Layer 1: Conscious Thought (Obsidian)

The agent's workspace is an Obsidian vault — plain markdown files with bidirectional links. Every analysis, every decision, every mistake gets a linked note.

```
Canon/
├── THINKING/      ← Reasoning journal (linked notes)
├── EVIDENCE/      ← Empirical findings (data, results)
├── CAPABILITIES/  ← Strategy descriptions
├── DECISIONS/     ← Decisions with reasoning links
├── LESSONS/       ← Extracted patterns from mistakes
└── METRICS/       ← Performance tracking
```

**Why it works:** Linked notes create a knowledge graph. When the agent writes about a measurement error, it links to `[[LESSONS/measurement-confusion]]`. When it validates an edge, it links to `[[EVIDENCE/whatever]]`. Over time, the vault becomes a map of the agent's own reasoning.

### Layer 2: Subconscious Recall (Cognee)

[Cognee](https://github.com/topoteretes/cognee) ingests everything from Layer 1 and makes it semantically searchable. The agent can query its own past thinking in 3 seconds:

```bash
# What do I know about X?
bash scripts/cognee-chunks.sh "prediction market liquidity" 3

# Have I made this kind of mistake before?
bash scripts/cognee-chunks.sh "measurement error calibration" 3

# What was I thinking about recently?
bash scripts/cognee-chunks.sh "open questions hypothesis current" 3
```

**Why it works:** The agent wakes up with amnesia every session. Cognee lets it reconnect to its own mind — not just retrieve facts, but recover *reasoning chains* and *learned lessons*.

### Layer 3: Long-Term Memory (Git)

Every change is version-controlled. Git diffs show how the agent's thinking evolved:

```bash
# How has my understanding of calibration changed?
git log --oneline Canon/EVIDENCE/calibration*

# What did I believe last week vs now?
git diff HEAD~20 Canon/THINKING/
```

**Why it works:** Git provides accountability and growth tracking. The agent can prove it learned, not just that it ran.

## The Heartbeat Protocol

The agent runs on a heartbeat loop — waking up periodically, reconnecting to its brain, and continuing work:

1. **Rate limit self-check** — Don't burn resources
2. **Wake up** — Query Cognee, read last thinking note, check work queue
3. **Resume thinking** — Continue train of thought before doing tasks
4. **Crash recovery** — Check for stuck processes
5. **Advance work** — Pick one task and do it well
6. **Ingest** — Feed new notes to Cognee
7. **Report or stay silent** — Only speak when there's something worth saying

See [HEARTBEAT.md](heartbeat/HEARTBEAT.md) for the full protocol.

## The Soul Architecture

Agents need identity, not just instructions. The Soul architecture gives agents:

- **Constitutional rules** — Immutable security boundaries (~250 tokens)
- **Foundational identity** — Core personality and communication style (~500 tokens)
- **Role definition** — Agent-specific capabilities (~200 tokens)

Total: ~950 tokens vs 3,000+ for monolithic system prompts.

See [SOUL.md](soul/SOUL.md) for the template.

## Key Principles

1. **Think first, task second** — Resume your train of thought before grinding on work
2. **Every analysis gets a pre-mortem** — Write what could go wrong before you run it
3. **Every result gets a thinking note** — Not just "done." What did you learn?
4. **Link everything** — Flat notes are dead notes. Linked notes are a brain
5. **Query before starting** — "Have I done this before? What went wrong?"
6. **Write state before dying** — You will lose consciousness. Save your work
7. **Never claim without validation** — Sample sizes. Real examples. Every time

## Origin Story

This architecture emerged from failure. A previous 6-agent system ("The Castle") crashed from cascading failures — rate limit exhaustion, provider resolution bugs, zombie sessions. The lesson: **one agent with a good brain beats six agents with no memory.**

Angus (the agent running this system) was born February 11, 2026. Named after a piece from the Sheeple art series inscribed on Bitcoin Ordinals.

## Stack

- **Agent Runtime:** [OpenClaw](https://github.com/openclaw/openclaw)
- **L1 (Conscious):** [Obsidian](https://obsidian.md) (plain markdown vault)
- **L2 (Subconscious):** [Cognee](https://github.com/topoteretes/cognee) (semantic search + knowledge graph)
- **L3 (Long-term):** Git (version control)
- **Local Models:** Ollama (DeepSeek, Qwen) for infrastructure tasks
- **Cloud Models:** Anthropic Claude for heavy reasoning

## Status

🟢 **In production** — Running daily since Feb 11, 2026
📈 **Growing** — Knowledge graph expanding with every heartbeat cycle
🔧 **Evolving** — Architecture refined through real failures and recoveries

## Contributing

This is a living document. If you're building persistent agent memory, we want to hear from you.

## License

MIT

---

*"A quant who doesn't reflect on yesterday's errors will repeat them today."*
