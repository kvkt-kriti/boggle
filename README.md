# Minerva — AP Credit Transfer Advisor

A Python web scraper and query tool that collects **AP exam credit
equivalencies** published by top public US universities and helps students
decide which AP courses to take in high school based on the school they want to
attend and the subject area of their intended major.

For each university it answers: *"If I score X on AP exam Y, which specific
course(s) will I get credit for, and how many credit hours?"*

## Why this is hard (and how this project handles it)

Every university publishes AP credit data differently — some use clean HTML
tables, others use PDFs or JavaScript search apps, and many block naive
scrapers. This project:

- sends realistic browser headers (`ap_transfer/http.py`) so sites that
  otherwise return `403/404` serve normally;
- uses a small **per-school parser** for each site's table layout, all sharing a
  common `BaseScraper` and normalized data model, so adding a school is easy;
- **normalizes** the many spellings of each AP exam (e.g. `"Mathematics -
  Calculus BC"`, `"Calc BC"` → `Calculus BC`) so results are comparable across
  schools (`ap_transfer/normalize.py`);
- stores results as both a **JSON snapshot** (`data/ap_equivalencies.json`) and a
  queryable **SQLite** database (`data/ap_equivalencies.db`).

## Currently supported schools

All are top-ranked US public universities that publish static HTML equivalency
tables:

| Code | University |
| --- | --- |
| `UF` | University of Florida |
| `UGA` | University of Georgia |
| `TAMU` | Texas A&M University |
| `GT` | Georgia Institute of Technology |
| `RU` | Rutgers University (School of Engineering) |
| `UMN` | University of Minnesota (Twin Cities) |

Schools that publish AP data only via PDFs (e.g. UW–Madison) or JavaScript
lookup apps (e.g. the UC system, Purdue) are natural follow-ups — the framework
is designed so each new school is one small parser module registered in
`ap_transfer/scrapers/__init__.py`.

## Install

```bash
pip install -r requirements.txt
```

## Usage

Scrape all supported schools (writes `data/ap_equivalencies.json` and `.db`):

```bash
python -m ap_transfer scrape
# or a subset:
python -m ap_transfer scrape --school UF GT
```

List the schools currently in the dataset:

```bash
python -m ap_transfer schools
```

Recommend the highest-value AP exams for a target school, optionally filtered by
the subject area of a major:

```bash
python -m ap_transfer recommend --school UF
python -m ap_transfer recommend --school GT --subject math
python -m ap_transfer recommend --school UGA --subject biology --min-score 4
```

Compare how one AP exam transfers across every school:

```bash
python -m ap_transfer exam "Calculus BC"
```

## Project layout

```
ap_transfer/
  http.py            # browser-headed fetch with retry/backoff
  models.py          # Equivalency / ScrapeResult data models
  normalize.py       # canonical AP exam names + course/credit extraction
  storage.py         # JSON + SQLite persistence
  advisor.py         # query & recommendation logic
  cli.py             # command-line interface
  scrapers/          # one module per university + registry
tests/
  fixtures/          # saved HTML pages (parsers tested offline)
  test_parsers.py
```

## Testing

Parsers are tested against saved HTML fixtures, so tests run without network
access:

```bash
python -m pytest -q
```

## Roadmap

- Add PDF and JavaScript-rendered schools (UW–Madison, UC campuses, Michigan,
  UT Austin) to reach the full top-20 public universities.
- Map AP credit to **specific major degree requirements** (needs per-major
  curriculum data) so recommendations can be tailored to a declared major rather
  than a subject keyword.
- Periodic re-scrape + change tracking, since universities revise equivalencies
  annually.
```

> Data is scraped from each university's official page and is subject to change;
> always confirm with the university before making decisions.
