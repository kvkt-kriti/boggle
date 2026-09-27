"""Boggle HTTP API — thin wrapper around ap_transfer.storage + advisor.

Run from repo root:
  uvicorn boggle_api.main:app --reload --port 8000
"""

from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure repo root is on path when launched as a module
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ap_transfer import advisor, storage  # noqa: E402
from boggle_api.majors import (  # noqa: E402
    MAJORS,
    SCHOOL_LOCATIONS,
    fit_badge,
    get_major,
    why_copy,
)

app = FastAPI(title="Boggle API", version="0.1.0")

_origins = os.getenv(
    "BOGGLE_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _rows():
    return storage.load_json()


@app.get("/health")
def health():
    return {"ok": True, "service": "boggle-api"}


@app.get("/schools")
def list_schools():
    pairs = advisor.schools(_rows())
    return [
        {
            "code": code,
            "name": name,
            "location": SCHOOL_LOCATIONS.get(code, ""),
        }
        for code, name in pairs
    ]


@app.get("/majors")
def list_majors():
    return [
        {
            "id": m.id,
            "name": m.name,
            "blurb": m.blurb,
            "index": i + 1,
        }
        for i, m in enumerate(MAJORS)
    ]


@app.get("/recommend")
def recommend(
    school: str = Query(..., min_length=1, description="School code, e.g. GT"),
    major: str | None = Query(None, description="Major id from /majors"),
    subject: str | None = Query(
        None,
        description="Optional advisor subject substring; overrides major hint if set",
    ),
    score: int | None = Query(None, ge=1, le=5),
    use_subject_filter: bool = Query(
        False,
        description="If true, apply major subject_hint (or subject) to advisor.recommend",
    ),
):
    rows = _rows()
    school_u = school.upper().strip()
    known = {c for c, _ in advisor.schools(rows)}
    if school_u not in known:
        raise HTTPException(status_code=404, detail=f"Unknown school: {school}")

    major_obj = get_major(major) if major else None
    subject_arg = subject
    if use_subject_filter and subject_arg is None and major_obj is not None:
        subject_arg = major_obj.subject_hint

    recs = advisor.recommend(
        rows,
        school_u,
        subject=subject_arg,
        expected_score=score,
    )

    source_url = ""
    for r in rows:
        if r.school == school_u and r.source_url:
            source_url = r.source_url
            break

    school_name = recs[0].school_name if recs else next(
        (n for c, n in advisor.schools(rows) if c == school_u),
        school_u,
    )

    items = []
    total_credits = 0.0
    for rec in recs:
        credits = float(rec.best_credits) if rec.best_credits is not None else 0.0
        total_credits += credits
        badge = fit_badge(rec.ap_exam, rec.courses, major_obj)
        items.append(
            {
                **asdict(rec),
                "fit": badge,
                "why": why_copy(rec.ap_exam, major_obj, school_name),
                "source_url": source_url,
            }
        )

    return {
        "school": school_u,
        "school_name": school_name,
        "source_url": source_url,
        "major": (
            {"id": major_obj.id, "name": major_obj.name} if major_obj else None
        ),
        "subject_filter": subject_arg,
        "exam_count": len(items),
        "total_credits": total_credits,
        "recommendations": items,
    }


@app.get("/compare")
def compare(exam: str = Query(..., min_length=1)):
    grouped = advisor.compare_exam(_rows(), exam)
    return {
        school: [e.to_dict() for e in eqs] for school, eqs in grouped.items()
    }
