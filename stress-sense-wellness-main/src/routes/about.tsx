import { createFileRoute } from "@tanstack/react-router";
import { HeartPulse, ShieldCheck, Sparkles } from "lucide-react";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — StressSense" },
      { name: "description", content: "Our mission is to make workplace wellness measurable, ethical, and beautifully simple." },
    ],
  }),
  component: AboutPage,
});

function AboutPage() {
  return (
    <div className="bg-background">
      <section className="mx-auto w-full max-w-4xl px-4 py-20 sm:px-6 lg:px-8">
        <p className="text-sm font-semibold text-primary">About</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight text-navy sm:text-5xl">
          Healthier teams build better software.
        </h1>
        <p className="mt-5 text-lg leading-relaxed text-muted-foreground">
          StressSense started in 2024 with a simple belief: engineering wellness should be as measurable as engineering output. We combine modern computer vision with evidence-based behavioral science to help IT teams understand and improve their wellbeing — without surveillance.
        </p>

        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {[
            { icon: HeartPulse, t: "Empathy first", d: "We design for humans, not metrics. Every signal respects the person behind it." },
            { icon: ShieldCheck, t: "Privacy by default", d: "On-device processing and aggregated insights keep individuals safe." },
            { icon: Sparkles, t: "Evidence-based", d: "Recommendations grounded in occupational health research, not hype." },
          ].map((v) => (
            <div key={v.t} className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-soft text-primary">
                <v.icon className="h-5 w-5" />
              </div>
              <h3 className="mt-4 text-base font-semibold text-foreground">{v.t}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{v.d}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 rounded-2xl border border-border bg-muted/40 p-8">
          <h2 className="text-2xl font-semibold tracking-tight text-navy">Our mission</h2>
          <p className="mt-3 text-muted-foreground">
            To help every IT team build a culture where wellbeing and performance reinforce each other. We measure what matters, surface what helps, and protect what's personal.
          </p>
        </div>
      </section>
    </div>
  );
}
