import { createFileRoute } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";
import heroImg from "@/assets/hero-illustration.jpg";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Brain,
  Camera,
  CheckCircle2,
  HeartPulse,
  Lock,
  ShieldCheck,
  Users,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "StressSense — Smart Workplace Stress Monitoring Platform" },
      {
        name: "description",
        content:
          "Monitor employee wellness and stress levels using intelligent behavioral analysis and facial emotion recognition.",
      },
    ],
  }),
  component: Index,
});

function Hero() {
  return (
    <section className="relative overflow-hidden border-b border-border">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[520px]"
        style={{ background: "var(--gradient-hero)" }}
      />
      <div className="mx-auto w-full max-w-6xl px-4 pt-20 pb-16 text-center sm:px-6 sm:pt-24 lg:px-8">
        <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-border bg-background/80 px-3 py-1.5 text-xs font-medium text-muted-foreground shadow-sm backdrop-blur hover:bg-background transition-all">
          <span className="flex h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
          Now in private beta for engineering teams
        </div>
        <h1 className="mx-auto mt-6 max-w-3xl text-balance text-4xl font-semibold tracking-tight text-navy sm:text-5xl lg:text-[3.5rem] lg:leading-[1.05]">
          Workplace wellness, measured with precision.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-balance text-base leading-relaxed text-muted-foreground sm:text-lg">
          StressSense helps IT teams monitor stress, prevent burnout, and build healthier engineering cultures — privacy-first by design.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/analysis"
            className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-sm transition-all hover:opacity-90 hover:shadow-md"
          >
            Start free analysis <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            to="/features"
            className="inline-flex items-center justify-center rounded-lg border border-border bg-background px-5 py-3 text-sm font-semibold text-foreground transition-all hover:bg-muted hover:shadow-sm"
          >
            View product
          </Link>
        </div>
        <div className="mx-auto mt-6 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5"><ShieldCheck className="h-3.5 w-3.5" />HIPAA-aligned</span>
          <span className="text-border">·</span>
          <span className="inline-flex items-center gap-1.5"><Lock className="h-3.5 w-3.5" />On-device processing</span>
          <span className="text-border">·</span>
          <span className="inline-flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5" />SOC 2 ready</span>
        </div>

        <div className="relative mx-auto mt-14 max-w-5xl">
          <div className="overflow-hidden rounded-xl border border-border bg-card shadow-[var(--shadow-elevated)] transition-all hover:shadow-[var(--shadow-elevated)] hover:-translate-y-1 duration-300">
            <div className="flex items-center gap-1.5 border-b border-border bg-muted/40 px-4 py-2.5">
              <span className="h-2.5 w-2.5 rounded-full bg-destructive/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/60" />
              <span className="ml-3 text-xs text-muted-foreground">app.stresssense.io / dashboard</span>
            </div>
            <img
              src={heroImg}
              alt="StressSense wellness dashboard"
              width={1280}
              height={960}
              className="h-auto w-full"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function LogoCloud() {
  const logos = ["NORTHWIND", "ACME CLOUD", "LUMEN IT", "MERIDIAN", "FIRSTLIGHT", "ATLAS LABS"];
  return (
    <section className="border-b border-border bg-background">
      <div className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p className="text-center text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
          Trusted by engineering &amp; people teams at
        </p>
        <div className="mt-6 grid grid-cols-2 items-center gap-x-8 gap-y-4 sm:grid-cols-3 lg:grid-cols-6">
          {logos.map((l) => (
            <div key={l} className="text-center text-sm font-semibold tracking-[0.15em] text-muted-foreground/70 transition-colors hover:text-foreground">
              {l}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const features = [
  { icon: Camera, title: "Facial Emotion Recognition", desc: "On-device analysis detects subtle stress signals from facial expressions in real time." },
  { icon: Brain, title: "Behavioral Analysis", desc: "Combine sleep, workload, and activity signals into a clear daily wellness score." },
  { icon: BarChart3, title: "Team Analytics", desc: "Privacy-preserving aggregate insights for HR and engineering leaders." },
  { icon: HeartPulse, title: "Burnout Prevention", desc: "Proactive alerts and AI recommendations before stress becomes burnout." },
  { icon: Users, title: "Built for IT Teams", desc: "Tailored for engineers, ops, and on-call rotations with high cognitive load." },
  { icon: ShieldCheck, title: "Privacy by Design", desc: "Your data stays yours. Granular controls and full transparency, always." },
];

function Features() {
  return (
    <section className="mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-sm font-semibold text-primary">Platform</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight text-navy sm:text-4xl">Everything wellness teams need</h2>
        <p className="mt-3 text-base text-muted-foreground">A complete stack for measuring, understanding, and improving workplace wellbeing.</p>
      </div>
      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="group rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] transition-all hover:-translate-y-1 hover:shadow-[var(--shadow-card)] hover:border-primary/20">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-soft text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all shadow-sm">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="mt-4 text-base font-semibold text-foreground">{f.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Stats() {
  const stats = [
    { v: "92%", l: "users report less burnout" },
    { v: "3.4×", l: "earlier stress detection" },
    { v: "120+", l: "engineering teams" },
    { v: "99.9%", l: "uptime SLA" },
  ];
  return (
    <section className="border-y border-border bg-muted/30">
      <div className="mx-auto grid w-full max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:px-8">
        {stats.map((s) => (
          <div key={s.l}>
            <div className="text-3xl font-semibold tracking-tight text-navy">{s.v}</div>
            <div className="mt-1 text-sm text-muted-foreground">{s.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Testimonials() {
  const items = [
    { name: "Priya Mehta", role: "Engineering Manager, Acme Cloud", quote: "StressSense surfaced burnout risk in our on-call rotation weeks before we'd have noticed. Game-changing." },
    { name: "James Carter", role: "Head of People, Northwind", quote: "The cleanest wellness analytics I've seen. Our managers actually open the dashboard every Monday." },
    { name: "Aiko Tanaka", role: "CTO, Lumen IT", quote: "Privacy-first architecture made approval easy. The insights are genuinely actionable." },
  ];
  return (
    <section className="mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-semibold tracking-tight text-navy sm:text-4xl">Trusted by wellness-forward teams</h2>
        <p className="mt-3 text-muted-foreground">Hear from leaders building healthier engineering cultures.</p>
      </div>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {items.map((t) => (
          <figure key={t.name} className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
            <blockquote className="text-sm leading-relaxed text-foreground">"{t.quote}"</blockquote>
            <figcaption className="mt-4 flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-soft text-sm font-semibold text-primary">{t.name.charAt(0)}</div>
              <div>
                <div className="text-sm font-semibold text-foreground">{t.name}</div>
                <div className="text-xs text-muted-foreground">{t.role}</div>
              </div>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="mx-auto w-full max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
      <div className="rounded-3xl border border-border bg-navy p-10 text-center text-navy-foreground shadow-[var(--shadow-elevated)] sm:p-14 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent pointer-events-none" />
        <div className="relative z-10">
          <Activity className="mx-auto h-9 w-9 opacity-90" />
          <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">Build a healthier engineering culture</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-navy-foreground/80 sm:text-base">Start your wellness baseline in under five minutes. No setup, no hardware.</p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Link to="/analysis" className="inline-flex items-center rounded-lg bg-background px-6 py-3 text-sm font-semibold text-navy hover:opacity-90 shadow-md transition-all hover:shadow-lg">Start Analysis</Link>
            <Link to="/contact" className="inline-flex items-center rounded-lg border border-white/20 px-6 py-3 text-sm font-semibold text-navy-foreground hover:bg-white/10 transition-all">Talk to sales</Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function Index() {
  return (
    <>
      <Hero />
      <LogoCloud />
      <Stats />
      <Features />
      <Testimonials />
      <CTA />
    </>
  );
}
