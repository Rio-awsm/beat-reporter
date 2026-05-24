def kb_query_facts(beat_id: int, entity: str | None = None, query: str | None = None) -> dict:
    return {"facts": [], "note": "stub — implemented in M6"}

def kb_search_prose(beat_id: int, query: str, k: int = 5) -> dict:
    return {"hits": [], "note": "stub — implemented in M6"}

def kb_check_source(domain: str) -> dict:
    return {"domain": domain, "reliability": None, "seen": 0, "note": "stub — implemented in M6"}