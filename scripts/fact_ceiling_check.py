"""Mini EXP-000 Part A: does the fact suite survive at each model size band?

The inclusion band is 0.25 <= accuracy <= 0.85 (fact-suite/README.md S2). Items at ceiling
cannot show movement, AND the truth-acquisition hazard needs agents that start wrong.
The suite was written for 7-9B models. If 26-80B models sit at ceiling, the band empties.
"""
import json, os, time, urllib.request, urllib.error
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
FACTS = json.loads(Path("docs/03-design/fact-suite/candidates.json").read_text(encoding="utf-8"))["items"]

ENDPOINTS = {
    "nvidia": ("https://integrate.api.nvidia.com/v1/chat/completions", os.environ["NVIDIA_API_KEY"]),
    "gmi":    ("https://api.gmi-serving.com/v1/chat/completions",      os.environ["GMI_API_KEY"]),
}
MODELS = [
    ("nvidia", "meta/llama-3.1-8b-instruct",        "8B   Meta"),
    ("gmi",    "google/gemma-4-26b-a4b-it",         "26B  Google"),
    ("gmi",    "Qwen/Qwen3-Next-80B-A3B-Instruct",  "80B  Alibaba"),
]

def ask(prov, model, prompt):
    url, key = ENDPOINTS[prov]
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 8, "temperature": 0.0}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        m = d["choices"][0]["message"]
        return ((m.get("content") or m.get("reasoning_content") or "")).strip().upper()
    except Exception:
        return None

def verdict(txt):
    if txt is None: return None
    t, f = "TRUE" in txt, "FALSE" in txt
    return None if t == f else t

# 12 items spanning the difficulty range
SAMPLE = [FACTS[i] for i in (0, 2, 6, 7, 10, 13, 14, 15, 17, 19, 23, 27)]
print(f"{'fact':<7}{'domain':<12}", end="", flush=True)
for _, _, lab in MODELS: print(f"{lab:<14}", end="")
print(flush=True)
print("-" * 62, flush=True)

score = {lab: [] for _, _, lab in MODELS}
for it in SAMPLE:
    print(f"{it['id']:<7}{it['domain'][:11]:<12}", end="", flush=True)
    for prov, model, lab in MODELS:
        q = (f"Is this statement true or false?\n\"{it['s_true']}\"\n"
             "Answer with one word: TRUE or FALSE.")
        v = verdict(ask(prov, model, q))
        score[lab].append(v)
        print(f"{('OK' if v is True else 'wrong' if v is False else '?'):<14}", end="", flush=True)
        time.sleep(0.7)
    print(flush=True)

print(flush=True)
print("accuracy on s_true (higher = closer to ceiling):", flush=True)
for _, _, lab in MODELS:
    vals = [v for v in score[lab] if v is not None]
    acc = sum(vals) / len(vals) if vals else float("nan")
    band = "IN BAND" if 0.25 <= acc <= 0.85 else ("CEILING" if acc > 0.85 else "FLOOR")
    print(f"  {lab:<14} {acc:.2f}  n={len(vals):<3} {band}", flush=True)
print("DONE", flush=True)
