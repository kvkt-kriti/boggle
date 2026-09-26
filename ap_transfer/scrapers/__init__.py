"""Registry of available university scrapers (top-20 publics + extras)."""

from __future__ import annotations

from .base import BaseScraper
from .gatech import GeorgiaTechScraper
from .osu import OSUScraper
from .purdue import PurdueScraper
from .rutgers import RutgersScraper
from .tamu import TAMUScraper
from .uc import (
    UCBScraper,
    UCDScraper,
    UCIScraper,
    UCLAScraper,
    UCSBScraper,
    UCSDScraper,
)
from .uf import UFScraper
from .uga import UGAScraper
from .uiuc import UIUCScraper
from .umd import UMDScraper
from .umich import UMichScraper
from .umn import UMNScraper
from .unc import UNCScraper
from .uta import UTAustinScraper
from .uva import UVAScraper
from .uwash import UWASHScraper
from .uwis import UWISScraper

# US News 2026 Top Public National Universities (20 schools), then extras we
# already support (Texas A&M, Minnesota) kept for students targeting those.
SCRAPER_CLASSES: list[type[BaseScraper]] = [
    # Top 20 publics (2026)
    UCBScraper,
    UCLAScraper,
    UMichScraper,
    UNCScraper,
    UVAScraper,
    UCSDScraper,
    UFScraper,
    UTAustinScraper,
    GeorgiaTechScraper,
    UCDScraper,
    UCIScraper,
    UIUCScraper,
    UWISScraper,
    UCSBScraper,
    OSUScraper,
    RutgersScraper,
    UMDScraper,
    UWASHScraper,
    PurdueScraper,
    UGAScraper,
    # Extra publics already supported
    TAMUScraper,
    UMNScraper,
]

TOP20_CODES = {
    "UCB",
    "UCLA",
    "UMICH",
    "UNC",
    "UVA",
    "UCSD",
    "UF",
    "UTA",
    "GT",
    "UCD",
    "UCI",
    "UIUC",
    "UWIS",
    "UCSB",
    "OSU",
    "RU",
    "UMD",
    "UW",
    "PU",
    "UGA",
}

SCRAPERS: dict[str, type[BaseScraper]] = {c.code: c for c in SCRAPER_CLASSES}


def get_scraper(code: str) -> BaseScraper:
    try:
        return SCRAPERS[code.upper()]()
    except KeyError as exc:
        raise KeyError(f"Unknown school code: {code!r}. Known: {', '.join(SCRAPERS)}") from exc


def all_scrapers() -> list[BaseScraper]:
    return [c() for c in SCRAPER_CLASSES]


def top20_scrapers() -> list[BaseScraper]:
    return [c() for c in SCRAPER_CLASSES if c.code in TOP20_CODES]


__all__ = [
    "SCRAPERS",
    "SCRAPER_CLASSES",
    "TOP20_CODES",
    "get_scraper",
    "all_scrapers",
    "top20_scrapers",
    "BaseScraper",
]
