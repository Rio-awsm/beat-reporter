CREATE TABLE IF NOT EXISTS beats (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    description  TEXT,
    created_at   TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    beat_id         INTEGER NOT NULL REFERENCES beats(id),
    title           TEXT NOT NULL,
    body_md         TEXT NOT NULL,
    appendix_md     TEXT,
    status          TEXT NOT NULL DEFAULT 'draft',  -- draft | published | killed
    angle           TEXT,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    published_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_beat ON articles(beat_id);