## Task Routing Decision

**Task**: {{task_description}}
**Task tokens**: {{task_tokens}}
**Complexity**: {{complexity_level}}
**Decomposition needed**: {{decompose_flag}}

### Top Matches

| Skill | Score | Rationale |
|-------|-------|-----------|
{{#matches}}
| {{name}} | {{score}} | {{reason}} |
{{/matches}}

### Subtasks

{{#subtasks}}
1. **{{text}}** → Skill: `{{suggested_skill}}` (confidence: {{score}})
{{/subtasks}}

### Execution Plan

1. Invoke `{{primary_skill}}` for primary task
2. {{#has_subtasks}}{{subtask_steps}}{{/has_subtasks}}

### Fallback

If `{{primary_skill}}` fails: {{fallback_skill}} (score: {{fallback_score}}).
If no fallback skill qualifies: {{manual_action}}.
