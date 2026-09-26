"""Core data models shared across scrapers and storage."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True)
class Equivalency:
    """A single AP-exam-to-course credit award at one university.

    One row represents: at ``school``, scoring ``score`` on ``ap_exam`` grants
    the courses in ``courses`` (``credits`` credit hours). ``award_raw`` keeps
    the university's original wording so nothing is lost in normalization.
    """

    school: str  # short code, e.g. "UF"
    school_name: str  # full name, e.g. "University of Florida"
    ap_exam: str  # normalized exam name, e.g. "Calculus BC"
    ap_exam_raw: str  # exam name exactly as published
    score: int  # AP score (typically 3, 4, or 5)
    courses: list[str]  # extracted course codes, e.g. ["MAC 2311", "MAC 2312"]
    award_raw: str  # full award text as published
    credits: float | None  # credit hours awarded, if stated
    gen_ed: str | None = None  # general/liberal-education notes, if any
    source_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Equivalency":
        return cls(
            school=d["school"],
            school_name=d["school_name"],
            ap_exam=d["ap_exam"],
            ap_exam_raw=d["ap_exam_raw"],
            score=int(d["score"]),
            courses=list(d.get("courses") or []),
            award_raw=d.get("award_raw", ""),
            credits=d.get("credits"),
            gen_ed=d.get("gen_ed"),
            source_url=d.get("source_url", ""),
        )


@dataclass
class ScrapeResult:
    """Everything one school scraper produced in a run."""

    school: str
    school_name: str
    source_url: str
    equivalencies: list[Equivalency] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and len(self.equivalencies) > 0
