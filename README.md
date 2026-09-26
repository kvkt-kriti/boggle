# Minerva — AP Credit Transfer Advisor

A Python scraper, query tool, and **student web app** that collects AP exam
credit equivalencies from the **top 20 public US universities** (US News 2026)
and recommends which AP classes to take based on a target college and major.

For each university it answers: *"If I score X on AP exam Y, which course(s)
will I get credit for?"* The web app turns that into: *"I'm aiming for this
college and major — which APs should I take?"*

## Coverage

All 20 schools from the 2026 US News Top Public National Universities ranking,
plus Texas A&M and Minnesota (already supported):

| Code | University |
| --- | --- |
| `UCB` | University of California, Berkeley |
| `UCLA` | University of California, Los Angeles |
| `UMICH` | University of Michigan |
| `UNC` | University of North Carolina at Chapel Hill |
| `UVA` | University of Virginia |
| `UCSD` | University of California, San Diego |
| `UF` | University of Florida |
| `UTA` | The University of Texas at Austin |
| `GT` | Georgia Institute of Technology |
| `UCD` | University of California, Davis |
| `UCI` | University of California, Irvine |
| `UIUC` | University of Illinois Urbana-Champaign |
| `UWIS` | University of Wisconsin–Madison |
| `UCSB` | University of California, Santa Barbara |
| `OSU` | The Ohio State University |
| `RU` | Rutgers University (School of Engineering) |
| `UMD` | University of Maryland, College Park |
| `UW` | University of Washington |
| `PU` | Purdue University |
| `UGA` | University of Georgia |
| `TAMU` | Texas A&M University *(extra)* |
| `UMN` | University of Minnesota Twin Cities *(extra)* |

Some campuses publish AP data as HTML tables, some as PDFs (UMD), and UC
campuses as prose summaries. A few sites block live bots; those scrapers fall
back to a saved fixture (UVA) or Wayback Machine snapshot (Michigan).

## Install

```bash
pip install -r requirements.txt
```

## Student web app

```bash
python -m webapp.app
# open http://127.0.0.1:5000
```

Pick a college + major (+ optional expected AP score). Minerva returns a ranked
list of AP exams that earn useful credit for that combination.

## CLI

```bash
python -m ap_transfer scrape
python -m ap_transfer schools
python -m ap_transfer majors
python -m ap_transfer recommend --school GT --major computer_science --score 4
python -m ap_transfer exam "Calculus BC"
```

## Project layout

```
ap_transfer/
  scrapers/          # one module per university + registry
  majors.py          # major → AP subject mapping for recommendations
  advisor.py         # query & recommendation logic
  cli.py
webapp/              # Flask student UI
data/ap_equivalencies.json
tests/fixtures/      # saved pages for offline parser tests
```

## Testing

```bash
python -m pytest -q
```

## Roadmap

- Richer UC / major-college-specific award variants (Engineering vs L&S).
- Map AP credit onto **official major degree requirements** (needs per-major
  curriculum data) instead of subject-keyword heuristics.
- Periodic re-scrape + change tracking.
```

> Data is scraped from each university's official page and is subject to change;
> always confirm with the university before making decisions.
