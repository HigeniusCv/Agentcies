"""Unified multi-provider LLM client with logprob support where available.

The scientific reason this module exists: a Likert response read as a *single
sampled token* is a high-variance measurement. Read as a *probability
distribution over the tokens "1".."5"*, it becomes a continuous, low-variance
measurement, which changes the power calculation by roughly an order of
magnitude (see docs/04-ANALYSIS-AND-POWER.md).

Provider capability matrix (as configured here):

    provider    logprobs   seed    notes
    ---------   --------   -----   ---------------------------------------
    openai      yes        yes     top_logprobs up to 20
    anthropic   no         no      sampled readout only; use replicates
    gemini      partial    no      response_logprobs; availability varies
    ollama      no*        yes     *swap for vLLM to get full logprobs
    vllm        yes        yes     OpenAI-compatible; the open-weight path

Because vLLM exposes an OpenAI-compatible API, open-weight models get
first-class logprob support by pointing OpenAIClient at the vLLM base_url.
That is the recommended route for any analysis that needs internal signals.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

__all__ = [
    "Message",
    "TokenLogprobs",
    "Response",
    "LLMClient",
    "OpenAIClient",
    "AnthropicClient",
    "GeminiClient",
    "OllamaClient",
    "build_client",
    "ProviderError",
]


class ProviderError(RuntimeError):
    """Raised when a provider call fails after retries."""


@dataclass(frozen=True)
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass(frozen=True)
class TokenLogprobs:
    """Top-k logprobs at a single generated position."""

    position: int
    chosen: str
    top: dict[str, float]  # token -> logprob

    def probs(self) -> dict[str, float]:
        return {tok: math.exp(lp) for tok, lp in self.top.items()}


@dataclass
class Response:
    text: str
    model: str
    provider: str
    logprobs: list[TokenLogprobs] | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_s: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def has_logprobs(self) -> bool:
        return bool(self.logprobs)

    @property
    def total_tokens(self) -> int:
        return (self.prompt_tokens or 0) + (self.completion_tokens or 0)


def _post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    timeout: float = 180.0,
    retries: int = 4,
) -> dict[str, Any]:
    """POST JSON with exponential backoff on transient failures."""
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:  # noqa: PERF203
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            last_err = ProviderError(f"HTTP {exc.code} from {url}: {detail}")
            # 4xx other than 429 are not worth retrying.
            if exc.code < 500 and exc.code != 429:
                raise last_err from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_err = ProviderError(f"{type(exc).__name__} calling {url}: {exc}")
        if attempt < retries - 1:
            time.sleep(2.0 ** attempt)
    raise last_err or ProviderError(f"unknown failure calling {url}")


class LLMClient:
    """Base interface. Subclasses implement `complete`."""

    provider: str = "base"
    supports_logprobs: bool = False

    def __init__(self, model: str, *, api_key: str | None = None, base_url: str | None = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def complete(
        self,
        messages: Sequence[Message],
        *,
        max_tokens: int = 512,
        temperature: float = 1.0,
        top_logprobs: int | None = None,
        seed: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Response:
        raise NotImplementedError

    # -- shared helpers -------------------------------------------------
    @staticmethod
    def _split_system(messages: Sequence[Message]) -> tuple[str | None, list[Message]]:
        system = None
        rest: list[Message] = []
        for m in messages:
            if m.role == "system" and system is None:
                system = m.content
            else:
                rest.append(m)
        return system, rest

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"{type(self).__name__}(model={self.model!r})"


class OpenAIClient(LLMClient):
    """OpenAI Chat Completions. Also serves any OpenAI-compatible server
    (vLLM, LM Studio, together, openrouter) via `base_url`."""

    provider = "openai"
    supports_logprobs = True

    def __init__(self, model: str, *, api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            model,
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=(base_url or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/"),
        )

    def complete(
        self,
        messages: Sequence[Message],
        *,
        max_tokens: int = 512,
        temperature: float = 1.0,
        top_logprobs: int | None = None,
        seed: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Response:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if top_logprobs:
            payload["logprobs"] = True
            payload["top_logprobs"] = min(int(top_logprobs), 20)
        if seed is not None:
            payload["seed"] = seed
        if stop:
            payload["stop"] = list(stop)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        t0 = time.time()
        data = _post_json(f"{self.base_url}/chat/completions", payload, headers)
        dt = time.time() - t0

        choice = data["choices"][0]
        text = choice["message"].get("content") or ""
        lps = None
        content_lp = (choice.get("logprobs") or {}).get("content")
        if content_lp:
            lps = [
                TokenLogprobs(
                    position=i,
                    chosen=entry.get("token", ""),
                    top={t["token"]: float(t["logprob"]) for t in entry.get("top_logprobs", [])},
                )
                for i, entry in enumerate(content_lp)
            ]
        usage = data.get("usage") or {}
        return Response(
            text=text,
            model=data.get("model", self.model),
            provider=self.provider,
            logprobs=lps,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            latency_s=dt,
            raw=data,
        )


class AnthropicClient(LLMClient):
    """Anthropic Messages API.

    NOTE: the Messages API does not expose token logprobs. Every Likert
    readout from an Anthropic model is therefore a *sampled* readout and
    needs replicates to reach the same precision a single logprob readout
    gives elsewhere. This asymmetry is a real design constraint, not an
    implementation gap -- see docs/04 for the effective-N consequences.
    """

    provider = "anthropic"
    supports_logprobs = False

    def __init__(self, model: str, *, api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            model,
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            base_url=(base_url or os.environ.get("ANTHROPIC_BASE_URL") or "https://api.anthropic.com").rstrip("/"),
        )

    def complete(
        self,
        messages: Sequence[Message],
        *,
        max_tokens: int = 512,
        temperature: float = 1.0,
        top_logprobs: int | None = None,
        seed: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Response:
        system, rest = self._split_system(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": m.role, "content": m.content} for m in rest],
        }
        if system:
            payload["system"] = system
        if stop:
            payload["stop_sequences"] = list(stop)

        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key

        t0 = time.time()
        data = _post_json(f"{self.base_url}/v1/messages", payload, headers)
        dt = time.time() - t0

        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        usage = data.get("usage") or {}
        return Response(
            text=text,
            model=data.get("model", self.model),
            provider=self.provider,
            logprobs=None,
            prompt_tokens=usage.get("input_tokens"),
            completion_tokens=usage.get("output_tokens"),
            latency_s=dt,
            raw=data,
        )


class GeminiClient(LLMClient):
    """Google Gemini generateContent.

    Logprob availability varies by model and API version; when
    `response_logprobs` is honoured the top candidates are parsed, otherwise
    `logprobs` comes back None and the sampled readout path is used.
    """

    provider = "gemini"
    supports_logprobs = True

    def __init__(self, model: str, *, api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            model,
            api_key=api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
            base_url=(base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/"),
        )

    def complete(
        self,
        messages: Sequence[Message],
        *,
        max_tokens: int = 512,
        temperature: float = 1.0,
        top_logprobs: int | None = None,
        seed: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Response:
        system, rest = self._split_system(messages)
        contents = [
            {"role": ("model" if m.role == "assistant" else "user"), "parts": [{"text": m.content}]}
            for m in rest
        ]
        gen_cfg: dict[str, Any] = {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        }
        if top_logprobs:
            gen_cfg["responseLogprobs"] = True
            gen_cfg["logprobs"] = min(int(top_logprobs), 20)
        if stop:
            gen_cfg["stopSequences"] = list(stop)

        payload: dict[str, Any] = {"contents": contents, "generationConfig": gen_cfg}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["x-goog-api-key"] = self.api_key

        t0 = time.time()
        try:
            data = _post_json(url, payload, headers)
        except ProviderError as exc:
            # Older/smaller models reject responseLogprobs; degrade gracefully.
            if top_logprobs and "logprob" in str(exc).lower():
                gen_cfg.pop("responseLogprobs", None)
                gen_cfg.pop("logprobs", None)
                data = _post_json(url, payload, headers)
            else:
                raise
        dt = time.time() - t0

        cand = (data.get("candidates") or [{}])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)

        lps = None
        lp_result = cand.get("logprobsResult") or {}
        top_cands = lp_result.get("topCandidates") or []
        if top_cands:
            lps = []
            for i, entry in enumerate(top_cands):
                cands = entry.get("candidates") or []
                lps.append(
                    TokenLogprobs(
                        position=i,
                        chosen=(cands[0].get("token", "") if cands else ""),
                        top={c.get("token", ""): float(c.get("logProbability", 0.0)) for c in cands},
                    )
                )

        usage = data.get("usageMetadata") or {}
        return Response(
            text=text,
            model=self.model,
            provider=self.provider,
            logprobs=lps,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
            latency_s=dt,
            raw=data,
        )


class OllamaClient(LLMClient):
    """Local Ollama server (/api/chat).

    Ollama is the cheap way to get a *population* of open-weight respondents,
    which is what the Bayesian-Truth-Serum and surprisingly-popular arms need.
    It does not reliably expose logprobs; when internal signals are required,
    serve the same weights with vLLM and use `OpenAIClient` against it.
    """

    provider = "ollama"
    supports_logprobs = False

    def __init__(self, model: str, *, api_key: str | None = None, base_url: str | None = None):
        super().__init__(
            model,
            api_key=None,
            base_url=(base_url or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/"),
        )

    def complete(
        self,
        messages: Sequence[Message],
        *,
        max_tokens: int = 512,
        temperature: float = 1.0,
        top_logprobs: int | None = None,
        seed: int | None = None,
        stop: Sequence[str] | None = None,
    ) -> Response:
        options: dict[str, Any] = {"temperature": temperature, "num_predict": max_tokens}
        if seed is not None:
            options["seed"] = seed
        if stop:
            options["stop"] = list(stop)
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": options,
        }
        t0 = time.time()
        data = _post_json(f"{self.base_url}/api/chat", payload, {"Content-Type": "application/json"})
        dt = time.time() - t0
        return Response(
            text=(data.get("message") or {}).get("content", ""),
            model=self.model,
            provider=self.provider,
            logprobs=None,
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            latency_s=dt,
            raw=data,
        )


_REGISTRY: dict[str, type[LLMClient]] = {
    "openai": OpenAIClient,
    "vllm": OpenAIClient,  # OpenAI-compatible
    "anthropic": AnthropicClient,
    "gemini": GeminiClient,
    "ollama": OllamaClient,
}


def build_client(spec: str, *, base_url: str | None = None, api_key: str | None = None) -> LLMClient:
    """Build a client from a `provider:model` spec.

    >>> build_client("anthropic:claude-opus-4-6")        # doctest: +SKIP
    >>> build_client("ollama:llama3.1:8b")               # doctest: +SKIP
    >>> build_client("vllm:Qwen/Qwen3-8B", base_url="http://localhost:8000/v1")  # doctest: +SKIP
    """
    provider, _, model = spec.partition(":")
    provider = provider.strip().lower()
    if not model:
        raise ValueError(f"spec must be 'provider:model', got {spec!r}")
    try:
        cls = _REGISTRY[provider]
    except KeyError:
        raise ValueError(f"unknown provider {provider!r}; known: {sorted(_REGISTRY)}") from None
    return cls(model.strip(), api_key=api_key, base_url=base_url)


def capability_table(specs: Iterable[str]) -> list[dict[str, Any]]:
    """Summarise what measurement each configured model supports."""
    rows = []
    for spec in specs:
        client = build_client(spec)
        rows.append(
            {
                "spec": spec,
                "provider": client.provider,
                "model": client.model,
                "logprobs": client.supports_logprobs,
                "readout": "logprob" if client.supports_logprobs else "sampled",
            }
        )
    return rows
