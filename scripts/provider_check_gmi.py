import json, os, time, urllib.request, urllib.error
KEY = os.environ["GMI_API_KEY"]
URL = "https://api.gmi-serving.com/v1/chat/completions"
UA  = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
PROBE = ('Is this statement true or false?\n'
         '"The adult human skeleton normally contains 206 bones."\n'
         'Answer with one word: TRUE or FALSE.')

# Open-weight models only, spanning distinct pretraining lineages.
MODELS = [
    ("google/gemma-4-26b-a4b-it",          "Google"),
    ("google/gemma-4-31b-it",              "Google"),
    ("Qwen/Qwen3.5-27B",                   "Alibaba"),
    ("Qwen/Qwen3.5-35B-A3B",               "Alibaba"),
    ("Qwen/Qwen3-Next-80B-A3B-Instruct",   "Alibaba"),
    ("deepseek-ai/DeepSeek-V4-Flash",      "DeepSeek"),
    ("zai-org/GLM-4.7-FP8",                "Zhipu"),
    ("MiniMaxAI/MiniMax-M3",               "MiniMax"),
    ("moonshotai/Kimi-K2.5",               "Moonshot"),
    ("XiaomiMiMo/MiMo-V2.5",               "Xiaomi"),
    ("bytedance/seed-2.0-mini",            "ByteDance"),
    ("tencent/Hy3",                        "Tencent"),
]
print(f"{'model':<38}{'lineage':<11}{'http':>5}{'ms':>7}  answer  tokens(in/out)", flush=True)
print("-" * 96, flush=True)
ok = []
for m, lin in MODELS:
    body = json.dumps({"model": m, "messages": [{"role": "user", "content": PROBE}],
                       "max_tokens": 16, "temperature": 0.0}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": UA, "Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=75) as r:
            d = json.load(r)
        ms = int((time.time() - t0) * 1000)
        msg = d["choices"][0]["message"]
        c = (msg.get("content") or "").strip().replace("\n", " ")
        rc = (msg.get("reasoning_content") or "").strip()
        u = d.get("usage", {})
        flag = " [REASONING]" if (rc and not c) else ""
        print(f"{m:<38}{lin:<11}{200:>5}{ms:>7}  {c[:14]!r}{flag}  {u.get('prompt_tokens')}/{u.get('completion_tokens')}", flush=True)
        if c and not rc:
            ok.append((m, lin, ms))
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: msg2 = json.loads(raw)["error"]["message"][:44]
        except Exception: msg2 = raw[:44]
        print(f"{m:<38}{lin:<11}{e.code:>5}{'':>7}  {msg2}", flush=True)
    except Exception as e:
        print(f"{m:<38}{lin:<11}{'ERR':>5}{'':>7}  {type(e).__name__}", flush=True)
    time.sleep(1.0)

print(f"\nDIRECT-ANSWER MODELS: {len(ok)}", flush=True)
seen = set()
for m, lin, ms in ok:
    mark = "" if lin in seen else "  <- new lineage"
    seen.add(lin)
    print(f"  {m:<40} {lin:<10} {ms:>6}ms{mark}", flush=True)
print(f"\ndistinct lineages with a working direct-answer model: {len(seen)}", flush=True)
print("DONE", flush=True)
