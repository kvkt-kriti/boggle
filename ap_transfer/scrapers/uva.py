"""University of Virginia AP credit scraper.

UVA's Undergraduate Record site often returns HTTP 202 to automated clients.
We therefore also accept a simple three-column HTML table (used by the saved
fixture) and, when live fetch fails, fall back to the committed fixture.
"""

from __future__ import annotations

from pathlib import Path

from ..http import FetchError, fetch
from ..models import Equivalency, ScrapeResult
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper
from .scores import expand_scores

_FIXTURE = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "uva.html"


class UVAScraper(BaseScraper):
    code = "UVA"
    name = "University of Virginia"
    url = "https://records.ureg.virginia.edu/content.php?catoid=72&navoid=6694"

    def scrape(self) -> ScrapeResult:
        result = ScrapeResult(school=self.code, school_name=self.name, source_url=self.url)
        html = None
        try:
            html = fetch(self.url)
        except FetchError:
            if _FIXTURE.exists():
                html = _FIXTURE.read_text(encoding="utf-8")
                result.source_url = self.url + " (fixture fallback)"
            else:
                result.error = "UVA page blocked automated access and no fixture is available"
                return result
        try:
            result.equivalencies = self.parse(html)
        except Exception as exc:  # noqa: BLE001
            result.error = f"parse error: {exc}"
        return result

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        target = None
        for table in soup.find_all("table"):
            first = table.find(["th", "td"])
            if not first:
                continue
            label = first.get_text(" ", strip=True).lower()
            if "ap examination" in label or label == "ap exam":
                target = table
                break
        if target is None:
            raise ValueError("UVA: could not find the AP Examination table")

        out: list[Equivalency] = []
        current_exam = ""
        for tr in target.find_all("tr")[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            if len(cells) < 3:
                continue
            exam, score_s, award = cells[0], cells[1], cells[2]
            if exam:
                current_exam = exam
            if not current_exam:
                continue
            if score_s.lower() in {"n/a", "na", ""} or award.lower() in {"n/a", "na", ""}:
                continue
            scores = expand_scores(score_s)
            if not scores:
                continue
            if "exemption" in award.lower() and "credit" not in award.lower():
                # Placement-only rows still useful for advising; keep with 0 credits.
                courses = extract_courses(award)
                credits = 0.0
            else:
                courses = extract_courses(award)
                credits = extract_credits(award)
            for score in scores:
                out.append(
                    self.make(
                        current_exam,
                        score,
                        award,
                        courses=courses,
                        credits=credits,
                    )
                )
        return out
