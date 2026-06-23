#!/usr/bin/env bash
# check-alias-tokens.sh
# Skill: ig-check-jeckyll-links — Step 1 & 2: source-level alias check
#
# Covers:
#   - every {{token}} used in input/pagecontent/*.md
#   - whether each token is defined in the includes alias chain
#   - whether pages that use tokens include variable-definitions.md
#   - whether any triple-brace {{{token}}} (malformed) forms exist
#
# Usage:
#   ./.github/skills/ig-check-jeckyll-links/check-alias-tokens.sh [repo-root]
#
# Exit code:
#   0  all checks pass
#   N  number of defects found

set -euo pipefail

ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PAGECONTENT="$ROOT/input/pagecontent"
INCLUDES="$ROOT/input/includes"
VAR_DEF="$INCLUDES/variable-definitions.md"
FHIR_RES="$INCLUDES/fhir-resources.md"

echo "=== Jekyll Alias Token Check (source) ==="
echo "Root: $ROOT"
echo ""

# ── 1. Build the set of defined alias names ───────────────────────────────────
# Collect {% assign name = ... %} from variable-definitions.md and fhir-resources.md
# (fhir-resources.md is itself included at the bottom of variable-definitions.md)
DEFINED_TOKENS=$( \
  grep -h -oP "assign\s+\K\w+" "$VAR_DEF" "$FHIR_RES" 2>/dev/null \
  | sort -u || true \
)

echo "Defined aliases : $(printf '%s\n' "$DEFINED_TOKENS" | wc -l | tr -d ' ')"
echo ""

# ── 2. Check each active pagecontent page ─────────────────────────────────────
TOTAL_ISSUES=0
PAGES_WITH_TOKENS=0

while IFS= read -r page; do
  bname=$(basename "$page")

  # Collect normal {{token}} usages — exclude triple-brace
  USED_TOKENS=$(grep -oP "\{\{[A-Za-z][A-Za-z0-9_]+\}\}" "$page" 2>/dev/null \
    | grep -oP "[A-Za-z][A-Za-z0-9_]+" | sort -u || true)

  # Collect malformed {{{token}}} usages
  TRIPLE_TOKENS=$(grep -oP "\{\{\{[A-Za-z][A-Za-z0-9_]+\}\}\}" "$page" 2>/dev/null | sort -u || true)

  [ -z "$USED_TOKENS" ] && [ -z "$TRIPLE_TOKENS" ] && continue
  PAGES_WITH_TOKENS=$((PAGES_WITH_TOKENS + 1))

  PAGE_ISSUES=0

  # 2a. Pages that use {{token}} must include variable-definitions.md
  if [ -n "$USED_TOKENS" ]; then
    HAS_INCLUDE=$(grep -c "include variable-definitions.md" "$page" 2>/dev/null || echo 0)
    if [ "$HAS_INCLUDE" -eq 0 ]; then
      echo "  MISSING_INCLUDE  [$bname]  no {% include variable-definitions.md %}"
      PAGE_ISSUES=$((PAGE_ISSUES + 1))
    fi
  fi

  # 2b. Every {{token}} must be defined
  while IFS= read -r token; do
    [ -z "$token" ] && continue
    if ! printf '%s\n' "$DEFINED_TOKENS" | grep -qx "$token"; then
      echo "  UNDEFINED_TOKEN  [$bname]  {{$token}} is used but not defined in includes"
      PAGE_ISSUES=$((PAGE_ISSUES + 1))
    fi
  done <<< "$USED_TOKENS"

  # 2c. Malformed triple-brace tokens
  if [ -n "$TRIPLE_TOKENS" ]; then
    while IFS= read -r triple; do
      [ -z "$triple" ] && continue
      echo "  MALFORMED_TOKEN  [$bname]  $triple  (triple-brace leaks literal '}' into output)"
      PAGE_ISSUES=$((PAGE_ISSUES + 1))
    done <<< "$TRIPLE_TOKENS"
  fi

  if [ "$PAGE_ISSUES" -eq 0 ]; then
    echo "  PASS             [$bname]"
  fi

  TOTAL_ISSUES=$((TOTAL_ISSUES + PAGE_ISSUES))

done < <(find "$PAGECONTENT" -maxdepth 1 -name "*.md" | sort)

echo ""
echo "Pages with tokens : $PAGES_WITH_TOKENS"
echo "Total defects     : $TOTAL_ISSUES"
echo ""

if [ "$TOTAL_ISSUES" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
else
  echo "RESULT: FAIL"
  exit "$TOTAL_ISSUES"
fi
