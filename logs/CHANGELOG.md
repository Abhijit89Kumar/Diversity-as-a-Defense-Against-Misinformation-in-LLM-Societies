# Repository Changelog

Structural changes to the repository. Scientific decisions go in `DECISION-REGISTER.md`;
session narrative goes in `RESEARCH-LOG.md`.

---

## 2026-08-07 — Repository initialised

**Added**
- Governance layer: `docs/00-governance/SOP-000` … `SOP-080`.
- Registers: `logs/RESEARCH-LOG.md`, `logs/DECISION-REGISTER.md`,
  `logs/OPEN-QUESTIONS.md`, `logs/RISK-REGISTER.md`, `logs/CHANGELOG.md`.
- Templates: `meta/templates/`.
- `README.md`, `CLAUDE.md`, `.gitignore`.
- Directory skeleton: `docs/{00-governance,01-specifications,02-literature,03-design,04-analysis,05-paper}`,
  `logs/`, `meta/`, `src/`, `configs/`, `experiments/`, `data/`, `results/`.

**Moved**
- The four original `.docx` specification files from the repository root to
  `docs/01-specifications/source-docx/`. Content unchanged; originals preserved byte-for-byte.

**Generated**
- `docs/01-specifications/SPEC-1-master-research-specification.md`
- `docs/01-specifications/SPEC-2-system-architecture.md`
- `docs/01-specifications/SPEC-3-experimental-protocol.md`
- `docs/01-specifications/SPEC-4-roadmap-and-collaboration.md`

  Faithful Markdown conversions of the four `.docx` files. Read-only source of record
  per `DR-0002`. Word-level content preserved; tables containing code or ASCII diagrams
  rendered as fenced blocks.

**Note on version control.** `git` is not yet initialised for this folder. Initialising
it is the first recommended action — every reproducibility guarantee in SOP-040 depends
on commit-level provenance. No commits have been made on the user's behalf.
