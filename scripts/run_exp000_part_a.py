"""EXP-000 Part A — isolated baseline.

Every candidate model answers every candidate fact **alone**, with no communication. Closes
G1 rows **D1** (isolated accuracy per model), **C3** (fact validation against the stratified
inclusion rules) and contributes to **D2** (`H(c)`) and **E1** (tokens and timing).

Part A is also the **isolated control arm** required by `OQ-0026`, so it is a reportable
condition rather than throwaway pilot work.

Design of record: `fact-suite/README.md` v0.2 (stratified rules), `MODEL-POOL.md` v0.2,
`AMD-0002 §1` (both claims probed separately, majority over M paraphrases).

Run:
    python scripts/run_exp000_part_a.py --out experiments/EXP-000/data

Concurrency is **one worker per model**. Each model is queried sequentially within its own
worker, which respects per-model rate limits while keeping wall-clock bounded. Firing many
workers at one model would produce 429s and contaminate the timing record.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from llm_society_sim.prompts import TEMPLATE_VERSION, probe_prompts, template_hash  # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
ENDPOINTS = {
    "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
    "gmi": "https://api.gmi-serving.com/v1/chat/completions",
}

# From MODEL-POOL.md v0.2 §4, all measured reliable in EXP-A04.
# (provider, model_id, lineage, reasoning_control, min_interval_s)
POOL = [
    ("gmi", "Qwen/Qwen3-Next-80B-A3B-Instruct", "Alibaba", None, 0.4),
    ("gmi", "deepseek-ai/DeepSeek-V3.2", "DeepSeek", None, 0.4),
    ("gmi", "MiniMaxAI/MiniMax-M3", "MiniMax", None, 0.4),
    ("gmi", "moonshotai/Kimi-K2.5", "Moonshot", None, 0.4),
    ("nvidia", "meta/llama-3.1-8b-instruct", "Meta", None, 0.6),
    ("nvidia", "nvidia/nvidia-nemotron-nano-9b-v2", "NVIDIA", "no_think", 0.6),
]

SYSTEM = "You answer factual questions."
_write_lock = threading.Lock()


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()
    except Exception:
        return "unknown"


def call(provider, model, control, question, timeout=45.0):
    key = os.environ["NVIDIA_API_KEY" if provider == "nvidia" else "GMI_API_KEY"]
    system = ("/no_think\n" + SYSTEM) if control == "no_think" else SYSTEM
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": question}],
        "max_tokens": 24, "temperature": 0.0,
    }
    if control == "effort_low":
        payload["reasoning_effort"] = "low"
    req = urllib.request.Request(
        ENDPOINTS[provider], data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": UA, "Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.load(r)
        msg = d["choices"][0]["message"]
        raw = ((msg.get("content") or "") + " " + (msg.get("reasoning_content") or "")).strip()
        u = d.get("usage", {}) or {}
        up = raw.upper()
        # Unparseable stays unparseable -- never coerced (AMD-0002 §1.1).
        answer = ("TRUE" in up) if (("TRUE" in up) != ("FALSE" in up)) else None
        return {"ok": True, "ms": int((time.time() - t0) * 1000), "answer": answer,
                "raw": raw[:120], "in": u.get("prompt_tokens"), "out": u.get("completion_tokens"),
                "served_model": d.get("model")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "ms": int((time.time() - t0) * 1000), "error": f"http_{e.code}"}
    except Exception as e:
        return {"ok": False, "ms": int((time.time() - t0) * 1000), "error": type(e).__name__}


def worker(spec, facts, n_para, swap_subset, sink, progress):
    provider, model, lineage, control, gap = spec
    for fi, item in enumerate(facts):
        for claim_key in ("s_true", "s_false"):
            orders = (False, True) if item["id"] in swap_subset else (False,)
            for swap in orders:
                for k, q in enumerate(probe_prompts(item[claim_key], n_para, swap_order=swap)):
                    res = call(provider, model, control, q)
                    rec = {
                        "provider": provider, "model_id": model, "lineage": lineage,
                        "fact_id": item["id"], "claim": claim_key, "paraphrase": k,
                        "swap_order": swap, "stratum_prior": item["stratum_prior"],
                        "construct": item["construct"], **res,
                    }
                    with _write_lock:
                        sink.write(json.dumps(rec) + "\n")
                        sink.flush()
                    time.sleep(gap)
        progress[model] = fi + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "experiments" / "EXP-000" / "data")
    ap.add_argument("--paraphrases", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="debug: cap number of facts")
    args = ap.parse_args()

    facts = json.loads((REPO / "docs/03-design/fact-suite/candidates.json")
                       .read_text(encoding="utf-8"))["items"]
    if args.limit:
        facts = facts[: args.limit]
    # Option-order nuisance check (V2) on a subset -- doubling every item would double cost
    # for a nuisance estimate that does not need item-level resolution.
    swap_subset = {f["id"] for f in facts[::4]}

    args.out.mkdir(parents=True, exist_ok=True)
    raw_path = args.out / "raw_probes.jsonl"

    per_model = len(facts) * 2 * args.paraphrases + len(swap_subset) * 2 * args.paraphrases
    print(f"facts={len(facts)}  models={len(POOL)}  paraphrases={args.paraphrases}")
    print(f"order-swap subset={len(swap_subset)} items")
    print(f"~{per_model} calls per model, ~{per_model * len(POOL)} total\n", flush=True)

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    progress: dict = {}
    t0 = time.time()
    with raw_path.open("w", encoding="utf-8") as sink:
        threads = [threading.Thread(target=worker,
                                    args=(s, facts, args.paraphrases, swap_subset, sink, progress),
                                    daemon=True) for s in POOL]
        for t in threads:
            t.start()
        while any(t.is_alive() for t in threads):
            time.sleep(20)
            done = ", ".join(f"{m.split('/')[-1][:18]}={n}" for m, n in sorted(progress.items()))
            print(f"  [{int(time.time()-t0):>4}s] {done}", flush=True)
        for t in threads:
            t.join()

    manifest = {
        "experiment": "EXP-000-PartA",
        "started_utc": started,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "prompt_template_version": TEMPLATE_VERSION,
        "prompt_template_hash": template_hash(),
        "fact_suite_version": "0.2",
        "n_facts": len(facts),
        "n_paraphrases": args.paraphrases,
        "order_swap_subset": sorted(swap_subset),
        "pool": [{"provider": p, "model_id": m, "lineage": l, "reasoning_control": c}
                 for p, m, l, c, _ in POOL],
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nwrote {raw_path} and manifest.json", flush=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
