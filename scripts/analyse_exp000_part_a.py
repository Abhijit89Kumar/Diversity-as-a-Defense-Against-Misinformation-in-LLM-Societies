"""EXP-000 Part A analysis — capability, fact validation, diversity, probe reliability.

Reads the immutable raw probe log and produces the artefacts listed in
`experiments/EXP-000/README.md` §5. Analysis is a pure function of logged data and never
re-hits an API (SOP-040 §2).

Run:
    python scripts/analyse_exp000_part_a.py --data experiments/EXP-000/data
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]

# fact-suite/README.md v0.2 §2 -- fixed BEFORE this data existed.
RETENTION_BAND = (0.70, 0.97)
ACQUISITION_BAND = (0.20, 0.65)
PER_MODEL_MIN, PER_MODEL_MAX = 0.05, 0.99
S_FALSE_MAX = 0.15
MIN_RETENTION, MIN_ACQUISITION = 10, 6
MIN_REASONING_ACQ = 3
H_RANGE_MIN = 0.15  # OQ-0051


def majority(series: pd.Series) -> float:
    """Fraction of parseable probes answering TRUE."""
    vals = series.dropna()
    return float(vals.mean()) if len(vals) else float("nan")


def load(data_dir: Path) -> pd.DataFrame:
    rows = [json.loads(l) for l in (data_dir / "raw_probes.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["answer"] = df["answer"].astype("object").where(df["answer"].notna(), None)
    return df


def diversity_measures(correct: np.ndarray) -> dict:
    """Diversity over a (n_models, n_items) 0/1 correctness matrix.

    Three measures, deliberately. Kim (arXiv:2607.20768) shows the joint-correctness proxy is
    collinear with (1 - mean accuracy) at rho = 0.991, so reporting it alone would be close to
    reporting accuracy twice (`OQ-0051`). The chance-corrected companions are the check.
    """
    n = correct.shape[0]
    if n < 2:
        return {"H_errorcorr": 0.0, "H_disagreement": 0.0, "Q_statistic": float("nan")}
    corrs, disagree, qs = [], [], []
    for i, j in itertools.combinations(range(n), 2):
        a, b = correct[i], correct[j]
        if a.std() == 0 or b.std() == 0:
            corrs.append(1.0)  # no variance -> treat as perfectly correlated
        else:
            corrs.append(float(np.corrcoef(a, b)[0, 1]))
        disagree.append(float((a != b).mean()))
        n11 = float(((a == 1) & (b == 1)).sum()); n00 = float(((a == 0) & (b == 0)).sum())
        n10 = float(((a == 1) & (b == 0)).sum()); n01 = float(((a == 0) & (b == 1)).sum())
        denom = n11 * n00 + n01 * n10
        qs.append((n11 * n00 - n01 * n10) / denom if denom else float("nan"))
    return {
        "H_errorcorr": 1.0 - float(np.mean(corrs)),
        "H_disagreement": float(np.mean(disagree)),
        "Q_statistic": float(np.nanmean(qs)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=REPO / "experiments" / "EXP-000" / "data")
    args = ap.parse_args()
    df = load(args.data)

    ok = df[df["ok"] == True]  # noqa: E712
    print(f"records {len(df)} | ok {len(ok)} | failed {len(df) - len(ok)}")
    unparse = ok["answer"].isna().mean()
    print(f"unparseable rate {unparse:.3%}\n")

    # ---------------------------------------------------------------- accuracy per model x fact
    base = ok[~ok["swap_order"]]
    acc = (base[base["claim"] == "s_true"]
           .groupby(["model_id", "lineage", "fact_id", "construct", "stratum_prior"])["answer"]
           .apply(majority).rename("acc_true").reset_index())
    fal = (base[base["claim"] == "s_false"]
           .groupby(["model_id", "fact_id"])["answer"]
           .apply(majority).rename("endorse_false").reset_index())
    acc = acc.merge(fal, on=["model_id", "fact_id"], how="left")
    acc.to_csv(args.data / "accuracy_by_model_fact.csv", index=False)

    per_model = acc.groupby(["model_id", "lineage"])["acc_true"].agg(["mean", "std", "count"])
    print("ISOLATED ACCURACY (D1)")
    print(per_model.round(3).to_string(), "\n")

    # ---------------------------------------------------------------- fact validation (C3)
    item = acc.groupby(["fact_id", "construct", "stratum_prior"]).agg(
        pool_acc=("acc_true", "mean"), min_model=("acc_true", "min"),
        max_model=("acc_true", "max"), false_max=("endorse_false", "max")).reset_index()

    def classify(r):
        if r.false_max > S_FALSE_MAX:
            return "excluded:endorses_falsehood"
        if not (PER_MODEL_MIN <= r.min_model and r.max_model <= PER_MODEL_MAX):
            return "excluded:per_model_bounds"
        if RETENTION_BAND[0] <= r.pool_acc <= RETENTION_BAND[1]:
            return "retention"
        if ACQUISITION_BAND[0] <= r.pool_acc <= ACQUISITION_BAND[1]:
            return "acquisition"
        return "excluded:out_of_band"

    item["stratum"] = item.apply(classify, axis=1)
    item = item.sort_values("pool_acc", ascending=False)
    item.to_csv(args.data / "fact_validation.csv", index=False)

    counts = item["stratum"].value_counts().to_dict()
    print("FACT VALIDATION (C3)")
    for k, v in sorted(counts.items()):
        print(f"  {k:<32} {v}")
    ret = int(counts.get("retention", 0)); acq = int(counts.get("acquisition", 0))
    reasoning_acq = int(((item.stratum == "acquisition") & (item.construct == "reasoning")).sum())
    print(f"\n  retention {ret} (need >={MIN_RETENTION})   "
          f"acquisition {acq} (need >={MIN_ACQUISITION})   "
          f"reasoning-in-acquisition {reasoning_acq} (need >={MIN_REASONING_ACQ})")
    passed = ret >= MIN_RETENTION and acq >= MIN_ACQUISITION and reasoning_acq >= MIN_REASONING_ACQ
    print(f"  SUITE VALIDATION: {'PASS' if passed else 'FAIL - recruit more items'}\n")

    retained = item[item.stratum.isin(["retention", "acquisition"])]["fact_id"].tolist()
    (args.data / "retained_facts.json").write_text(json.dumps({
        "retention": item[item.stratum == "retention"]["fact_id"].tolist(),
        "acquisition": item[item.stratum == "acquisition"]["fact_id"].tolist(),
        "excluded": item[item.stratum.str.startswith("excluded")][
            ["fact_id", "stratum", "pool_acc"]].to_dict("records"),
        "rules": {"retention_band": RETENTION_BAND, "acquisition_band": ACQUISITION_BAND,
                  "s_false_max": S_FALSE_MAX, "per_model_bounds": [PER_MODEL_MIN, PER_MODEL_MAX]},
        "validation_passed": bool(passed),
    }, indent=2), encoding="utf-8")

    # ---------------------------------------------------------------- diversity (D2, OQ-0051)
    grid = acc[acc.fact_id.isin(retained)].pivot_table(
        index="model_id", columns="fact_id", values="acc_true")
    correct = (grid.round() == 1).astype(int).to_numpy()
    models = list(grid.index)

    rows = []
    for r in range(2, len(models) + 1):
        for combo in itertools.combinations(range(len(models)), r):
            m = diversity_measures(correct[list(combo)])
            rows.append({"cohort": "+".join(models[i].split("/")[-1][:14] for i in combo),
                         "k": r, "a_bar": float(grid.iloc[list(combo)].mean().mean()), **m})
    div = pd.DataFrame(rows).sort_values("H_errorcorr")
    div.to_csv(args.data / "diversity_by_cohort.csv", index=False)

    h_lo, h_hi = float(div.H_errorcorr.min()), float(div.H_errorcorr.max())
    # The ladder spans D0 (identical models, H = 0 by construction) to the most diverse cohort.
    h_range = h_hi - 0.0
    print("DIVERSITY (D2) and the OQ-0051 range check")
    print(f"  H_errorcorr across {len(div)} candidate cohorts: {h_lo:.3f} to {h_hi:.3f}")
    print(f"  ladder range vs D0 (H=0): {h_range:.3f}   criterion >= {H_RANGE_MIN}")
    print(f"  OQ-0051: {'PASS - H1 estimable' if h_range >= H_RANGE_MIN else 'FAIL - H1 NOT estimable as specified'}")
    if len(div):
        best = div.iloc[-1]
        print(f"  most diverse: {best.cohort}  H={best.H_errorcorr:.3f}  "
              f"disagreement={best.H_disagreement:.3f}  Q={best.Q_statistic:.3f}")
    # Kim's collinearity check on our own data
    if len(div) > 3:
        rho = np.corrcoef(div.H_errorcorr, 1 - div.a_bar)[0, 1]
        print(f"  corr(H_errorcorr, 1 - a_bar) = {rho:+.3f}   "
              f"(Kim reports rho = 0.991 for this measure family)")
    print()

    (args.data / "diversity_range.json").write_text(json.dumps({
        "h_min": h_lo, "h_max": h_hi, "ladder_range_vs_D0": h_range,
        "criterion": H_RANGE_MIN, "passed": bool(h_range >= H_RANGE_MIN),
        "n_cohorts_evaluated": len(div),
    }, indent=2), encoding="utf-8")

    # ---------------------------------------------------------------- probe reliability (V1/V2)
    agree = (base.dropna(subset=["answer"])
             .groupby(["model_id", "fact_id", "claim"])["answer"]
             .apply(lambda s: max(s.mean(), 1 - s.mean())))
    swapped = ok[ok.fact_id.isin(ok[ok.swap_order]["fact_id"].unique())]
    order = (swapped.dropna(subset=["answer"])
             .groupby(["model_id", "fact_id", "claim", "swap_order"])["answer"].mean()
             .unstack("swap_order"))
    order_delta = (order[True] - order[False]).abs().dropna() if order.shape[1] == 2 else pd.Series(dtype=float)

    rel = pd.DataFrame({"paraphrase_agreement": agree.groupby("model_id").median()})
    rel["order_sensitivity"] = order_delta.groupby("model_id").mean()
    rel.to_csv(args.data / "probe_reliability.csv")
    print("PROBE RELIABILITY (V1 / V2)")
    print(rel.round(3).to_string())
    med = float(agree.median())
    print(f"\n  median paraphrase agreement {med:.3f}  criterion >= 0.80  "
          f"-> {'PASS' if med >= 0.80 else 'FAIL - stop and redesign'}")
    if len(order_delta):
        print(f"  mean |order effect| {order_delta.mean():.3f}")
    print()

    # ---------------------------------------------------------------- cost & timing (E1)
    timing = ok.groupby("model_id").agg(
        calls=("ms", "size"), p50_ms=("ms", "median"),
        in_tok=("in", "mean"), out_tok=("out", "mean"))
    timing["total_in"] = ok.groupby("model_id")["in"].sum()
    timing["total_out"] = ok.groupby("model_id")["out"].sum()
    timing.to_csv(args.data / "cost_and_timing.csv")
    print("COST & TIMING (E1)")
    print(timing.round(1).to_string())
    print(f"\n  total calls {len(df)}, input tokens {int(ok['in'].sum()):,}, "
          f"output tokens {int(ok['out'].sum()):,}")
    fails = df[df["ok"] == False]  # noqa: E712
    if len(fails):
        print(f"  failures by type: {fails['error'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
