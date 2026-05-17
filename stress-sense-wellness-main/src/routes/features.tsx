import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  BarChart3,
  Brain,
  Camera,
  HeartPulse,
  Lock,
  MessageCircle,
  Moon,
  ShieldCheck,
  Sparkles,
  Timer,
  Users,
} from "lucide-react";

export const Route = createFileRoute("/features")({
  head: () => ({
    meta: [
      { title: "Features — StressSense" },
      { name: "description", content: "Facial emotion recognition, behavioral analysis, team analytics, and AI wellness coaching for IT teams." },
    ],
  }),
  component: FeaturesPage,
});

const groups = [
  {
    title: "Detect",
    blurb: "Always-on, privacy-first signals",
    items: [
      { icon: Camera, title: "Facial Emotion Recognition", desc: "On-device CV detects subtle stress and fatigue signals during work sessions." },
      { icon: Brain, title: "Behavioral Analysis", desc: "Sleep, workload, and activity combined into a daily wellness baseline." },
      { icon: HeartPulse, title: "Burnout Risk Score", desc: "Composite index that flags risk well before symptoms appear." },
    ],
  },
  {
    title: "Understand",
    blurb: "Beautiful, actionable analytics",
    items: [
      { icon: BarChart3, title: "Team Analytics", desc: "Aggregated, anonymized insights for HR and engineering leaders." },
      { icon: Activity, title: "Mood Trends", desc: "Track emotional patterns over weeks and quarters." },
      { icon: Moon, title: "Sleep Tracking", desc: "Correlate rest with focus, mood, and productivity outcomes." },
    ],
  },
  {
    title: "Improve",
    blurb: "Coaching that adapts to you",
    items: [
      { icon: MessageCircle, title: "Wellness Assistant", desc: "Personal AI coach with daily nudges and break reminders." },
      { icon: Timer, title: "Smart Breaks", desc: "Micro-pauses scheduled around your meeting load and focus time." },
      { icon: Sparkles, title: "Personalized Tips", desc: "Evidence-based recommendations tailored to your patterns." },
    ],
  },
];

function FeaturesPage() {
  return (
    <div className="bg-background">
      <section className="mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-semibold text-primary">Features</p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-navy sm:text-5xl">A complete wellness platform</h1>
          <p className="mt-4 text-base text-muted-foreground sm:text-lg">From detection to coaching, StressSense gives modern teams the tools to monitor, understand, and improve workplace wellbeing.</p>
        </div>

        <div className="mt-16 space-y-16">
          {groups.map((g) => (
            <div key={g.title}>
              <div className="flex flex-col items-baseline justify-between gap-2 border-b border-border pb-4 sm:flex-row">
                <h2 className="text-2xl font-semibold tracking-tight text-navy">{g.title}</h2>
                <p className="text-sm text-muted-foreground">{g.blurb}</p>
              </div>
              <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {g.items.map((i) => (
                  <div key={i.title} className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] transition-all hover:-translate-y-0.5 hover:shadow-[var(--shadow-card)]">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-soft text-primary">
                      <i.icon className="h-5 w-5" />
                    </div>
                    <h3 className="mt-4 text-base font-semibold text-foreground">{i.title}</h3>
                    <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{i.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-20 grid gap-6 rounded-2xl border border-border bg-muted/40 p-6 sm:grid-cols-3 sm:p-10">
          <div className="flex items-start gap-3"><ShieldCheck className="mt-1 h-5 w-5 text-primary" /><div><div className="font-semibold text-foreground">HIPAA-aligned</div><p className="text-sm text-muted-foreground">Privacy-first architecture with audit logs.</p></div></div>
          <div className="flex items-start gap-3"><Lock className="mt-1 h-5 w-5 text-primary" /><div><div className="font-semibold text-foreground">Local processing</div><p className="text-sm text-muted-foreground">Camera analysis runs on-device by default.</p></div></div>
          <div className="flex items-start gap-3"><Users className="mt-1 h-5 w-5 text-primary" /><div><div className="font-semibold text-foreground">Team-friendly</div><p className="text-sm text-muted-foreground">Aggregated insights without surveillance.</p></div></div>
        </div>

        <div className="mt-12 text-center">
          <Link to="/analysis" className="inline-flex items-center rounded-md bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90">Try the analysis</Link>
        </div>
      </section>
    </div>
  );
}
