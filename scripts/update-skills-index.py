#!/usr/bin/env python3
"""
Build or update skills-index.json from scan output.

Usage:
  bash scan-skills.sh | python3 update-skills-index.py [--force]
  python3 update-skills-index.py --help

No pip dependencies -- stdlib only.
"""

import json
import sys
import os
import re
from datetime import datetime, timezone, timedelta

STOP_WORDS = {
    "the", "a", "an", "when", "use", "for", "this", "that", "with",
    "from", "your", "will", "have", "been", "can", "how", "what",
    "why", "who", "and", "or", "not", "but", "if", "then", "else",
    "in", "on", "at", "to", "of", "by", "is", "it", "its", "be",
    "as", "are", "was", "were", "has", "had", "do", "does", "did",
    "should", "would", "could", "may", "might", "shall", "must",
    "you", "we", "he", "she", "they", "me", "us", "him", "her",
    "them", "my", "our", "his", "their", "all", "any", "each",
    "every", "both", "few", "more", "most", "other", "some",
    "such", "no", "only", "own", "same", "so", "than", "too",
    "very", "just", "about", "also", "into", "over", "after",
    "before", "between", "under", "again", "further", "once",
    "here", "there", "which", "these", "those",
}

CATEGORY_KEYWORDS = {
    "video": ["video", "composition", "scene", "transition", "render",
              "caption", "subtitle", "voiceover", "audio", "tts", "transcribe",
              "overlay", "narration", "footage", "clip"],
    "animation": ["animation", "anime", "gsap", "lottie", "css-animation",
                  "waapi", "keyframe", "timeline", "easing", "motion", "tween"],
    "web": ["website", "url", "capture", "screenshot", "page", "browser",
            "fetch", "html", "css", "dom", "http"],
    "dev": ["build", "deploy", "test", "debug", "review", "refactor",
            "commit", "branch", "merge", "code", "api", "function"],
    "data": ["database", "sql", "query", "schema", "migrate", "data"],
    "config": ["config", "settings", "install", "uninstall", "permission",
               "hook", "env", "environment"],
}


def extract_keywords(text):
    """Extract meaningful keywords from description text."""
    text = text.lower()
    tokens = re.findall(r'[a-z0-9_-]+', text)
    tokens = [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]
    return list(dict.fromkeys(tokens))


def detect_category(keywords):
    """Detect category by keyword overlap."""
    scores = {}
    kwset = set(keywords)
    for cat, ckw in CATEGORY_KEYWORDS.items():
        hits = len(kwset & set(ckw))
        if hits > 0:
            scores[cat] = hits
    if scores:
        return max(scores, key=scores.get)
    return "general"


def detect_cross_refs(description):
    """Detect cross-references to other skills."""
    refs = []
    patterns = [
        r'see the (\S+) skill',
        r'use (\S+) instead',
        r'requires (\S+)',
        r'load the (\S+) skill',
        r'references?:?\s*(\S+)',
        r'related:?\s*(\S+)',
    ]
    for pat in patterns:
        for m in re.findall(pat, description, re.IGNORECASE):
            name = m.strip().rstrip('.')
            if name not in refs and len(name) > 1:
                refs.append(name)
    return refs


def detect_platforms(description):
    """Detect if skill is Claude-specific or portable."""
    claude_tools = ["Skill", "TaskCreate", "TaskUpdate", "TodoWrite",
                    "Bash", "Write", "Edit", "Read", "Glob", "Grep"]
    if any(tool in description for tool in claude_tools):
        return ["claude-code"]
    return ["any"]


def build_index(skills_data, existing_index=None):
    """Build the full index from scan data."""
    existing_skills = {}
    overrides = {}
    if existing_index:
        existing_skills = existing_index.get("skills", {})
        overrides = existing_index.get("_overrides", {})

    skills = {}
    for entry in skills_data:
        name = entry["name"]
        desc = entry.get("description", "")
        keywords = extract_keywords(desc)

        # Apply manual overrides if present
        if name in overrides:
            ov = overrides[name]
            if "trigger_keywords" in ov:
                keywords = ov["trigger_keywords"]

        prev = existing_skills.get(name, {})

        skills[name] = {
            "name": name,
            "path": entry["path"],
            "description": desc[:200],
            "trigger_keywords": keywords,
            "category": detect_category(keywords),
            "cross_refs": detect_cross_refs(desc),
            "platforms": detect_platforms(desc),
            "hash": entry.get("hash", ""),
            "stale": False,
        }

    # Mark removed skills as stale
    if existing_skills:
        for name, data in existing_skills.items():
            if name not in skills and data.get("stale"):
                # Was stale last cycle -- remove it now
                pass
            elif name not in skills:
                # First time missing -- mark stale
                data["stale"] = True
                skills[name] = data

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "scan_paths": [".agents/skills", "skills"],
        "total_skills": len([s for s in skills.values() if not s.get("stale")]),
        "_overrides": overrides,
        "skills": skills,
    }


def main():
    force = "--force" in sys.argv
    output_path = os.path.join(os.path.dirname(__file__), "..", "skills-index.json")

    # Check if update is needed
    if not force and os.path.exists(output_path):
        try:
            with open(output_path) as f:
                existing = json.load(f)
            gen_time = datetime.fromisoformat(existing["generated"])
            age = datetime.now(timezone.utc) - gen_time
            if age < timedelta(hours=24):
                print(f"Index is {age.total_seconds()/3600:.1f}h old, skipping (use --force to override)", file=sys.stderr)
                return 0
        except (json.JSONDecodeError, KeyError, ValueError):
            pass  # Corrupt index, rebuild

    # Read scan data from stdin
    try:
        scan_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON from scan: {e}", file=sys.stderr)
        return 1

    # Load existing index for merging
    existing = None
    if os.path.exists(output_path):
        try:
            with open(output_path) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    index = build_index(scan_data, existing)

    with open(output_path, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    active = sum(1 for s in index["skills"].values() if not s.get("stale"))
    stale = sum(1 for s in index["skills"].values() if s.get("stale"))
    print(f"Index written: {active} active, {stale} stale", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
