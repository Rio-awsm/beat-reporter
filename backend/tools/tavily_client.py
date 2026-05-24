import hashlib, json, time
from pathlib import Path
from tavily import TavilyClient
from config import settings

CACHE_DIR = Path("./data/tavily_cache")
CACHE_TTL_SECONDS = 24 * 60 * 60   # 24h

def _key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

def _read_cache(k: str):
    f = CACHE_DIR / f"{k}.json"
    if not f.exists(): return None
    data = json.loads(f.read_text())
    if time.time() - data["ts"] > CACHE_TTL_SECONDS: return None
    return data["value"]

def _write_cache(k: str, value):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{k}.json").write_text(json.dumps({"ts": time.time(), "value": value}))

_tavily = TavilyClient(api_key=settings.tavily_api_key)

def web_search(query: str, max_results: int = 5, depth: str = "basic") -> dict:
    payload = {"q": query, "n": max_results, "depth": depth}
    k = _key(payload)
    cached = _read_cache(k)
    if cached is not None:
        return {"cached": True, **cached}

    r = _tavily.search(query=query, max_results=max_results, search_depth=depth)
    value = {
        "results": [
            {"title": x["title"], "url": x["url"], "content": x.get("content", "")}
            for x in r.get("results", [])
        ]
    }
    _write_cache(k, value)
    return {"cached": False, **value}

def web_fetch(url: str) -> dict:
    payload = {"url": url}
    k = _key(payload)
    cached = _read_cache(k)
    if cached is not None:
        return {"cached": True, **cached}

    r = _tavily.extract(urls=[url])
    results = r.get("results", [])
    value = {"url": url, "content": results[0]["raw_content"] if results else ""}
    _write_cache(k, value)
    return {"cached": False, **value}