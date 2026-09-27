"""UI major catalog and keyword maps for fit badges / WHY IT'S HERE copy.

Credits and course awards always come from advisor.recommend — these maps only
drive presentation (badges, explanations, chat context) and optional subject hints.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Major:
    id: str
    name: str
    blurb: str
    # Keywords used to label CORE / STRONG / NICE against exam + course text
    core_keywords: tuple[str, ...]
    strong_keywords: tuple[str, ...]
    # Optional advisor subject substring (narrow); null means unfiltered recommend
    subject_hint: str | None = None


MAJORS: list[Major] = [
    Major(
        "computer-science",
        "Computer Science",
        "Software, algorithms, and systems.",
        ("computer science", "computer science a", "computer science principles"),
        ("calculus", "statistics", "physics"),
        "computer",
    ),
    Major(
        "data-science",
        "Data Science",
        "Statistics, computing, and evidence.",
        ("statistics", "computer science"),
        ("calculus", "physics", "economics"),
        "statistics",
    ),
    Major(
        "engineering",
        "Engineering",
        "Mechanical, electrical, civil, and more.",
        ("physics", "calculus", "chemistry"),
        ("computer science", "statistics"),
        "physics",
    ),
    Major(
        "mathematics-physics",
        "Mathematics / Physics",
        "Theory, modelling, and discovery.",
        ("calculus", "physics", "statistics"),
        ("chemistry", "computer science"),
        "calculus",
    ),
    Major(
        "pre-med-biology",
        "Pre-Med / Biology",
        "Medicine and the life sciences.",
        ("biology", "chemistry", "physics"),
        ("statistics", "psychology", "calculus"),
        "biology",
    ),
    Major(
        "environmental-science",
        "Environmental Science",
        "Climate, ecosystems, and policy.",
        ("environmental", "biology", "chemistry"),
        ("geography", "physics", "statistics"),
        "environmental",
    ),
    Major(
        "psychology",
        "Psychology",
        "Mind, behavior, and research.",
        ("psychology",),
        ("statistics", "biology", "human geography"),
        "psychology",
    ),
    Major(
        "business",
        "Business",
        "Finance, marketing, management.",
        ("economics", "statistics"),
        ("calculus", "computer science", "psychology"),
        "economics",
    ),
    Major(
        "economics",
        "Economics",
        "Markets, policy, and data.",
        ("economics", "statistics", "calculus"),
        ("government", "computer science"),
        "economics",
    ),
    Major(
        "public-policy",
        "Public Policy / Political Science",
        "Government, law, and civic life.",
        ("government", "politics", "history"),
        ("economics", "statistics", "human geography"),
        "government",
    ),
    Major(
        "english-humanities",
        "English / Humanities",
        "Literature, writing, and culture.",
        ("english", "literature", "history", "art history"),
        ("human geography", "psychology", "spanish", "french"),
        "english",
    ),
    Major(
        "communications",
        "Communications / Media",
        "Writing, media, and public voice.",
        ("english", "language"),
        ("psychology", "history", "art", "statistics"),
        "english",
    ),
    Major(
        "architecture-design",
        "Architecture / Design",
        "Space, form, and visual craft.",
        ("art", "drawing", "2-d", "3-d", "studio"),
        ("physics", "calculus", "history"),
        "art",
    ),
    Major(
        "education",
        "Education",
        "Teaching, learning, and schools.",
        ("psychology", "history", "english"),
        ("statistics", "biology", "human geography"),
        "psychology",
    ),
    Major(
        "undecided",
        "Undecided / Exploring",
        "Keep options open across fields.",
        ("calculus", "english", "statistics"),
        ("biology", "history", "computer science", "physics"),
        None,
    ),
]

SCHOOL_LOCATIONS: dict[str, str] = {
    "UF": "Gainesville, FL",
    "UGA": "Athens, GA",
    "TAMU": "College Station, TX",
    "GT": "Atlanta, GA",
    "RU": "New Brunswick, NJ",
    "UMN": "Minneapolis, MN",
}


def get_major(major_id: str) -> Major | None:
    for m in MAJORS:
        if m.id == major_id:
            return m
    return None


def fit_badge(exam: str, courses: list[str], major: Major | None) -> str:
    """Return CORE FOR YOUR MAJOR | STRONG MATCH | NICE-TO-HAVE for UI only."""
    if major is None:
        return "STRONG MATCH"
    hay = " ".join([exam, *courses]).lower()
    if any(k in hay for k in major.core_keywords):
        return "CORE FOR YOUR MAJOR"
    if any(k in hay for k in major.strong_keywords):
        return "STRONG MATCH"
    return "NICE-TO-HAVE"


def why_copy(exam: str, major: Major | None, school_name: str) -> str:
    if major is None:
        return (
            f"{exam} appears on {school_name}'s published AP credit chart and "
            "earns transferable credit toward your degree."
        )
    if major.id == "undecided":
        return (
            f"{exam} clears published credit at {school_name}, keeping doors open "
            "while you decide on a major."
        )
    return (
        f"This supports a {major.name} path at {school_name} and unlocks credit "
        "you'd otherwise earn in an early-semester course — confirm on the official chart."
    )
