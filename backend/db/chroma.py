import chromadb
from pathlib import Path
from config import settings

_client = None

def get_chroma():
    global _client
    if _client is None:
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=settings.chroma_path)
    return _client

def get_or_create_collection(beat_id: int):
    return get_chroma().get_or_create_collection(
        name=f"beat_{beat_id}_prose",
        metadata={"hnsw:space": "cosine"},
    )