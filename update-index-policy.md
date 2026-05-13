# Index Update Policy

## When to Update

Update `skills-index.json` when:

1. **Missing**: file does not exist (first run)
2. **Stale**: `generated` timestamp is > 24 hours old
3. **Skill added**: a new `SKILL.md` appears under any scanned path
4. **Skill removed**: a path in the index no longer exists on disk
5. **Skill changed**: SHA256 hash of a SKILL.md differs from stored hash
6. **Explicit request**: user asks to update/reload skills

## Scan Locations

```
.agents/skills/*/SKILL.md
skills/*/SKILL.md
$SKILLS_PATH (colon-separated, each entry scanned for SKILL.md)
```

## Update Process

```bash
bash scripts/scan-skills.sh | python3 scripts/update-skills-index.py
```

What happens:
1. `scan-skills.sh` walks all scan locations, extracts YAML frontmatter + computes SHA256 per SKILL.md
2. Outputs JSON array to stdout
3. `update-skills-index.py` reads the JSON, merges with existing index, writes `skills-index.json`

## Stale Entries

When a skill path no longer exists on disk:
1. First cycle: mark `"stale": true`, keep in index (allows "skill not found" fallback to fire properly)
2. Second cycle: remove from index permanently

## Manual Overrides

The index supports manual keyword additions. If `skills-index.json` has a `_overrides` key, those keywords are merged into the auto-extracted ones and preserved across rebuilds. Users can edit `_overrides` directly in the JSON:

```json
{
  "_overrides": {
    "hyperframes": {"trigger_keywords": ["video", "animation", "composition"]}
  }
}
```

## Hash Storage

Per-skill SHA256 is stored to detect changes. Only the SKILL.md's own content is hashed — not references/, scripts/, or other companion files. This avoids unnecessary index rebuilds for documentation-only changes.
