import { createFileRoute } from "@tanstack/react-router";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BellRing,
  Brain,
  HeartPulse,
  Moon,
  Sparkles,
} from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — StressSense" },
      { name: "description", content: "Wellness analytics dashboard with stress trends, mood, sleep, and burnout risk." },
    ],
  }),
  component: DashboardPage,
});

const stressTrend = [
  { d: "Mon", stress: 42, wellness: 78 },
  { d: "Tue", stress: 48, wellness: 74 },
  { d: "Wed", stress: 55, wellness: 70 },
  { d: "Thu", stress: 51, wellness: 72 },
  { d: "Fri", stress: 38, wellness: 81 },
  { d: "Sat", stress: 28, wellness: 88 },
  { d: "Sun", stress: 24, wellness: 90 },
];

const moodData = [
  { d: "Mon", v: 6 },
  { d: "Tue", v: 5 },
  { d: "Wed", v: 4 },
  { d: "Thu", v: 6 },
  { d: "Fri", v: 8 },
  { d: "Sat", v: 9 },
  { d: "Sun", v: 9 },
];

const sleepData = [
  { d: "Mon", h: 6.2 },
  { d: "Tue", h: 5.8 },
  { d: "Wed", h: 5.4 },
  { d: "Thu", h: 6.5 },
  { d: "Fri", h: 7.1 },
  { d: "Sat", h: 8.0 },
  { d: "Sun", h: 8.2 },
];

const PRIMARY = "oklch(0.62 0.14 250)";
const NAVY = "oklch(0.28 0.06 256)";
const SOFT = "oklch(0.86 0.06 250)";

function StatCard({
  icon: Icon,
  label,
  value,
  delta,
  positive,
  hint,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
  delta: string;
  positive: boolean;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-soft)]">
      <div className="flex items-center justify-between">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary">
          <Icon className="h-4.5 w-4.5" />
        </div>
        <span
          className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${
            positive ? "bg-success/15 text-success" : "bg-destructive/10 text-destructive"
          }`}
        >
          {positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
          {delta}
        </span>
      </div>
      <div className="mt-4 text-sm text-muted-foreground">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight text-navy">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{hint}</div>
    </div>
  );
}

function DashboardPage() {
  const recommendations = [
    { icon: Moon, title: "Aim for 7+ hours of sleep", desc: "Your sleep dropped midweek. Try a wind-down routine tonight." },
    { icon: Sparkles, title: "Take a 5-minute break", desc: "Two hours of focus detected. A short walk will reset attention." },
    { icon: HeartPulse, title: "Light exercise", desc: "A 20-minute walk can lower your stress score by ~12%." },
  ];

  return (
    <div className="bg-muted/30">
      <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-semibold text-primary">Overview</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-navy">Wellness Dashboard</h1>
            <p className="mt-1 text-sm text-muted-foreground">Your weekly stress, mood, and recovery analytics.</p>
          </div>
          <div className="inline-flex rounded-lg border border-border bg-background p-1 text-sm">
            {["Week", "Month", "Quarter"].map((p, i) => (
              <button
                key={p}
                className={`rounded-md px-3 py-1.5 transition-colors ${
                  i === 0 ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard icon={Activity} label="Stress score" value="38" delta="12%" positive hint="Lower is better" />
          <StatCard icon={HeartPulse} label="Wellness score" value="81" delta="6%" positive hint="Out of 100" />
          <StatCard icon={Brain} label="Burnout risk" value="Low" delta="2%" positive hint="Stable trend" />
          <StatCard icon={Moon} label="Avg sleep" value="6.7h" delta="3%" positive={false} hint="Goal: 7.5h" />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] lg:col-span-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-foreground">Weekly stress &amp; wellness</h3>
                <p className="text-xs text-muted-foreground">Composite analysis of behavior and emotion signals</p>
              </div>
            </div>
            <div className="mt-6 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stressTrend} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
                  <defs>
                    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={PRIMARY} stopOpacity={0.35} />
                      <stop offset="100%" stopColor={PRIMARY} stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={NAVY} stopOpacity={0.25} />
                      <stop offset="100%" stopColor={NAVY} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.93 0.01 250)" vertical={false} />
                  <XAxis dataKey="d" stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} />
                  <YAxis stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid oklch(0.93 0.01 250)", boxShadow: "var(--shadow-soft)" }} />
                  <Area type="monotone" dataKey="wellness" stroke={NAVY} strokeWidth={2} fill="url(#g2)" />
                  <Area type="monotone" dataKey="stress" stroke={PRIMARY} strokeWidth={2} fill="url(#g1)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
            <div className="flex items-center gap-2">
              <BellRing className="h-4 w-4 text-primary" />
              <h3 className="text-base font-semibold text-foreground">Recommendations</h3>
            </div>
            <ul className="mt-4 space-y-3">
              {recommendations.map((r) => (
                <li key={r.title} className="flex gap-3 rounded-xl border border-border bg-background p-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary-soft text-primary">
                    <r.icon className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-foreground">{r.title}</div>
                    <div className="text-xs text-muted-foreground">{r.desc}</div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
            <h3 className="text-base font-semibold text-foreground">Mood trend</h3>
            <p className="text-xs text-muted-foreground">Self-reported on a 1–10 scale</p>
            <div className="mt-6 h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={moodData} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.93 0.01 250)" vertical={false} />
                  <XAxis dataKey="d" stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} />
                  <YAxis stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} domain={[0, 10]} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid oklch(0.93 0.01 250)" }} />
                  <Line type="monotone" dataKey="v" stroke={PRIMARY} strokeWidth={2.5} dot={{ r: 3, fill: PRIMARY }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
            <h3 className="text-base font-semibold text-foreground">Sleep tracking</h3>
            <p className="text-xs text-muted-foreground">Hours per night</p>
            <div className="mt-6 h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sleepData} margin={{ left: -20, right: 8, top: 8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.93 0.01 250)" vertical={false} />
                  <XAxis dataKey="d" stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} />
                  <YAxis stroke="oklch(0.5 0.02 256)" tickLine={false} axisLine={false} fontSize={12} />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid oklch(0.93 0.01 250)" }} />
                  <Bar dataKey="h" fill={SOFT} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
          <h3 className="text-base font-semibold text-foreground">Productivity insights</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {[
              { t: "Focus time", v: "4h 12m", h: "Daily average" },
              { t: "Meeting load", v: "32%", h: "Of working hours" },
              { t: "Deep work blocks", v: "5", h: "This week" },
            ].map((x) => (
              <div key={x.t} className="rounded-xl border border-border bg-background p-4">
                <div className="text-sm text-muted-foreground">{x.t}</div>
                <div className="mt-1 text-xl font-semibold text-navy">{x.v}</div>
                <div className="text-xs text-muted-foreground">{x.h}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
