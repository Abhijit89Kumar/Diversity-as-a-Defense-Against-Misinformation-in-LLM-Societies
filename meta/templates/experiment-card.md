---
id: EXP-XXX
title: <short title>
status: PLANNED | RUNNING | COMPLETE | ABANDONED
type: PILOT | CONFIRMATORY | EXPLORATORY | NEGATIVE-CONTROL
preregistered: yes | no | partially (explain)
opened: YYYY-MM-DD
---

# EXP-XXX — <title>

## Purpose

What question does this experiment answer? Which `OQ-XXXX` or hypothesis does it serve?

## Design

| | |
|---|---|
| Factors and levels | |
| Cells | |
| Replications per cell | |
| Unit of randomisation | |
| **Unit of analysis** | |
| Fixed vs resampled per replication | graph realisation: … / agent→node assignment: … / prompt phrasing: … / sampling seed: … |
| N runs total | |
| Estimated calls | generation: … probing: … total: … |
| Estimated cost | |
| Estimated wall-clock | |

## Pre-committed analysis

For confirmatory experiments this must match the frozen preregistration, and say so.
For exploratory experiments, say so plainly — the label is not a demerit.

- Primary outcome and its formula:
- Test, unit of analysis, and n at that unit:
- Assumptions and the pre-decided fallback if they fail:
- Correction applied:
- Smallest effect size of interest:
- Exclusion rules (decided before running):
- Stopping rule:

## Negative control

What condition in this experiment *must* show no effect? What do we conclude if it does?

## Execution record

| Field | Value |
|---|---|
| git commit | |
| git dirty | |
| config hash | |
| launched (UTC) | |
| finished (UTC) | |
| runs succeeded / failed | |
| API failure rate by provider | |
| actual cost | |
| data location + checksum | |

## Deviations from plan

Anything that differed from the design above, when it was noticed, and whether any
outcome data had been seen at that point.

## Result

→ `RESULTS.md`
