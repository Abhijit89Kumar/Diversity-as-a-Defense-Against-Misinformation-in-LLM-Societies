---
id: RELEASE-SCOPE
title: Release scope and dual-use position
status: ACTIVE
version: 1.0
created: 2026-08-07
backed_by: DR-0010, DR-0011
closes: OQ-0022 · G1 checklist row E6
---

# Release scope and dual-use position

Required by SOP-080 §4 and brought forward by `DR-0010` (public repository from day one).
**Due before the first agent-facing code is committed**, which is imminent — so it is
settled here rather than deferred to submission.

---

## 1. The honest statement of the tension

This project builds a tool that **propagates misinformation through networks of LLM agents
and measures which populations and structures are most vulnerable.** Written plainly, the
artefact includes:

- an injection harness that instructs an agent to argue persuasively for a false claim;
- a corpus of paired true/false claims with authority framing designed to be persuasive;
- measurements of which network structures and population compositions spread falsehood
  fastest.

That is dual-use, and pretending otherwise would be worse than useless. The question is not
whether the tension exists but whether publication is net-positive, and what specifically
should and should not ship.

## 2. Why publication is net-positive

1. **The capability is not scarce.** Instructing a model to argue for a false claim requires
   one sentence in a system prompt. Anyone with an API key already has this. The framework
   adds no capability that an adversary lacks; it adds *measurement*.
2. **The output is a defence result.** The primary finding concerns what makes populations
   *resistant*. Defenders need to know whether diversity protects; attackers gain little
   from being told that homogeneous systems are fragile, which is already published (Ju et
   al.; NetSafe; Wan et al. report 58.9% contamination under full connectivity).
3. **Measurement is the precondition for mitigation.** There is currently no standard way to
   quantify misinformation resilience in a multi-agent system. Without one, "our system is
   robust" is unfalsifiable marketing.
4. **The falsehoods are deliberately inert.** See §3.

## 3. The design choice that makes this straightforward

The corpus contains **absurd, verifiable falsehoods about physics, chemistry, biology and
arithmetic**: the speed of light is 150,000 km/s; the tongue has taste zones; the ball costs
$0.10. Nothing about health decisions, politics, elections, identifiable people, or any
social group.

This was the right scientific choice first — clean, uncontested ground truth is what makes a
truth-retention metric meaningful — and it removes an entire category of ethical objection as
a side effect. **The released corpus cannot function as disinformation about anything anyone
cares about.**

Two rules follow, and they are binding:

- **The fact suite stays scientifically inert.** Extending it to real-world, socially charged
  misinformation is Future Work *with an ethics review attached*, not a scope increase.
- **No real organisation, person, journal or identifier is named** in any injected string.
  Generic authority frames only (`fact-suite/README.md` §3). SPEC-3 v1.0 attributed fabricated
  claims to real scientific bodies; that is corrected and must not regress.

## 4. Release decisions

| Artefact | Ship? | Reasoning |
|---|---|---|
| Simulation engine, topology builders, memory operator | **Yes** | General-purpose multi-agent infrastructure; nothing misuse-specific |
| Metrics and analysis pipeline | **Yes** | The measurement contribution; useless to an attacker |
| Fact suite (31 candidates + retained set, with measured accuracies) | **Yes** | The benchmark contribution; inert by construction (§3) |
| Injection harness and seed-persona template | **Yes** | Necessary for reproducibility, and no more capable than a one-line prompt |
| Full logged trajectory dataset | **Yes**, after a scan | Durable scientific artefact (SOP-040 §2). Scan before release for anything inadvertently sensitive in generated text |
| Per-model vulnerability ranking | **Yes, with framing** | Publishable, but presented as a robustness evaluation, not a targeting guide. Report the measurement protocol so others can re-run it on their own models rather than treating our numbers as a league table |
| **Optimised / tuned persuasion prompts** | **NO** | See §5 |
| Automated prompt-optimisation loop against agent populations | **NO** | See §5 |

## 5. The one thing we do not ship, and why

**A ranked set of empirically most-effective persuasion prompts, and any code that searches
for them.**

H3 manipulates *stated certainty* while holding argument content fixed (AMD-0001 §2). That is
a controlled comparison of a linguistic variable, and reporting its effect is legitimate
science. What we will not do is invert it into an optimiser — searching prompt space for the
formulation that maximises cascade size, then publishing the winners ranked by efficacy.

The distinction is real:

- *"High stated certainty increases belief shift by X, holding content fixed"* is a
  **finding**. It informs defences (e.g. discount confident assertions from peers).
- *"Here are the twenty prompts that most reliably flip an 8B agent, in order"* is a
  **capability uplift**. It is directly operational, it transfers with no adaptation, and it
  does nothing for a defender that the aggregate finding does not already do.

This is the "tuned ranking" case flagged in `OQ-0022`, and the answer is no. If a reviewer
asks for it, the answer is still no, and this document is the reason.

**Consequence for the code:** H3's certainty manipulation uses a small, fixed, hand-written
template set, versioned and published. No search, no optimisation loop, no efficacy ranking
of individual prompt strings in the released artefacts.

## 6. What goes in the paper

A Broader Impact section stating §1 plainly, the §2 argument, the §3 design choice, and the
§5 withholding **with its reasoning**. Reviewers respond well to a specific, argued
withholding and poorly to a generic assurance that impact was considered.

## 7. Review triggers

This position is revisited if any of the following occur — recorded so the decision does not
silently expire:

- the fact suite is proposed to include socially charged content;
- any prompt-optimisation or search component is proposed;
- the framework is extended to agents with tool access or external side effects, which
  changes the harm model entirely;
- a collaborator or venue requests release of anything in the §4 "NO" row.

---

## Changelog

| Version | Date | Change | DR |
|---|---|---|---|
| 1.0 | 2026-08-07 | Initial issue; closes OQ-0022 | DR-0011 |
