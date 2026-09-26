"""Minerva student web app: pick a college + major → recommended AP classes."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from ap_transfer import advisor, storage
from ap_transfer.majors import list_majors
from ap_transfer.scrapers import SCRAPERS, TOP20_CODES

app = Flask(__name__)

# Display names only. Credit numbers always come from the scraped snapshot.
_DISPLAY = {
    "UCB": ("UC Berkeley", "Berkeley, CA"),
    "UCLA": ("UCLA", "Los Angeles, CA"),
    "UMICH": ("Michigan", "Ann Arbor, MI"),
    "UNC": ("UNC", "Chapel Hill, NC"),
    "UVA": ("UVA", "Charlottesville, VA"),
    "UCSD": ("UC San Diego", "La Jolla, CA"),
    "UF": ("Florida", "Gainesville, FL"),
    "UTA": ("UT Austin", "Austin, TX"),
    "GT": ("Georgia Tech", "Atlanta, GA"),
    "UCD": ("UC Davis", "Davis, CA"),
    "UCI": ("UC Irvine", "Irvine, CA"),
    "UIUC": ("Illinois", "Urbana, IL"),
    "UWIS": ("Wisconsin", "Madison, WI"),
    "UCSB": ("UC Santa Barbara", "Santa Barbara, CA"),
    "OSU": ("Ohio State", "Columbus, OH"),
    "RU": ("Rutgers", "New Brunswick, NJ"),
    "UMD": ("Maryland", "College Park, MD"),
    "UW": ("Washington", "Seattle, WA"),
    "PU": ("Purdue", "West Lafayette, IN"),
    "UGA": ("Georgia", "Athens, GA"),
    "TAMU": ("Texas A&M", "College Station, TX"),
    "UMN": ("Minnesota", "Minneapolis, MN"),
}

_BLURBS = {
    "computer_science": "Software, algorithms, and systems.",
    "engineering": "Mechanical, electrical, civil, and more.",
    "biology": "Life sciences and lab foundations.",
    "chemistry": "General chemistry and the math behind it.",
    "physics": "Mechanics, electricity, and calculus.",
    "math": "Calculus, statistics, and computing.",
    "economics": "Markets, policy, and data.",
    "business": "Finance, marketing, management.",
    "psychology": "Behavior, stats, and biology.",
    "political_science": "Government, history, and policy.",
    "history": "U.S., European, and world history.",
    "english": "Writing, literature, and history.",
    "premed": "Medicine and the life sciences.",
    "nursing": "Biology, chemistry, and psychology.",
    "environmental": "Earth systems, biology, and chemistry.",
    "communications": "Writing, media, and public life.",
    "art": "Studio practice and art history.",
    "music": "Theory and musicianship.",
    "education": "A broad base for teaching.",
    "undecided": "Keep your options open.",
}


def _schools_payload():
    rows = storage.load_json()
    present = {code: name for code, name in advisor.schools(rows)}
    ordered = []
    for code, _cls in SCRAPERS.items():
        if code not in present:
            continue
        short, location = _DISPLAY.get(code, (present[code], ""))
        ordered.append(
            {
                "code": code,
                "name": present[code],
                "short": short,
                "location": location,
                "top20": code in TOP20_CODES,
            }
        )
    top = [s for s in ordered if s["top20"]]
    extra = [s for s in ordered if not s["top20"]]
    return top + extra


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/schools")
def api_schools():
    return jsonify(_schools_payload())


@app.get("/api/majors")
def api_majors():
    return jsonify(
        [{"id": m.id, "name": m.name, "blurb": _BLURBS.get(m.id, "")} for m in list_majors()]
    )


def _tier_dict(tier) -> dict:
    return {
        "score": tier.score,
        "courses": tier.courses,
        "credits": tier.credits,
        "award_raw": tier.award_raw,
    }


@app.get("/api/plan")
def api_plan():
    """Major plan built only from scraped equivalencies."""
    school = (request.args.get("school") or "").upper().strip()
    major = (request.args.get("major") or "").strip()
    score_raw = request.args.get("score")
    score = int(score_raw) if score_raw and score_raw.isdigit() else None
    if not school or not major:
        return jsonify({"error": "school and major are required"}), 400
    rows = storage.load_json()
    if not rows:
        return jsonify({"error": "No equivalency data loaded. Run scrape first."}), 503
    try:
        plans = advisor.build_plan(rows, school, major, expected_score=score)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    school_name = next((r.school_name for r in rows if r.school == school), school)
    short, location = _DISPLAY.get(school, (school_name, ""))
    source = next((p.source_url for p in plans if p.source_url), "")
    if not source:
        source = next((r.source_url for r in rows if r.school == school), "")
        source = source.split(" (fixture")[0]
    return jsonify(
        {
            "school": school,
            "school_name": school_name,
            "short": short,
            "location": location,
            "major": major,
            "score": score,
            "source_url": source,
            "exams": [
                {
                    "ap_exam": p.ap_exam,
                    "relevance": p.relevance,
                    "min_score": p.floor.score,
                    "courses": p.floor.courses,
                    "credits": p.floor.credits,
                    "award_raw": p.floor.award_raw,
                    "max_credits": max((t.credits or 0) for t in p.tiers),
                    "tiers": [_tier_dict(t) for t in p.tiers],
                }
                for p in plans
            ],
        }
    )


@app.get("/api/recommend")
def api_recommend():
    school = (request.args.get("school") or "").upper().strip()
    major = (request.args.get("major") or "").strip() or None
    score_raw = request.args.get("score")
    score = int(score_raw) if score_raw and score_raw.isdigit() else None
    if not school:
        return jsonify({"error": "school is required"}), 400
    rows = storage.load_json()
    if not rows:
        return jsonify({"error": "No equivalency data loaded. Run scrape first."}), 503
    try:
        recs = advisor.recommend(rows, school, major=major, expected_score=score)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    source = next((r.source_url for r in rows if r.school == school), "")
    school_name = next((r.school_name for r in rows if r.school == school), school)
    return jsonify(
        {
            "school": school,
            "school_name": school_name,
            "major": major,
            "score": score,
            "source_url": source,
            "recommendations": [
                {
                    "ap_exam": r.ap_exam,
                    "min_score": r.min_score,
                    "best_score": r.best_score,
                    "credits": r.best_credits,
                    "courses": r.courses,
                    "award_raw": r.award_raw,
                }
                for r in recs
            ],
        }
    )


def main() -> None:
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
