"""University of Wisconsin–Madison AP credit scraper."""

from __future__ import annotations

from ..models import Equivalency
from ..normalize import extract_courses
from .base import BaseScraper
from .scores import expand_scores, parse_hours_token


class UWISScraper(BaseScraper):
    code = "UWIS"
    name = "University of Wisconsin–Madison"
    url = "https://guide.wisc.edu/undergraduate/"

    def parse(self, html: str) -> list[Equivalency]:
        soup = self.soup(html)
        out: list[Equivalency] = []
        in_ap = False
        for el in soup.find_all(["h2", "h3", "h4", "table"]):
            if el.name in {"h2", "h3", "h4"}:
                title = el.get_text(" ", strip=True)
                if "Advanced Placement" in title or title.strip() == "AP":
                    in_ap = True
                    continue
                if in_ap and (
                    "International Baccalaureate" in title
                    or title.startswith("IB")
                    or "GCE" in title
                    or "CLEP" in title
                ):
                    break
                continue
            if not in_ap or el.name != "table":
                continue
            header = [c.get_text(" ", strip=True) for c in (el.find("tr").find_all(["th", "td"]) if el.find("tr") else [])]
            if not header or "Exam" not in header[0]:
                continue
            for tr in el.find_all("tr")[1:]:
                cells = [c.get_text(" ", strip=True).replace("\xa0", " ") for c in tr.find_all(["th", "td"])]
                if len(cells) < 4:
                    continue
                exam, score_s, course, hours = cells[0], cells[1], cells[2], cells[3]
                gen_ed = cells[5] if len(cells) > 5 else (cells[4] if len(cells) > 4 else None)
                scores = expand_scores(score_s)
                if not scores or not exam:
                    continue
                courses = extract_courses(course)
                credits = parse_hours_token(hours)
                for score in scores:
                    out.append(
                        self.make(
                            exam,
                            score,
                            course,
                            courses=courses,
                            credits=credits,
                            gen_ed=gen_ed or None,
                        )
                    )
        return out
