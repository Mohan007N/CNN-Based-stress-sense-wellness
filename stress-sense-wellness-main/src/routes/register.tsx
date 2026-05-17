import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, CheckCircle2 } from "lucide-react";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Create account — StressSense" },
      { name: "description", content: "Create your StressSense workspace and start measuring wellness." },
    ],
  }),
  component: RegisterPage,
});

function RegisterPage() {
  const benefits = [
    "On-device facial emotion analysis",
    "Weekly wellness analytics",
    "AI-powered recommendations",
    "Privacy-first by design",
  ];
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden bg-navy p-12 text-navy-foreground lg:flex lg:flex-col lg:justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10"><Activity className="h-4 w-4" /></span>
          <span className="text-base font-semibold">StressSense</span>
        </Link>
        <div>
          <h2 className="text-3xl font-semibold tracking-tight">Healthier teams, better software.</h2>
          <p className="mt-3 max-w-md text-sm text-navy-foreground/75">Join hundreds of engineering teams using StressSense to measure and improve workplace wellbeing.</p>
          <ul className="mt-8 space-y-3 text-sm">
            {benefits.map((b) => (
              <li key={b} className="flex items-center gap-2 text-navy-foreground/90">
                <CheckCircle2 className="h-4 w-4 text-primary" /> {b}
              </li>
            ))}
          </ul>
        </div>
        <p className="text-xs text-navy-foreground/60">© {new Date().getFullYear()} StressSense, Inc.</p>
      </div>

      <div className="flex items-center justify-center bg-background px-4 py-10">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 lg:hidden">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground"><Activity className="h-4 w-4" /></span>
            <span className="text-base font-semibold text-navy">StressSense</span>
          </Link>
          <h1 className="mt-6 text-2xl font-semibold tracking-tight text-navy lg:mt-0">Create your account</h1>
          <p className="mt-1 text-sm text-muted-foreground">Start your wellness baseline in under five minutes.</p>

          <form className="mt-6 space-y-4" onSubmit={(e) => e.preventDefault()}>
            <div className="grid grid-cols-2 gap-3">
              <Field label="First name" />
              <Field label="Last name" />
            </div>
            <Field label="Work email" type="email" />
            <Field label="Company" />
            <Field label="Password" type="password" />
            <button className="w-full rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90">Create account</button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account? <Link to="/login" className="font-medium text-primary hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({ label, type = "text" }: { label: string; type?: string }) {
  return (
    <div>
      <label className="text-sm font-medium text-foreground">{label}</label>
      <input
        type={type}
        className="mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
      />
    </div>
  );
}
