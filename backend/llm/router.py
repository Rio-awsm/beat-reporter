from enum import Enum
from typing import Optional, Any
from openai import AsyncOpenAI, RateLimitError, APIError, APIConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
from config import settings

log = logging.getLogger(__name__)

class Provider(str, Enum):
    CEREBRAS = "cerebras"
    GROQ = "groq"
    SAMBANOVA = "sambanova"
    OPENROUTER = "openrouter"

PROVIDER_CONFIG = {
    Provider.CEREBRAS:  ("https://api.cerebras.ai/v1",     settings.cerebras_api_key),
    Provider.GROQ:      ("https://api.groq.com/openai/v1", settings.groq_api_key),
    Provider.SAMBANOVA: ("https://api.sambanova.ai/v1",    settings.sambanova_api_key),
    Provider.OPENROUTER:("https://openrouter.ai/api/v1",   settings.openrouter_api_key),
}

# (provider, model) chains per agent. Top of list = primary; rest = fallbacks.
# VERIFY MODEL IDS — they rotate.
AGENT_CHAINS: dict[str, list[tuple[Provider, str]]] = {
    "reporter": [
        (Provider.OPENROUTER,   "openrouter/owl-alpha"),
        (Provider.CEREBRAS,   "llama3.1-8b"),
        (Provider.SAMBANOVA,  "Meta-Llama-3.3-70B-Instruct"),
        (Provider.OPENROUTER, "nvidia/nemotron-3-super-120b-a12b:free"),
    ],
    "factchecker": [
        (Provider.GROQ,       "llama-3.3-70b-versatile"),
        (Provider.CEREBRAS,   "llama3.1-8b"),
        (Provider.SAMBANOVA,  "Meta-Llama-3.3-70B-Instruct"),
    ],
    "editor": [
        (Provider.CEREBRAS,   "llama3.1-8b"),
        (Provider.SAMBANOVA,  "Meta-Llama-3.3-70B-Instruct"),
        (Provider.GROQ,       "llama-3.3-70b-versatile"),
    ],
    "librarian": [
        (Provider.GROQ,       "llama-3.1-8b-instant"),
        (Provider.CEREBRAS,   "llama-3.1-8b"),
        (Provider.GROQ,       "llama-3.3-70b-versatile"),
    ],
}

_clients: dict[Provider, AsyncOpenAI] = {}

def _client(provider: Provider) -> AsyncOpenAI:
    if provider not in _clients:
        base_url, key = PROVIDER_CONFIG[provider]
        _clients[provider] = AsyncOpenAI(base_url=base_url, api_key=key, timeout=60.0)
    return _clients[provider]

class AllProvidersFailed(Exception):
    pass

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((APIConnectionError,)),
    reraise=True,
)
async def _try_one(provider: Provider, model: str, messages, **kwargs):
    return await _client(provider).chat.completions.create(
        model=model, messages=messages, **kwargs
    )

async def complete(
    agent: str,
    messages: list[dict],
    *,
    tools: Optional[list[dict]] = None,
    tool_choice: Optional[str | dict] = None,
    temperature: float = 0.4,
    max_tokens: int = 2048,
    response_format: Optional[dict] = None,
):
    """Try each (provider, model) in the agent's chain until one succeeds."""
    chain = AGENT_CHAINS[agent]
    last_err: Exception | None = None

    for provider, model in chain:
        kwargs: dict[str, Any] = {"temperature": temperature, "max_tokens": max_tokens}
        if tools:           kwargs["tools"] = tools
        if tool_choice:     kwargs["tool_choice"] = tool_choice
        if response_format: kwargs["response_format"] = response_format

        try:
            log.info(f"[{agent}] -> {provider.value}/{model}")
            r = await _try_one(provider, model, messages, **kwargs)
            return {
                "provider": provider.value,
                "model": model,
                "message": r.choices[0].message,
                "raw": r,
            }
        except RateLimitError as e:
            log.warning(f"[{agent}] {provider.value} rate-limited, falling back")
            last_err = e
        except APIError as e:
            log.warning(f"[{agent}] {provider.value} API error: {e}, falling back")
            last_err = e
        except Exception as e:
            log.exception(f"[{agent}] {provider.value} unexpected: {e}")
            last_err = e

    raise AllProvidersFailed(f"All providers in chain for '{agent}' failed. Last: {last_err}")