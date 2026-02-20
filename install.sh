#!/usr/bin/env bash
#
# 🧠 Mapping the Brain — Quick Install
# 
# Sets up the multi-layer persistent memory architecture for AI agents:
#   L1: Obsidian vault (conscious thinking)
#   L2: Cognee semantic memory (subconscious recall)  
#   L3: Git version history (long-term memory)
#   L4: Decision Spine (operational memory)
#
# Requirements: git, python 3.10+, pip
# Optional: Obsidian (for L1 vault editing)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Chipp11/mapping-the-brain/main/install.sh | bash
#
#   Or clone and run:
#   git clone https://github.com/Chipp11/mapping-the-brain.git
#   cd mapping-the-brain && bash install.sh
#
# ─────────────────────────────────────────────────────────

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${BLUE}[info]${NC}  $*"; }
ok()    { echo -e "${GREEN}[  ok]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
fail()  { echo -e "${RED}[fail]${NC}  $*"; exit 1; }

# ─── Preflight checks ───

echo ""
echo "🧠 Mapping the Brain — Installer"
echo "─────────────────────────────────"
echo ""

command -v git    >/dev/null 2>&1 || fail "git is required. Install it first."
command -v python3 >/dev/null 2>&1 || fail "python3 is required (3.10+). Install it first."

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  fail "Python 3.10+ required (found $PY_VERSION)"
fi
ok "Python $PY_VERSION"

# ─── Clone or update repo ───

BRAIN_DIR="${BRAIN_DIR:-$HOME/mapping-the-brain}"

if [ -d "$BRAIN_DIR/.git" ]; then
  info "Updating existing install at $BRAIN_DIR"
  cd "$BRAIN_DIR" && git pull --ff-only 2>/dev/null || warn "Git pull failed — continuing with existing version"
else
  info "Cloning to $BRAIN_DIR"
  git clone https://github.com/Chipp11/mapping-the-brain.git "$BRAIN_DIR"
fi

cd "$BRAIN_DIR"
ok "Repository ready"

# ─── Create vault structure (L1 — Obsidian) ───

VAULT_DIR="${VAULT_DIR:-$BRAIN_DIR/vault}"

info "Setting up Obsidian vault at $VAULT_DIR"

mkdir -p "$VAULT_DIR"/{Canon/{DECISIONS,EVIDENCE,METRICS,THINKING},memory,spine/events}

# Create starter files if they don't exist
if [ ! -f "$VAULT_DIR/SOUL.md" ]; then
  cp soul/SOUL.md "$VAULT_DIR/SOUL.md" 2>/dev/null || cat > "$VAULT_DIR/SOUL.md" << 'SOUL'
# SOUL.md — Who I Am

Define your agent's identity here:
- **Name:** (your agent's name)
- **Nature:** (what kind of creature is it?)
- **Vibe:** (formal? sarcastic? warm? direct?)
- **Emoji:** (signature emoji)

## How I Operate
- (add your principles)

## What I'm Not
- (add your boundaries)
SOUL
fi

if [ ! -f "$VAULT_DIR/AGENTS.md" ]; then
  cp examples/AGENTS.md "$VAULT_DIR/AGENTS.md" 2>/dev/null || cat > "$VAULT_DIR/AGENTS.md" << 'AGENTS'
# AGENTS.md — Workspace Instructions

## Every Session
1. Read `SOUL.md` — this is who you are
2. Read `memory/` — recent context
3. Read `MEMORY.md` — long-term memory

## Memory
- **Daily notes:** `memory/YYYY-MM-DD.md`
- **Long-term:** `MEMORY.md`
- Write things down. "Mental notes" don't survive restarts.
AGENTS
fi

if [ ! -f "$VAULT_DIR/MEMORY.md" ]; then
  cat > "$VAULT_DIR/MEMORY.md" << 'MEM'
# MEMORY.md — Long-Term Memory

(Your agent's curated memories will accumulate here over time.)
MEM
fi

if [ ! -f "$VAULT_DIR/HEARTBEAT.md" ]; then
  cp heartbeat/HEARTBEAT.md "$VAULT_DIR/HEARTBEAT.md" 2>/dev/null || cat > "$VAULT_DIR/HEARTBEAT.md" << 'HB'
# HEARTBEAT.md — Periodic Wake-Up

When you receive a heartbeat:
1. Check what's changed since last wake-up
2. Review any pending tasks
3. Update memory if needed
4. Reply HEARTBEAT_OK if nothing needs attention
HB
fi

ok "Vault structure created"

# ─── Set up Python environment (L2 — Cognee) ───

info "Setting up Python environment for Cognee..."

VENV_DIR="$BRAIN_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Install cognee
pip install --quiet --upgrade pip
pip install --quiet cognee 2>/dev/null && ok "Cognee installed" || {
  warn "Cognee install failed — trying with relaxed deps"
  pip install --quiet cognee --no-deps 2>/dev/null && ok "Cognee installed (no-deps)" || warn "Cognee install failed. You can install it manually later: pip install cognee"
}

# Install sentence-transformers for local embeddings (Brain Index future)
pip install --quiet sentence-transformers 2>/dev/null && ok "Sentence-transformers installed" || warn "sentence-transformers install skipped"

deactivate

# ─── Set up Decision Spine (L4) ───

info "Setting up Decision Spine..."

mkdir -p "$VAULT_DIR/spine/events"

if [ ! -f "$VAULT_DIR/spine/events/spine.jsonl" ]; then
  touch "$VAULT_DIR/spine/events/spine.jsonl"
fi

ok "Spine ready at $VAULT_DIR/spine/events/spine.jsonl"

# ─── Initialize Git (L3) ───

info "Initializing Git for version history..."

cd "$VAULT_DIR"

if [ ! -d .git ]; then
  git init -q
  cat > .gitignore << 'GI'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.trash/
*.tmp
__pycache__/
.venv/
GI
  git add -A
  git commit -q -m "🧠 Brain initialized" 2>/dev/null || true
fi

ok "Git history active"

# ─── Create convenience scripts ───

info "Creating helper scripts..."

# Search script
cat > "$BRAIN_DIR/search.sh" << 'SEARCH'
#!/usr/bin/env bash
# Search your brain — semantic + lexical
# Usage: ./search.sh "your query" [top_k]

QUERY="${1:?Usage: ./search.sh \"query\" [top_k]}"
TOP_K="${2:-5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$SCRIPT_DIR/.venv/bin/activate" 2>/dev/null

python3 - "$QUERY" "$TOP_K" << 'PY'
import sys, asyncio

async def search():
    try:
        import cognee
        results = await cognee.search(sys.argv[1])
        for i, r in enumerate(results[:int(sys.argv[2])]):
            text = r.get('text', str(r)) if isinstance(r, dict) else str(r)
            print(f"\n--- Result {i+1} ---")
            print(text[:500])
    except ImportError:
        print("Cognee not installed. Run: pip install cognee")
    except Exception as e:
        print(f"Search failed: {e}")

asyncio.run(search())
PY
SEARCH
chmod +x "$BRAIN_DIR/search.sh"

# Ingest script
cat > "$BRAIN_DIR/ingest.sh" << 'INGEST'
#!/usr/bin/env bash
# Ingest vault files into Cognee semantic memory
# Usage: ./ingest.sh [path]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT="${1:-$SCRIPT_DIR/vault}"

source "$SCRIPT_DIR/.venv/bin/activate" 2>/dev/null

python3 - "$VAULT" << 'PY'
import sys, os, asyncio

async def ingest():
    try:
        import cognee
        vault = sys.argv[1]
        
        files = []
        for root, dirs, fnames in os.walk(vault):
            for f in fnames:
                if f.endswith('.md'):
                    files.append(os.path.join(root, f))
        
        if not files:
            print(f"No .md files found in {vault}")
            return
        
        print(f"Found {len(files)} markdown files")
        
        for f in files:
            await cognee.add(f)
            print(f"  + {os.path.relpath(f, vault)}")
        
        print("\nRunning cognify (this may take a minute)...")
        await cognee.cognify()
        print("✓ Ingestion complete")
        
    except ImportError:
        print("Cognee not installed. Run: pip install cognee")
    except Exception as e:
        print(f"Ingestion failed: {e}")

asyncio.run(ingest())
PY
INGEST
chmod +x "$BRAIN_DIR/ingest.sh"

# Spine writer
cat > "$BRAIN_DIR/log-decision.sh" << 'SPINE'
#!/usr/bin/env bash
# Log a decision to the spine
# Usage: ./log-decision.sh "strategy" "hypothesis" "confidence"

STRATEGY="${1:?Usage: ./log-decision.sh strategy hypothesis confidence}"
HYPOTHESIS="${2:-no hypothesis}"
CONFIDENCE="${3:-0.5}"
SPINE_FILE="$(cd "$(dirname "$0")" && pwd)/vault/spine/events/spine.jsonl"

DECISION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "{\"event\":\"DecisionProposed\",\"decision_id\":\"$DECISION_ID\",\"strategy\":\"$STRATEGY\",\"hypothesis\":\"$HYPOTHESIS\",\"confidence\":$CONFIDENCE,\"timestamp\":\"$TIMESTAMP\"}" >> "$SPINE_FILE"

echo "✓ Decision logged: $DECISION_ID"
echo "  Strategy: $STRATEGY"
echo "  Hypothesis: $HYPOTHESIS"
echo "  Confidence: $CONFIDENCE"
SPINE
chmod +x "$BRAIN_DIR/log-decision.sh"

ok "Helper scripts created"

# ─── Summary ───

echo ""
echo "─────────────────────────────────"
echo -e "${GREEN}🧠 Brain setup complete!${NC}"
echo "─────────────────────────────────"
echo ""
echo "  📁 Repo:      $BRAIN_DIR"
echo "  📓 Vault:     $VAULT_DIR"
echo "  🐍 Python:    $VENV_DIR"
echo "  📜 Spine:     $VAULT_DIR/spine/events/spine.jsonl"
echo ""
echo "  Quick start:"
echo "    1. Open $VAULT_DIR in Obsidian"
echo "    2. Edit SOUL.md to define your agent"
echo "    3. Run ./ingest.sh to index your vault"
echo "    4. Run ./search.sh \"query\" to search"
echo "    5. Run ./log-decision.sh \"strategy\" \"hypothesis\" 0.7"
echo ""
echo "  Git (L3 memory):"
echo "    cd $VAULT_DIR && git log --oneline"
echo ""
echo "  Docs: https://github.com/Chipp11/mapping-the-brain"
echo ""
