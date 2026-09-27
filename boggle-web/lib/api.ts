export type School = {
  code: string;
  name: string;
  location: string;
};

export type Major = {
  id: string;
  name: string;
  blurb: string;
  index: number;
};

export type Recommendation = {
  ap_exam: string;
  min_score: number;
  best_score: number;
  best_credits: number | null;
  courses: string[];
  award_raw: string;
  school: string;
  school_name: string;
  fit: string;
  why: string;
  source_url: string;
};

export type RecommendResponse = {
  school: string;
  school_name: string;
  source_url: string;
  major: { id: string; name: string } | null;
  subject_filter: string | null;
  exam_count: number;
  total_credits: number;
  recommendations: Recommendation[];
};

function apiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL ?? "";
  return raw.replace(/\/$/, "");
}

export function hasApiBase(): boolean {
  return Boolean(apiBase());
}

async function apiGet<T>(path: string, query?: Record<string, string | undefined>): Promise<T> {
  const base = apiBase();
  if (!base) {
    throw new Error(
      "NEXT_PUBLIC_API_URL is not set. Copy boggle-web/.env.example to .env.local.",
    );
  }
  const cleanPath = path.replace(/^\//, "");
  const url = new URL(`${base}/${cleanPath}`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v != null && v !== "") url.searchParams.set(k, v);
    }
  }
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function fetchSchools() {
  return apiGet<School[]>("schools");
}

export function fetchMajors() {
  return apiGet<Major[]>("majors");
}

export function fetchRecommend(opts: {
  school: string;
  major?: string;
  score?: string;
}) {
  return apiGet<RecommendResponse>("recommend", {
    school: opts.school,
    major: opts.major,
    score: opts.score,
  });
}
