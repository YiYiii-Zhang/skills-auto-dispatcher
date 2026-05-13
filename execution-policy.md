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

Walk in order, stop at first success:

1. **Retry same skill once**: reload index first (guard against stale path)
2. **Next-best match**: from route-task.py output, pick the match with the next highest score (must be >= 0.3, and score diff from primary < 0.3)
3. **Direct read**: read the target SKILL.md directly and follow instructions without the Skill tool
4. **Generic approach**: handle the task without any skill, using general reasoning
5. **Ask user**: report what failed and what alternatives exist

### Rules

- Never retry the same skill+task combination more than once.
- Never silently retry — tell the user which fallback step you are on.
- If a fallback skill also fails, continue down the chain.
- Track failed skills per session to avoid cycles.

## Timeouts

- Skill invocation: 5 minutes without output → report to user, proceed to fallback
- Index rebuild: 30 seconds → use stale index if available, warn user
- route-task.py: 10 seconds → fall back to manual keyword matching

## Safety

- Do not auto-execute skills marked `"category": "destructive"` without user confirmation, regardless of confidence score.
- If a skill failure could leave the system in a broken state: pause and ask user before proceeding.
