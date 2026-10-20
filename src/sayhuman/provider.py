"""Explicit opt-in provider for OpenAI-compatible chat-completions APIs."""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlsplit


class ProviderError(RuntimeError):
    """A user-actionable, non-secret-leaking provider error."""


@dataclass(frozen=True)
class ProviderConfig:
    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 30.0

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        key = os.getenv("SAYHUMAN_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
        model = os.getenv("SAYHUMAN_MODEL", "")
        url = os.getenv("SAYHUMAN_BASE_URL", "https://api.openai.com/v1")
        try:
            timeout = float(os.getenv("SAYHUMAN_TIMEOUT_SECONDS", "30"))
        except ValueError as exc:
            raise ProviderError("SAYHUMAN_TIMEOUT_SECONDS must be numeric") from exc
        return cls(api_key=key, model=model, base_url=url, timeout=timeout)

    def validate(self) -> None:
        if not self.api_key:
            raise ProviderError("Set SAYHUMAN_API_KEY or OPENAI_API_KEY before using --llm")
        if "\r" in self.api_key or "\n" in self.api_key:
            raise ProviderError("API key contains invalid newline characters")
        if not self.model:
            raise ProviderError("Set SAYHUMAN_MODEL to a chat-capable model available to your provider")
        parsed = urlsplit(self.base_url)
        is_local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if (parsed.scheme != "https" and not (is_local and parsed.scheme == "http")) or not parsed.netloc:
            raise ProviderError("SAYHUMAN_BASE_URL must use HTTPS (HTTP allowed only for localhost)")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ProviderError("SAYHUMAN_BASE_URL cannot contain credentials, query or fragment")
        if self.timeout <= 0 or self.timeout > 180:
            raise ProviderError("Timeout must be greater than 0 and no more than 180 seconds")


def generate(system_prompt: str, user_prompt: str, config: ProviderConfig | None = None) -> str:
    config = config or ProviderConfig.from_env()
    config.validate()
    endpoint = config.base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps({"model": config.model, "temperature": 0.3,
                          "messages": [{"role": "system", "content": system_prompt},
                                       {"role": "user", "content": user_prompt}]}).encode("utf-8")
    request = urllib.request.Request(endpoint, data=payload, method="POST",
                                     headers={"Authorization": "Bearer " + config.api_key,
                                              "Content-Type": "application/json", "Accept": "application/json"})
    try:
        # Reject automatic off-origin redirects by using a restrictive opener.
        opener = urllib.request.build_opener(_NoRedirect())
        with opener.open(request, timeout=config.timeout) as response:
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ProviderError("Provider response exceeds 2 MB safety limit")
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"Provider HTTP {exc.code}; check provider access and model") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ProviderError("Provider connection failed or timed out") from exc
    try:
        content = json.loads(raw)["choices"][0]["message"]["content"]
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            text = "".join(x.get("text", "") for x in content if isinstance(x, dict))
            if text.strip():
                return text.strip()
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise ProviderError("Malformed provider chat-completions response") from exc
    raise ProviderError("Provider returned an empty text response")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise ProviderError("Redirect refused to protect API credentials")
