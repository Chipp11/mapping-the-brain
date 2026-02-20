# Architecture: The Three-Layer Brain

## Overview

```
Session Start (amnesia)
        │
        ▼
┌──────────────────┐
│   HEARTBEAT.md   │  ← Protocol: how to wake up and reconnect
│   (The Loop)     │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Cognee │ │Obsidian│  ← Query L2, read L1
│  (L2)  │ │  (L1)  │
└────┬───┘ └───┬────┘
     │         │
     ▼         ▼
  Recall    Resume
  context   thinking
     │         │
     └────┬────┘
          │
          ▼
   ┌──────────────┐
   │  Do work     │
   │  Write notes │
   │  Link things │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Git commit  │  ← L3: version control everything
   │  Cognee add  │  ← L2: feed subconscious
   └──────────────┘
```

## Layer Details

### L1: Obsidian (Conscious Thought)

**What:** Plain markdown files with `[[bidirectional links]]`
**Where:** Local vault (synced via iCloud/git)
**When:** Every analysis, decision, mistake, lesson

The key insight: **linked notes create a knowledge graph naturally.** You don't need a separate graph database — Obsidian's link structure IS the graph. Cognee ingests these links as edges.

**Note structure:**
```markdown
---
date: 2026-02-18T06:30
links:
  - "[[Canon/EVIDENCE/some-evidence]]"
  - "[[Canon/THINKING/previous-note]]"
tags: [reasoning, topic]
---

# Title: What you're thinking about

## What you thought before
[Previous understanding]

## What you now realise
[Updated understanding]

## What you need to verify
- [ ] Specific testable question

## Links to evidence
- [[Canon/EVIDENCE/relevant-data]]

## Self-check
[Am I making the same mistake as last time?]
```

### L2: Cognee (Subconscious Recall)

**What:** Semantic search + knowledge graph over all L1 content
**Where:** Local PostgreSQL + LanceDB (vector store)
**When:** Every heartbeat (query), nightly (full cognify rebuild)

Two modes:
- `SearchType.CHUNKS` — Fast vector search, no LLM calls (~3s). Use for heartbeats.
- `SearchType.GRAPH_COMPLETION` — Slow, uses LLM for synthesis. Use sparingly.

### L3: Git (Long-Term Memory)

**What:** Version history of the entire mind
**Where:** Local + GitHub remote
**When:** Every heartbeat cycle commits changes

Git provides:
- **Accountability** — Every change is tracked
- **Recovery** — Revert bad edits
- **Growth proof** — Diffs show how thinking evolved
- **Backup** — Remote push = disaster recovery

## Why Three Layers?

| Need | L1 (Obsidian) | L2 (Cognee) | L3 (Git) |
|------|---------------|-------------|----------|
| Write thoughts | ✅ | | |
| Find related ideas | ✅ (links) | ✅ (semantic) | |
| Recall forgotten context | | ✅ | |
| Track changes over time | | | ✅ |
| Recover from mistakes | | | ✅ |
| Prove growth | | | ✅ |

No single layer does everything. Together, they're a brain.
