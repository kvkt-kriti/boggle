"""Query and recommendation logic over scraped equivalencies.

The end goal is to help a student decide which AP exams to take given the school
they want to attend and the subject area of their intended major.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import Equivalency


def schools(rows: list[Equivalency]) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for r in rows:
        seen.setdefault(r.school, r.school_name)
    return sorted(seen.items())


def _matches_subject(row: Equivalency, subject: str) -> bool:
    s = subject.lower()
    haystack = " ".join(
        [row.ap_exam, row.ap_exam_raw, " ".join(row.courses), row.gen_ed or ""]
    ).lower()
    return s in haystack


@dataclass
class Recommendation:
    ap_exam: str
    min_score: int  # lowest score that earns any credit
    best_score: int  # score that earns the most credit
    best_credits: float | None
    courses: list[str]
    award_raw: str
    school: str
    school_name: str


def recommend(
    rows: list[Equivalency],
    school: str,
    *,
    subject: str | None = None,
    expected_score: int | None = None,
) -> list[Recommendation]:
    """Recommend AP exams worth taking for a school (optionally by subject).

    Results are grouped per AP exam and ranked by the credit hours awarded, so a
    student sees the highest-value exams first. When ``expected_score`` is given,
    only awards a student could earn at that score (i.e. requiring that score or
    lower) are considered.
    """
    school = school.upper()
    pool = [r for r in rows if r.school == school]
    if subject:
        pool = [r for r in pool if _matches_subject(r, subject)]
    if expected_score is not None:
        pool = [r for r in pool if r.score <= expected_score]

    by_exam: dict[str, list[Equivalency]] = defaultdict(list)
    for r in pool:
        by_exam[r.ap_exam].append(r)

    recs: list[Recommendation] = []
    for exam, group in by_exam.items():
        credited = [g for g in group if g.courses or (g.credits or 0) > 0]
        if not credited:
            continue
        best = max(credited, key=lambda g: (g.credits or 0, g.score))
        recs.append(
            Recommendation(
                ap_exam=exam,
                min_score=min(g.score for g in credited),
                best_score=best.score,
                best_credits=best.credits,
                courses=best.courses,
                award_raw=best.award_raw,
                school=best.school,
                school_name=best.school_name,
            )
        )
    recs.sort(key=lambda r: (-(r.best_credits or 0), r.ap_exam))
    return recs


def compare_exam(rows: list[Equivalency], exam_query: str) -> dict[str, list[Equivalency]]:
    """For one AP exam, return the award(s) at each school (keyed by school code)."""
    from .normalize import normalize_exam

    target = normalize_exam(exam_query)
    out: dict[str, list[Equivalency]] = defaultdict(list)
    for r in rows:
        if r.ap_exam == target:
            out[r.school].append(r)
    for code in out:
        out[code].sort(key=lambda r: r.score)
    return dict(out)
