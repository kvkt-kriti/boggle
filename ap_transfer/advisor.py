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
    major: str | None = None,
    expected_score: int | None = None,
) -> list[Recommendation]:
    """Recommend AP exams worth taking for a school (optionally by subject/major).

    Results are grouped per AP exam and ranked by the credit hours awarded, so a
    student sees the highest-value exams first. When ``expected_score`` is given,
    only awards a student could earn at that score (i.e. requiring that score or
    lower) are considered.

    ``major`` is a major id from :mod:`ap_transfer.majors`. Priority exams for
    that major are sorted first, then remaining credit-bearing exams matched by
    subject keywords.
    """
    school = school.upper()
    pool = [r for r in rows if r.school == school]

    major_obj = None
    if major:
        from .majors import get_major

        major_obj = get_major(major)
        if major_obj is None:
            raise ValueError(f"Unknown major id: {major!r}")

    if subject:
        pool = [r for r in pool if _matches_subject(r, subject)]
    elif major_obj is not None:
        # Keep rows that match any major keyword OR are a priority exam.
        priority = {e.lower() for e in major_obj.priority_exams}
        filtered = []
        for r in pool:
            if r.ap_exam.lower() in priority or any(
                _matches_subject(r, kw) for kw in major_obj.keywords
            ):
                filtered.append(r)
        pool = filtered

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

    if major_obj is not None:
        priority_order = {e: i for i, e in enumerate(major_obj.priority_exams)}

        def sort_key(r: Recommendation) -> tuple:
            pri = priority_order.get(r.ap_exam, 1000)
            return (pri, -(r.best_credits or 0), r.ap_exam)

        recs.sort(key=sort_key)
    else:
        recs.sort(key=lambda r: (-(r.best_credits or 0), r.ap_exam))
    return recs


@dataclass
class AwardTier:
    """The best published award at one AP score."""

    score: int
    courses: list[str]
    credits: float | None
    award_raw: str


@dataclass
class PlanExam:
    """One AP exam on a student's plan, with every real score tier."""

    ap_exam: str
    relevance: str  # core | strong | elective
    tiers: list[AwardTier]
    source_url: str

    @property
    def floor(self) -> AwardTier:
        """Award guaranteed at the lowest qualifying score."""
        return self.tiers[0]


def _credited(group: list[Equivalency]) -> list[Equivalency]:
    return [g for g in group if g.courses or (g.credits or 0) > 0]


def _best_row(rows: list[Equivalency]) -> Equivalency:
    def key(g: Equivalency) -> tuple:
        # Prefer a real course code over a blanket "1XXX" placeholder when
        # the school publishes both for the same score.
        concrete = sum(1 for c in g.courses if "X" not in c.upper())
        return (g.credits or 0, concrete, len(g.courses), -g.score)

    return max(rows, key=key)


def build_plan(
    rows: list[Equivalency],
    school: str,
    major: str,
    *,
    expected_score: int | None = None,
) -> list[PlanExam]:
    """Build a major-specific AP plan from scraped equivalencies.

    Each exam keeps one award per published score. The floor tier is the award
    at the lowest qualifying score, so "score N+" never claims courses that
    only unlock at a higher score. When ``expected_score`` is set, tiers above
    that score are dropped and the remaining best award is what that score
    actually earns.
    """
    from .majors import get_major

    major_obj = get_major(major)
    if major_obj is None:
        raise ValueError(f"Unknown major id: {major!r}")

    school = school.upper()
    priority = list(major_obj.priority_exams)
    priority_l = {e.lower(): i for i, e in enumerate(priority)}
    pool = [r for r in rows if r.school == school]
    pool = [
        r
        for r in pool
        if r.ap_exam.lower() in priority_l
        or any(_matches_subject(r, kw) for kw in major_obj.keywords)
    ]

    by_exam: dict[str, list[Equivalency]] = defaultdict(list)
    for r in pool:
        by_exam[r.ap_exam].append(r)

    plans: list[PlanExam] = []
    for exam, group in by_exam.items():
        credited = _credited(group)
        if expected_score is not None:
            credited = [g for g in credited if g.score <= expected_score]
        if not credited:
            continue
        by_score: dict[int, list[Equivalency]] = defaultdict(list)
        for g in credited:
            by_score[g.score].append(g)
        tiers = []
        for score in sorted(by_score):
            best = _best_row(by_score[score])
            tiers.append(
                AwardTier(
                    score=score,
                    courses=list(best.courses),
                    credits=best.credits,
                    award_raw=best.award_raw,
                )
            )
        if exam.lower() in priority_l and priority_l[exam.lower()] < 3:
            relevance = "core"
        elif exam.lower() in priority_l:
            relevance = "strong"
        else:
            relevance = "elective"
        source = next((g.source_url for g in credited if g.source_url), "")
        source = source.split(" (fixture")[0]
        plans.append(
            PlanExam(ap_exam=exam, relevance=relevance, tiers=tiers, source_url=source)
        )

    rank = {"core": 0, "strong": 1, "elective": 2}

    def sort_key(p: PlanExam) -> tuple:
        pri = priority_l.get(p.ap_exam.lower(), 1000)
        top = max((t.credits or 0) for t in p.tiers)
        return (rank[p.relevance], pri, -top, p.ap_exam)

    plans.sort(key=sort_key)
    return plans


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
