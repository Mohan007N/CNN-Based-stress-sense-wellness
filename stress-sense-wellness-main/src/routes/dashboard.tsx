import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState, useRef } from "react";
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
  Camera,
  HeartPulse,
  Maximize2,
  Minimize2,
  Moon,
  RefreshCw,
  Sparkles,
  Video,
  VideoOff,
} from "lucide-react";
import { getAccessToken } from "@/lib/api";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — StressSense" },
      { name: "description", content: "Real-time wellness analytics dashboard with stress trends, mood, and emotion detection." },
    ],
  }),
  component: DashboardPage,
});

const PRIMARY = "oklch(0.62 0.14 250)";
const NAVY = "oklch(0.28 0.06 256)";
const SOFT = "oklch(0.86 0.06 250)";

interface RealtimeStats {
  current_stress_level: string;
  current_stress_score: number;
  dominant_emotion: string;
  total_checks_today: number;
  avg_stress_today: number;
  avg_stress_week: number;
  stress_trend: string;
  stress_change_percent: number;
  last_updated: string;
}

function StatCard({
  icon: Icon,
  label,
  value,
  delta,
  positive,
  hint,
  loading,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
  delta: string;
  positive: boolean;
  hint: string;
  loading?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-soft)]">
      <div className="flex items-center justify-between">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-soft text-primary">
          <Icon className="h-4.5 w-4.5" />
        </div>
        {!loading && (
          <span
            className={`inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium ${
              positive ? "bg-success/15 text-success" : "bg-destructive/10 text-destructive"
            }`}
          >
            {positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {delta}
          </span>
        )}
      </div>
      <div className="mt-4 text-sm text-muted-foreground">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight text-navy">
        {loading ? (
          <div className="h-8 w-20 animate-pulse rounded bg-muted"></div>
        ) : (
          value
        )}
      </div>
      <div className="mt-1 text-xs text-muted-foreground">{hint}</div>
    </div>
  );
}

function CameraPanel() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState("neutral");
  const containerRef = useRef<HTMLDivElement>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsActive(true);
        toast.success("Camera activated");
      }
    } catch (error) {
      console.error("Camera error:", error);
      toast.error("Failed to access camera");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsActive(false);
      toast.info("Camera stopped");
    }
  };

  const toggleFullscreen = async () => {
    if (!containerRef.current) return;

    try {
      if (!isFullscreen) {
        await containerRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (error) {
      console.error("Fullscreen error:", error);
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      stopCamera();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={`rounded-2xl border border-border bg-card shadow-[var(--shadow-soft)] ${
        isFullscreen ? "fixed inset-0 z-50 rounded-none" : "p-6"
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Camera className="h-4 w-4 text-primary" />
          <h3 className="text-base font-semibold text-foreground">Live Emotion Detection</h3>
        </div>
        <div className="flex items-center gap-2">
          {isActive && (
            <button
              onClick={toggleFullscreen}
              className="rounded-lg p-2 hover:bg-muted transition-colors"
              title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
            >
              {isFullscreen ? (
                <Minimize2 className="h-4 w-4" />
              ) : (
                <Maximize2 className="h-4 w-4" />
              )}
            </button>
          )}
          <button
            onClick={isActive ? stopCamera : startCamera}
            className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? "bg-destructive/10 text-destructive hover:bg-destructive/20"
                : "bg-primary text-primary-foreground hover:opacity-90"
            }`}
          >
            {isActive ? (
              <>
                <VideoOff className="mr-1.5 inline h-4 w-4" />
                Stop
              </>
            ) : (
              <>
                <Video className="mr-1.5 inline h-4 w-4" />
                Start
              </>
            )}
          </button>
        </div>
      </div>

      <div className={`mt-4 relative ${isFullscreen ? "h-[calc(100vh-120px)]" : "h-80"} bg-muted rounded-xl overflow-hidden`}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />
        {!isActive && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-muted-foreground">
            <Camera className="h-12 w-12 mb-3" />
            <p className="text-sm">Click "Start" to begin emotion detection</p>
          </div>
        )}
        {isActive && (
          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between">
            <div className="rounded-lg bg-black/70 backdrop-blur-sm px-4 py-2 text-white">
              <div className="text-xs opacity-75">Current Emotion</div>
              <div className="text-lg font-semibold capitalize">{currentEmotion}</div>
            </div>
            <div className="rounded-lg bg-black/70 backdrop-blur-sm px-3 py-2">
              <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DashboardPage() {
  const [realtimeStats, setRealtimeStats] = useState<RealtimeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchRealtimeStats = async () => {
    try {
      const token = getAccessToken();
      if (!token) {
        toast.error("Please login to view dashboard");
        return;
      }

      const response = await fetch("http://localhost:5000/api/dashboard/realtime-stats", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();
      if (data.success && data.realtime) {
        setRealtimeStats(data.realtime);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error("Failed to fetch realtime stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRealtimeStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchRealtimeStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const stressTrend = [
    { d: "Mon", stress: 42, wellness: 78 },
    { d: "Tue", stress: 48, wellness: 74 },
    { d: "Wed", stress: 55, wellness: 70 },
    { d: "Thu", stress: 51, wellness: 72 },
    { d: "Fri", stress: 38, wellness: 81 },
    { d: "Sat", stress: 28, wellness: 88 },
    { d: "Sun", stress: 24, wellness: 90 },
  ];

  const recommendations = [
    { icon: Moon, title: "Aim for 7+ hours of sleep", desc: "Better sleep improves stress resilience by 40%." },
    { icon: Sparkles, title: "Take a 5-minute break", desc: "Short breaks improve focus and reduce stress." },
    { icon: HeartPulse, title: "Light exercise", desc: "A 20-minute walk can lower stress by ~12%." },
  ];

  const getStressColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "low":
        return "text-success";
      case "moderate":
        return "text-warning";
      case "high":
        return "text-destructive";
      default:
        return "text-muted-foreground";
    }
  };

  return (
    <div className="bg-muted/30 min-h-screen">
      <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-semibold text-primary">Real-time Overview</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-navy">Wellness Dashboard</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Live stress monitoring and wellness analytics
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchRealtimeStats}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-sm hover:bg-muted transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
            <div className="text-xs text-muted-foreground">
              Updated: {lastUpdate.toLocaleTimeString()}
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={Activity}
            label="Current Stress"
            value={realtimeStats ? realtimeStats.current_stress_level : "Loading..."}
            delta={realtimeStats ? `${Math.abs(realtimeStats.stress_change_percent)}%` : "0%"}
            positive={realtimeStats ? realtimeStats.stress_trend === "decreasing" : false}
            hint={realtimeStats ? `Score: ${realtimeStats.current_stress_score}` : "Loading..."}
            loading={loading}
          />
          <StatCard
            icon={Brain}
            label="Dominant Emotion"
            value={realtimeStats ? realtimeStats.dominant_emotion : "Unknown"}
            delta={realtimeStats ? `${realtimeStats.total_checks_today} checks` : "0"}
            positive={true}
            hint="Today's primary emotion"
            loading={loading}
          />
          <StatCard
            icon={HeartPulse}
            label="Today's Average"
            value={realtimeStats ? `${realtimeStats.avg_stress_today}` : "0"}
            delta={realtimeStats ? `vs ${realtimeStats.avg_stress_week} weekly` : "0"}
            positive={realtimeStats ? realtimeStats.avg_stress_today < realtimeStats.avg_stress_week : false}
            hint="Stress score average"
            loading={loading}
          />
          <StatCard
            icon={Moon}
            label="Wellness Trend"
            value={realtimeStats ? realtimeStats.stress_trend : "Stable"}
            delta={realtimeStats ? `${realtimeStats.total_checks_today} today` : "0"}
            positive={realtimeStats ? realtimeStats.stress_trend !== "increasing" : true}
            hint="Based on recent data"
            loading={loading}
          />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <CameraPanel />
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
            <div className="flex items-center gap-2">
              <BellRing className="h-4 w-4 text-primary" />
              <h3 className="text-base font-semibold text-foreground">AI Recommendations</h3>
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

        <div className="mt-6 rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-foreground">Weekly Stress & Wellness Trend</h3>
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

        <div className="mt-6 rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)]">
          <h3 className="text-base font-semibold text-foreground">Quick Actions</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <Link
              to="/analysis"
              className="rounded-xl border border-border bg-background p-4 hover:bg-muted transition-colors"
            >
              <Camera className="h-5 w-5 text-primary mb-2" />
              <div className="text-sm font-medium text-foreground">Start Analysis</div>
              <div className="text-xs text-muted-foreground">Run emotion detection</div>
            </Link>
            <button className="rounded-xl border border-border bg-background p-4 hover:bg-muted transition-colors text-left">
              <HeartPulse className="h-5 w-5 text-primary mb-2" />
              <div className="text-sm font-medium text-foreground">Log Wellness</div>
              <div className="text-xs text-muted-foreground">Manual entry</div>
            </button>
            <button className="rounded-xl border border-border bg-background p-4 hover:bg-muted transition-colors text-left">
              <Brain className="h-5 w-5 text-primary mb-2" />
              <div className="text-sm font-medium text-foreground">View Reports</div>
              <div className="text-xs text-muted-foreground">Detailed analytics</div>
            </button>
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>
            Developed by{" "}
            <a
              href="https://www.linkedin.com/in/mohanakrishnan-n-576565312/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Mohana Krishnan
            </a>{" "}
            | StressSense v1.0.0
          </p>
          <p className="mt-1">
            Contact: hello@stresssense.app | +1 (555) 010-2025 | 410 Market St, San Francisco, CA
          </p>
        </div>
      </div>
    </div>
  );
}
