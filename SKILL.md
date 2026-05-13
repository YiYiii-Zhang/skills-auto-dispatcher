---
name: skills-auto-dispatcher
argument-hint: <task description>
allowed-tools: [Bash, Read, Skill]
description: >
  Use when: (1) the user gives a task that spans multiple domains or tools,
  (2) you are unsure which skill matches a task, (3) a skill invocation failed
  and you need a fallback, (4) the user asks what skills are available,
  (5) new skills may have been installed and the index is stale.
  Also available as explicit slash command: /route <task>
---

# Skills Auto-Dispatcher

Usage: `/route <task description>` or auto-triggered by description match.

## 1. Ensure Index

```bash
bash .agents/skills/skills-auto-dispatcher/scripts/scan-skills.sh | python3 .agents/skills/skills-auto-dispatcher/scripts/update-skills-index.py
```

Run if `skills-index.json` is missing or older than 24h.

## 2. Score Task

```bash
python3 .agents/skills/skills-auto-dispatcher/scripts/route-task.py "$ARGUMENTS"
```

## 3. Route

| Score | Action |
|-------|--------|
| >= 0.7 | `Skill` tool |
| 0.5 – 0.7 | `Skill` tool, confirm with user |
| 0.3 – 0.5 | Suggest, don't auto-execute |
| < 0.3 or decompose | Split into subtasks, re-score each |

## 4. Fallback

On failure: next-best match → read SKILL.md directly → handle manually → ask user.

Full details: [dispatcher.md](dispatcher.md), [execution-policy.md](execution-policy.md).
