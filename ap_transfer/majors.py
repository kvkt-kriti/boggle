"""Major → subject keyword mapping for AP recommendations.

True major-requirement matching needs per-school degree audits. Until that
exists, we map common high-school-facing majors to the AP exams / course
subjects that typically satisfy prerequisites or gen-eds for that major.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Major:
    id: str
    name: str
    # Keywords matched against ap_exam / courses / gen_ed text.
    keywords: tuple[str, ...]
    # Extra AP exam names that are almost always useful for this major.
    priority_exams: tuple[str, ...] = ()


MAJORS: list[Major] = [
    Major(
        "computer_science",
        "Computer Science",
        ("computer", "math", "calculus", "statistics", "physics"),
        ("Computer Science A", "Computer Science Principles", "Calculus BC", "Calculus AB", "Statistics"),
    ),
    Major(
        "engineering",
        "Engineering",
        ("math", "calculus", "physics", "chemistry", "computer"),
        ("Calculus BC", "Calculus AB", "Physics C: Mechanics", "Physics C: Electricity & Magnetism", "Chemistry", "Computer Science A"),
    ),
    Major(
        "biology",
        "Biology / Life Sciences",
        ("biology", "chem", "math", "statistics", "environmental"),
        ("Biology", "Chemistry", "Calculus AB", "Statistics", "Environmental Science"),
    ),
    Major(
        "chemistry",
        "Chemistry",
        ("chem", "math", "calculus", "physics"),
        ("Chemistry", "Calculus BC", "Physics C: Mechanics", "Physics 1"),
    ),
    Major(
        "physics",
        "Physics",
        ("physics", "math", "calculus"),
        ("Physics C: Mechanics", "Physics C: Electricity & Magnetism", "Calculus BC", "Calculus AB"),
    ),
    Major(
        "math",
        "Mathematics / Statistics",
        ("math", "calculus", "statistics", "computer"),
        ("Calculus BC", "Calculus AB", "Statistics", "Computer Science A", "Precalculus"),
    ),
    Major(
        "economics",
        "Economics / Business",
        ("econ", "math", "calculus", "statistics", "government"),
        ("Macroeconomics", "Microeconomics", "Calculus AB", "Statistics", "US Government and Politics"),
    ),
    Major(
        "business",
        "Business / Finance",
        ("econ", "math", "calculus", "statistics", "computer"),
        ("Macroeconomics", "Microeconomics", "Calculus AB", "Statistics", "Computer Science Principles"),
    ),
    Major(
        "psychology",
        "Psychology",
        ("psych", "biology", "statistics", "math"),
        ("Psychology", "Statistics", "Biology", "Calculus AB"),
    ),
    Major(
        "political_science",
        "Political Science / Government",
        ("government", "history", "econ", "english"),
        ("US Government and Politics", "Comparative Government and Politics", "US History", "Macroeconomics", "English Language and Composition"),
    ),
    Major(
        "history",
        "History",
        ("history", "english", "government", "geography"),
        ("US History", "European History", "World History", "Human Geography", "English Literature and Composition"),
    ),
    Major(
        "english",
        "English / Literature",
        ("english", "literature", "history", "art history"),
        ("English Language and Composition", "English Literature and Composition", "US History", "Art History"),
    ),
    Major(
        "premed",
        "Pre-Med / Health",
        ("biology", "chem", "physics", "math", "statistics", "psych"),
        ("Biology", "Chemistry", "Physics 1", "Calculus AB", "Statistics", "Psychology"),
    ),
    Major(
        "nursing",
        "Nursing",
        ("biology", "chem", "psych", "statistics", "math"),
        ("Biology", "Chemistry", "Psychology", "Statistics"),
    ),
    Major(
        "environmental",
        "Environmental Science",
        ("environmental", "biology", "chem", "geography", "stats"),
        ("Environmental Science", "Biology", "Chemistry", "Human Geography", "Statistics"),
    ),
    Major(
        "communications",
        "Communications / Media",
        ("english", "history", "psych", "government"),
        ("English Language and Composition", "Psychology", "US Government and Politics", "US History"),
    ),
    Major(
        "art",
        "Art / Design",
        ("art", "studio", "drawing", "history"),
        ("Studio Art: 2-D Design", "Studio Art: Drawing", "Studio Art: 3-D Design", "Art History"),
    ),
    Major(
        "music",
        "Music",
        ("music",),
        ("Music Theory",),
    ),
    Major(
        "education",
        "Education",
        ("english", "history", "math", "psych"),
        ("English Language and Composition", "US History", "Psychology", "Calculus AB", "Statistics"),
    ),
    Major(
        "undecided",
        "Undecided / Exploring",
        ("english", "math", "history", "science", "biology", "chem"),
        (
            "English Language and Composition",
            "Calculus AB",
            "US History",
            "Biology",
            "Statistics",
            "Computer Science Principles",
        ),
    ),
]

MAJORS_BY_ID = {m.id: m for m in MAJORS}


def get_major(major_id: str) -> Major | None:
    return MAJORS_BY_ID.get(major_id)


def list_majors() -> list[Major]:
    return list(MAJORS)
