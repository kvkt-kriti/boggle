type Props = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
  className?: string;
  variant?: "primary" | "hero" | "ghost";
};

export function PrimaryButton({
  children,
  onClick,
  type = "button",
  disabled,
  className = "",
  variant = "primary",
}: Props) {
  const base =
    "inline-flex items-center justify-center rounded-full px-7 py-3 text-[13px] font-semibold uppercase tracking-[0.14em] transition disabled:cursor-not-allowed disabled:opacity-40";
  const styles =
    variant === "hero"
      ? "bg-cream-soft text-forest hover:bg-white"
      : variant === "ghost"
        ? "border border-forest/25 bg-transparent text-forest hover:bg-forest/5"
        : "bg-forest-soft text-white hover:bg-forest";

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${styles} ${className}`}
    >
      {children}
    </button>
  );
}
