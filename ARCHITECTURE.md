# 🏗️ Architecture

**System-level spec for the Brain — from memory layers to institutional discipline.**

---

## The Full Stack

The Brain started as three layers: think, remember, prove you grew. That's necessary. It's not sufficient.

An agent that remembers its mistakes but can't prove its decisions were sound is a journal, not an institution. What follows is the complete architecture — the original L1/L2/L3 brain plus the structural additions that make it auditable, measurable, and safe to upgrade.

```
┌───────────────────────────────────────────┐
│                 HUMAN UI                  │
│    dashboards · overrides · kill switch   │
└─────────────────────▲─────────────────────┘
                      │ policy edits / approvals
                      ▼
┌───────────────────────────────────────────────────────────┐
│                POLICY ENGINE (Ma'at)                      │
│    rules · risk calc · veto authority · approval gates    │
└─────────────▲─────────────────────────────────▲───────────┘
              │ PolicyChecked / Vetoed          │ reads events
              │                                 │
              ▼                                 ▼
┌───────────────────────────────────────────────────────────┐
│                  L4: DECISION SPINE                       │
│                append-only event log                      │
│    propose → check → dispatch → execute → outcome         │
└─────────────▲─────────────────────────────────▲───────────┘
              │ decision_id required            │ outcome events
              │                                 │
              ▼                                 ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│      AGENT RUNTIME        │  │         SCRIBE            │
│   Heartbeat + Soul +      │  │  deterministic reconciler │
│   planners                │  │  (polls tools, emits      │
└───────────────▲───────────┘  │   OutcomeObserved)        │
                │ tool calls   └──────────────▲────────────┘
                ▼                             │ polls
┌───────────────────────────────────────────────────────────┐
│                    TOOL GATEWAY                           │
│   ONLY place with secrets · allowlists · throttles · CBs │
└───────────────▲───────────────────────────────▲───────────┘
                │ reads/writes                  │ reads
                ▼                               ▼
┌───────────────────────────┐  ┌──────────────────────────┐
│     BRAIN (L1/L2/L3)     │  │      DATA SOURCES        │
│  Obsidian · Cognee · Git  │  │  markets · news · chain  │
└───────────────────────────┘  └──────────────────────────┘
```

---

## The One Invariant

> **No tool call without a `decision_id`.**

That's the institutional threshold. Every action traces back to a decision. Every decision traces back to reasoning. Every outcome traces back to an action.

Break this chain and you lose auditability. Maintain it and you get:

- **Autonomy becomes auditable** — you can replay any decision
- **Eval becomes real** — confidence vs outcome, measured
- **Drift becomes detectable** — rolling windows over decision quality
- **Upgrades become safe** — A/B test models against the same spine

---

## Layer Definitions

### L1: Conscious Thought (Obsidian)

The agent's workspace. Plain markdown with bidirectional links.

```
Canon/
├── THINKING/      ← Reasoning journal (linked notes)
├── EVIDENCE/      ← Empirical findings (data, results)
├── CAPABILITIES/  ← Strategy descriptions
├── DECISIONS/     ← Decisions with reasoning links
├── LESSONS/       ← Extracted patterns from mistakes
└── METRICS/       ← Performance tracking
```

**Role:** Where the agent thinks. Human-readable. Browsable in Obsidian. Every analysis gets a pre-mortem. Every result gets a thinking note. Link everything.

### L2: Subconscious Recall (Cognee)

Semantic search + knowledge graph over everything in L1.

```bash
# What do I know about X?
bash scripts/cognee-chunks.sh "prediction market liquidity" 3

# Have I made this kind of mistake before?
bash scripts/cognee-chunks.sh "measurement error calibration" 3
```

**Role:** How the agent remembers. Reconnects to its own mind after waking from amnesia. Not just facts — reasoning chains and learned lessons.

**Health invariants:**
- Monitor node/edge counts, duplicate entity ratio, oldest unverified edge
- Avoid `cognify()` during heartbeat cycles (ingestion is a background task)
- Domain-specific extraction schemas beat generic prompting

### L3: Long-Term Memory (Git)

Version control over the entire Canon.

```bash
# How has my understanding changed?
git log --oneline Canon/EVIDENCE/calibration*

# What did I believe last week vs now?
git diff HEAD~20 Canon/THINKING/
```

**Role:** Proof the agent grew. Accountability. Diffable reasoning evolution.

### L4: Decision Spine (Event Log)

Append-only event stream. Every decision the agent makes — from proposal through policy check through execution through outcome — is an event.

```
spine/
├── schema/
│   └── decision_event.schema.json
├── writer/
│   └── spine_write.py
├── reader/
│   └── spine_query.py
└── materialize/
    └── materialize_state.py
```

**Role:** What the agent decided and why. The audit trail. The source of truth for eval, drift detection, and calibration.

**Event types (minimum viable):**

| Event | Emitted by | Contains |
|-------|-----------|----------|
| `DecisionProposed` | Agent Runtime | hypothesis, confidence, alternatives, inputs |
| `PolicyChecked` | Ma'at | pass/fail, rules applied, veto reason |
| `ActionDispatched` | Tool Gateway | tool, parameters, decision_id |
| `ActionExecuted` | Tool Gateway | result, latency, errors |
| `ActionFailed` | Tool Gateway | error type, retry status |
| `OutcomeObserved` | Scribe | settlement, PnL, resolution source |

Events are immutable. Never rewrite history. The Scribe backfills outcomes; the agent never edits past events.

---

## Supporting Components

### Policy Engine (Ma'at)

Enforceable constraints evaluated before any action dispatches.

```
policy/
├── rules.yaml       # declarative rule definitions
├── evaluate.py      # rule evaluation engine
└── tests/           # rule unit tests
```

**Starter rules:**
- Max position size per trade
- Max concurrent workers
- Staleness threshold (reject if input data > N minutes old)
- Confidence gating (reject if stated confidence has no calibration history)

**Precedence hierarchy:**
```
Constitution > Evidence/Policy > Role > Identity preferences
```

Ma'at can veto. Ma'at cannot be overridden by identity preferences. Only the Human UI can override Ma'at, and that override is itself an event.

### Scribe

Deterministic reconciliation daemon. Watches for outcomes and backfills L4.

```
scribe/
├── reconcilers/
│   ├── polymarket.py    # poll market resolutions
│   └── binance.py       # poll trade fills/settlements
└── run_scribe.py        # scheduler
```

**Scribe emits only facts.** No reasoning, no interpretation. `OutcomeObserved` events contain: what resolved, when, what the result was, and the `decision_id` it relates to.

### Tool Gateway

The only component with secrets. Every external call goes through here.

**Responsibilities:**
- Secret management (API keys never touch agent runtime)
- Allowlists (agent can only call approved endpoints)
- Throttling (rate limits enforced at the gateway, not by the agent)
- Circuit breakers (cascading failures killed the Castle; never again)

**Hard rule:** Every tool call carries a `decision_id` header. No ID, no call. The gateway enforces the invariant.

### Eval

Turns memory into measurement. Reads L4 events and computes quantitative feedback that flows back into L1 as `Canon/METRICS/` notes.

```
eval/
├── calibration.py         # confidence vs win-rate curves
├── drift.py               # rolling performance windows
├── veto_analysis.py       # Ma'at effectiveness: saves vs false vetoes
└── source_attribution.py  # which data sources correlate with good decisions
```

**What you get:**
- Calibration curves across confidence buckets
- Drift alerts when win rate diverges from stated confidence
- Veto ROI — are risk checks saving money or killing edge?
- Input attribution — which sources of information actually help?

---

## Soul Architecture

Agents need identity, not just instructions. But identity must never override safety or evidence.

```
soul/
├── CONSTITUTION.md     # immutable constraints + security (~250 tokens)
├── IDENTITY.md         # voice, persona, communication style (~500 tokens)
├── ROLE_ANGUS.md       # capabilities, domains, tool permissions (~200 tokens)
└── SOUL.md             # overview, points to the above
```

**Total:** ~950 tokens vs 3,000+ for monolithic system prompts.

**Precedence (non-negotiable):**
```
1. CONSTITUTION — security boundaries, never overridden
2. POLICY (Ma'at) — risk constraints, evidence-based
3. ROLE — what this agent can do
4. IDENTITY — how this agent communicates
```

If identity says "I'm a bold, conviction-driven trader" and policy says "this position exceeds max risk," policy wins. Always.

---

## Separation of Concerns

Three things that look similar but must live in different places:

| Concern | Lives in | Enforced by |
|---------|---------|-------------|
| Operational loop semantics (phases, timing, crash recovery) | `heartbeat/HEARTBEAT.md` | Agent Runtime |
| Identity + voice + persona | `soul/` | Prompt construction |
| Enforceable constraints (risk, rate limits, gating) | `policy/` | Ma'at (machine-checkable) |

**Do not duplicate rules across these.** If a constraint is enforceable, it belongs in Policy. If it's a loop phase, it belongs in Heartbeat. If it's personality, it belongs in Soul.

---

## Directory Layout (Target State)

```
mapping-the-brain/
├── README.md
├── ARCHITECTURE.md             ← you are here
│
├── heartbeat/
│   └── HEARTBEAT.md            # operational loop protocol
│
├── soul/
│   ├── SOUL.md                 # overview
│   ├── CONSTITUTION.md         # immutable constraints
│   ├── IDENTITY.md             # voice + persona
│   └── ROLE_ANGUS.md           # agent-specific capabilities
│
├── spine/
│   ├── schema/
│   │   └── decision_event.schema.json
│   ├── writer/
│   │   └── spine_write.py
│   ├── reader/
│   │   └── spine_query.py
│   └── materialize/
│       └── materialize_state.py
│
├── policy/
│   ├── rules.yaml
│   ├── evaluate.py
│   └── tests/
│
├── scribe/
│   ├── reconcilers/
│   │   ├── polymarket.py
│   │   └── binance.py
│   └── run_scribe.py
│
├── eval/
│   ├── calibration.py
│   ├── drift.py
│   ├── veto_analysis.py
│   └── source_attribution.py
│
├── scripts/
│   ├── cognee-chunks.sh
│   └── cognee-health.sh
│
└── examples/
    └── end_to_end_cycle/
        └── WALKTHROUGH.md
```

---

## End-to-End Cycle (How It All Connects)

One complete loop through the entire architecture:

1. **Heartbeat wakes** → queries Cognee (L2) → reads last thinking note (L1)
2. **Agent identifies opportunity** → writes `Canon/THINKING/...` note (L1)
3. **Agent emits `DecisionProposed`** → hypothesis, confidence, inputs (L4)
4. **Ma'at evaluates** → emits `PolicyChecked` with pass/fail (L4)
5. **If passed:** Tool Gateway emits `ActionDispatched` + `ActionExecuted` (L4)
6. **Scribe polls** → market resolves → emits `OutcomeObserved` (L4)
7. **Eval runs** → computes calibration delta → writes `Canon/METRICS/...` (L1)
8. **Git commits** → diff shows what the agent learned (L3)
9. **Cognee ingests** → new knowledge searchable next wake-up (L2)
10. **Next heartbeat** → agent queries "have I made this mistake before?" → cycle continues

---

## Migration Path (From Here to There)

You don't build all of this at once. Priority order:

1. **Spine schema + writer** — start emitting `DecisionProposed` events today
2. **Soul split** — break SOUL.md into Constitution/Identity/Role
3. **Policy starter rules** — max position, max workers, staleness check
4. **Scribe for Polymarket** — backfill outcomes on settled markets
5. **Eval calibration** — first calibration curve from spine data
6. **Tool Gateway** — formalize what's currently implicit in Heartbeat
7. **End-to-end example** — document one complete cycle

Each step is independently useful. Each step makes the next one easier.

---

## Design Principles

1. **Think first, task second** — Resume your train of thought before grinding
2. **No tool call without decision_id** — The institutional invariant
3. **Events are immutable** — Never rewrite the spine
4. **Constitution beats identity** — Safety and evidence override personality
5. **Don't duplicate constraints** — Heartbeat ≠ Soul ≠ Policy
6. **Measure, don't claim** — If you can't show the calibration curve, don't say "learning"
7. **One agent with a good brain beats six agents with no memory** — But one agent with a good brain *and* institutional discipline beats everything

---

*"An institution is just a decision spine with a soul attached."*

---

## Appendix: Staleness as a First-Class Concern

Every input to a decision carries a `staleness_seconds` field. This is **required**, not optional.

Why: Stale data driving confident decisions is how you blow up. A 95% confidence call based on 30-minute-old market data is not a 95% confidence call — it's a guess wearing a suit.

**Rules:**
- Every `inputs[]` entry in `DecisionProposed` must include `staleness_seconds`
- Policy can reject decisions where any input exceeds a staleness threshold
- The agent must compute staleness at decision time, not at data fetch time
- If staleness cannot be determined, set to `-1` and document why

This is not bureaucracy. This is the difference between "I checked the price" and "I checked the price 47 seconds ago."
