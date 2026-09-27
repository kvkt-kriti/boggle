import Link from "next/link";
import { Logo } from "@/components/Logo";
import { PrimaryButton } from "@/components/PrimaryButton";

export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden text-cream-soft">
      <div
        aria-hidden
        className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_#2f5a4c_0%,_#1a3a32_45%,_#0f241f_100%)]"
      />
      <div
        aria-hidden
        className="absolute inset-0 opacity-35"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.06'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        }}
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/35"
      />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-6 md:px-10">
        <nav className="flex items-center justify-between">
          <Logo tone="light" href="/" />
          <p className="label-caps text-cream-soft/70">AP Credit Advisor</p>
        </nav>

        <section className="flex flex-1 flex-col items-center justify-center py-16 text-center">
          <p className="label-caps text-gold-soft/90">For students aiming high</p>
          <h1 className="mt-4 font-display text-6xl tracking-tight text-cream-soft md:text-8xl">
            Boggle
          </h1>
          <p className="mx-auto mt-6 max-w-xl font-display text-lg leading-relaxed text-cream-soft/85 md:text-xl">
            Which AP classes are actually worth taking for the college and major
            you want? We read the official credit charts, so you don&apos;t have to.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row">
            <Link href="/plan/school">
              <PrimaryButton variant="hero">Build my AP plan →</PrimaryButton>
            </Link>
            <p className="text-[13px] text-cream-soft/65">
              Top public universities · free
            </p>
          </div>
        </section>

        <footer className="flex items-center justify-between gap-4 pb-2 text-[12px] text-cream-soft/55">
          <p>Do not sell or share my personal info</p>
          <p>Help and resources</p>
        </footer>
      </div>
    </main>
  );
}
