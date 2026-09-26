"""University of Maryland AP credit scraper (PDF chart)."""

from __future__ import annotations

import io
import re

from ..http import FetchError, fetch_bytes
from ..models import Equivalency, ScrapeResult
from ..normalize import extract_courses, extract_credits
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token

_PDF_URL = "https://registrar.umd.edu/sites/default/files/2023-03/ap-gen-ed.pdf"

# Lines look like: "Biology (20) 4,5 8 BSCI 170/171 (DSNL)"
_ROW_RE = re.compile(
    r"^(?P<exam>[A-Za-z][A-Za-z0-9 &/\-:,()]+?)\s+"
    r"\(\d+\)\s+"
    r"(?P<score>[1-5](?:\s*,\s*[1-5]|\s*or\s*[1-5]|\s*[-–—]\s*[1-5]|[+])*)\s+"
    r"(?P<credits>\d+(?:\.\d+)?)\s+"
    r"(?P<award>.+)$"
)


class UMDScraper(BaseScraper):
    code = "UMD"
    name = "University of Maryland, College Park"
    url = _PDF_URL

    def scrape(self) -> ScrapeResult:
        result = ScrapeResult(school=self.code, school_name=self.name, source_url=self.url)
        try:
            data = fetch_bytes(self.url)
        except FetchError as exc:
            result.error = str(exc)
            return result
        try:
            result.equivalencies = self.parse_pdf(data)
        except Exception as exc:  # noqa: BLE001
            result.error = f"parse error: {exc}"
        return result

    def parse(self, html: str) -> list[Equivalency]:
        # Allow fixture tests to pass decoded PDF text.
        return self.parse_pdf(html.encode("utf-8", errors="ignore"))

    def parse_pdf(self, data: bytes) -> list[Equivalency]:
        try:
            from pypdf import PdfReader
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pypdf is required to parse the UMD AP chart") from exc

        reader = PdfReader(io.BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return self.parse_text(text)

    def parse_text(self, text: str) -> list[Equivalency]:
        out: list[Equivalency] = []
        current_exam = ""
        for raw in text.splitlines():
            line = re.sub(r"\s+", " ", raw).strip()
            if not line or line.lower().startswith("examination"):
                continue
            m = _ROW_RE.match(line)
            if not m:
                # Continuation score rows sometimes omit the exam name.
                m2 = re.match(
                    r"^(?P<score>[1-5](?:\s*,\s*[1-5]|\s*or\s*[1-5]|[+])*)\s+"
                    r"(?P<credits>\d+(?:\.\d+)?)\s+(?P<award>.+)$",
                    line,
                )
                if m2 and current_exam:
                    score_s, hours, award = m2.group("score"), m2.group("credits"), m2.group("award")
                else:
                    continue
            else:
                current_exam = re.sub(r"\s*\(\d+\)\s*$", "", m.group("exam")).strip()
                score_s, hours, award = m.group("score"), m.group("credits"), m.group("award")
            scores = expand_scores(score_s)
            if not scores or not current_exam:
                continue
            courses = extract_courses(award)
            credits = parse_hours_token(hours) or extract_credits(award)
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
