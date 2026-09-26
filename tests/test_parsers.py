"""Parser tests run against saved HTML fixtures (no network required)."""

from __future__ import annotations

import pathlib

import pytest

from ap_transfer.models import Equivalency
from ap_transfer.scrapers import (
    GeorgiaTechScraper,
    RutgersScraper,
    TAMUScraper,
    UFScraper,
    UGAScraper,
    UMNScraper,
)

FIX = pathlib.Path(__file__).parent / "fixtures"
SCRAPER_FILE = {
    UFScraper: "uf.html",
    UGAScraper: "uga.html",
    TAMUScraper: "tamu.html",
    GeorgiaTechScraper: "gatech.html",
    RutgersScraper: "rutgers.html",
    UMNScraper: "umn.html",
}


def parse(cls) -> list[Equivalency]:
    html = (FIX / SCRAPER_FILE[cls]).read_text(encoding="utf-8")
    return cls().parse(html)


@pytest.mark.parametrize("cls", list(SCRAPER_FILE))
def test_parser_produces_reasonable_data(cls):
    rows = parse(cls)
    assert len(rows) >= 40, f"{cls.__name__} produced too few rows"
    # Every row is well-formed.
    for r in rows:
        assert r.school and r.school_name
        assert r.ap_exam and r.ap_exam_raw
        assert 1 <= r.score <= 5
        assert r.source_url.startswith("http")
    # A healthy majority carry extracted course codes.
    with_courses = sum(1 for r in rows if r.courses)
    assert with_courses / len(rows) >= 0.7


def _find(rows, exam, score):
    matches = [r for r in rows if r.ap_exam == exam and r.score == score]
    return matches[0] if matches else None


def test_uf_calculus_bc():
    r = _find(parse(UFScraper), "Calculus BC", 5)
    assert r is not None
    assert r.courses == ["MAC 2311", "MAC 2312"]
    assert r.credits == 8.0


def test_uga_calculus_bc_sums_credits_and_drops_exemptions():
    r = _find(parse(UGAScraper), "Calculus BC", 5)
    assert r is not None
    # 0-credit placement exemptions (MATH 1101/1113) are dropped.
    assert r.courses == ["MATH 2250", "MATH 2260"]
    assert r.credits == 8.0


def test_tamu_bare_credit_hours_parsed():
    r = _find(parse(TAMUScraper), "African American Studies", 3)
    assert r is not None
    assert r.courses == ["AFST 289"]
    assert r.credits == 3.0


def test_gatech_inline_score_and_course():
    r = _find(parse(GeorgiaTechScraper), "Calculus BC", 5)
    assert r is not None
    assert r.courses == ["MATH 1551", "MATH 1552"]
    assert r.credits == 6.0


def test_rutgers_expands_score_list():
    rows = parse(RutgersScraper)
    r4 = _find(rows, "Calculus BC", 4)
    r5 = _find(rows, "Calculus BC", 5)
    assert r4 and r5
    assert r4.courses == ["01:640:151", "01:640:152"]
    assert r4.credits == 8.0


def test_umn_titlecase_courses():
    r = _find(parse(UMNScraper), "Calculus BC", 5)
    assert r is not None
    assert r.courses == ["Math 1271"]
    assert r.credits == 4.0


def test_normalize_exam_aliases():
    from ap_transfer.normalize import normalize_exam

    assert normalize_exam("Mathematics - Calculus BC") == "Calculus BC"
    assert normalize_exam("Calc BC") == "Calculus BC"
    assert normalize_exam("AP Calculus BC") == "Calculus BC"
    assert normalize_exam("Economics: Macroeconomics") == "Macroeconomics"
