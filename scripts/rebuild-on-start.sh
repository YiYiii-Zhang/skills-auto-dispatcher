#!/usr/bin/env bash
# SessionStart hook: rebuild skills index to catch new/removed skills.
# The scan is fast (<1s for ~60 skills), so we just run it every session.
# No pip dependencies, no network calls — deterministic and safe.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

bash "$SCRIPT_DIR/scan-skills.sh" | python3 "$SCRIPT_DIR/update-skills-index.py"
