"""The student plan must quote scraped awards, not invented course codes."""

from __future__ import annotations

import pathlib

from ap_transfer import advisor
from ap_transfer.scrapers import UFScraper

FIX = pathlib.Path(__file__).parent / "fixtures"


def test_uf_cs_plan_uses_real_calculus_bc_tiers():
    rows = UFScraper().parse((FIX / "uf.html").read_text(encoding="utf-8"))
    plans = advisor.build_plan(rows, "UF", "computer_science")
    calc = next(p for p in plans if p.ap_exam == "Calculus BC")
    by_score = {t.score: t for t in calc.tiers}
    assert by_score[3].courses == ["MAC 2311"]
    assert by_score[3].credits == 4.0
    assert by_score[5].courses == ["MAC 2311", "MAC 2312"]
    assert by_score[5].credits == 8.0
    # Floor is the score-3 award, not the score-5 package.
    assert calc.floor.courses == ["MAC 2311"]
    assert calc.relevance == "core"


def test_expected_score_drops_higher_tiers():
    rows = UFScraper().parse((FIX / "uf.html").read_text(encoding="utf-8"))
    plans = advisor.build_plan(rows, "UF", "computer_science", expected_score=3)
    calc = next(p for p in plans if p.ap_exam == "Calculus BC")
    assert [t.score for t in calc.tiers] == [3]
    assert calc.tiers[0].courses == ["MAC 2311"]
