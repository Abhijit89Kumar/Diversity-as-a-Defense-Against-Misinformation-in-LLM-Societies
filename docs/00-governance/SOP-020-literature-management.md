---
id: SOP-020
title: Literature Management
status: ACTIVE
version: 1.0
created: 2026-08-07
---

# SOP-020 — Literature Management

Governs how prior art is found, read, recorded, and cited. Derives from SOP-000 P1.

The failure this SOP prevents: **spending eight weeks building something that was
published eighteen months ago.** For a project whose entire value proposition is
novelty, the literature review is not preparation for the research — it *is* research,
and it is the highest-leverage work in the project.

---

## 1. Search discipline

A literature search is only complete when it has been run across **all** of these,
and the coverage is recorded:

| Channel | Purpose |
|---|---|
| arXiv (cs.MA, cs.CL, cs.AI, cs.SI, cs.CY) | Preprints; where this field actually lives |
| ACL Anthology | *ACL / EMNLP / NAACL / COLM published versions |
| OpenReview | NeurIPS / ICLR / ICML submissions **and their reviews** |
| Semantic Scholar / Google Scholar | Citation graph traversal |
| Proceedings of AAMAS, WWW, ICWSM, CSCW | Multi-agent and computational social science |
| GitHub | Existing implementations; often ahead of papers |

Two traversals are mandatory and are the ones people skip:

- **Forward citation search** on each close prior work — who has cited it since?
  This is how you find the paper that already did your experiment.
- **Backward citation search** — what did the close prior work cite that we have
  not read?

Record each search in `docs/02-literature/SEARCH-LOG.md`: date, channel, query
string, number of hits, number triaged in. An unrecorded search cannot be trusted
to have happened, and cannot be re-run when a reviewer asks "did you consider X?"

---

## 2. Triage

Three tiers. Be honest about which tier a paper is in; the temptation is to
downgrade threatening papers.

| Tier | Criterion | Action |
|---|---|---|
| **A — Direct competitor** | Studies misinformation/false-belief/manipulation propagation among communicating LLM agents, or the safety effect of multi-agent topology | Read in full. Write a `LIT-xxxx` note. Add a row to the Prior Art Matrix. Must be positioned against explicitly in the paper. |
| **B — Load-bearing** | Supplies a method, metric, or assumption we rely on (belief probing, opinion dynamics, debate, diversity) | Read the relevant sections. `LIT-xxxx` note. Cite. |
| **C — Context** | Background, framing, related but not overlapping | Skim. Bib entry. Cite where useful. No note required. |

**Tier-A papers get a dedicated section in `docs/02-literature/PRIOR-ART-REVIEW.md`
stating, in one sentence each: what they did, what they measured, and precisely what
they left open that we do.** If we cannot write that third sentence for a Tier-A
paper, we do not yet have a contribution and the design must change.

---

## 3. Literature notes (`LIT-xxxx`)

One file per Tier-A/B paper: `docs/02-literature/notes/LIT-xxxx-short-slug.md`.
Template at `meta/templates/literature-note.md`. Required content:

- Full citation and link. **DOI or arXiv ID mandatory.**
- Claim of the paper in one sentence, in our words.
- Experimental setup: agents, models, N, topology, rounds, task, metrics.
- What they found, including effect sizes if reported.
- **Threat to us:** how close is this to our contribution? Rated 1–5.
- **Gift to us:** method, baseline, dataset, or framing we can adopt or must beat.
- Weaknesses / what a reviewer would attack.
- Where we cite it.

The "threat" rating is the point of the note. Maintain a sorted view of the top
threats in `PRIOR-ART-REVIEW.md`.

---

## 4. Citation integrity

**Non-negotiable rules:**

1. A reference enters `references.bib` only after a human has opened the source and
   confirmed the title, authors, venue, and year.
2. A claim is attributed to a paper only after a human has located that claim in
   that paper. Not the abstract — the claim.
3. AI-suggested citations are `[UNVERIFIED]` until (1) and (2) are done. Language
   models fabricate plausible references and mis-attribute real ones; this is the
   single most common way a first paper gets embarrassed.
4. Cite the published version where one exists; note the arXiv version too.
5. Never cite a paper you have not read at least the abstract, intro, method, and
   results of. "Cited from another paper's related-work section" is how errors
   propagate through a literature.

6. **Never characterise a paper from a prose summary of it.** Extract the actual text —
   `pdftotext`, the arXiv `/html/` rendering, or the raw HTML — and read that. Summarising
   layers (including AI fetch tools) invert facts.

   > This rule was written because it fired. During the round-2 sweep, a fetch tool's
   > built-in summariser fabricated the entire experimental setup of `arXiv:2601.05606` —
   > reporting "3, 5, 7 and 9 agents", "models run as separate homogeneous groups", "random
   > graphs", and "adversarial fraction varied 0/20/40/60%". Ground truth from the PDF:
   > N = 7 fixed, model families **mixed within one network** (the opposite of the summary),
   > no random graphs, and **no adversarial agents at all**. It inverted the single most
   > decision-relevant fact about the highest-priority paper in the queue.
   >
   > Had that summary been trusted, the project would have concluded H1 and H4 were
   > pre-empted and possibly abandoned a valid contribution.

7. **Verify the identifier, not just the title.** Confirm the arXiv ID or DOI resolves to
   the paper you think it does. IDs transcribed from search snippets are unreliable; check
   that the ID's date prefix is consistent with the claimed publication date.

`docs/02-literature/references.bib` is the single bibliography. Everything cites
from it.

---

## 5. Living the review

The prior-art review is not a one-off. Re-run the Tier-A searches:

- at **G1** (design freeze) — full sweep;
- at **G3** (matrix launch) — delta since G1;
- at **G5** (submission) — delta since G3, because something *will* have appeared,
  and it is far better that we cite it than that a reviewer does.

Each re-run appends to `SEARCH-LOG.md`.

---

## 6. Positioning statement

By G1, `docs/02-literature/PRIOR-ART-REVIEW.md` must end with a **positioning
statement** of at most 150 words that completes this sentence honestly:

> "Given [closest prior work], this paper's contribution is [X], which is new
> because [Y], and which we demonstrate by [Z]."

If that sentence cannot be written without hedging, the project is not ready to
leave G1, regardless of how much of the engineering is done. Writing code is not a
substitute for having a contribution.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue | DR-0001 |
