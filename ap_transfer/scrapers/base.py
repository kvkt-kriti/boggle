"""Base class for per-university AP equivalency scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from ..http import FetchError, fetch
from ..models import Equivalency, ScrapeResult


class BaseScraper(ABC):
    """A scraper for one university's published AP equivalency table.

    Subclasses set :attr:`code`, :attr:`name`, :attr:`url` and implement
    :meth:`parse`. Keeping parsing separate from fetching lets us unit-test
    parsers against saved HTML fixtures without network access.
    """

    code: str = ""  # short code, e.g. "UF"
    name: str = ""  # full name, e.g. "University of Florida"
    url: str = ""  # source page

    @abstractmethod
    def parse(self, html: str) -> list[Equivalency]:
        """Parse page HTML into a list of Equivalency rows."""

    def soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def make(
        self,
        ap_exam_raw: str,
        score: int,
        award_raw: str,
        *,
        courses: list[str],
        credits: float | None,
        gen_ed: str | None = None,
        normalized: str | None = None,
    ) -> Equivalency:
        from ..normalize import normalize_exam

        return Equivalency(
            school=self.code,
            school_name=self.name,
            ap_exam=normalized or normalize_exam(ap_exam_raw),
            ap_exam_raw=ap_exam_raw.strip(),
            score=score,
            courses=courses,
            award_raw=award_raw.strip(),
            credits=credits,
            gen_ed=(gen_ed or None),
            source_url=self.url,
        )

    def scrape(self) -> ScrapeResult:
        """Fetch the live page and parse it into a :class:`ScrapeResult`."""
        result = ScrapeResult(school=self.code, school_name=self.name, source_url=self.url)
        try:
            html = fetch(self.url)
        except FetchError as exc:
            result.error = str(exc)
            return result
        try:
            result.equivalencies = self.parse(html)
        except Exception as exc:  # noqa: BLE001 - surface parser errors per-school
            result.error = f"parse error: {exc}"
        return result
