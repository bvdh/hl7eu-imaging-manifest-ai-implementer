#!/usr/bin/env bash
# check-rendered-tokens.sh
# Skill: ig-check-jeckyll-links — Step 3: rendered-output alias check
#
# Covers:
#   - build freshness: output/en/<page>.html must be newer than input/pagecontent/<page>.md
#   - absence of literal {{token}} strings leaked into rendered HTML (unresolved aliases)
#   - pages not in sushi-config pages are reported as skipped, not failed
#
# Precondition: run after a complete IG build (./_build.sh build).
# If any page is stale, the script reports it and exits non-zero without inspecting
# the rendered content for that page.
#
# Usage:
#   ./.github/skills/ig-check-jeckyll-links/check-rendered-tokens.sh [repo-root]
#
# Exit code:
#   0  all checks pass (or all token-using pages are covered by fresh output)
#   N  number of failures + stale pages

set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PAGECONTENT="$ROOT/input/pagecontent"
OUTPUT_EN="$ROOT/output/en"

echo "=== Jekyll Alias Token Check (rendered output) ==="
echo "Root: $ROOT"
echo ""

TOTAL_ISSUES=0
STALE_COUNT=0

while IFS= read -r page; do
  bname=$(basename "$page" .md)
  rendered="$OUTPUT_EN/$bname.html"

  # Only process pages that have {{token}} usages
  USED=$(grep -oP "\{\{[A-Za-z][A-Za-z0-9_]+\}\}" "$page" 2>/dev/null || true)
  [ -z "$USED" ] && continue

  # Skip pages with no rendered output (not in sushi-config pages list)
  if [ ! -f "$rendered" ]; then
    echo "  SKIP    [$bname.md]  no rendered output — page may not be declared in sushi-config pages"
    continue
  fi

  # ── Freshness check ──────────────────────────────────────────────────────────
  src_epoch=$(stat -c "%Y" "$page")
  out_epoch=$(stat -c "%Y" "$rendered")

  if [ "$src_epoch" -gt "$out_epoch" ]; then
    src_ts=$(stat -c "%y" "$page" | cut -d'.' -f1)
    out_ts=$(stat -c "%y" "$rendered" | cut -d'.' -f1)
    echo "  STALE   [$bname.md]  source $src_ts > output $out_ts — rebuild before checking"
    STALE_COUNT=$((STALE_COUNT + 1))
    TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    continue
  fi

  # ── Unresolved token check ───────────────────────────────────────────────────
  # Any literal {{token}} in the rendered HTML means the alias was not expanded
  UNRESOLVED=$(grep -oP "\{\{[A-Za-z][A-Za-z0-9_]+\}\}" "$rendered" 2>/dev/null | sort -u || true)

  if [ -n "$UNRESOLVED" ]; then
    while IFS= read -r tok; do
      [ -z "$tok" ] && continue
      echo "  FAIL    [$bname.html]  unresolved token in rendered output: $tok"
      TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
    done <<< "$UNRESOLVED"
    continue
  fi

  echo "  PASS    [$bname.html]"

done < <(find "$PAGECONTENT" -maxdepth 1 -name "*.md" | sort)

echo ""
if [ "$STALE_COUNT" -gt 0 ]; then
  echo "Stale pages : $STALE_COUNT  (run ./_build.sh build then re-run this script)"
fi
echo "Total issues: $TOTAL_ISSUES"
echo ""

if [ "$TOTAL_ISSUES" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
else
  echo "RESULT: FAIL"
  exit "$TOTAL_ISSUES"
fi
