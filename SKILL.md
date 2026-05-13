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

Always run before routing to catch stale/removed skills.

## 2. Score Task

```bash
python3 .agents/skills/skills-auto-dispatcher/scripts/route-task.py "$ARGUMENTS"
```

## 3. Route

| Score | Action |
|-------|--------|
| >= 0.3 | `Skill` tool (auto-execute, user can interrupt if wrong) |
| < 0.3 | No match — tell user "没有匹配的 skill，我直接处理" |
| tie    | Two skills same score — tell user, let them pick |
| decompose | Split into subtasks, route each independently |
| empty   | No matches at all — tell user, proceed with general reasoning |

## 4. Unmapped Words

If route-task.py returns `unmapped_words`, these are Chinese words in the task that have no English mapping. Tell the user and offer to add them:

> "这些词没有映射: 部署前。要不要加到自定义词库里？"

If user says yes, edit `custom-cn-mappings.json` to add the missing mappings.

## 5. Fallback

On failure: next-best match → read SKILL.md directly → handle manually → ask user.

Full details: [dispatcher.md](dispatcher.md), [execution-policy.md](execution-policy.md).
