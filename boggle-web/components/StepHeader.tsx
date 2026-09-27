type Props = {
  step: 1 | 2;
  title: string;
  subtitle: string;
};

export function StepHeader({ step, title, subtitle }: Props) {
  return (
    <header className="mb-8 max-w-2xl">
      <p className="label-caps text-gold">Step {step} of 2</p>
      <h1 className="mt-3 font-display text-4xl leading-tight text-ink md:text-5xl">
        {title}
      </h1>
      <p className="mt-3 text-[15px] leading-relaxed text-ink-muted">{subtitle}</p>
    </header>
  );
}
