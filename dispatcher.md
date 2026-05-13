# Dispatcher Decision Flow

The dispatcher is a chain: index → analyze → match → execute → fallback. Each step is a distinct decision gate.

## Step 1: Load Index

Read `skills-index.json`. Parse the `skills` map and the `generated` timestamp.

If file is missing: build it.
```
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py
```

If `generated` is older than 24 hours: rebuild (same command).

## Step 2: Analyze Task

Extract from the user's request:

- **Primary verb**: build, fix, deploy, capture, create, convert, translate, add, remove, install, debug, review, refactor
- **Domain nouns**: video, website, animation, caption, voice, audio, database, api, component, style, test, config, deploy, registry, block
- **Complexity signals**: "and also", "then", "after that", multiple paragraphs, numbered list, multiple URLs, multiple file paths
- **Artifacts**: URLs, file paths, code snippets, error messages

## Step 3: Match

```bash
python3 scripts/route-task.py "<full task text>"
```

Read the JSON output. For each match:
- `score >= 0.7`: strong match, proceed
- `score 0.5-0.7`: reasonable match, confirm with user if ambiguous
- `score 0.3-0.5`: weak match, treat as suggestion only
- `score < 0.3`: no match — decompose or handle manually

When 2+ skills score close (within 0.15): present the top 2 to the user, let them pick.

## Step 4: Decompose (if needed)

Decomposition is needed when:
- `route-task.py` returns `"decompose": true`
- Task contains conjunction words spanning domains
- Task has numbered/comma-separated list of distinct actions
- No single skill scores >= 0.3

How to decompose:
1. Split on natural boundaries: "and", "then", "also", line breaks, numbered items
2. For each subtask longer than 3 words: re-run route-task.py
3. Create TaskCreate items for each subtask
4. Route each subtask independently

## Step 5: Execute

**Claude Code**: `Skill` tool with the matched skill name.

**Other platforms**: Read the skill's SKILL.md path (from index) and follow instructions directly.

If the skill has `cross_refs`: load those referenced skills too. If a cross-ref is marked REQUIRED, load it before the main skill.

## Step 6: Handle Results

- **Success**: deliver output to user. If subtask chain, proceed to next.
- **Failure**: jump to [execution-policy.md](execution-policy.md). Walk the fallback chain. Do not retry the same skill+task combo.

## Quick Reference

```
TASK → index fresh? → analyze → route-task.py → score
                                                   |
                          >= 0.3 ──────────────────→ execute
                          < 0.3 ───────────────────→ "没有匹配的 skill，我直接处理"
                          empty ───────────────────→ same as < 0.3
                          decompose ───────────────→ split into subtasks

                          EXECUTE → success → deliver
                                 → failure → fallback → deliver
```
