"""NVIDIA API Catalog backend (OpenAI-compatible endpoint).

Implements the `Backend` protocol against `https://integrate.api.nvidia.com/v1`, per
`DR-0012`. The engine is unchanged — which is the payoff of having built against a protocol
boundary while we had no compute at all (`DR-0009`).

**Measured behaviour of this endpoint (2026-08-09), which shapes everything below:**

- The `/v1/models` listing is a **catalogue, not an availability list**. Of 13 UI-badged
  "free endpoint" models tested, 6 responded, 2 returned HTTP 410 ("has reached its ..."),
  and 5 timed out — one of them twice at a 180 s timeout, so not a cold start.
- Latency spans **233 ms to 56 s** on the same free tier.
- **Several models are reasoning models.** They emit chain-of-thought into
  `message.reasoning_content` and leave `message.content` empty until the budget allows them
  to finish. A 24-token budget yields *no answer at all*.

Consequences encoded here: availability is probed rather than assumed, `reasoning_content` is
handled explicitly, and every failure is returned as a structured error rather than a
placeholder string (SOP-040 §6).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Sequence

from .backends import Generation, ProbeAnswer, parse_true_false
from .memory import Message, TokenCounter, heuristic_token_count

__all__ = ["NvidiaBackend", "probe_availability"]

BASE_URL = "https://integrate.api.nvidia.com/v1"


@dataclass(slots=True)
class _Reply:
    content: str
    reasoning: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class NvidiaBackend:
    """One served model on the NVIDIA API Catalog.

    Args:
        model_id: Catalogue id, e.g. ``meta/llama-3.1-8b-instruct``.
        api_key: Defaults to ``$NVIDIA_API_KEY``. **Never hard-code a key** — `.env` is
            gitignored and a committed key must be rotated immediately (SOP-040 §1).
        is_reasoning: If True, allow a larger completion budget and read the answer out of
            whichever field the model populates. Detectable with :func:`probe_availability`.
        min_interval_s: Client-side spacing between calls. The free tier is rate-limited per
            minute; pacing here is cheaper than handling 429s.
        tokenizer: The model's own token counter. Strongly preferred over the heuristic —
            a shared counter would make the memory budget mean different amounts of text per
            family, and family composition *is* the manipulation (`CONFOUND-REGISTER` M5).
            HuggingFace tokenizers run on CPU, so this costs nothing even with no GPU.
    """

    def __init__(
        self,
        model_id: str,
        *,
        api_key: str | None = None,
        is_reasoning: bool = False,
        min_interval_s: float = 1.6,
        max_retries: int = 3,
        timeout_s: float = 90.0,
        tokenizer: TokenCounter | None = None,
    ) -> None:
        key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise RuntimeError(
                "NVIDIA_API_KEY is not set. Copy .env.example to .env and fill it in; "
                ".env is gitignored and must never be committed."
            )
        self.name = f"nvidia:{model_id}"
        self.model_id = model_id
        self._key = key
        self.is_reasoning = is_reasoning
        self.min_interval_s = min_interval_s
        self.max_retries = max_retries
        self.timeout_s = timeout_s
        self._counter = tokenizer or heuristic_token_count
        self._last_call = 0.0

    # ------------------------------------------------------------------ protocol

    def token_counter(self) -> TokenCounter:
        return self._counter

    def generate(
        self, *, system: str, turn: str, history: Sequence[Message],
        max_tokens: int, temperature: float, seed: int,
    ) -> Generation:
        messages = [{"role": "system", "content": system}]
        for m in history:
            messages.append({"role": "user", "content": f"[Agent {m.sender}] {m.content}"})
        messages.append({"role": "user", "content": turn})

        # A reasoning model spends most of its budget before saying anything, so give it room.
        budget = max_tokens * 8 if self.is_reasoning else max_tokens
        reply, error = self._chat(messages, max_tokens=budget, temperature=temperature, seed=seed)
        if error is not None:
            return Generation(text=None, error=error)

        text = reply.content or reply.reasoning
        if not text:
            # Budget exhausted mid-reasoning: no usable message. Recorded, not fabricated.
            return Generation(
                text=None, error="empty_completion",
                prompt_tokens=reply.prompt_tokens, completion_tokens=reply.completion_tokens,
            )
        return Generation(
            text=text,
            prompt_tokens=reply.prompt_tokens,
            completion_tokens=reply.completion_tokens,
            finish_reason=reply.finish_reason,
            meta={"used_reasoning_field": str(not reply.content)},
        )

    def probe(
        self, *, system: str, history: Sequence[Message], question: str, seed: int
    ) -> ProbeAnswer:
        messages = [{"role": "system", "content": system}]
        for m in history:
            messages.append({"role": "user", "content": f"[Agent {m.sender}] {m.content}"})
        messages.append({"role": "user", "content": question})

        # Probe budget is the dominant cost driver: the matrix is ~144k probes (AMD-0002).
        # A reasoning model needs ~100x the tokens of a direct answerer for the same bit of
        # information, which is why probe-model choice is a budget decision, not a detail.
        budget = 512 if self.is_reasoning else 8
        reply, error = self._chat(messages, max_tokens=budget, temperature=0.0, seed=seed)
        if error is not None:
            return ProbeAnswer(answer=None, error=error)

        raw = reply.content or reply.reasoning
        answer = parse_true_false(raw)
        if answer is None and reply.content and reply.reasoning:
            answer = parse_true_false(reply.content)  # prefer the final answer over the trace
        # An unparseable probe stays unparseable. Coercing it to a default would manufacture
        # belief states and bias the outcome under study (AMD-0002 §1.1).
        return ProbeAnswer(answer=answer, raw=(raw or "")[:200])

    # ------------------------------------------------------------------ transport

    def _chat(
        self, messages: list[dict], *, max_tokens: int, temperature: float, seed: int
    ) -> tuple[_Reply | None, str | None]:
        payload: dict = {
            "model": self.model_id,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if temperature > 0:
            payload["seed"] = seed  # best-effort; hosted determinism is not guaranteed

        body = json.dumps(payload).encode()
        last = "unknown_error"

        for attempt in range(self.max_retries):
            gap = time.monotonic() - self._last_call
            if gap < self.min_interval_s:
                time.sleep(self.min_interval_s - gap)

            req = urllib.request.Request(
                f"{BASE_URL}/chat/completions", data=body,
                headers={
                    "Authorization": f"Bearer {self._key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            self._last_call = time.monotonic()
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                    d = json.load(r)
                msg = d["choices"][0]["message"]
                usage = d.get("usage", {})
                return _Reply(
                    content=(msg.get("content") or "").strip(),
                    reasoning=(msg.get("reasoning_content") or "").strip(),
                    prompt_tokens=int(usage.get("prompt_tokens") or 0),
                    completion_tokens=int(usage.get("completion_tokens") or 0),
                    finish_reason=d["choices"][0].get("finish_reason") or "stop",
                ), None

            except urllib.error.HTTPError as e:
                last = f"http_{e.code}"
                if e.code == 429:  # rate limited -- back off and retry
                    time.sleep(2 ** attempt * 2)
                    continue
                if e.code == 410:  # model retired or at capacity -- retrying will not help
                    return None, "http_410_unavailable"
                if 400 <= e.code < 500:
                    return None, last
                time.sleep(2 ** attempt)
            except TimeoutError:
                last = "timeout"
                time.sleep(2 ** attempt)
            except Exception as e:  # noqa: BLE001 - transport errors are data, not crashes
                last = type(e).__name__
                time.sleep(2 ** attempt)

        return None, last


# ---------------------------------------------------------------------- availability


def probe_availability(model_ids: Sequence[str], *, api_key: str | None = None) -> list[dict]:
    """Check which catalogue entries actually serve, and whether they emit reasoning traces.

    **Run this before every experiment, and record the result with the run manifest.** The
    catalogue lists models it will not serve, and availability changed *during* our own
    testing. This is `RK-0005` (model availability) in its hosted form — and it already
    materialised once, on Groq.
    """
    out: list[dict] = []
    for mid in model_ids:
        be = NvidiaBackend(mid, api_key=api_key, min_interval_s=1.0, max_retries=1, timeout_s=60)
        t0 = time.monotonic()
        reply, error = be._chat(
            [{"role": "user", "content": "Reply with exactly one word: OK"}],
            max_tokens=16, temperature=0.0, seed=0,
        )
        out.append({
            "model_id": mid,
            "available": error is None,
            "error": error,
            "latency_ms": int((time.monotonic() - t0) * 1000),
            "emits_reasoning": bool(reply and reply.reasoning and not reply.content),
            "sample": ((reply.content or reply.reasoning)[:60] if reply else ""),
        })
    return out
