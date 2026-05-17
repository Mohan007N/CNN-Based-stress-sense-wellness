import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { useState } from "react";
import { Activity, Menu, X } from "lucide-react";

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/features", label: "Features" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/analysis", label: "Analysis" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
] as const;

export function SiteLayout() {
  const [open, setOpen] = useState(false);
  const { location } = useRouterState();
  const isAuthRoute = location.pathname === "/login" || location.pathname === "/register";

  if (isAuthRoute) return <Outlet />;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-background/90 backdrop-blur-md shadow-sm">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link to="/" className="flex items-center gap-2 group">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy text-navy-foreground shadow-sm group-hover:shadow-md transition-all">
              <Activity className="h-4 w-4" />
            </span>
            <span className="text-base font-semibold tracking-tight text-navy">StressSense</span>
          </Link>

          <nav className="hidden items-center gap-1 md:flex">
            {navLinks.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                activeOptions={{ exact: l.to === "/" }}
                className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-all hover:text-foreground hover:bg-muted data-[status=active]:text-foreground data-[status=active]:bg-primary-soft"
              >
                {l.label}
              </Link>
            ))}
          </nav>

          <div className="hidden items-center gap-2 md:flex">
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-all"
            >
              Sign in
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-navy px-4 py-2 text-sm font-semibold text-navy-foreground shadow-sm transition-all hover:opacity-90 hover:shadow-md"
            >
              Get started →
            </Link>
          </div>

          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border hover:bg-muted transition-all md:hidden"
            aria-label="Toggle menu"
          >
            {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>

        {open && (
          <div className="border-t border-border bg-background md:hidden animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="mx-auto flex w-full max-w-7xl flex-col gap-1 px-4 py-4">
              {navLinks.map((l) => (
                <Link
                  key={l.to}
                  to={l.to}
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-all"
                >
                  {l.label}
                </Link>
              ))}
              <div className="mt-3 flex gap-2">
                <Link to="/login" onClick={() => setOpen(false)} className="flex-1 rounded-lg border border-border px-3 py-2.5 text-center text-sm font-medium hover:bg-muted transition-all">Login</Link>
                <Link to="/register" onClick={() => setOpen(false)} className="flex-1 rounded-lg bg-primary px-3 py-2.5 text-center text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90 transition-all">Get started</Link>
              </div>
            </div>
          </div>
        )}
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-border bg-muted/30">
        <div className="mx-auto grid w-full max-w-7xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-4 lg:px-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
                <Activity className="h-4 w-4" />
              </span>
              <span className="text-base font-semibold text-navy">StressSense</span>
            </div>
            <p className="mt-3 max-w-sm text-sm leading-relaxed text-muted-foreground">
              Workplace wellness and stress monitoring built for modern IT teams. Privacy-first, evidence-based, designed to scale.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Product</h4>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li><Link to="/features" className="hover:text-foreground transition-colors">Features</Link></li>
              <li><Link to="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link></li>
              <li><Link to="/analysis" className="hover:text-foreground transition-colors">Analysis</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Company</h4>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li><Link to="/about" className="hover:text-foreground transition-colors">About</Link></li>
              <li><Link to="/contact" className="hover:text-foreground transition-colors">Contact</Link></li>
              <li><Link to="/login" className="hover:text-foreground transition-colors">Login</Link></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-border">
          <div className="mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-2 px-4 py-5 text-xs text-muted-foreground sm:flex-row sm:px-6 lg:px-8">
            <p>© {new Date().getFullYear()} StressSense, Inc. All rights reserved.</p>
            <p className="flex items-center gap-1">
              <span className="h-1 w-1 rounded-full bg-success" />
              Designed for healthier workplaces
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
