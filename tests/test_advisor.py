"""Tests for the query/recommendation layer using parsed fixture data."""

from __future__ import annotations

import pathlib

from ap_transfer import advisor
from ap_transfer.scrapers import all_scrapers

FIX = pathlib.Path(__file__).parent / "fixtures"
_FILE = {"UF": "uf", "UGA": "uga", "TAMU": "tamu", "GT": "gatech", "RU": "rutgers", "UMN": "umn"}


def _all_rows():
    rows = []
    for sc in all_scrapers():
        html = (FIX / f"{_FILE[sc.code]}.html").read_text(encoding="utf-8")
        rows.extend(sc.parse(html))
    return rows


def test_recommend_sorted_by_credits():
    rows = _all_rows()
    recs = advisor.recommend(rows, "UF")
    assert recs
    credits = [r.best_credits or 0 for r in recs]
    assert credits == sorted(credits, reverse=True)


def test_recommend_subject_filter():
    rows = _all_rows()
    recs = advisor.recommend(rows, "GT", subject="math")
    exams = {r.ap_exam for r in recs}
    assert "Calculus BC" in exams
    assert "Biology" not in exams


def test_recommend_expected_score_limits_awards():
    rows = _all_rows()
    low = advisor.recommend(rows, "UF", expected_score=3)
    for r in low:
        assert r.best_score <= 3


def test_compare_exam_spans_schools():
    rows = _all_rows()
    table = advisor.compare_exam(rows, "Calculus BC")
    assert {"UF", "GT", "UGA", "RU", "TAMU", "UMN"}.issubset(table.keys())
