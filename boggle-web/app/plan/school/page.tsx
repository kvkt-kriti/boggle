"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Logo } from "@/components/Logo";
import { PrimaryButton } from "@/components/PrimaryButton";
import { SearchInput } from "@/components/SearchInput";
import { SelectionCard } from "@/components/SelectionCard";
import { StepHeader } from "@/components/StepHeader";
import { fetchSchools, type School } from "@/lib/api";
import { loadSchool, saveSchool } from "@/lib/plan-storage";

export default function SchoolPage() {
  const router = useRouter();
  const [schools, setSchools] = useState<School[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const existing = loadSchool();
    if (existing) setSelected(existing.code);
    fetchSchools()
      .then(setSchools)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return schools;
    return schools.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        s.code.toLowerCase().includes(q) ||
        s.location.toLowerCase().includes(q),
    );
  }, [schools, query]);

  function continueNext() {
    const school = schools.find((s) => s.code === selected);
    if (!school) return;
    saveSchool(school);
    router.push("/plan/major");
  }

  return (
    <main className="min-h-screen bg-cream">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col px-6 py-6 md:px-8">
        <nav className="mb-10 flex items-center justify-between">
          <Logo />
          <p className="text-[13px] tracking-[0.16em] text-ink-faint">01 — 02</p>
        </nav>

        <StepHeader
          step={1}
          title="Where are you aiming?"
          subtitle="Choose the public university you have your eye on."
        />

        <SearchInput
          value={query}
          onChange={setQuery}
          placeholder="Search schools..."
          className="mb-6"
        />

        {loading ? (
          <p className="text-ink-muted">Loading schools…</p>
        ) : error ? (
          <p className="rounded-xl border border-red-200 bg-white px-4 py-3 text-sm text-red-800">
            {error}
          </p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {filtered.map((s) => (
              <SelectionCard
                key={s.code}
                selected={selected === s.code}
                title={s.name}
                subtitle={s.location || s.code}
                onClick={() => setSelected(s.code)}
              />
            ))}
          </div>
        )}

        <div className="mt-auto flex items-center justify-between gap-4 pt-10 pb-4">
          <Link
            href="/"
            className="label-caps text-ink-muted hover:text-forest"
          >
            ← Home
          </Link>
          <PrimaryButton disabled={!selected} onClick={continueNext}>
            Continue →
          </PrimaryButton>
        </div>
      </div>
    </main>
  );
}
