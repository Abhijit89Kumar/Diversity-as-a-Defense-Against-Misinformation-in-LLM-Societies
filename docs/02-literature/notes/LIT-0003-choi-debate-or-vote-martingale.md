---
id: LIT-0003
citekey: choi2025debate
tier: B
threat: 2
read_by: AI-assisted (Claude Opus 5) — arXiv abstract page, primary source
read_on: 2026-08-07
---

# LIT-0003 — Debate or Vote: the martingale result

**Full citation.** Choi, Hyeong Kyu; Zhu, Xiaojin; Li, Sharon. "Debate or Vote: Which Yields
Better Decisions in Multi-Agent Large Language Models?" arXiv:2508.17536, 24 Aug 2025.
**Link:** <https://arxiv.org/abs/2508.17536> · Code released (URL in abstract).

> ## ⚠ Citation correction
>
> `OQ-0043` recorded this as **"Huang, Qiang, et al. 'Debate or vote: LLM multi-agent debate
> is a martingale on belief of the correct answer.' OpenReview, 2025."** The authors are
> **Choi, Zhu and Li**; the venue is arXiv; the title differs. The claim attributed to it,
> however, is **correct**.
>
> This is the **fourth** citation in this review to arrive mis-attributed via a secondary
> source. SOP-020 §4.6–4.7 keeps earning its cost.

## One-sentence claim

Majority voting accounts for most of the benefit usually attributed to multi-agent debate,
because debate itself induces a **martingale** on belief in the correct answer and therefore
cannot improve expected correctness on its own.

## The result we rely on — verbatim

> *"we propose a theoretical framework that models debate as a stochastic process. We prove
> that it induces a martingale over agents' belief trajectories, implying that debate alone
> does not improve expected correctness."*

And the escape clause, which matters for us as much as the theorem:

> *"targeted interventions, by biasing the belief update toward correction, can meaningfully
> enhance debate effectiveness."*

Empirical scope: seven NLP benchmarks; MAD decomposed into majority voting and inter-agent
debate, with the two contributions assessed separately.

## Why this is a gift rather than a threat — threat 2/5

**It supplies the theoretical prediction for our negative control.** AMD-0002 §5 states that
in the no-injection arm the expected belief trajectory should be flat. That was `[UNVERIFIED]`
and contingent; it is now grounded in a stated, proved result. Very few simulation papers
have an *a priori* theoretical prediction to check their negative control against, and this
gives us one for free.

**It sharpens what H1 is about.** If the mean is a martingale, the mean is uninformative by
construction — the action is in the variance and the tails. That is precisely the cascade
framing adopted in `DR-0008`. Reporting mean belief as a headline would be reporting a
theorem rather than a finding.

**And it names the mechanism our hypothesis proposes.** Their escape from the martingale is
"biasing the belief update toward correction". H1 proposes that *functional diversity* is one
such bias — agents that fail independently are less likely to reinforce a shared error. That
reframes H1 from an empirical hunch into a candidate answer to a question this paper poses.

## What it leaves open

- **No adversary.** Debate is studied as an accuracy-improvement mechanism, not under
  injected misinformation. Our regime is untouched.
- **No architectural heterogeneity** as an intervention.
- **No network topology** — panel-style debate.
- The martingale is derived under assumptions (homogeneous agents, uniform belief updates —
  see `LIT-0004`) that our design deliberately violates. **That is the point:** if debate
  among homogeneous agents is a martingale, then "does heterogeneity break the martingale?"
  is a well-posed theoretical question, and H1 is a test of it.

## Where we cite it

- [x] Related Work — the debate-reliability literature
- [x] Method — theoretical prediction for the no-injection control arm (AMD-0002 §5)
- [x] Introduction — motivation for a cascade/tail framing rather than a mean framing

## Verification

- [x] Existence, title, authors, date confirmed from the arXiv abstract page
- [ ] Full text read — **abstract only so far.** The martingale's exact assumptions must be
      read before AMD-0002 §5's test is finalised, since the prediction's validity depends on
      whether our setup satisfies them.
- [ ] Human sign-off (deferred to the final citation pass)
