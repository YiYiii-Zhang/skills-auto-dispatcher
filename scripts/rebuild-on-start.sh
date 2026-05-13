#!/usr/bin/env bash
# SessionStart hook: detect new/missing skills and rebuild index if needed.
# Only rebuilds when there's actual change — no-op otherwise.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(dirname "$SCRIPT_DIR")/.."
INDEX_FILE="$SKILLS_DIR/skills-index.json"

if [ ! -f "$INDEX_FILE" ]; then
  echo "[dispatcher] skills-index.json missing, building..."
  bash "$SCRIPT_DIR/scan-skills.sh" | python3 "$SCRIPT_DIR/update-skills-index.py"
  exit 0
fi

# Count SKILL.md files on disk
on_disk=$(find "$SKILLS_DIR" -maxdepth 2 -name "SKILL.md" -not -path "*/templates/*" | wc -l | tr -d ' ')

# Count skills in index
in_index=$(python3 -c "
import json
try:
    with open('$INDEX_FILE') as f:
        idx = json.load(f)
    skills = idx.get('skills', {})
    active = sum(1 for s in skills.values() if not s.get('stale'))
    print(active)
except: print(0)
")

if [ "$on_disk" -ne "$in_index" ]; then
  echo "[dispatcher] skills changed: $in_index indexed vs $on_disk on disk — rebuilding..."
  bash "$SCRIPT_DIR/scan-skills.sh" | python3 "$SCRIPT_DIR/update-skills-index.py"
else
  echo "[dispatcher] index up to date ($in_index skills)"
fi
