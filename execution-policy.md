# Execution Policy

## Invocation

**Claude Code**: Use the `Skill` tool with the matched skill name.
**Other platforms**: Read the skill's SKILL.md path (from `skills-index.json` → `path` field) and follow instructions using the platform's native tools.

## Pre-execution Checks

Before invoking a skill:
1. Verify the skill path exists on disk (stale index guard).
2. If the index says `platforms: ["claude-code"]` and you are on a different platform: read the skill directly, adapt tool-specific instructions.

## Failure Handling

### Failure Detection

A skill invocation has failed when:
- Skill tool returns an error
- Skill's SKILL.md cannot be read (file missing)
- Skill execution produces no output within 5 minutes
- Skill execution produces output that indicates failure (crash, error message)
- Skill's instructions cannot be followed (missing dependency, platform mismatch)

### Fallback Chain

Walk in order:

1. **Tell user what failed**: which skill, why (invocation error / wrong match). One sentence.
2. **Check next-best match** from route-task.py output:
   - Score >= 0.3: "下一个是 (skill, score X)，要试吗?"
   - Score < 0.3 or no more candidates: "没有更好的候选了，我手动处理"
3. **User says yes** → try next match. If that also fails, repeat from step 1.
4. **User says no** or exhausted → handle the task without any skill.

Don't re-run route-task.py during fallback — reuse the original result.

### Rules

- Never retry the same skill on the same task.
- Never silently retry — always tell user what happened.
- Track failed skills per session to avoid cycles.

## Timeouts

- Skill invocation: 5 minutes without output → report to user, proceed to fallback
- Index rebuild: 30 seconds → use stale index if available, warn user
- route-task.py: 10 seconds → fall back to manual keyword matching

## Safety

- Do not auto-execute skills marked `"category": "destructive"` without user confirmation, regardless of confidence score.
- If a skill failure could leave the system in a broken state: pause and ask user before proceeding.
