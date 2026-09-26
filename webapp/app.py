"""Minerva student web app: pick a college + major → recommended AP classes."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from ap_transfer import advisor, storage
from ap_transfer.majors import list_majors
from ap_transfer.scrapers import SCRAPERS, TOP20_CODES

app = Flask(__name__)


def _schools_payload():
    rows = storage.load_json()
    present = {code: name for code, name in advisor.schools(rows)}
    # Prefer top-20 ordering; append any extras that have data.
    ordered = []
    seen = set()
    for code, cls in SCRAPERS.items():
        if code in TOP20_CODES and code in present:
            ordered.append(
                {
                    "code": code,
                    "name": present[code],
                    "top20": True,
                }
            )
            seen.add(code)
    for code, name in present.items():
        if code not in seen:
            ordered.append({"code": code, "name": name, "top20": code in TOP20_CODES})
    return ordered


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/schools")
def api_schools():
    return jsonify(_schools_payload())


@app.get("/api/majors")
def api_majors():
    return jsonify([{"id": m.id, "name": m.name} for m in list_majors()])


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
