"""Persistence for scraped equivalencies: JSON export and a queryable SQLite DB."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Equivalency

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
JSON_PATH = DATA_DIR / "ap_equivalencies.json"
DB_PATH = DATA_DIR / "ap_equivalencies.db"


def _ensure_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def dedupe(rows: Iterable[Equivalency]) -> list[Equivalency]:
    """Drop exact-duplicate equivalencies, preserving first-seen order."""
    seen: set[tuple] = set()
    out: list[Equivalency] = []
    for r in rows:
        key = (r.school, r.ap_exam, r.score, tuple(r.courses), r.credits, r.award_raw)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def save_json(rows: Iterable[Equivalency], path: Path = JSON_PATH) -> Path:
    _ensure_dir()
    payload = [r.to_dict() for r in dedupe(rows)]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_json(path: Path = JSON_PATH) -> list[Equivalency]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Equivalency.from_dict(d) for d in data]


def save_sqlite(rows: Iterable[Equivalency], path: Path = DB_PATH) -> Path:
    _ensure_dir()
    rows = dedupe(rows)
    conn = sqlite3.connect(path)
    try:
        conn.execute("DROP TABLE IF EXISTS equivalencies")
        conn.execute(
            """
            CREATE TABLE equivalencies (
                school       TEXT NOT NULL,
                school_name  TEXT NOT NULL,
                ap_exam      TEXT NOT NULL,
                ap_exam_raw  TEXT NOT NULL,
                score        INTEGER NOT NULL,
                courses      TEXT NOT NULL,
                award_raw    TEXT NOT NULL,
                credits      REAL,
                gen_ed       TEXT,
                source_url   TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO equivalencies
            (school, school_name, ap_exam, ap_exam_raw, score, courses,
             award_raw, credits, gen_ed, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r.school,
                    r.school_name,
                    r.ap_exam,
                    r.ap_exam_raw,
                    r.score,
                    "; ".join(r.courses),
                    r.award_raw,
                    r.credits,
                    r.gen_ed,
                    r.source_url,
                )
                for r in rows
            ],
        )
        conn.execute("CREATE INDEX idx_school ON equivalencies(school)")
        conn.execute("CREATE INDEX idx_exam ON equivalencies(ap_exam)")
        conn.commit()
    finally:
        conn.close()
    return path
