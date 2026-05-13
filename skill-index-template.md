# Skills Index Schema

`skills-index.json` is the machine-readable skills registry. Generated automatically, read by both scripts and models.

## File: `skills-index.json`

```json
{
  "generated": "2026-05-13T10:00:00+08:00",
  "scan_paths": [
    ".agents/skills",
    "skills"
  ],
  "total_skills": 15,
  "_overrides": {},
  "skills": {
    "hyperframes": {
      "name": "hyperframes",
      "path": ".agents/skills/hyperframes/SKILL.md",
      "description": "Create video compositions, animations, title cards...",
      "trigger_keywords": ["video", "composition", "animation", "caption", "subtitle", "voiceover", "scene", "transition"],
      "category": "video",
      "cross_refs": ["hyperframes-cli", "hyperframes-media", "waapi", "animejs"],
      "platforms": ["claude-code"],
      "hash": "abc123def456",
      "stale": false
    }
  }
}
```

## Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Skill identifier (directory name) |
| `path` | string | Relative path to SKILL.md |
| `description` | string | First 200 chars from the YAML description |
| `trigger_keywords` | [string] | Keywords that signal this skill should fire |
| `category` | string | `video` \| `animation` \| `web` \| `dev` \| `data` \| `config` \| `general` |
| `cross_refs` | [string] | Other skill names referenced by this skill |
| `platforms` | [string] | `["claude-code"]` or `["any"]` |
| `hash` | string | SHA256 of SKILL.md content |
| `stale` | bool | Path no longer exists on disk |

## Category Detection Rules

Categories are derived from keyword overlap:

| Keywords | Category |
|----------|----------|
| video, composition, scene, transition, render, caption, subtitle, voiceover, audio, tts, transcribe | `video` |
| animation, anime, gsap, lottie, css-animation, waapi, keyframe | `animation` |
| website, url, capture, screenshot, page, browser, fetch | `web` |
| build, deploy, test, debug, review, refactor, commit, branch, merge | `dev` |
| database, sql, query, schema, migrate, data | `data` |
| config, settings, install, uninstall, permission, hook | `config` |
| (none of the above) | `general` |

## Cross-Reference Detection

Detected from the skill's description and body:
- "see the X skill" → cross_ref: X
- "use X instead" → cross_ref: X
- "requires X" → cross_ref: X (marked as required)
- "related: X" → cross_ref: X

## Platform Detection

- `["claude-code"]`: SKILL.md references Claude-specific tools (Skill, TaskCreate, TaskUpdate, Bash, Write, Edit, Read)
- `["any"]`: pure markdown instructions or uses only bash/python scripts
