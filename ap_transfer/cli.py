"""Command-line interface for the AP transfer equivalency tool."""

from __future__ import annotations

import argparse
import sys

from . import advisor, storage
from .scrapers import SCRAPERS, all_scrapers, get_scraper


def _cmd_scrape(args: argparse.Namespace) -> int:
    scrapers = [get_scraper(c) for c in args.school] if args.school else all_scrapers()
    all_rows = []
    print(f"Scraping {len(scrapers)} school(s)...\n")
    failures = 0
    for sc in scrapers:
        result = sc.scrape()
        if result.ok:
            all_rows.extend(result.equivalencies)
            print(f"  [ok]   {sc.code:5} {sc.name:45} {len(result.equivalencies):4} rows")
        else:
            failures += 1
            print(f"  [FAIL] {sc.code:5} {sc.name:45} {result.error}")
    if not all_rows:
        print("\nNo data scraped.", file=sys.stderr)
        return 1
    json_path = storage.save_json(all_rows)
    db_path = storage.save_sqlite(all_rows)
    print(f"\nSaved {len(all_rows)} equivalencies from {len(scrapers) - failures} school(s).")
    print(f"  JSON:   {json_path}")
    print(f"  SQLite: {db_path}")
    return 0


def _load_or_exit() -> list:
    rows = storage.load_json()
    if not rows:
        print("No data found. Run 'scrape' first.", file=sys.stderr)
        sys.exit(1)
    return rows


def _cmd_schools(args: argparse.Namespace) -> int:
    rows = _load_or_exit()
    print("Schools in dataset:\n")
    for code, name in advisor.schools(rows):
        n = sum(1 for r in rows if r.school == code)
        print(f"  {code:5} {name:45} {n:4} equivalencies")
    return 0


def _fmt_courses(courses: list[str], award: str) -> str:
    if courses:
        return ", ".join(courses)
    return award[:48]


def _cmd_recommend(args: argparse.Namespace) -> int:
    rows = _load_or_exit()
    recs = advisor.recommend(
        rows, args.school, subject=args.subject, expected_score=args.score
    )
    if not recs:
        print("No matching AP exams found.")
        return 0
    name = recs[0].school_name
    header = f"AP exams worth taking for {name} ({args.school.upper()})"
    if args.subject:
        header += f" — subject filter: '{args.subject}'"
    if args.score:
        header += f" — expected score: {args.score}"
    print(header + "\n")
    print(f"  {'AP Exam':40} {'MinScore':8} {'Best':5} {'Credits':7} Courses")
    print("  " + "-" * 92)
    for r in recs:
        cred = f"{r.best_credits:g}" if r.best_credits is not None else "-"
        print(
            f"  {r.ap_exam[:40]:40} {r.min_score:^8} {r.best_score:^5} "
            f"{cred:^7} {_fmt_courses(r.courses, r.award_raw)}"
        )
    source = next((r.source_url for r in rows if r.school == args.school.upper()), "")
    print(f"\n  {len(recs)} exam(s). Source: {source}")
    return 0


def _cmd_exam(args: argparse.Namespace) -> int:
    rows = _load_or_exit()
    table = advisor.compare_exam(rows, args.exam)
    if not table:
        print(f"No school in the dataset grants credit for '{args.exam}'.")
        return 0
    from .normalize import normalize_exam

    print(f"Cross-school comparison for AP {normalize_exam(args.exam)}:\n")
    for code, items in sorted(table.items()):
        name = items[0].school_name
        print(f"  {name} ({code}):")
        for it in items:
            cred = f"{it.credits:g}" if it.credits is not None else "-"
            courses = ", ".join(it.courses) or it.award_raw[:60]
            print(f"     score {it.score}: {courses}  [{cred} cr]")
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ap_transfer",
        description="Scrape and query AP credit transfer equivalencies at top public US universities.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("scrape", help="Scrape equivalencies and save to data/")
    sp.add_argument(
        "--school", nargs="*", metavar="CODE",
        help=f"Limit to specific school code(s): {', '.join(SCRAPERS)}",
    )
    sp.set_defaults(func=_cmd_scrape)

    ss = sub.add_parser("schools", help="List schools in the dataset")
    ss.set_defaults(func=_cmd_schools)

    sr = sub.add_parser("recommend", help="Recommend AP exams for a school")
    sr.add_argument("--school", required=True, help="School code, e.g. UF")
    sr.add_argument("--subject", help="Filter by subject/major keyword, e.g. 'math'")
    sr.add_argument(
        "--score", type=int, choices=[1, 2, 3, 4, 5],
        help="The AP score you expect to earn; shows only awards you'd qualify for",
    )
    sr.set_defaults(func=_cmd_recommend)

    se = sub.add_parser("exam", help="Compare one AP exam across all schools")
    se.add_argument("exam", help="AP exam name, e.g. 'Calculus BC'")
    se.set_defaults(func=_cmd_exam)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
