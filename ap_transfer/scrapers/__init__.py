"""Registry of available university scrapers."""

from __future__ import annotations

from .base import BaseScraper
from .gatech import GeorgiaTechScraper
from .rutgers import RutgersScraper
from .tamu import TAMUScraper
from .uf import UFScraper
from .uga import UGAScraper
from .umn import UMNScraper

# Ordered list of scraper classes. Add new schools here.
SCRAPER_CLASSES: list[type[BaseScraper]] = [
    UFScraper,
    UGAScraper,
    TAMUScraper,
    GeorgiaTechScraper,
    RutgersScraper,
    UMNScraper,
]

SCRAPERS: dict[str, type[BaseScraper]] = {c.code: c for c in SCRAPER_CLASSES}


def get_scraper(code: str) -> BaseScraper:
    try:
        return SCRAPERS[code.upper()]()
    except KeyError as exc:
        raise KeyError(f"Unknown school code: {code!r}. Known: {', '.join(SCRAPERS)}") from exc


def all_scrapers() -> list[BaseScraper]:
    return [c() for c in SCRAPER_CLASSES]


__all__ = ["SCRAPERS", "SCRAPER_CLASSES", "get_scraper", "all_scrapers", "BaseScraper"]
