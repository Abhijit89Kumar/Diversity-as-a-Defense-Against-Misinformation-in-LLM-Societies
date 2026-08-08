---
id: SOP-010
title: Documentation & Logging
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-010 — Documentation & Logging

Governs how work is recorded. Derives from SOP-000 P1, P7, P8.

---

## 1. The four logs

### 1.1 `logs/RESEARCH-LOG.md` — the lab notebook

**Append-only. One entry per working session.** Written at the *end* of the session,
not the start. If a session produced nothing, the entry says so — that is data about
where time went.

Required fields per entry:

```markdown
## YYYY-MM-DD — <session title>
**Participant(s):** <who, including "AI-assisted (model)" if applicable>
**Phase / Gate:** <e.g. G1 — Design>
**Goal:** <what this session set out to do, one sentence>

### Done
- <what actually happened, with links to files/commits>

### Found
- <findings, surprises, things that changed our mind — link evidence>

### Decided
- <DR-xxxx references; if a decision was made, it belongs in the register too>

### Open / Next
- <OQ-xxxx raised or closed; concrete next action with an owner>
```

Rules:
- Never edit a past entry. Supersede it with a new dated entry.
- "Found" is the most valuable field. Record things that surprised you, including
  things that made the project look harder. Especially those.
- Link, don't restate. The log points at artefacts; it is not a copy of them.

### 1.2 `logs/DECISION-REGISTER.md` — why the project looks the way it does

A decision record (`DR-xxxx`) is required whenever a choice:
- changes a hypothesis, metric, or analysis;
- changes the experimental design or its scope;
- changes a core architectural component;
- commits money or more than one day of compute;
- resolves an open question marked P0 or P1;
- deviates from a specification in `docs/01-specifications/`.

Format is in `meta/templates/decision-record.md`. Every DR must include
**Options considered** and **Consequences**, including the bad ones. A DR with one
option and no downside is not a decision, it is a rationalisation.

Decisions are never deleted. They are **Superseded by DR-yyyy** and stay in place.

### 1.3 `logs/OPEN-QUESTIONS.md` — what we do not yet know

Every unresolved question that could change the design gets an `OQ-xxxx` with a
priority:

| Priority | Meaning | Rule |
|---|---|---|
| **P0** | Could invalidate the study | Must close before G1. Blocks the design freeze. |
| **P1** | Could materially change results or interpretation | Must close before G3 (matrix launch). |
| **P2** | Affects quality or presentation | Close before G5 (submission). |
| **P3** | Interesting; future work | May stay open; goes in Future Work. |

An OQ is closed only by a `DR-xxxx` or by cited evidence. "We decided not to worry
about it" is a valid closure *if written down as a DR with the reasoning*.

### 1.4 `logs/RISK-REGISTER.md` — what could go wrong

`RK-xxxx` entries with likelihood, impact, owner, mitigation, and a **trigger** —
the observable event that means the mitigation must now be executed. A risk without
a trigger is a worry, not a risk.

---

## 2. Document conventions

- **Format:** Markdown, UTF-8, LF endings. One sentence per line is *not* required,
  but keep lines under ~100 chars where practical so diffs stay readable.
- **Front matter:** every governance and design document carries YAML front matter
  with `id`, `title`, `status`, `version`, `created`.
- **Status values:** `DRAFT` → `ACTIVE` → `SUPERSEDED` / `RETIRED`. Never delete a
  superseded document; mark it and add a pointer to its replacement.
- **Dates:** always absolute ISO-8601 (`2026-08-07`). Never "last week", "recently",
  "next sprint". Relative dates rot.
- **Claims:** every non-obvious factual claim carries `[@citekey]`, `EXP-xxx`, or
  `[UNVERIFIED]`.
- **Numbers:** any number that came from a computation carries a pointer to the
  script or notebook that produced it.

---

## 3. What gets documented, and when

| Event | Record | Where | When |
|---|---|---|---|
| Working session | Log entry | RESEARCH-LOG | End of session |
| Design choice | DR | DECISION-REGISTER | Before implementing |
| Deviation from spec | DR + amendment | DECISION-REGISTER + `docs/03-design/` | Before implementing |
| Paper read | Literature note | `docs/02-literature/notes/LIT-xxxx.md` | Same day |
| Experiment launched | Experiment card | `experiments/EXP-xxx/README.md` | Before launch |
| Experiment finished | Result summary | `experiments/EXP-xxx/RESULTS.md` | Same day |
| Bug found in a shipped result | DR + log entry + corrected artefact | All three | Immediately |
| Money spent | Line in budget ledger | `logs/RESEARCH-LOG.md` + budget table | Same day |

---

## 4. Definition of done

No task starts without a written done-condition. A done-condition is a statement
someone else could check without asking you. Examples:

- Bad: "Implement the router."
- Good: "`src/llm_society_sim/router.py` issues 100 concurrent completions across
  three providers, respects per-provider RPM, retries with backoff, and emits a
  structured log line per call including provider, model, latency, and token counts.
  Verified by `tests/test_router.py` passing and a 100-call smoke run logged in
  `experiments/EXP-000/`."

---

## 5. Session hygiene for AI-assisted work

See SOP-080 §3 for the integrity requirements. Operationally:

- Every AI-assisted session produces a RESEARCH-LOG entry naming the model.
- AI-generated text that enters a specification, the preregistration, or the paper
  must be read and verified line-by-line by a human before its `[UNVERIFIED]` tag
  is removed.
- AI-generated *citations* are treated as false until the source has been opened
  and the claim checked against it. This is non-negotiable; fabricated or
  mis-attributed references are the fastest way to destroy a first paper's
  credibility.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
