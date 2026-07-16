#!/usr/bin/env bash
# check-pack.sh — pack self-check. Run from anywhere; it cd's to the pack root.
#
# Checks:
#   1. no leftover {{placeholders}} in examples/ (the literal "{{…}}" prose mention is allowed)
#   2. no dangling governing-doc names (PRODUCT.md / TASKS.md / DECISIONS.md) outside the
#      one allowed mention in reference/behavioral-guidelines.md
#   3. every relative markdown link target exists
#   4. skills-library/ folders and the README index stay in sync (both directions)
#
# Optional pre-commit hook — install it yourself (never auto-installed; same consent rule
# as trigger arming):
#   cp scripts/check-pack.sh .git/hooks/pre-commit

set -u
cd "$(dirname "$0")/.." || exit 1
fail=0
note() { printf 'FAIL: %s\n' "$1"; fail=1; }

# 1 — placeholder scan (examples only; templates/ and reference/ legitimately contain {{…}})
hits=$(grep -rn '{{' examples/ 2>/dev/null | grep -v '{{…}}')
if [ -n "$hits" ]; then printf '%s\n' "$hits"; note 'leftover {{placeholder}} in examples/'; fi

# 2 — dangling governing-doc names
hits=$(grep -rnE 'PRODUCT\.md|TASKS\.md|DECISIONS\.md' --include='*.md' --exclude-dir=.git . \
       | grep -v '^\./reference/behavioral-guidelines\.md:')
if [ -n "$hits" ]; then printf '%s\n' "$hits"; note 'governing-doc name outside the allowed baseline header'; fi

# 3 — relative markdown link targets exist
while IFS='|' read -r file target; do
  case "$target" in
    http://*|https://*|mailto:*) continue ;;
  esac
  [ "${target#\#}" = "$target" ] || continue   # anchor-only link
  target="${target%%#*}"
  [ -z "$target" ] && continue
  dir=$(dirname "$file")
  [ -e "$dir/$target" ] || note "broken link: $file -> $target"
done < <(grep -rnoE --include='*.md' --exclude-dir=.git '\]\([^)]+\)' . \
         | sed -E 's/^([^:]+):[0-9]+:\]\((.+)\)$/\1|\2/')

# 4 — skills-library index sync
for d in skills-library/*/; do
  name=$(basename "$d")
  grep -q "(${name}/SKILL.md)" skills-library/README.md \
    || note "skills-library/${name} has no row in skills-library/README.md"
done
while read -r name; do
  [ -d "skills-library/${name}" ] || note "index row '${name}' has no skills-library folder"
done < <(grep -oE '\]\([a-z0-9-]+/SKILL\.md\)' skills-library/README.md | sed -E 's/^\]\(([^/]+).*/\1/')

if [ "$fail" -eq 0 ]; then
  echo 'check-pack: all checks passed'
else
  exit 1
fi
