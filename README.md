# Skills Auto-Dispatcher

Automatically detects which skills match a task, routes to them, decomposes complex work, and handles failures.

Works across Claude Code, Codex, Copilot, Gemini CLI, and any agent that can read markdown and run bash/python.

## Quick Start

```bash
# 1. Build the index
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py --force

# 2. Route a task
python3 scripts/route-task.py "create a video from https://example.com"
```

Output:
```json
{
  "matches": [
    {"skill": "website-to-hyperframes", "score": 0.85, "reason": "matched web keywords"}
  ],
  "subtasks": [],
  "decompose": false
}
```

## Install

### Claude Code

Copy or symlink into `.agents/skills/`:

```bash
git clone https://github.com/YiYiii-Zhang/skills-auto-dispatcher.git .agents/skills/skills-auto-dispatcher
```

Rebuild index with your own skills:

```bash
bash .agents/skills/skills-auto-dispatcher/scripts/scan-skills.sh \
  | python3 .agents/skills/skills-auto-dispatcher/scripts/update-skills-index.py --force
```

### Auto-trigger (one-time setup)

Add this line to your CLAUDE.md so every task is auto-routed:

```markdown
收到新任务时，先跑 `python3 .agents/skills/skills-auto-dispatcher/scripts/route-task.py "<task>"`，
有 >= 0.7 的匹配就调 Skill，没有则正常处理。
```

| Platform | Config file |
|----------|-------------|
| Claude Code | `CLAUDE.md` (项目根目录) |
| GitHub Copilot | `.github/copilot-instructions.md` |
| Codex CLI | `AGENTS.md` |

### Other Platforms (Codex, Copilot, Gemini CLI, etc.)

Same install. If the platform does not auto-discover skills, read `dispatcher.md` directly when a task arrives and follow its decision flow. The scripts run on any machine with bash + python3.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Entry point, triggers on multi-domain tasks |
| `dispatcher.md` | Full decision flow: index → analyze → match → execute → fallback |
| `task-router.md` | Matching algorithm and confidence thresholds |
| `execution-policy.md` | Failure handling, fallback chain, timeouts |
| `update-index-policy.md` | When and how to maintain skills-index.json |
| `skill-index-template.md` | Schema reference for skills-index.json |
| `examples.md` | 5 concrete usage scenarios |
| `scripts/scan-skills.sh` | Discover all SKILL.md files, output JSON |
| `scripts/update-skills-index.py` | Build/update skills-index.json from scan |
| `scripts/route-task.py` | Score a task against the index, suggest matches |
| `templates/` | Human-readable index and routing worksheet templates |

## Dependencies

- bash
- python3 (stdlib only, no pip packages)

## Maintenance

```bash
# Rebuild index (e.g., after installing new skills)
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py --force

# Run router on a test task to verify
python3 scripts/route-task.py "debug my failing test"
```
