"""Parser smoke tests for newly added top-20 school scrapers."""

from __future__ import annotations

import pathlib

import pytest

from ap_transfer.scrapers import (
    OSUScraper,
    PurdueScraper,
    UCBScraper,
    UCLAScraper,
    UIUCScraper,
    UMDScraper,
    UMichScraper,
    UNCScraper,
    UTAustinScraper,
    UVAScraper,
    UWASHScraper,
    UWISScraper,
)
from ap_transfer.scrapers.scores import expand_scores

FIX = pathlib.Path(__file__).parent / "fixtures"


def _html(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8", errors="ignore")


@pytest.mark.parametrize(
    "cls,fixture,minimum",
    [
        (UNCScraper, "unc.html", 50),
        (OSUScraper, "osu.html", 40),
        (UIUCScraper, "uiuc.html", 40),
        (UWASHScraper, "uwash.html", 40),
        (PurdueScraper, "purdue.html", 40),
        (UWISScraper, "uwis.html", 40),
        (UTAustinScraper, "uta.html", 30),
        (UMichScraper, "umich.html", 30),
        (UVAScraper, "uva.html", 40),
            (UCLAScraper, "ucla.html", 15),
            (UCBScraper, "ucb.html", 5),
        ],
    )
def test_new_parsers_produce_rows(cls, fixture, minimum):
    rows = cls().parse(_html(fixture))
    assert len(rows) >= minimum, f"{cls.__name__} produced {len(rows)} rows"
    for r in rows[:5]:
        assert r.school and r.ap_exam
        assert 1 <= r.score <= 5


def test_umd_pdf_parser():
    data = (FIX / "umd.pdf").read_bytes()
    rows = UMDScraper().parse_pdf(data)
    assert len(rows) >= 25
    exams = {r.ap_exam for r in rows}
    assert any("Calculus" in e or e.startswith("Calculus") for e in exams) or any(
        "Biology" in e for e in exams
    ) or len(exams) >= 10


def test_expand_scores_tokens():
    assert expand_scores("3+") == [3, 4, 5]
    assert expand_scores("3-5") == [3, 4, 5]
    assert expand_scores("4 or 5") == [4, 5]
    assert expand_scores("3,4,5") == [3, 4, 5]


def test_unc_calculus_bc():
    rows = UNCScraper().parse(_html("unc.html"))
    matches = [r for r in rows if r.ap_exam == "Calculus BC" and r.score == 3]
    assert matches
    assert "MATH 231" in matches[0].courses or any("231" in c for c in matches[0].courses)


def test_osu_calculus_bc():
    rows = OSUScraper().parse(_html("osu.html"))
    matches = [r for r in rows if r.ap_exam == "Calculus BC"]
    assert matches
    assert matches[0].credits and matches[0].credits >= 8


def test_recommend_by_major():
    from ap_transfer import advisor
    from ap_transfer.scrapers import UFScraper

    rows = UFScraper().parse((FIX / "uf.html").read_text(encoding="utf-8"))
    recs = advisor.recommend(rows, "UF", major="computer_science")
    exams = [r.ap_exam for r in recs]
    assert "Computer Science A" in exams or "Calculus BC" in exams
    # Priority exams should appear near the top.
    assert exams[0] in {
        "Computer Science A",
        "Computer Science Principles",
        "Calculus BC",
        "Calculus AB",
        "Statistics",
    }
