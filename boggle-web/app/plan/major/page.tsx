"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { Logo } from "@/components/Logo";
import { PrimaryButton } from "@/components/PrimaryButton";
import { SearchInput } from "@/components/SearchInput";
import { SelectionCard } from "@/components/SelectionCard";
import { StepHeader } from "@/components/StepHeader";
import { fetchMajors, type Major } from "@/lib/api";
import { loadSchool, saveMajor } from "@/lib/plan-storage";

export default function MajorPage() {
  const router = useRouter();
  const [majors, setMajors] = useState<Major[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!loadSchool()) {
      router.replace("/plan/school");
      return;
    }
    fetchMajors()
      .then(setMajors)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return majors;
    return majors.filter(
      (m) =>
        m.name.toLowerCase().includes(q) || m.blurb.toLowerCase().includes(q),
    );
  }, [majors, query]);

  function showPlan() {
    const major = majors.find((m) => m.id === selected);
    if (!major) return;
    saveMajor({ id: major.id, name: major.name });
    router.push("/plan/results");
  }

  return (
    <main className="min-h-screen bg-cream">
      <div className="mx-auto flex min-h-screen max-w-3xl flex-col px-6 py-6 md:px-8">
        <nav className="mb-10 flex items-center justify-between">
          <Logo />
          <p className="text-[13px] tracking-[0.16em] text-ink-faint">02 — 02</p>
        </nav>

        <StepHeader
          step={2}
          title="What might you study?"
          subtitle="Choose from 15 academic paths. You can change it later — nothing here is binding."
        />

        <SearchInput
          value={query}
          onChange={setQuery}
          placeholder="Search majors or interests..."
          className="mb-6"
        />

        {loading ? (
          <p className="text-ink-muted">Loading majors…</p>
        ) : error ? (
          <p className="rounded-xl border border-red-200 bg-white px-4 py-3 text-sm text-red-800">
            {error}
          </p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {filtered.map((m) => (
              <SelectionCard
                key={m.id}
                selected={selected === m.id}
                index={String(m.index).padStart(2, "0")}
                title={m.name}
                subtitle={m.blurb}
                onClick={() => setSelected(m.id)}
              />
            ))}
          </div>
        )}

        <div className="mt-auto flex items-center justify-between gap-4 pt-10 pb-4">
          <Link
            href="/plan/school"
            className="label-caps text-ink-muted hover:text-forest"
          >
            ← College
          </Link>
          <PrimaryButton disabled={!selected} onClick={showPlan}>
            Show my plan →
          </PrimaryButton>
        </div>
      </div>
    </main>
  );
}
