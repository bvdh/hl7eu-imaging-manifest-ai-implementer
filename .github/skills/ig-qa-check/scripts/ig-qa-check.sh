#!/usr/bin/env bash
# IG QA Check — build-when-needed + deterministic quality evidence collector.
#
# Collects the deterministic evidence the ig-qa-check skill needs:
#   - Build freshness detection (and optional build when outputs are stale/missing)
#   - QA error/warning/broken-link counts from the publisher qa.html for R4 and R5
#   - Valid profile inventory per FHIR version (from generated StructureDefinition-*.json)
#   - Profile references found in narrative text and PlantUML image sources, classified
#     as OK / VERSION-SPECIFIC / BROKEN against the per-version profile inventory
#   - Description sections of all profiles, dumped for applicability review
#
# Spelling, grammar, and description-applicability judgements are performed by the
# agent using the report produced here (see SKILL.md).
#
# Usage:
#   ig-qa-check.sh [--no-build] [--force-build]
#     (default)      build only when outputs are missing or stale
#     --no-build     never build; report freshness only
#     --force-build  always rebuild before checking

set -u

BUILD_MODE="auto"
for arg in "$@"; do
  case "$arg" in
    --no-build)    BUILD_MODE="none" ;;
    --force-build) BUILD_MODE="force" ;;
    -h|--help)
      grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

# --- Resolve IG root (same precedence as sibling skills) ---
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
workspace_root="$(cd "$script_dir/../../../.." && pwd)"
resolver="$workspace_root/.github/skills/branch-context-management/scripts/resolve-branch-context.sh"
resolved_fork_root=""
if [[ -f "$resolver" ]]; then
  resolver_output="$(bash "$resolver" 2>/dev/null || true)"
  resolved_fork_root="$(echo "$resolver_output" | sed -n 's/^FORK_ROOT=//p')"
fi

if [[ -d "$workspace_root/ig-src" && -f "$workspace_root/_preProcessAndCheckAll.sh" ]]; then
  IG_ROOT="$workspace_root"
elif [[ -n "$resolved_fork_root" && -d "$resolved_fork_root/ig-src" && -f "$resolved_fork_root/_preProcessAndCheckAll.sh" ]]; then
  IG_ROOT="$resolved_fork_root"
elif [[ -d "$workspace_root/hl7eu-imaging-fork/ig-src" && -f "$workspace_root/hl7eu-imaging-fork/_preProcessAndCheckAll.sh" ]]; then
  IG_ROOT="$workspace_root/hl7eu-imaging-fork"
else
  echo "ERROR: Could not locate IG root (need ig-src/ and _preProcessAndCheckAll.sh)." >&2
  exit 1
fi

cd "$IG_ROOT" || exit 1

timestamp="$(date +%Y%m%d-%H%M%S)"
log_dir="$IG_ROOT/build-logs"
mkdir -p "$log_dir"
REPORT="$log_dir/ig-qa-check-$timestamp.md"

R4_OUT="$IG_ROOT/igs/imaging-r4/output"
R5_OUT="$IG_ROOT/igs/imaging-r5/output"

# --- Build freshness detection ---
is_stale() {
  local out_qa="$1/qa.html"
  [[ ! -f "$out_qa" ]] && return 0
  # Any tracked source file newer than the QA artifact means the build is stale.
  if find "$IG_ROOT/ig-src" -type f -newer "$out_qa" -print -quit 2>/dev/null | grep -q .; then
    return 0
  fi
  return 1
}

build_needed="no"
if is_stale "$R4_OUT" || is_stale "$R5_OUT"; then
  build_needed="yes"
fi

did_build="no"
build_status="skipped"
if [[ "$BUILD_MODE" == "force" || ( "$BUILD_MODE" == "auto" && "$build_needed" == "yes" ) ]]; then
  echo "Building IG (mode=$BUILD_MODE, stale=$build_needed) ..."
  build_log="$log_dir/ig-qa-check-build-$timestamp.log"
  if bash "$IG_ROOT/_preProcessAndCheckAll.sh" > "$build_log" 2>&1; then
    build_status="ok"
  else
    build_status="failed (see $build_log)"
  fi
  did_build="yes"
fi

# --- Parse QA counts from publisher qa.html comment line ---
qa_counts() {
  local out="$1"
  local qa="$out/qa.html"
  if [[ ! -f "$qa" ]]; then
    echo "missing"
    return
  fi
  # Comment line looks like: <!-- ... broken links = 0, errors = 1, warn = 27, info = 78-->
  local line
  line="$(grep -oiE 'broken links = [0-9]+, errors = [0-9]+, warn = [0-9]+, info = [0-9]+' "$qa" | head -1)"
  if [[ -z "$line" ]]; then
    # Fallback to qa.txt header (err = X, warn = Y, info = Z)
    local hdr
    hdr="$(grep -m1 -E '^err = ' "$out/qa.txt" 2>/dev/null || true)"
    echo "${hdr:-unparsed}"
    return
  fi
  echo "$line"
}

R4_QA="$(qa_counts "$R4_OUT")"
R5_QA="$(qa_counts "$R5_OUT")"

broken_of() { echo "$1" | grep -oiE 'broken links = [0-9]+' | grep -oE '[0-9]+' | head -1; }
R4_BROKEN="$(broken_of "$R4_QA")"
R5_BROKEN="$(broken_of "$R5_QA")"

# --- Profile inventory + reference/description analysis (python) ---
PY_OUT="$(IG_ROOT="$IG_ROOT" python3 - <<'PY'
import os, re, glob, json

ig_root = os.environ["IG_ROOT"]

def inventory(version_dir):
    inv = {}
    for path in glob.glob(os.path.join(version_dir, "output", "StructureDefinition-*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            continue
        if data.get("resourceType") != "StructureDefinition":
            continue
        sid = data.get("id") or os.path.basename(path)[len("StructureDefinition-"):-len(".json")]
        inv[sid] = {
            "name": data.get("name", ""),
            "title": data.get("title", ""),
            "derivation": data.get("derivation", ""),
            "kind": data.get("kind", ""),
            "url": data.get("url", ""),
        }
    return inv

r4 = inventory(os.path.join(ig_root, "igs", "imaging-r4"))
r5 = inventory(os.path.join(ig_root, "igs", "imaging-r5"))
all_ids = sorted(set(r4) | set(r5))

# --- Example coverage: read the publisher-rendered per-profile examples page ---
# The generated StructureDefinition-<Id>-examples.html states
# "No examples are currently available" when the profile has none, and otherwise
# lists the conforming examples. This is the publisher's own determination and is
# robust across R4/R5 (which use different canonical bases). Multi-language builds
# render the real page under output/en/; output/*.html are redirect stubs.
_NO_EXAMPLES = "No examples are currently available"

def examples_page_flag(version_dir, sid):
    """True if the profile's examples page lists examples, False if it states none,
    None if no rendered examples page was found."""
    for base in (os.path.join(version_dir, "output", "en"),
                 os.path.join(version_dir, "output")):
        p = os.path.join(base, "StructureDefinition-%s-examples.html" % sid)
        if not os.path.exists(p):
            continue
        try:
            html = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            return None
        if len(html) < 800:  # language-redirect stub, not the rendered page
            continue
        return _NO_EXAMPLES not in html
    return None

V4 = os.path.join(ig_root, "igs", "imaging-r4")
V5 = os.path.join(ig_root, "igs", "imaging-r5")

def needs_example(meta):
    # Resource profiles defined by this IG are expected to have at least one example.
    return meta.get("derivation") == "constraint" and meta.get("kind") == "resource"

def has_example(sid, version_dir, ver_inv):
    if sid not in ver_inv:
        return None  # profile not present in this version
    return examples_page_flag(version_dir, sid)


# Valid LOCAL reference targets = every StructureDefinition-*.html page actually
# generated for that version (this includes derived views such as -definitions,
# and excludes external-package models, which are linked by absolute URL).
def html_targets(version_dir):
    targets = set()
    for path in glob.glob(os.path.join(version_dir, "output", "StructureDefinition-*.html")):
        base = os.path.basename(path)[len("StructureDefinition-"):-len(".html")]
        targets.add(base)
    return targets

html4 = html_targets(os.path.join(ig_root, "igs", "imaging-r4"))
html5 = html_targets(os.path.join(ig_root, "igs", "imaging-r5"))

# --- Scan narrative + image sources for profile references ---
scan_dirs = [
    os.path.join(ig_root, "ig-src", "input", "pagecontent"),
    os.path.join(ig_root, "ig-src", "input", "intro-notes"),
    os.path.join(ig_root, "ig-src", "input", "includes"),
    os.path.join(ig_root, "ig-src", "input", "images-source"),
]
ref_re = re.compile(r"StructureDefinition-([A-Za-z0-9_-]+?)(?=\.html|\.json|[^A-Za-z0-9_-]|$)")
_boundary = set('("\'[ \t>=)')

def is_external(line, start):
    """True if this match belongs to an absolute (http/https) URL, not a local link."""
    pre = line[:start]
    cut = 0
    for i in range(len(pre) - 1, -1, -1):
        if pre[i] in _boundary:
            cut = i + 1
            break
    return "://" in pre[cut:]

refs = {}  # id -> list of "relpath:line"
for d in scan_dirs:
    for root, _, files in os.walk(d):
        for fn in files:
            if not fn.lower().endswith((".md", ".plantuml", ".puml", ".html", ".xml", ".liquid.md")):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for m in ref_re.finditer(line):
                            if is_external(line, m.start()):
                                continue  # external-package StructureDefinition, not a local profile
                            sid = m.group(1)
                            rel = os.path.relpath(fp, ig_root)
                            refs.setdefault(sid, []).append(f"{rel}:{i}")
            except Exception:
                continue

def classify(sid):
    in4, in5 = sid in html4, sid in html5
    if not in4 and not in5:
        return "BROKEN"
    if in4 != in5:
        return "VERSION-SPECIFIC"
    return "OK"

broken, version_specific = [], []
for sid in sorted(refs):
    c = classify(sid)
    if c == "BROKEN":
        broken.append((sid, refs[sid]))
    elif c == "VERSION-SPECIFIC":
        loc = "R4-only" if sid in html4 else "R5-only"
        version_specific.append((sid, loc, refs[sid]))

# --- Alias usage for profile/resource references (prefer [[[...]]]) ---
# The IG publisher resolves [[[Name]]] to a link for any named profile/resource.
# Liquid aliases (defined via {% assign %} in includes) that point to a profile,
# actor, capability, or operation page should be replaced by the [[[...]]] form
# unless that form does not work (e.g. custom display text is required).
alias_def_re = re.compile(r'\{%\s*assign\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(.*?)"\s*%\}')
conf_re = re.compile(r'(StructureDefinition|ActorDefinition|CapabilityStatement|OperationDefinition)-([A-Za-z0-9_.-]+?)\.html')
profile_aliases = {}  # alias name -> target id of the profile/resource it links to
inc_dir = os.path.join(ig_root, "ig-src", "input", "includes")
for root, _, files in os.walk(inc_dir):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        try:
            text = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in alias_def_re.finditer(text):
            name, val = m.group(1), m.group(2)
            cm = conf_re.search(val)
            if cm:
                profile_aliases[name] = cm.group(2)

alias_use_re = re.compile(r'\{\{-?\s*([A-Za-z_][A-Za-z0-9_]*)\s*-?\}\}')
alias_refs = {}  # alias name -> list of "relpath:line"
for d in [os.path.join(ig_root, "ig-src", "input", "pagecontent"),
          os.path.join(ig_root, "ig-src", "input", "intro-notes"),
          inc_dir]:
    for root, _, files in os.walk(d):
        for fn in files:
            if not fn.lower().endswith((".md", ".liquid.md")):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for m in alias_use_re.finditer(line):
                            name = m.group(1)
                            if name in profile_aliases:
                                rel = os.path.relpath(fp, ig_root)
                                alias_refs.setdefault(name, []).append(f"{rel}:{i}")
            except Exception:
                continue

# --- URL vs alias review ---
# Build a map of every URL that is already exposed through a liquid alias, then
# scan narrative for raw URLs. A raw URL that matches an alias should be replaced
# by that alias; a raw URL pointing to an HL7 IG or IHE spec should get a new alias.
# Parse alias definitions line by line: some source lines are malformed (missing
# closing quote / %}), so a multi-line regex would bleed URLs across aliases.
alias_line_re = re.compile(r"\{%\s*assign\s+([A-Za-z0-9_-]+)\s*=\s*(.*)$")
url_re = re.compile(r'https?://[^\s"\'\)\]<>}]+')

def norm_url(u):
    return u.rstrip('/.,;:)]"\'')

alias_urls = {}  # normalized url -> list of alias names
for root, _, files in os.walk(inc_dir):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        try:
            text = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for line in text.splitlines():
            m = alias_line_re.search(line)
            if not m:
                continue
            name, val = m.group(1), m.group(2)
            for um in url_re.finditer(val):
                nu = norm_url(um.group(0))
                alias_urls.setdefault(nu, [])
                if name not in alias_urls[nu]:
                    alias_urls[nu].append(name)

def is_hl7_ihe(u):
    lu = u.lower()
    # Operational HL7 sites (issue tracker, wiki, chat) are not IGs/specs.
    if any(h in lu for h in ("jira.hl7.org", "confluence.hl7.org", "chat.fhir.org")):
        return False
    return ("hl7.org" in lu or "ihe.net" in lu or "ihe.org" in lu
            or "/ig/hl7-eu" in lu or "/ig/hl7" in lu or "hl7.eu" in lu)

url_findings = {}  # normalized url -> {kind, aliases, locations}
for d in [os.path.join(ig_root, "ig-src", "input", "pagecontent"),
          os.path.join(ig_root, "ig-src", "input", "intro-notes"),
          inc_dir]:
    for root, _, files in os.walk(d):
        for fn in files:
            if not fn.lower().endswith((".md", ".liquid.md")):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        if "{% assign" in line:
                            continue  # skip alias definitions themselves
                        for um in url_re.finditer(line):
                            nu = norm_url(um.group(0))
                            if nu in alias_urls:
                                kind, aliases = "alias-exists", alias_urls[nu]
                            elif is_hl7_ihe(nu):
                                kind, aliases = "suggest-alias", []
                            else:
                                continue
                            rel = os.path.relpath(fp, ig_root)
                            rec = url_findings.setdefault(nu, {"kind": kind, "aliases": aliases, "locations": []})
                            rec["locations"].append(f"{rel}:{i}")
            except Exception:
                continue

# --- Description review data: profile, field, and slice descriptions ---
# Field/slice descriptions are read from the generated StructureDefinition
# differential (resolved element paths + slice names). The source FSH file is
# mapped by profile name so the agent knows where to edit.
name_to_fsh = {}
for fp in glob.glob(os.path.join(ig_root, "ig-src", "input", "fsh", "**", "*.fsh"), recursive=True):
    try:
        text = open(fp, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for m in re.finditer(r"(?m)^Profile:\s*(\S+)", text):
        name_to_fsh.setdefault(m.group(1), os.path.relpath(fp, ig_root))

def load_sd(sid):
    """Load the full StructureDefinition JSON, preferring R5 then R4."""
    for ver, vd in (("R5", "imaging-r5"), ("R4", "imaging-r4")):
        p = os.path.join(ig_root, "igs", vd, "output", f"StructureDefinition-{sid}.json")
        if os.path.exists(p):
            try:
                return ver, json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
    return None, None

def collect_descriptions():
    entries = []
    for sid in all_ids:
        ver, sd = load_sd(sid)
        if sd is None:
            continue
        elements = []
        for el in sd.get("differential", {}).get("element", []):
            short = el.get("short", "")
            definition = el.get("definition", "")
            comment = el.get("comment", "")
            slice_name = el.get("sliceName", "")
            # Keep elements that carry a description or that define a slice.
            if not (short or definition or comment or slice_name):
                continue
            elements.append({
                "path": el.get("id") or el.get("path", ""),
                "slice": slice_name,
                "short": short,
                "definition": definition,
                "comment": comment,
            })
        entries.append({
            "name": sd.get("name", sid),
            "id": sid,
            "title": sd.get("title", ""),
            "version": ver,
            "desc": sd.get("description", ""),
            "file": name_to_fsh.get(sd.get("name", ""), ""),
            "elements": elements,
        })
    return entries

descs = collect_descriptions()

print("<<<INVENTORY>>>")
for sid in all_ids:
    meta = r4.get(sid) or r5.get(sid) or {}
    ne = needs_example(meta)
    ex4v = has_example(sid, V4, r4)
    ex5v = has_example(sid, V5, r5)
    print(json.dumps({
        "id": sid,
        "title": meta.get("title", ""),
        "name": meta.get("name", ""),
        "r4": sid in r4,
        "r5": sid in r5,
        "needs_example": ne,
        "r4ex": ex4v,
        "r5ex": ex5v,
    }))
print("<<<MISSINGEXAMPLES>>>")
for sid in all_ids:
    meta = r4.get(sid) or r5.get(sid) or {}
    if not needs_example(meta):
        continue
    miss = []
    if has_example(sid, V4, r4) is False:
        miss.append("R4")
    if has_example(sid, V5, r5) is False:
        miss.append("R5")
    if miss:
        print(json.dumps({"id": sid, "title": meta.get("title", ""), "missing": miss}))
print("<<<REFCOUNT>>>")
print(json.dumps({"referenced": len(refs), "broken": len(broken), "version_specific": len(version_specific), "alias_refs": sum(len(v) for v in alias_refs.values()), "url_alias_replaceable": sum(1 for r in url_findings.values() if r["kind"] == "alias-exists"), "url_suggest_alias": sum(1 for r in url_findings.values() if r["kind"] == "suggest-alias")}))
print("<<<BROKEN>>>")
for sid, locs in broken:
    print(json.dumps({"id": sid, "locations": locs[:20]}))
print("<<<VERSIONSPECIFIC>>>")
for sid, loc, locs in version_specific:
    print(json.dumps({"id": sid, "where": loc, "locations": locs[:20]}))
print("<<<ALIASREFS>>>")
for name in sorted(alias_refs):
    print(json.dumps({"alias": name, "target": profile_aliases[name], "locations": alias_refs[name][:20]}))
print("<<<URLREVIEW>>>")
for nu in sorted(url_findings):
    r = url_findings[nu]
    print(json.dumps({"url": nu, "kind": r["kind"], "aliases": r["aliases"], "locations": r["locations"][:20]}))
print("<<<DESCRIPTIONS>>>")
for e in descs:
    print(json.dumps(e))
PY
)"

# --- Assemble markdown report ---
section() { awk -v s="<<<$1>>>" -v e="<<<$2>>>" '$0==s{f=1;next} $0==e{f=0} f' <<<"$PY_OUT"; }

{
  echo "# IG QA Check Report"
  echo
  echo "- Generated: $(date -Iseconds)"
  echo "- IG root: \`$IG_ROOT\`"
  echo "- Build mode: \`$BUILD_MODE\`  |  Stale before run: \`$build_needed\`  |  Built this run: \`$did_build\`  |  Build status: \`$build_status\`"
  echo
  echo "## 1. Build & QA Summary"
  echo
  echo "| Version | QA counts (from qa.html) | Broken links |"
  echo "|---|---|---|"
  echo "| R4 | ${R4_QA} | ${R4_BROKEN:-?} |"
  echo "| R5 | ${R5_QA} | ${R5_BROKEN:-?} |"
  echo
  if [[ "${R4_BROKEN:-1}" == "0" && "${R5_BROKEN:-1}" == "0" ]]; then
    echo "Broken-link check: **PASS** (0 broken links in both versions)."
  else
    echo "Broken-link check: **REVIEW** — non-zero or unparsed broken-link count; inspect \`igs/imaging-r*/output/qa.html\`."
  fi
  echo

  echo "## 2. Profile Reference Integrity"
  echo
  echo "Profile ids referenced as \`StructureDefinition-<Id>\` in narrative text and PlantUML sources,"
  echo "checked against the generated profile inventory of each FHIR version."
  echo
  refcount="$(section REFCOUNT BROKEN | head -1)"
  echo "Reference summary: \`$refcount\`"
  echo
  echo "### 2a. BROKEN references (id exists in neither R4 nor R5)"
  broken_lines="$(section BROKEN VERSIONSPECIFIC)"
  if [[ -z "$broken_lines" ]]; then
    echo "None. **PASS**"
  else
    echo "$broken_lines" | while IFS= read -r l; do
      [[ -z "$l" ]] && continue
      id="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')"
      locs="$(echo "$l" | python3 -c 'import sys,json;print(", ".join(json.load(sys.stdin)["locations"]))')"
      echo "- \`$id\` — $locs"
    done
  fi
  echo
  echo "### 2b. VERSION-SPECIFIC references (exists in only one version)"
  echo "Not necessarily an error, but confirm the surrounding text guards the version (R4 vs R5)."
  vs_lines="$(section VERSIONSPECIFIC ALIASREFS)"
  if [[ -z "$vs_lines" ]]; then
    echo
    echo "None."
  else
    echo
    echo "$vs_lines" | while IFS= read -r l; do
      [[ -z "$l" ]] && continue
      id="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')"
      where="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["where"])')"
      locs="$(echo "$l" | python3 -c 'import sys,json;print(", ".join(json.load(sys.stdin)["locations"]))')"
      echo "- \`$id\` ($where) — $locs"
    done
  fi
  echo
  echo "### 2c. Alias references that should use the \`[[[...]]]\` pattern"
  echo "Profiles and resources should be referenced with the IG publisher \`[[[Name]]]\` cross-reference."
  echo "Liquid aliases (\`{{ alias }}\`) that link to a profile/actor/capability/operation page are listed"
  echo "below with their recommended replacement. Keep an alias only if \`[[[...]]]\` does not work"
  echo "(for example when custom display text is required)."
  alias_lines="$(section ALIASREFS URLREVIEW)"
  if [[ -z "$alias_lines" ]]; then
    echo
    echo "None. **PASS**"
  else
    echo
    echo "$alias_lines" | while IFS= read -r l; do
      [[ -z "$l" ]] && continue
      alias="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["alias"])')"
      target="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["target"])')"
      locs="$(echo "$l" | python3 -c 'import sys,json;print(", ".join(json.load(sys.stdin)["locations"]))')"
      echo "- \`{{ $alias }}\` → replace with \`[[[$target]]]\` — $locs"
    done
  fi
  echo
  echo "### 2d. URL references (use aliases; add aliases for HL7/IHE)"
  echo "Raw URLs in narrative should reuse an existing liquid alias. URLs pointing to an HL7 IG or"
  echo "IHE spec that have no alias should get one added in \`ig-src/input/includes/variable-definitions.md\`."
  url_lines="$(section URLREVIEW DESCRIPTIONS)"
  if [[ -z "$url_lines" ]]; then
    echo
    echo "None. **PASS**"
  else
    echo
    echo "$url_lines" | while IFS= read -r l; do
      [[ -z "$l" ]] && continue
      echo "$l" | python3 -c 'import sys,json
d=json.load(sys.stdin)
locs=", ".join(d["locations"])
if d["kind"]=="alias-exists":
    aliases=" or ".join("{{ %s }}" % a for a in d["aliases"])
    print("- `%s` → replace with %s — %s" % (d["url"], aliases, locs))
else:
    print("- `%s` (HL7/IHE, no alias) → add an alias in includes/variable-definitions.md and replace — %s" % (d["url"], locs))'
    done
  fi
  echo

  echo "## 3. Profile Inventory (for prose-name review)"
  echo
  echo "Use this table to verify that human-readable profile names used in prose match a real profile"
  echo "and that the version claimed in the text matches the R4/R5 columns. The Ex columns show whether"
  echo "a resource profile has at least one example in that version (\`n/a\` = not a resource profile)."
  echo
  echo "| Id | Title | Name | R4 | R5 | R4 ex | R5 ex |"
  echo "|---|---|---|:--:|:--:|:--:|:--:|"
  section INVENTORY MISSINGEXAMPLES | while IFS= read -r l; do
    [[ -z "$l" ]] && continue
    echo "$l" | python3 -c 'import sys,json
d=json.load(sys.stdin)
def ex(present, has):
    if not present: return " "
    if not d["needs_example"]: return "n/a"
    if has is None: return "?"
    return "yes" if has else "**no**"
print("| `%s` | %s | %s | %s | %s | %s | %s |" % (d["id"], d["title"], d["name"], "yes" if d["r4"] else "-", "yes" if d["r5"] else "-", ex(d["r4"], d["r4ex"]), ex(d["r5"], d["r5ex"])))'
  done
  echo
  echo "### 3a. Profiles missing examples"
  echo "Every resource profile defined by this IG should have at least one conforming example."
  missex_lines="$(section MISSINGEXAMPLES REFCOUNT)"
  if [[ -z "$missex_lines" ]]; then
    echo
    echo "None. **PASS**"
  else
    echo
    echo "$missex_lines" | while IFS= read -r l; do
      [[ -z "$l" ]] && continue
      id="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')"
      title="$(echo "$l" | python3 -c 'import sys,json;print(json.load(sys.stdin)["title"])')"
      miss="$(echo "$l" | python3 -c 'import sys,json;print(", ".join(json.load(sys.stdin)["missing"]))')"
      echo "- \`$id\` ($title) — missing in: $miss"
    done
  fi
  echo

  echo "## 4. Profile, Field & Slice Descriptions (for applicability review)"
  echo
  echo "For each profile, confirm the Description accurately describes the profile's actual content."
  echo "Then, for every constrained field and slice, confirm its short/definition/comment corresponds"
  echo "to that element's purpose in this IG. Flag descriptions that are generic, stale, copied from"
  echo "another element/profile, contradict the cardinality/binding, or do not match the element's role."
  echo "Field and slice descriptions are read from the generated differential (\`version\` shows the source)."
  echo
  section DESCRIPTIONS END | while IFS= read -r l; do
    [[ -z "$l" ]] && continue
    echo "$l" | python3 -c 'import sys,json
d=json.load(sys.stdin)
print("### %s (`%s`)  — from %s" % (d.get("title") or d["name"], d["id"] or "no-id", d.get("version","?")))
print()
print("- Source: `%s`" % (d["file"] or "(unmapped)"))
print("- Name: `%s`" % d["name"])
print()
print("**Profile description:**")
print()
print("> " + (d["desc"].replace("\n","\n> ") if d["desc"] else "_(no description)_"))
print()
els = d.get("elements", [])
if not els:
    print("_No profile-specific field/slice descriptions in the differential._")
    print()
else:
    print("| Element (path) | Slice | Short | Definition / Comment |")
    print("|---|---|---|---|")
    for e in els:
        def cell(s):
            return (s or "").replace("|","\\|").replace("\n"," ").strip()
        defcom = cell(e.get("definition",""))
        com = cell(e.get("comment",""))
        if com:
            defcom = (defcom + " _(comment: " + com + ")_").strip()
        print("| `%s` | %s | %s | %s |" % (cell(e.get("path","")), cell(e.get("slice","")) or "-", cell(e.get("short","")) or "-", defcom or "-"))
    print()'
  done

  echo "## 5. Current-Status Page"
  echo
  cs_page="$IG_ROOT/ig-src/input/pagecontent/current-status.md"
  sushi_cfg="$IG_ROOT/ig-src/sushi-config.liquid.yaml"
  if [[ ! -f "$cs_page" ]]; then
    echo "current-status.md not found at \`ig-src/input/pagecontent/current-status.md\` — **REVIEW** (page missing)."
  else
    cs_version="$(grep -m1 -E '^version:' "$sushi_cfg" 2>/dev/null | sed -E 's/^version:[[:space:]]*//; s/[[:space:]]*#.*$//')"
    ig_ver="$(grep -m1 '"ig-ver"' "$R4_OUT/qa.json" 2>/dev/null | sed -E 's/.*"ig-ver"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')"
    echo "- Page: \`ig-src/input/pagecontent/current-status.md\`"
    echo "- IG version (sushi-config): \`${cs_version:-unknown}\`  |  built ig-ver (qa.json): \`${ig_ver:-unknown}\`"
    if [[ "$sushi_cfg" -nt "$cs_page" ]]; then
      echo "- Freshness: **REVIEW** — sushi-config is newer than the page; the version/status text may be stale."
    else
      echo "- Freshness: page is at least as new as sushi-config."
    fi
    echo
    echo "Required status items (presence check against the page):"
    check_cs() {
      if grep -qiE "$2" "$cs_page"; then echo "- PASS: $1"; else echo "- MISSING: $1"; fi
    }
    check_cs "R4 build URL" 'imaging-r4'
    check_cs "R5 build URL" 'imaging-r5'
    check_cs "0.1.0 ballot release" '0\.1\.0'
    check_cs "v1.0.0-alpha projectathon snapshot" '1\.0\.0-alpha'
    check_cs "May 2026 ballot reconciliation" 'May 2026'
    check_cs "EHDS / European Commission future-update note" 'EHDS|European Commission'
    echo
    echo "Page content (for currency review):"
    echo
    sed 's/^/> /' "$cs_page"
    echo
    echo "Judge whether this still reflects the current status: the version agrees with the built ig-ver,"
    echo "the ballot-reconciliation phase is current, referenced releases/snapshots are still accurate, and"
    echo "no superseded dates or claims remain. Use the \`current-status-page-check\` skill for the"
    echo "authoritative pass/fail against the full status criteria."
  fi
  echo

  echo "## 6. Semantic Checks (agent to complete)"
  echo
  echo "The following require agent judgement — see SKILL.md:"
  echo "- Spelling review of narrative pages and profile descriptions."
  echo "- Grammar / readability review of narrative pages and profile descriptions."
  echo "- Description applicability review using Section 4 against each profile's rendered elements."
  echo "- Prose profile-name review using Section 3 (names/titles not written as StructureDefinition-<Id> links)."
  echo "- Visual inspection of figures for profile names, using Section 3 as the source of truth."
  echo "- Current-status page currency review using Section 5 and the \`current-status-page-check\` skill."
} > "$REPORT"

echo
echo "IG QA Check report written to: $REPORT"
echo "Broken links — R4: ${R4_BROKEN:-?}, R5: ${R5_BROKEN:-?}"

# Exit non-zero if a definite failure was found (broken profile refs or build failure).
fail=0
[[ "$build_status" == failed* ]] && fail=1
if section BROKEN VERSIONSPECIFIC | grep -q .; then fail=1; fi
[[ "${R4_BROKEN:-1}" != "0" || "${R5_BROKEN:-1}" != "0" ]] && fail=1
exit $fail
