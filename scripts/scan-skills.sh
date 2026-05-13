#!/usr/bin/env bash
set -euo pipefail

find_project_root() {
    local dir
    dir=$(pwd)
    while [ "$dir" != "/" ]; do
        for d in ".claude/skills" ".agents/skills" ".github/skills" ".git"; do
            if [ -d "$dir/$d" ]; then
                echo "$dir"
                return 0
            fi
        done
        dir=$(dirname "$dir")
    done
    pwd
}

PROJECT_ROOT=$(find_project_root)

escape_json() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\n/\\n/g; s/\t/\\t/g; s/\r/\\r/g'
}

# Build list of (path, maxdepth) pairs. Plugins first — highest priority for new users.
declare -a SCAN_SPECS=()

if [ $# -gt 0 ]; then
    for p in "${@}"; do
        SCAN_SPECS+=("$p|2")
    done
else
    # Plugin marketplace — where most users install their first skills
    [ -d "$HOME/.claude/plugins" ] && SCAN_SPECS+=("$HOME/.claude/plugins|10")
    [ -d "$PROJECT_ROOT/.claude/plugins" ] && SCAN_SPECS+=("$PROJECT_ROOT/.claude/plugins|10")

    # Local project skills
    [ -d "$PROJECT_ROOT/.claude/skills" ] && SCAN_SPECS+=("$PROJECT_ROOT/.claude/skills|2")
    [ -d "$PROJECT_ROOT/.agents/skills" ] && SCAN_SPECS+=("$PROJECT_ROOT/.agents/skills|2")
    [ -d "$PROJECT_ROOT/.github/skills" ] && SCAN_SPECS+=("$PROJECT_ROOT/.github/skills|2")
    [ -d "$PROJECT_ROOT/skills" ] && SCAN_SPECS+=("$PROJECT_ROOT/skills|2")

    if [ -n "${SKILLS_PATH:-}" ]; then
        IFS=':' read -ra EXTRA <<< "$SKILLS_PATH"
        for p in "${EXTRA[@]}"; do
            SCAN_SPECS+=("$p|2")
        done
    fi
fi

first=true
printf '['

for spec in "${SCAN_SPECS[@]}"; do
    search_path="${spec%%|*}"
    maxdepth="${spec##*|}"

    [ -d "$search_path" ] || continue

    while IFS= read -r skill_md; do
        [ -z "$skill_md" ] && continue
        skill_dir=$(dirname "$skill_md")
        skill_name=$(basename "$skill_dir")

        frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | sed '1d;$d' || true)

        fm_name=$(echo "$frontmatter" | grep -m1 '^name:' | sed 's/^name:[[:space:]]*//; s/^"//; s/"$//; s/^'\''//; s/'\''$//' || echo "")
        [ -n "$fm_name" ] && skill_name="$fm_name"

        desc=$(echo "$frontmatter" | grep -m1 '^description:' | sed 's/^description:[[:space:]]*//' || echo "")
        [ "$desc" = "|" ] && desc=""
        [ "$desc" = ">" ] && desc=""
        [ "$desc" = '""' ] && desc=""
        [ "$desc" = "''" ] && desc=""
        if [ -z "$desc" ]; then
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
    done < <(find -L "$search_path" -maxdepth "$maxdepth" -name 'SKILL.md' -print 2>/dev/null || true)
done

printf ']\n'
