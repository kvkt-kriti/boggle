type Fit = string;

export function FitBadge({ fit }: { fit: Fit }) {
  if (fit === "CORE FOR YOUR MAJOR") {
    return (
      <span className="inline-flex rounded-full bg-forest px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-cream-soft">
        Core for your major
      </span>
    );
  }
  if (fit === "NICE-TO-HAVE") {
    return (
      <span className="inline-flex rounded-full bg-gold-soft px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-ink">
        Nice-to-have
      </span>
    );
  }
  return (
    <span className="inline-flex rounded-full bg-forest-muted px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] text-forest">
      Strong match
    </span>
  );
}
