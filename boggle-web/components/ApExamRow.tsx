"use client";

import { FitBadge } from "./FitBadge";
import type { Recommendation } from "@/lib/api";

type Props = {
  rank: number;
  rec: Recommendation;
  expanded: boolean;
  onToggle: () => void;
  schoolShort: string;
};

function awardLine(rec: Recommendation): string {
  const courses =
    rec.courses.length > 0 ? rec.courses.join(", ") : rec.award_raw || "Published award";
  return `Score ${rec.min_score}+ → ${courses}`;
}

export function ApExamRow({ rank, rec, expanded, onToggle, schoolShort }: Props) {
  const credits = rec.best_credits ?? 0;
  return (
    <article className="print-break border-b border-forest/10 py-6">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-start gap-4 text-left md:gap-6"
        aria-expanded={expanded}
      >
        <span className="w-10 shrink-0 font-display text-2xl text-gold md:w-12 md:text-3xl">
          {String(rank).padStart(2, "0")}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <h3 className="font-display text-xl text-forest md:text-2xl">
              AP {rec.ap_exam}
            </h3>
            <FitBadge fit={rec.fit} />
          </div>
          <p className="mt-1.5 text-[14px] text-ink-muted">{awardLine(rec)}</p>
        </div>
        <div className="flex shrink-0 items-center gap-2 pt-1">
          <span className="text-[12px] font-semibold uppercase tracking-[0.12em] text-ink">
            {credits} credits
          </span>
          <span
            aria-hidden
            className={`text-ink-faint transition ${expanded ? "rotate-180" : ""}`}
          >
            ▾
          </span>
        </div>
      </button>

      {expanded ? (
        <div className="mt-5 grid gap-3 pl-0 md:grid-cols-2 md:pl-16">
          <div className="rounded-xl border border-forest/10 bg-cream-soft p-5">
            <p className="label-caps text-ink-faint">CREDIT UNLOCKED</p>
            <p className="mt-3 font-display text-lg text-forest">
              {rec.courses.length ? rec.courses.join(", ") : rec.award_raw}
            </p>
            <p className="mt-3 text-[13px] text-ink-muted">
              Minimum score {rec.min_score} · {credits} credit hours
            </p>
          </div>
          <div className="rounded-xl border border-forest/10 bg-gold-soft/40 p-5">
            <p className="label-caps text-ink-faint">WHY IT&apos;S HERE</p>
            <p className="mt-3 text-[14px] leading-relaxed text-ink">{rec.why}</p>
            {rec.source_url ? (
              <a
                href={rec.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex label-caps text-gold hover:underline"
              >
                Official {schoolShort} chart ↗
              </a>
            ) : null}
          </div>
        </div>
      ) : null}
    </article>
  );
}
