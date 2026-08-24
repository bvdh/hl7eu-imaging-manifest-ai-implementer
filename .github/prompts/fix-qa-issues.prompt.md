---
description: 'Ensure a current IG build, then inspect and analyse the QA output (qa.html / qa.txt / qa.json), summarise errors, warnings and broken links, triage each into IG-content vs terminology/environment vs dependency, and recommend concrete fixes.'
---

# /fix-qa-issues

Analyse the latest FHIR IG Publisher QA output for the RAD.MADO / EU Imaging Manifest IG and
recommend fixes. Work from `${workspaceFolder}` (repo root); the IG lives in `imaging-manifest-fork/`.

## Step 1 — Ensure the build is current
QA files must be newer than the IG sources, otherwise the analysis is stale. Compare the newest
input mtime against `output/qa.json`:

```bash
cd imaging-manifest-fork
newest_input=$(find input sushi-config.yaml ig.ini -type f -printf '%T@\n' 2>/dev/null | sort -n | tail -1)
qa_time=$(stat -c '%Y' output/qa.json 2>/dev/null || echo 0)
awk -v i="${newest_input%.*}" -v q="$qa_time" 'BEGIN{print (q>=i)?"QA CURRENT":"QA STALE — rebuild needed"}'
```

- If **STALE** or `output/qa.json` is missing: run a build first (public tx), tee to a log, then
  continue. Use the `build-ig` skill for the full lifecycle; the minimal command is:
  ```bash
  cd /home/nly98977/SwArchives/bvdh/hl7eu-imaging-manifest-ai-implementer
  LOG="build-log/build-$(date +%Y%m%d-%H%M%S).log"; echo "Build log: $LOG"
  cd imaging-manifest-fork && ./_build.sh build 2>&1 | tee "../$LOG"
  ```
- If **CURRENT**: proceed to Step 2 without rebuilding.

## Step 2 — Locate and read the QA artifacts
In `imaging-manifest-fork/output/`:
- `qa.json` — machine counts (`errs`, `warnings`, `hints`, `suppressed-*`, `broken-links`).
- `qa.txt` — flat list of `ERROR:` / `WARNING:` / `INFORMATION:` lines with locations.
- `qa.html` — same content rendered (use for human links / context).
- `qa.compare.txt` — diff vs the previous run (regressions/improvements), if present.

Read counts and the error list:
```bash
cd imaging-manifest-fork/output
python3 -c "import json;d=json.load(open('qa.json'));print({k:d.get(k) for k in ['errs','warnings','hints','broken-links','suppressed-warnings','suppressed-hints']})"
grep -nE '^ERROR' qa.txt | sed -E 's/\(error message.*$//' | cut -c1-200
```

## Step 3 — Summarise
Report a compact summary: Errors / Warnings / Info / Broken Links counts, whether the build was
current or rebuilt, and the number of distinct error groups. Note any regressions from
`qa.compare.txt`.

## Step 4 — Triage each error into a category
| Category | Signals | Owner / fix path |
|---|---|---|
| **IG structural** | slicing "cannot be evaluated" / discriminator, cardinality (min/max), "Undefined element", "a matching slice is required", "Unable to find a profile match", broken links, "missing source file" | Fix FSH / profile / `sushi-config.yaml` in `imaging-manifest-fork/input/` |
| **Terminology / environment** | `... not found in the value set ...` **with** `(error message = Error from https://tx.fhir.org/r4: … cache '<uuid>' is not known …)`, `java.net.SocketTimeoutException: timeout`, `Local Error: The local terminology server cannot handle this request` | Not an IG defect — confirm with Step 5, attribute to the tracked tickets |
| **Dependency / package** | `dependsOn[...] inconsistent … canonical`, `points to the canonical … inconsistent`, package "could not be found" | `sushi-config.yaml` dependency versions / upstream package (often unfixable from the IG) |

## Step 5 — Confirm terminology errors (IG vs tx)
For each value-set error, re-validate the exact `system#code` **directly** against public tx
(single call, so it bypasses the batched session cache that fails mid-build):
```bash
tx_validate() { # $1=valueSet url  $2=system  $3=code
  local enc; enc=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=''))" "$3")
  curl -s --max-time 30 "https://tx.fhir.org/r4/ValueSet/\$validate-code?url=$1&system=$2&code=$enc" \
    | python3 -c "import sys,json;d=json.load(sys.stdin);p={x['name']:x.get('valueBoolean',x.get('valueString','')) for x in d.get('parameter',[])};print('result=',p.get('result'),'|',(p.get('message','') or '')[:100])"
}
# e.g. tx_validate "http://hl7.org/fhir/ValueSet/mimetypes" "urn:ietf:bcp:13" "application/dicom"
```
- `result = true` ⇒ the code is valid; the build ERROR is the **tx session-cache** issue, not the
  IG. Do not change the IG. This is tracked by
  [HL7/fhir-ig-publisher#1359](https://github.com/HL7/fhir-ig-publisher/issues/1359) (publisher
  should recover) and
  [HealthIntersections/FHIRsmith#279](https://github.com/HealthIntersections/FHIRsmith/issues/279)
  (server session lifecycle). Local copies + a weekly status check live in the
  `build-issue-tickets/` folder and `.github` memory.
- `result = false` ⇒ genuine **IG content** error; fix the example/profile that uses the code.

**Clearing poisoned tx-cache entries (often resolves the errors).** The publisher persists tx
responses under `imaging-manifest-fork/input-cache/txcache/*.cache`, and a dropped-session or
timeout response gets cached as a *negative* result that keeps re-failing on later builds. Deleting
the cache files that captured a connection/session error forces the publisher to re-query the tx
server on the next build, which typically makes the errors disappear once the server is responsive.
These files are regenerated on build, so removal is safe:
```bash
cd imaging-manifest-fork/input-cache/txcache
# list cache files that captured a tx connection/session failure
grep -rliE "not known to this server|SocketTimeoutException|The local terminology server cannot handle|Error from https?://" . 2>/dev/null
# remove them (regenerated on next build), then rebuild
grep -rlZiE "not known to this server|SocketTimeoutException|The local terminology server cannot handle|Error from https?://" . 2>/dev/null | xargs -0 rm -v --
```
After clearing, re-run the build (Step 1). A warm re-run against a responsive tx server usually
drops these errors to 0.

Optional (weekly): check the tracking tickets and, if either is closed, re-run the build to confirm
the cache errors are gone:
```bash
gh issue view 1359 --repo HL7/fhir-ig-publisher --json number,state,closedAt
gh issue view 279  --repo HealthIntersections/FHIRsmith --json number,state,closedAt
```

## Step 6 — Recommend fixes
For each error group, give a concrete recommendation:
- **IG structural** → the specific file + change (e.g. correct a slice discriminator, add a missing
  `sushi-config.yaml` page, fix a required element in an example under `input/fsh/`).
- **Terminology/environment** → "no IG change; environmental (tx cache) — tracked by #1359/#279",
  with the `tx_validate` evidence that the code is valid. If the errors persist, suggest clearing
  the poisoned `input-cache/txcache/*.cache` files (Step 5) to force a reload, then rebuilding.
- **Dependency/package** → the dependency to bump or the upstream limitation (note if unfixable
  from the IG, e.g. the `hl7.fhir.uv.xver-r5.r4` inconsistent-canonical error).

Present the result as: a one-line summary of counts, a table of error groups → category →
recommended action, and a short "safe to ignore (environmental)" list. Do not apply changes unless
asked — this command analyses and recommends.
