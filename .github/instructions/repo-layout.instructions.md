---
description: "Workspace layout, build entry point, and AI/automation pipeline for the HL7 EU Imaging Manifest AI-implementer repo. Apply when working on root-level automation, scripts, ai-result outputs, or .github configuration. Do NOT apply when editing files inside imaging-manifest-fork/ — that subtree has its own instruction file."
applyTo: "{scripts/**,ai-result/**,.github/**,examples/**}"
---

# Repo Layout

This repository separates AI/automation tooling from the IG source.

```
/                              ← automation root (this instruction applies here)
├── build.sh                   ← root build wrapper (logs to build-log/)
├── startLocalTxServer.sh      ← launch a local FHIRsmith terminology server (Docker)
├── tx-config/                 ← FHIRsmith config (config.json, library.yml), seeded into tx-data/
├── scripts/                   ← pipeline scripts (JS, Python, shell)
├── ai-result/                 ← generated CSV artifacts from the pipeline
├── examples/                  ← DICOM example files
├── .github/
│   ├── instructions/          ← Copilot instruction files (applyTo-scoped)
│   ├── skills/                ← Copilot skill files (build-ig, etc.)
│   └── workflows/             ← CI workflows
└── imaging-manifest-fork/     ← FHIR IG content (separate instruction file applies here)
```

`imaging-manifest-fork/` is a **plain fork copy** of the upstream IG repository. There is no git subtree or submodule; upstream sync is done manually.

---

# Building the IG

Use the root `build.sh` wrapper (it logs to `build-log/`), or `cd` into the fork:

```sh
# From the repo root:
./build.sh                 # local-tx build (default), logs to build-log/
./build.sh build           # standard build against public tx.fhir.org

# Or from inside the fork:
cd imaging-manifest-fork
./_build.sh                # standard build
./_build.sh -tx n/a        # offline (no terminology server)
./_build.sh localtx        # against a local tx server ($TX_URL, default http://localhost:8085/r4)
```

## Local terminology server

Long builds can lose the shared public tx.fhir.org session cache. Run a local
FHIRsmith terminology server (the tx.fhir.org software) instead:

```sh
./startLocalTxServer.sh    # repo root; auto-seeds tx-config/ into tx-data/ (gitignored)
# wait until: curl http://localhost:8085/r4/metadata  returns a CapabilityStatement
TX_URL=http://localhost:8085/r4 ./build.sh localtx
```

The `validate.yml` workflow references the build scripts and may need updating to reflect the layout.

Use the `build-ig` skill for the full build lifecycle, QA validation, and failure triage.

---

# AI/Automation Pipeline

The pipeline produces the CSVs in `ai-result/` by processing IG content and model mappings. It is fully re-runnable.

## Pipeline steps (scripts/)

| Script | Purpose |
|---|---|
| `downloadXtEHRModel.sh` | Download and extract XtEHR logical model into `XtEHR-models/` |
| `parseLogicalModels.js` | Parse logical models → `xtehr-model.csv` |
| `xtehr-mapping.sh` | Run XtEHR mapping transformation |
| `generateDataBasedOnModel.js` | Generate IG-derived data from the model |
| `extract-mado-ms-obligations.py` | Extract MADO must-support obligations → `ai-result/` CSVs (steps 1–7) |

## Pipeline order

1. `downloadXtEHRModel.sh` → refreshes `XtEHR-models/`
2. `node parseLogicalModels.js XtEHR-models xtehr-model.csv` → `xtehr-model.csv`
3. Edit `xtehr-model-mapping.ods`, export to `xtehr-model-mapping.tsv`
4. `xtehr-mapping.sh` → mapping result files
5. `python3 extract-mado-ms-obligations.py` → `ai-result/step*.csv`

## ai-result/ CSVs

| File | Content |
|---|---|
| `step1-ihe-mado-fields.csv` | IHE MADO must-support fields |
| `step2-eu-mado.csv` | EU MADO profile fields |
| `step3-ehds-fields.csv` | EHDS fields with cross-references |
| `step4-ihe-eu-mado-fields.csv` | IHE + EU MADO merged |
| `step5-ihe-eu-mado-ehds-fields.csv` | IHE + EU MADO + EHDS merged |
| `step6-all-fields.csv` | All fields combined |
| `step7-mapping.csv` | Final mapping output |

The agent may re-run any or all pipeline scripts to regenerate these files.

---

# Related Repositories

A similar repo using the same AI/automation tooling pattern for the HL7 EU Imaging Report IG is [bvdh/hl7eu-imaging-ai-implementer](https://github.com/bvdh/hl7eu-imaging-ai-implementer).

---

# Conventions

- Build scripts live inside `imaging-manifest-fork/`; automation scripts live in `scripts/`.
- Do not move or rename the `ai-result/` directory; downstream scripts reference it by that name.
- When adding a new instruction file, place it in `.github/instructions/` and set a precise `applyTo` glob so it does not conflict with this file or the `imaging-manifest-fork/` instruction file.
