import Link from "next/link";

type Props = {
  href?: string;
  tone?: "light" | "dark";
  className?: string;
};

export function Logo({ href = "/", tone = "dark", className = "" }: Props) {
  const color = tone === "light" ? "text-cream-soft" : "text-forest";
  const mark = (
    <span className={`inline-flex items-center gap-2 ${color} ${className}`}>
      <span
        aria-hidden
        className={`flex h-7 w-7 items-center justify-center rounded-full border ${
          tone === "light" ? "border-cream-soft/50" : "border-forest/30"
        }`}
      >
        <span
          className={`font-display text-sm leading-none ${
            tone === "light" ? "text-cream-soft" : "text-forest"
          }`}
        >
          B
        </span>
      </span>
      <span className="label-caps tracking-[0.22em]">Boggle</span>
    </span>
  );

  if (!href) return mark;
  return (
    <Link href={href} className="inline-flex no-underline" aria-label="Boggle home">
      {mark}
    </Link>
  );
}
