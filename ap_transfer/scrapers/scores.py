"""Shared helpers for expanding published AP score tokens into concrete scores."""

from __future__ import annotations

import re

from ..normalize import parse_scores

_RANGE_RE = re.compile(
    r"(?<!\d)([1-5])\s*[-–—to]+\s*([1-5])(?!\d)",
    re.I,
)
_PLUS_RE = re.compile(r"(?<!\d)([1-5])\s*\+(?!\d)")


def expand_scores(text: str) -> list[int]:
    """Expand score cells like ``3+``, ``3-5``, ``4 or 5``, ``3,4,5`` into ints."""
    if not text:
        return []
    t = text.strip().lower()
    if t in {"n/a", "na", "-", "—", ""}:
        return []

    scores: set[int] = set()
    for a, b in _RANGE_RE.findall(t):
        lo, hi = int(a), int(b)
        if lo > hi:
            lo, hi = hi, lo
        scores.update(range(lo, hi + 1))
    for m in _PLUS_RE.findall(t):
        scores.update(range(int(m), 6))
    scores.update(parse_scores(t))
    return sorted(s for s in scores if 1 <= s <= 5)


def parse_hours_token(text: str) -> float | None:
    """Parse a bare credit-hour cell like ``3``, ``3***``, or ``5,5,5`` (sum)."""
    if not text:
        return None
    nums = re.findall(r"\d+(?:\.\d+)?", text.replace("*", ""))
    if not nums:
        return None
    try:
        return float(sum(float(n) for n in nums))
    except ValueError:
        return None
