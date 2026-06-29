---
name: create-dicom-tables
description: 'Workflow orchestrator for split DICOM extraction: runs module and SR TID agents sequentially, reviews outputs, and iterates only after explicit user approval for each new run.'
argument-hint: 'Optional max iterations; default one full cycle with approval gates'
user-invocable: true
---

# Orchestrate DICOM Modules + SR TID Extraction

## Purpose
This skill is the orchestration entry point after splitting DICOM extraction into:
- module extraction track
- SR TID extraction track

It coordinates specialized agents in sequence, then asks the user for permission before each additional run cycle.

## Agents in This Workflow
0. Workflow orchestrator agent: .github/agents/dicom-extraction-workflow.agent.md
1. Module extractor: .github/agents/dicom-modules-extractor.agent.md
2. Module reviewer: .github/agents/dicom-modules-reviewer.agent.md
3. SR extractor: .github/agents/dicom-sr-tid-extractor.agent.md
4. SR reviewer: .github/agents/dicom-sr-tid-reviewer.agent.md

Recommended invocation path: use `DICOM Extraction Workflow` as the primary entry point, which coordinates the remaining four agents.

## Split Skills
- Module skill: .github/skills/create-dicom-modules-tables/SKILL.md
- SR skill: .github/skills/create-dicom-sr-tids-tables/SKILL.md

## Workflow
Run these steps in order.

1. Baseline run
- Run extractor script once.
- Capture baseline counts from ai-result/step10-dicom-summary.json.

2. Module improvement pass
- Invoke module extractor agent to improve module parsing.
- Invoke module reviewer agent to evaluate module outputs and produce corrective feedback.

3. SR improvement pass
- Invoke SR extractor agent to improve SR/TID parsing.
- Invoke SR reviewer agent to evaluate SR outputs and produce corrective feedback.

4. Consolidated rerun
- Re-run extractor script.
- Compare counts and quality deltas versus baseline.

5. Permission gate before another cycle
- Ask user explicitly whether to run another optimization cycle.
- Do not start a new cycle unless user approves.

## Mandatory Permission Prompt
Before each new run cycle after the first one, ask:
- Continue with another improvement run? Yes or No.

If No:
- Stop and report current quality status and remaining gaps.

If Yes:
- Repeat workflow steps 2 through 5.

## Quality Gates
A cycle is considered improved only when one or more of these conditions hold:
1. Authoritative module rows increased.
2. Authoritative SR rows increased.
3. Manual-review rows decreased without increasing missing required fields.
4. No regression in required-field completeness.

## Validation Commands
```bash
python3 .github/skills/create-dicom-tables/scripts/extract-dicom-tables.py --no-download --skip-url-check
wc -l ai-result/step10-dicom-modules.csv ai-result/step10-dicom-templates.csv \
  ai-result/step10-dicom-modules-manual-review.csv ai-result/step10-dicom-templates-manual-review.csv
cat ai-result/step10-dicom-summary.json
```

## Output Contract
After each cycle, provide:
1. Module authoritative/review counts (before and after)
2. SR authoritative/review counts (before and after)
3. Concrete parser changes made in that cycle
4. Top unresolved blockers and next proposed fix
