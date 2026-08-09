# Literature Search Log

Every search is recorded here: date, channel, query, hits, triaged in. An unrecorded
search cannot be trusted to have happened and cannot be re-run when a reviewer asks
"did you consider X?". Rules: SOP-020 §1.

Mandatory re-runs of the Tier-A queries at **G1**, **G3**, and **G5**.

| Date | Channel | Query | Hits | Triaged in | By |
|---|---|---|---|---|---|
| 2026-08-07 | Multi-channel automated sweep, round 1 | 5 angles: novelty/prior art; heterogeneity evidence; belief-measurement validity; simulation-study statistics; 2026 provider/cost/deadline reality | 27 sources fetched, 135 claims extracted | 25 adversarially verified → 12 confirmed, 13 refuted. 5 Tier-A, 5 Tier-B identified. | AI-assisted (Claude Opus 5) |
| 2026-08-08 | **Systematic channel sweep (G1 A1)** | ACL Anthology; GitHub/HF/code; AAMAS/WWW/ICWSM/CSCW/JASSS/PRE/PNAS/NHB; arXiv cs.MA/CL/AI/SI/CY/CR/LG + physics.soc-ph; **OpenReview submissions AND reviews**; forward-citation on Becker, Sela, Nilayam, Choi | **252 queries, 185 findings** | 5 highest-threat verified by hand against arXiv; rest `[UNVERIFIED]`. Raw output: `sweeps/2026-08-08-G1-A1-raw.json` | AI-assisted (Claude Opus 5) |
| 2026-08-07 | Automated sweep, round 2 | Verify 7 unfetched arXiv leads; belief-measurement validity; statistical standards & reviewer critique; provider free-tier limits & ToS; Modal/annotation/deadline logistics | in flight | in flight | AI-assisted (Claude Opus 5) |

**Round 1 coverage gap, recorded honestly:** only angles 1 and 2 produced surviving verified
claims. Feasibility (provider limits, Modal cost, annotator pay, deadlines) produced *none*,
and belief-measurement and statistics were answered only partially. Round 2 targets exactly
those gaps. Until it returns, **the budget and 8-week timeline are entirely unvetted.**

---

## Coverage checklist (SOP-020 §1)

For the G1 sweep, each channel must be marked done with a date:

- [x] arXiv — cs.MA
- [x] arXiv — cs.CL
- [x] arXiv — cs.AI
- [x] arXiv — cs.SI
- [x] arXiv — cs.CY
- [x] ACL Anthology
- [x] OpenReview (submissions **and reviews**) — threads located, incl. Becker et al. `N4Cq7phkDY`; **reviewer text not yet read**
- [x] Semantic Scholar / Google Scholar citation-graph traversal
- [x] AAMAS / WWW / ICWSM / CSCW proceedings
- [x] GitHub (existing implementations)
- [~] **Forward citation search** — done for Becker, Sela, Nilayam, Choi; **NetSafe and Zhu et al. outstanding**
- [~] **Backward citation search** — partial, folded into the forward passes

## Query bank

Maintained so the sweeps are repeatable. Add new productive queries as they are found.

**Novelty / direct competitors**
- misinformation propagation LLM multi-agent network
- manipulated knowledge spread LLM agent community
- false belief cascade language model agents
- multi-agent LLM network topology safety / robustness
- malicious agent multi-agent LLM system resilience
- LLM agent society simulation opinion dynamics
- conformity peer pressure LLM agents
- sycophancy multi-agent debate

**Heterogeneity**
- heterogeneous model multi-agent debate accuracy
- mixture of agents ensemble LLM
- diversity of thought LLM ensemble
- multi-agent debate ablation negative result

**Belief measurement**
- LLM calibration true false token probability
- verbalized confidence vs logit confidence LLM
- paraphrase consistency belief probing language model
- do language models have beliefs
- prompt sensitivity option order bias multiple choice LLM

**Method / statistics**
- reproducibility multi-agent LLM simulation
- statistical practice LLM evaluation seeds variance
- pseudoreplication nested design simulation study
