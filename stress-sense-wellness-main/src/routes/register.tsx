import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Activity, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { useState } from "react";
import { registerUser, storeAuthData } from "@/lib/api";
import { toast } from "sonner";

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
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    department: "",
    password: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const benefits = [
    "On-device facial emotion analysis",
    "Weekly wellness analytics",
    "AI-powered recommendations",
    "Privacy-first by design",
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      // Validate inputs
      if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
        setError("Please fill in all required fields");
        setIsLoading(false);
        return;
      }

      if (formData.password.length < 6) {
        setError("Password must be at least 6 characters long");
        setIsLoading(false);
        return;
      }

      // Prepare registration data
      const fullName = `${formData.firstName.trim()} ${formData.lastName.trim()}`;
      const registrationData = {
        full_name: fullName,
        email: formData.email,
        password: formData.password,
        department: formData.department || undefined,
      };

      // Call register API
      const response = await registerUser(registrationData);

      if (response.success && response.access_token && response.refresh_token && response.user) {
        // Store authentication data
        storeAuthData(response.access_token, response.refresh_token, response.user);
        
        // Show success message
        toast.success(response.message || "Account created successfully!");
        
        // Redirect to dashboard
        navigate({ to: "/dashboard" });
      } else {
        setError(response.error || "Registration failed. Please try again.");
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError("Unable to connect to server. Please check your connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden bg-navy p-12 text-navy-foreground lg:flex lg:flex-col lg:justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
            <Activity className="h-4 w-4" />
          </span>
          <span className="text-base font-semibold">StressSense</span>
        </Link>
        <div>
          <h2 className="text-3xl font-semibold tracking-tight">Healthier teams, better software.</h2>
          <p className="mt-3 max-w-md text-sm text-navy-foreground/75">
            Join hundreds of engineering teams using StressSense to measure and improve workplace wellbeing.
          </p>
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
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Activity className="h-4 w-4" />
            </span>
            <span className="text-base font-semibold text-navy">StressSense</span>
          </Link>
          <h1 className="mt-6 text-2xl font-semibold tracking-tight text-navy lg:mt-0">Create your account</h1>
          <p className="mt-1 text-sm text-muted-foreground">Start your wellness baseline in under five minutes.</p>

          {error && (
            <div className="mt-4 flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <div className="grid grid-cols-2 gap-3">
              <Field
                label="First name"
                value={formData.firstName}
                onChange={(v) => handleChange("firstName", v)}
                disabled={isLoading}
                required
              />
              <Field
                label="Last name"
                value={formData.lastName}
                onChange={(v) => handleChange("lastName", v)}
                disabled={isLoading}
                required
              />
            </div>
            <Field
              label="Work email"
              type="email"
              value={formData.email}
              onChange={(v) => handleChange("email", v)}
              disabled={isLoading}
              required
            />
            <Field
              label="Company / Department"
              value={formData.department}
              onChange={(v) => handleChange("department", v)}
              disabled={isLoading}
            />
            <Field
              label="Password"
              type="password"
              value={formData.password}
              onChange={(v) => handleChange("password", v)}
              disabled={isLoading}
              required
              placeholder="At least 6 characters"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create account"
              )}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  type = "text",
  value,
  onChange,
  disabled,
  required,
  placeholder,
}: {
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="text-sm font-medium text-foreground">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        required={required}
        placeholder={placeholder}
        className="mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
      />
    </div>
  );
}
