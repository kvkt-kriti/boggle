type Props = {
  selected: boolean;
  title: string;
  subtitle: string;
  index?: string;
  onClick: () => void;
};

export function SelectionCard({
  selected,
  title,
  subtitle,
  index,
  onClick,
}: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-2xl border px-5 py-5 text-left transition ${
        selected
          ? "border-forest bg-forest text-cream-soft shadow-soft"
          : "border-forest/10 bg-white text-ink hover:border-forest/25"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          {index ? (
            <p
              className={`mb-2 text-xs tracking-[0.12em] ${
                selected ? "text-cream-soft/60" : "text-ink-faint"
              }`}
            >
              {index}
            </p>
          ) : null}
          <p className="text-[16px] font-semibold leading-snug">{title}</p>
          <p
            className={`mt-1 text-[13px] leading-snug ${
              selected ? "text-cream-soft/75" : "text-ink-muted"
            }`}
          >
            {subtitle}
          </p>
        </div>
        {selected ? (
          <span
            aria-hidden
            className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-cream-soft text-sm text-forest"
          >
            ✓
          </span>
        ) : null}
      </div>
    </button>
  );
}
