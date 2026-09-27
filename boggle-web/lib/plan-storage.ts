export const PLAN_SCHOOL_KEY = "boggle.school";
export const PLAN_MAJOR_KEY = "boggle.major";

export type StoredSchool = {
  code: string;
  name: string;
  location: string;
};

export type StoredMajor = {
  id: string;
  name: string;
};

export function saveSchool(school: StoredSchool) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(PLAN_SCHOOL_KEY, JSON.stringify(school));
}

export function loadSchool(): StoredSchool | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(PLAN_SCHOOL_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredSchool;
  } catch {
    return null;
  }
}

export function saveMajor(major: StoredMajor) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(PLAN_MAJOR_KEY, JSON.stringify(major));
}

export function loadMajor(): StoredMajor | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(PLAN_MAJOR_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredMajor;
  } catch {
    return null;
  }
}
