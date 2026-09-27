"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ApExamRow } from "@/components/ApExamRow";
import { ChatDrawer } from "@/components/ChatDrawer";
import { Logo } from "@/components/Logo";
import { PrimaryButton } from "@/components/PrimaryButton";
import { fetchRecommend, type RecommendResponse } from "@/lib/api";
import type { StudentPlanContext } from "@/lib/mock-chat";
import { loadMajor, loadSchool } from "@/lib/plan-storage";

function schoolShortName(name: string, code: string): string {
  if (name.toLowerCase().includes("georgia institute")) return "Georgia Tech";
  if (name.toLowerCase().includes("florida")) return "UF";
  if (name.toLowerCase().includes("georgia") && code === "UGA") return "UGA";
  if (name.toLowerCase().includes("texas a&m")) return "Texas A&M";
  if (name.toLowerCase().includes("rutgers")) return "Rutgers";
  if (name.toLowerCase().includes("minnesota")) return "UMN";
  return name;
}

export default function ResultsPage() {
  const router = useRouter();
  const [plan, setPlan] = useState<RecommendResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [majorName, setMajorName] = useState("Your major");
  const [majorId, setMajorId] = useState("");

  useEffect(() => {
    const school = loadSchool();
    const major = loadMajor();
    if (!school || !major) {
      router.replace("/plan/school");
      return;
    }
    setMajorName(major.name);
    setMajorId(major.id);
    fetchRecommend({ school: school.code, major: major.id })
      .then((data) => {
        setPlan(data);
        if (data.recommendations[0]) {
          setExpanded(data.recommendations[0].ap_exam);
        }
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  const shortSchool = useMemo(() => {
    if (!plan) return "";
    return schoolShortName(plan.school_name, plan.school);
  }, [plan]);

  const displaySchool = shortSchool || plan?.school_name || "";

  const planContext: StudentPlanContext | null = useMemo(() => {
    if (!plan) return null;
    return {
      schoolCode: plan.school,
      schoolName: displaySchool || plan.school_name,
      majorId: majorId || plan.major?.id || "",
      majorName: majorName,
      totalCredits: plan.total_credits,
      examCount: plan.exam_count,
      recommendations: plan.recommendations.map((r) => ({
        ap_exam: r.ap_exam,
        best_credits: r.best_credits,
        min_score: r.min_score,
        courses: r.courses,
        fit: r.fit,
      })),
    };
  }, [plan, displaySchool, majorId, majorName]);

  return (
    <main className="min-h-screen bg-cream">
      <div className="mx-auto max-w-3xl px-6 py-6 md:px-8">
        <nav className="no-print mb-10 flex flex-wrap items-center justify-between gap-3">
          <Logo />
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => window.print()}
              className="label-caps text-ink-muted hover:text-forest"
            >
              Print / PDF
            </button>
            <Link href="/plan/school">
              <PrimaryButton variant="ghost" className="!px-5 !py-2.5">
                Edit choices
              </PrimaryButton>
            </Link>
          </div>
        </nav>

        {loading ? (
          <p className="text-ink-muted">Building your AP plan…</p>
        ) : error ? (
          <p className="rounded-xl border border-red-200 bg-white px-4 py-3 text-sm text-red-800">
            {error}
          </p>
        ) : plan ? (
          <>
            <header className="mb-8">
              <p className="label-caps text-gold">Your AP plan</p>
              <h1 className="mt-3 font-display text-4xl leading-tight text-ink md:text-5xl">
                {majorName} at {displaySchool}
              </h1>
              <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-ink-muted">
                {plan.exam_count} AP exams worth taking — roughly{" "}
                <strong className="font-semibold text-ink">
                  {Math.round(plan.total_credits)} credit hours
                </strong>
                , ranked by published credit from the official chart. Fit badges
                reflect your major context.
              </p>
            </header>

            <section>
              {plan.recommendations.map((rec, i) => (
                <ApExamRow
                  key={rec.ap_exam}
                  rank={i + 1}
                  rec={rec}
                  expanded={expanded === rec.ap_exam}
                  onToggle={() =>
                    setExpanded((cur) =>
                      cur === rec.ap_exam ? null : rec.ap_exam,
                    )
                  }
                  schoolShort={displaySchool}
                />
              ))}
            </section>

            <footer className="mt-12 border-t border-forest/10 pb-28 pt-8">
              <p className="max-w-2xl text-[14px] leading-relaxed text-ink-muted">
                Boggle reads published AP credit charts. Policies change year to
                year and by program, so confirm on the official source before you
                register.
              </p>
              {plan.source_url ? (
                <a
                  href={plan.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-4 inline-flex label-caps text-forest hover:underline"
                >
                  View {displaySchool} source ↗
                </a>
              ) : null}
            </footer>
          </>
        ) : null}
      </div>

      {plan && planContext ? (
        <>
          <button
            type="button"
            onClick={() => setChatOpen(true)}
            className="no-print fixed bottom-5 right-4 z-30 inline-flex max-w-[calc(100vw-2rem)] items-center gap-2 rounded-full bg-forest px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.14em] text-cream-soft shadow-lg hover:bg-forest-mid sm:bottom-6 sm:right-6 sm:px-5 sm:text-[12px]"
          >
            <span aria-hidden>✦</span>
            Ask about my plan
          </button>
          <ChatDrawer
            open={chatOpen}
            onClose={() => setChatOpen(false)}
            planContext={planContext}
          />
        </>
      ) : null}
    </main>
  );
}
