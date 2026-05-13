# Usage Examples

## Example 1: Simple Single-Skill Match

**User input**: "Create a 30-second product video from https://example.com"

**Dispatcher reasoning**:
- Tokens: create, 30-second, product, video, https, example.com
- route-task.py output: `website-to-hyperframes` (score: 0.85), `hyperframes` (score: 0.62)
- URL present + video keyword → website-to-hyperframes is the clear winner
- Confidence >= 0.7 → auto-route

**Action**: Invoke `website-to-hyperframes` skill.

---

## Example 2: Multi-Skill Decomposition

**User input**: "Capture my competitor's landing page and write me a competitive analysis"

**Dispatcher reasoning**:
- Tokens: capture, competitor, landing, page, write, competitive, analysis
- "and" detected → decomposition triggered
- Subtask 1: "Capture my competitor's landing page" → website-to-hyperframes (score: 0.72)
- Subtask 2: "write me a competitive analysis" → no matching skill (all scores < 0.3)
- Decomposition confirmed → route subtask 1, handle subtask 2 manually

**Action**: Create 2 TaskCreate items. Route subtask 1 to skill. Handle subtask 2 directly.

---

## Example 3: No Match

**User input**: "Optimize my PostgreSQL slow queries"

**Dispatcher reasoning**:
- Tokens: optimize, postgresql, slow, queries
- All skills score < 0.3
- No decomposition signals (no "and", "then", numbered items)
- No match → handle manually

**Action**: Tell user no matching skill exists. Handle directly.

---

## Example 4: Index Not Found (First Run)

**User input**: "Add captions to this video"

**Dispatcher reasoning**:
- `skills-index.json` missing → rebuild index
- Run `scan-skills.sh | update-skills-index.py`
- Index rebuilt with 15 skills found
- Re-run route-task.py: `hyperframes` (score: 0.78)
- Route to skill

**Action**: Silent index rebuild → route to hyperframes.

---

## Example 5: Skill Failure with Fallback

**User input**: "Make a video with animated text"

**Dispatcher reasoning**:
- route-task.py: `hyperframes` (score: 0.82), `css-animations` (score: 0.61)
- Invoke `hyperframes` → skill fails (missing dependency)
- Fallback 1: retry same skill after verifying path exists → still fails
- Fallback 2: next-best match `css-animations` (score: 0.61, diff 0.21 from primary)
  - Diff < 0.3 → qualifies as fallback
- Invoke `css-animations`

**Action**: Walk fallback chain. Report each step to user.
