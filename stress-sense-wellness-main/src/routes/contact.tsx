import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Mail, MapPin, Phone } from "lucide-react";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — StressSense" },
      { name: "description", content: "Talk to our team about workplace wellness, demos, or partnerships." },
    ],
  }),
  component: ContactPage,
});

function ContactPage() {
  const [sent, setSent] = useState(false);

  return (
    <div className="bg-background">
      <section className="mx-auto w-full max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="text-sm font-semibold text-primary">Contact</p>
            <h1 className="mt-2 text-4xl font-semibold tracking-tight text-navy sm:text-5xl">Let's talk wellness</h1>
            <p className="mt-4 text-muted-foreground">Tell us about your team. We'll get back to you within one business day.</p>

            <ul className="mt-8 space-y-4 text-sm">
              <li className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary"><Mail className="h-4 w-4" /></span> hello@stresssense.app</li>
              <li className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary"><Phone className="h-4 w-4" /></span> +1 (555) 010-2025</li>
              <li className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary"><MapPin className="h-4 w-4" /></span> 410 Market St, San Francisco, CA</li>
            </ul>
          </div>

          <form
            onSubmit={(e) => { e.preventDefault(); setSent(true); }}
            className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] sm:p-8"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="First name" />
              <Field label="Last name" />
            </div>
            <div className="mt-4"><Field label="Work email" type="email" /></div>
            <div className="mt-4"><Field label="Company" /></div>
            <div className="mt-4">
              <label className="text-sm font-medium text-foreground">How can we help?</label>
              <textarea
                rows={4}
                className="mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Tell us about your team and goals…"
              />
            </div>
            <button className="mt-6 inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90">
              {sent ? "Thanks — we'll be in touch!" : "Send message"}
            </button>
          </form>
        </div>
      </section>
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
