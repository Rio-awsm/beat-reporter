from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.sqlite import run_migrations, get_conn
from db.chroma import get_chroma

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    get_chroma()  # warm
    yield

app = FastAPI(title="Beat Reporter", lifespan=lifespan)

@app.get("/health")
def health():
    with get_conn() as conn:
        beats = conn.execute("SELECT COUNT(*) AS n FROM beats").fetchone()["n"]
    collections = [c.name for c in get_chroma().list_collections()]
    return {"ok": True, "beats": beats, "chroma_collections": collections}