# Task Routing Rules

How a task gets matched to a skill.

## Keyword Extraction

Keywords are stored per-skill in `skills-index.json` under `trigger_keywords`. They are extracted from the skill's `description` field (weight 3) and body text (weight 1).

Stop words are discarded: "the", "a", "an", "when", "use", "for", "this", "that", "with", "from", "your", "will", "have", "been", "can", "how", "what", "why", "who"

## Scoring Algorithm

```
score = (description_matches * 3 + body_matches * 1) / max(keyword_count, 1)
```

Boosts and penalties:
- `+0.2` if task text contains the exact skill name
- `+0.1` if task domain matches skill category
- `-0.1` if skill has a cross_reference whose trigger keywords match the task better
- Cap final score at 1.0

## Decomposition Detection

A task should be split into subtasks when:

1. **Conjunction signals**: "and", "then", "after", "also", "next", "finally" separating distinct actions
2. **Numbered lists**: "1. do X  2. do Y"
3. **Domain shifts**: "build the API AND design the landing page" (two different skill domains)
4. **Multiple artifacts**: 2+ URLs, 2+ file paths targeting different domains
5. **route-task.py returns `"decompose": true`**

Splitting rules:
- Split only at top-level conjunctions, not inside quoted strings or code blocks
- Minimum subtask length: 4 words (shorter fragments are context, not standalone tasks)
- Each subtask inherits full task context when routed

## Confidence Thresholds

| Score | Action |
|-------|--------|
| >= 0.85 | Very high — route without confirmation |
| 0.70 – 0.85 | High — route, brief confirmation |
| 0.50 – 0.70 | Moderate — route, explicit confirmation |
| 0.30 – 0.50 | Low — suggest, do not auto-execute |
| < 0.30 | No match — decompose or manual |

## Multiple Matches

When 2+ skills score within 0.15 of each other AND both >= 0.5:
1. Present both options with a one-line rationale
2. Ask user which to use
3. If user doesn't know: pick the higher-scored one, note the alternative

When scores are tied: prefer the skill with fewer cross_refs (more self-contained).
