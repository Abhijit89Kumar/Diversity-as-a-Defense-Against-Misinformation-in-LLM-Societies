"""Measured availability, reliability and reasoning behaviour across both providers.

Produces the evidence behind `MODEL-POOL.md` (`OQ-0055`). Required because the NVIDIA
`/v1/models` catalogue lists models it will not serve, and availability changed *during*
`EXP-A03` (`RK-0005` in its hosted form).

Run:
    python scripts/provider_sweep.py --out experiments/EXP-A04

Deliberately sequential. Parallel workers against a shared rate-limited endpoint produce
429s and corrupt the latency measurements this script exists to collect.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PROBE = ('Is this statement true or false?\n'
         '"The adult human skeleton normally contains 206 bones."\n'
         'Answer with one word: TRUE or FALSE.')

ENDPOINTS = {
    "nvidia": "https://integrate.api.nvidia.com/v1/chat/completions",
    "gmi": "https://api.gmi-serving.com/v1/chat/completions",
}

# (provider, model_id, lineage, reasoning_control)
# reasoning_control: None | "no_think" | "effort_low"  -- see EXP-A03 §1.1
CANDIDATES = [
    # --- NVIDIA free endpoints
    ("nvidia", "meta/llama-3.1-8b-instruct",           "Meta",     None),
    ("nvidia", "nvidia/nemotron-mini-4b-instruct",     "NVIDIA",   None),
    ("nvidia", "nvidia/nvidia-nemotron-nano-9b-v2",    "NVIDIA",   "no_think"),
    ("nvidia", "nvidia/nemotron-3-nano-30b-a3b",       "NVIDIA",   "no_think"),
    ("nvidia", "openai/gpt-oss-20b",                   "OpenAI",   "effort_low"),
    ("nvidia", "openai/gpt-oss-120b",                  "OpenAI",   "effort_low"),
    ("nvidia", "mistralai/mistral-nemotron",           "Mistral",  None),
    ("nvidia", "meta/llama-3.1-70b-instruct",          "Meta",     None),
    ("nvidia", "nvidia/llama-3.3-nemotron-super-49b-v1.5", "NVIDIA", "no_think"),
    ("nvidia", "minimaxai/minimax-m3",                 "MiniMax",  None),
    # --- GMI (open weights only; closed frontier APIs are out of scope)
    ("gmi", "google/gemma-4-26b-a4b-it",               "Google",   None),
    ("gmi", "google/gemma-4-31b-it",                   "Google",   None),
    ("gmi", "Qwen/Qwen3-Next-80B-A3B-Instruct",        "Alibaba",  None),
    ("gmi", "Qwen/Qwen3.5-27B",                        "Alibaba",  None),
    ("gmi", "Qwen/Qwen3.6-35B-A3B",                    "Alibaba",  None),
    ("gmi", "MiniMaxAI/MiniMax-M3",                    "MiniMax",  None),
    ("gmi", "moonshotai/Kimi-K2.5",                    "Moonshot", None),
    ("gmi", "deepseek-ai/DeepSeek-V3.2",               "DeepSeek", None),
    ("gmi", "zai-org/GLM-5.2-FP8",                     "Zhipu",    None),
    ("gmi", "XiaomiMiMo/MiMo-V2.5",                    "Xiaomi",   None),
]

N_TRIALS = 3


def call(provider: str, model: str, control: str | None, timeout: float = 45.0) -> dict:
    key = os.environ["NVIDIA_API_KEY" if provider == "nvidia" else "GMI_API_KEY"]
    system = "/no_think\nYou answer factual questions." if control == "no_think" \
        else "You answer factual questions."
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": PROBE}],
        "max_tokens": 16, "temperature": 0.0,
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
        content = (msg.get("content") or "").strip()
        reasoning = (msg.get("reasoning_content") or "").strip()
        u = d.get("usage", {}) or {}
        text = (content or reasoning).upper()
        answer = None
        if ("TRUE" in text) != ("FALSE" in text):
            answer = "TRUE" in text
        return {"ok": True, "ms": int((time.time() - t0) * 1000),
                "answer": answer, "leaked_reasoning": bool(reasoning),
                "in": u.get("prompt_tokens"), "out": u.get("completion_tokens")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"http_{e.code}"}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--trials", type=int, default=N_TRIALS)
    args = ap.parse_args()

    print(f"{'provider':<9}{'model':<44}{'lineage':<10}{'ok':>5}{'p50 ms':>8}{'out':>5}  notes",
          flush=True)
    print("-" * 104, flush=True)

    results = []
    for provider, model, lineage, control in CANDIDATES:
        trials = [call(provider, model, control) for _ in range(args.trials)]
        good = [t for t in trials if t["ok"]]
        rec = {
            "provider": provider, "model_id": model, "lineage": lineage,
            "reasoning_control": control, "trials": args.trials,
            "n_ok": len(good),
            "reliability": len(good) / args.trials,
            "p50_ms": int(statistics.median([t["ms"] for t in good])) if good else None,
            "completion_tokens": good[0]["out"] if good else None,
            "leaked_reasoning": any(t.get("leaked_reasoning") for t in good),
            "answers": [t.get("answer") for t in good],
            "errors": sorted({t["error"] for t in trials if not t["ok"]}),
        }
        results.append(rec)
        note = ""
        if rec["errors"]:
            note = ",".join(rec["errors"])
        elif rec["leaked_reasoning"]:
            note = "leaks reasoning"
        elif len(set(rec["answers"])) > 1:
            note = "INCONSISTENT across trials"
        print(f"{provider:<9}{model:<44}{lineage:<10}"
              f"{rec['n_ok']}/{args.trials:<3}"
              f"{(rec['p50_ms'] if rec['p50_ms'] is not None else 0):>8}"
              f"{(rec['completion_tokens'] or 0):>5}  {note}", flush=True)
        time.sleep(0.5)

    usable = [r for r in results if r["reliability"] == 1.0 and not r["leaked_reasoning"]]
    lineages = sorted({r["lineage"] for r in usable})
    print(f"\nFully reliable, clean-answer models: {len(usable)}/{len(results)}", flush=True)
    print(f"Distinct lineages available: {len(lineages)} -> {', '.join(lineages)}", flush=True)
    for r in sorted(usable, key=lambda x: x["p50_ms"]):
        print(f"  {r['provider']:<8}{r['model_id']:<44}{r['lineage']:<10}{r['p50_ms']:>6} ms",
              flush=True)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "provider_sweep.json").write_text(json.dumps({
            "swept_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "trials_per_model": args.trials,
            "results": results,
            "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        }, indent=2), encoding="utf-8")
        print(f"\nwrote {args.out / 'provider_sweep.json'}", flush=True)
    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
