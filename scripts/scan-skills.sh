#!/usr/bin/env bash
set -euo pipefail

SEARCH_PATHS=()
if [ $# -gt 0 ]; then
    SEARCH_PATHS=("${@}")
else
    [ -d ".agents/skills" ] && SEARCH_PATHS+=(".agents/skills")
    [ -d "skills" ] && SEARCH_PATHS+=("skills")
    if [ -n "${SKILLS_PATH:-}" ]; then
        IFS=':' read -ra EXTRA <<< "$SKILLS_PATH"
        SEARCH_PATHS+=("${EXTRA[@]}")
    fi
fi

escape_json() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\t/\\t/g; s/\r/\\r/g'
}

first=true
printf '['

for search_path in "${SEARCH_PATHS[@]}"; do
    [ -d "$search_path" ] || continue
    while IFS= read -r skill_md; do
        [ -z "$skill_md" ] && continue
        skill_dir=$(dirname "$skill_md")
        skill_name=$(basename "$skill_dir")

        frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | sed '1d;$d' || true)

        desc=$(echo "$frontmatter" | grep -m1 '^description:' | sed 's/^description:[[:space:]]*//' || echo "")
        # Treat YAML block scalar indicators as empty → trigger fallback
        [ "$desc" = "|" ] && desc=""
        [ "$desc" = ">" ] && desc=""
        if [ -z "$desc" ]; then
            # Capture indented continuation lines after "description: |" or "description: >"
            desc=$(echo "$frontmatter" | awk '
                /^description:/{flag=1; next}
                flag {
                    if ($0 ~ /^[a-zA-Z_-]+:/) exit
                    gsub(/^[[:space:]]+/, "")
                    printf "%s ", $0
                }
            ' | sed 's/[[:space:]]*$//')
        fi
        [ -z "$desc" ] && desc="$skill_name"

        hash=$(shasum -a 256 "$skill_md" 2>/dev/null | cut -d' ' -f1)

        [ "$first" != "true" ] && printf ','
        first=false

        esc_name=$(escape_json "$skill_name")
        esc_path=$(escape_json "$skill_md")
        esc_desc=$(escape_json "$desc")
        printf '{"name":"%s","path":"%s","description":"%s","hash":"%s"}' \
            "$esc_name" "$esc_path" "$esc_desc" "$hash"
    done < <(find "$search_path" -maxdepth 2 -name 'SKILL.md' -print 2>/dev/null || true)
done

printf ']\n'
