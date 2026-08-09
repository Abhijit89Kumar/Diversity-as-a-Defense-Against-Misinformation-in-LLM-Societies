import json, os, sys, time, urllib.request, urllib.error

KEY = os.environ["NVIDIA_API_KEY"]
URL = "https://integrate.api.nvidia.com/v1/chat/completions"
CANDIDATES = [
    "meta/llama-3.1-8b-instruct",
    "nvidia/nvidia-nemotron-nano-9b-v2",
    "nvidia/llama-3.1-nemotron-nano-8b-v1",
    "nvidia/nemotron-mini-4b-instruct",
    "meta/llama-3.2-3b-instruct",
    "qwen/qwen3-next-80b-a3b-instruct",
    "openai/gpt-oss-20b",
    "mistralai/mixtral-8x7b-instruct-v0.1",
    "mistralai/mistral-nemotron",
    "google/gemma-4-31b-it",
    "z-ai/glm-5.2",
    "meta/llama-3.3-70b-instruct",
    "nvidia/nemotron-3-nano-30b-a3b",
]
PROBE = ('Is this statement true or false?\n'
         '"The adult human skeleton normally contains 206 bones."\n'
         'Answer with one word: TRUE or FALSE.')

def extract(msg):
    for k in ("content", "reasoning_content"):
        v = msg.get(k)
        if v:
            return k, v.strip().replace("\n", " ")[:44]
    return "empty", ""

ok = []
print(f"{'model':<44}{'http':>5}{'ms':>7}  field / answer", flush=True)
print("-" * 96, flush=True)
for m in CANDIDATES:
    body = json.dumps({"model": m,
                       "messages": [{"role": "user", "content": PROBE}],
                       "max_tokens": 24, "temperature": 0.0}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "Accept": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.load(r)
        ms = int((time.time() - t0) * 1000)
        field, txt = extract(d["choices"][0]["message"])
        u = d.get("usage", {})
        print(f"{m:<44}{200:>5}{ms:>7}  [{field}] {txt!r} in={u.get('prompt_tokens','?')} out={u.get('completion_tokens','?')}", flush=True)
        if txt:
            ok.append((m, ms, field))
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            detail = str(json.loads(raw).get("detail", raw))[:58]
        except Exception:
            detail = raw[:58]
        print(f"{m:<44}{e.code:>5}{'':>7}  {detail}", flush=True)
    except Exception as e:
        print(f"{m:<44}{'ERR':>5}{'':>7}  {type(e).__name__}: {str(e)[:50]}", flush=True)
    time.sleep(0.8)

print(f"\nWORKING: {len(ok)}/{len(CANDIDATES)}", flush=True)
for m, ms, f in ok:
    print(f"  {m:<44} {ms:>6} ms  ({f})", flush=True)
