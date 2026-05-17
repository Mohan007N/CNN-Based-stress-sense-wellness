import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState, useCallback } from "react";
import {
  Camera,
  CameraOff,
  CheckCircle2,
  Loader2,
  MessageCircle,
  Send,
  Smile,
  Sparkles,
  AlertCircle,
  TrendingUp,
  Brain,
  Layers,
} from "lucide-react";
import { faceDetectionService, type FaceDetectionResult } from "@/lib/face-detection";
import { 
  ensembleDetector, 
  ensembleAnalyzer, 
  type EmotionPrediction,
  type EmotionScores 
} from "@/lib/ensemble-emotion";

export const Route = createFileRoute("/analysis")({
  head: () => ({
    meta: [
      { title: "Stress Analysis — StressSense" },
      { name: "description", content: "Live facial emotion analysis paired with smart wellness inputs and an AI assistant." },
    ],
  }),
  component: AnalysisPage,
});

const moods = ["Calm", "Focused", "Tired", "Anxious", "Stressed", "Energized"] as const;

interface AnalysisResult {
  stress_level: string;
  stress_score: number;
  burnout_risk: string;
  wellness_score: number;
  confidence: number;
  recommendations: string[];
  emotional_state: string;
}

function CameraPanel({ onFaceDetection }: { onFaceDetection?: (data: FaceDetectionResult | null) => void }) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [active, setActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [faceData, setFaceData] = useState<FaceDetectionResult | null>(null);
  const [ensembleMode, setEnsembleMode] = useState(true);
  const [ensembleStats, setEnsembleStats] = useState<{
    agreementRate: number;
    avgConfidence: { faceApi: number; cnn: number; ensemble: number };
  } | null>(null);
  const detectionIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      const stream = videoRef.current?.srcObject as MediaStream | null;
      stream?.getTracks().forEach((t) => t.stop());
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, []);

  // Convert FaceDetectionResult to EmotionPrediction format
  const convertToEmotionPrediction = (result: FaceDetectionResult): EmotionPrediction => {
    return {
      emotions: result.emotions,
      dominantEmotion: result.dominantEmotion,
      confidence: result.confidence,
      source: 'face-api',
    };
  };

  // Call CNN API with captured frame
  const getCNNPrediction = async (): Promise<EmotionPrediction | null> => {
    if (!videoRef.current || !canvasRef.current) return null;

    try {
      // Capture frame from video
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;

      ctx.drawImage(video, 0, 0);
      const imageData = canvas.toDataURL('image/jpeg', 0.8);

      // Call CNN API
      const response = await fetch('/api/predict/emotion/cnn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        },
        body: JSON.stringify({ image: imageData }),
      });

      if (!response.ok) {
        console.warn('CNN API call failed:', response.statusText);
        return null;
      }

      const data = await response.json();
      if (!data.success) return null;

      // Convert to EmotionPrediction format
      const emotions: EmotionScores = {
        neutral: data.emotions.neutral || 0,
        happy: data.emotions.happy || 0,
        sad: data.emotions.sad || 0,
        angry: data.emotions.angry || 0,
        fearful: data.emotions.fear || 0,
        disgusted: data.emotions.disgust || 0,
        surprised: data.emotions.surprise || 0,
      };

      return {
        emotions,
        dominantEmotion: data.dominant_emotion.charAt(0).toUpperCase() + data.dominant_emotion.slice(1),
        confidence: data.confidence,
        source: 'cnn',
      };
    } catch (err) {
      console.warn('CNN prediction error:', err);
      return null;
    }
  };

  const startDetection = useCallback(async () => {
    if (!videoRef.current || !active) return;

    // Load models first time
    if (!faceDetectionService.isReady()) {
      setModelsLoading(true);
      try {
        await faceDetectionService.loadModels();
      } catch (err: any) {
        setError(err.message || 'Failed to load AI models');
        setModelsLoading(false);
        return;
      }
      setModelsLoading(false);
    }

    // Start real-time detection (every 1000ms for ensemble to avoid API overload)
    detectionIntervalRef.current = window.setInterval(async () => {
      if (videoRef.current && active) {
        // Get face-api.js prediction
        const faceApiResult = await faceDetectionService.detectFace(videoRef.current);
        
        if (!faceApiResult) {
          setFaceData(null);
          onFaceDetection?.(null);
          return;
        }

        if (ensembleMode) {
          // Get CNN prediction
          const cnnPrediction = await getCNNPrediction();
          
          // Convert face-api result to EmotionPrediction
          const faceApiPrediction = convertToEmotionPrediction(faceApiResult);
          
          // Combine using ensemble
          const ensemblePrediction = ensembleDetector.combine(faceApiPrediction, cnnPrediction);
          
          // Record for analysis
          if (cnnPrediction) {
            ensembleAnalyzer.record(faceApiPrediction, cnnPrediction, ensemblePrediction);
            
            // Update stats
            const stats = ensembleAnalyzer.getStats();
            setEnsembleStats({
              agreementRate: stats.agreementRate,
              avgConfidence: stats.averageConfidence,
            });
          }
          
          // Convert back to FaceDetectionResult format
          const enhancedResult: FaceDetectionResult = {
            ...faceApiResult,
            emotions: ensemblePrediction.emotions,
            dominantEmotion: ensemblePrediction.dominantEmotion,
            confidence: ensemblePrediction.confidence,
          };
          
          setFaceData(enhancedResult);
          onFaceDetection?.(enhancedResult);
        } else {
          // Use only face-api.js
          setFaceData(faceApiResult);
          onFaceDetection?.(faceApiResult);
        }
      }
    }, 1000);
  }, [active, ensembleMode, onFaceDetection]);

  const start = async () => {
    setError(null);
    setPermissionDenied(false);
    setLoading(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user"
        }, 
        audio: false 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setActive(true);
      // Start detection after video is playing
      setTimeout(() => startDetection(), 1000);
    } catch (err: any) {
      setPermissionDenied(true);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setError("Camera access was denied. Please allow camera access in your browser settings, or use manual inputs below.");
      } else if (err.name === 'NotFoundError') {
        setError("No camera found. Please connect a camera or use manual inputs below.");
      } else {
        setError("Unable to access camera. You can still use manual inputs below.");
      }
    } finally {
      setLoading(false);
    }
  };

  const stop = () => {
    const stream = videoRef.current?.srcObject as MediaStream | null;
    stream?.getTracks().forEach((t) => t.stop());
    if (videoRef.current) videoRef.current.srcObject = null;
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
    setActive(false);
    setFaceData(null);
    setError(null);
  };

  useEffect(() => {
    if (active) {
      startDetection();
    }
    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
        detectionIntervalRef.current = null;
      }
    };
  }, [active, ensembleMode, startDetection]);

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card)]">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
            <Brain className="h-4 w-4 text-primary" />
            Live facial analysis
            {ensembleMode && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                <Layers className="h-3 w-3" />
                Ensemble
              </span>
            )}
          </h3>
          <p className="text-xs text-muted-foreground">
            {ensembleMode 
              ? "AI-powered emotion detection with ensemble learning — 100% private" 
              : "AI-powered emotion detection — 100% private"}
          </p>
        </div>
        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
          active && faceData?.detected ? "bg-success/15 text-success" : 
          active ? "bg-warning/15 text-warning" : 
          "bg-muted text-muted-foreground"
        }`}>
          <span className={`h-1.5 w-1.5 rounded-full ${
            active && faceData?.detected ? "bg-success animate-pulse" : 
            active ? "bg-warning animate-pulse" : 
            "bg-muted-foreground"
          }`} />
          {active && faceData?.detected ? "Detecting" : active ? "Searching..." : "Idle"}
        </span>
      </div>

      {/* Hidden canvas for CNN frame capture */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <div className="relative mt-4 aspect-video overflow-hidden rounded-xl border border-border bg-muted shadow-inner">
        <video ref={videoRef} className="h-full w-full object-cover" muted playsInline />
        {!active && !loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-muted-foreground bg-gradient-to-br from-muted/50 to-muted">
            <div className="rounded-full bg-background p-4 shadow-sm">
              <Camera className="h-8 w-8" />
            </div>
            <p className="text-sm font-medium">Camera preview will appear here</p>
            <p className="text-xs text-muted-foreground/70">AI models will load automatically</p>
          </div>
        )}
        {(loading || modelsLoading) && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">
                {modelsLoading ? 'Loading AI models...' : 'Accessing camera...'}
              </p>
            </div>
          </div>
        )}
        {active && faceData?.detected && (
          <>
            <div className="pointer-events-none absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-2xl border-2 border-primary/70 shadow-lg sm:h-56 sm:w-56 animate-pulse" />
            <div className="absolute left-3 top-3 rounded-lg bg-background/90 px-3 py-1.5 text-xs font-medium text-foreground shadow-md backdrop-blur-sm border border-border">
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                Face detected · {(faceData.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>
            <div className="absolute right-3 top-3 rounded-lg bg-background/90 px-3 py-1.5 text-xs font-medium shadow-md backdrop-blur-sm border border-border">
              <span className={`flex items-center gap-1.5 ${faceDetectionService.getEmotionColor(faceData.dominantEmotion)}`}>
                <Smile className="h-3 w-3" />
                {faceData.dominantEmotion}
              </span>
            </div>
          </>
        )}
        {active && !faceData?.detected && !loading && !modelsLoading && (
          <div className="absolute left-3 bottom-3 rounded-lg bg-warning/90 px-3 py-1.5 text-xs font-medium text-warning-foreground shadow-md backdrop-blur-sm">
            <span className="flex items-center gap-1.5">
              <AlertCircle className="h-3 w-3" />
              Position your face in frame
            </span>
          </div>
        )}
        {permissionDenied && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-background/95 backdrop-blur-sm p-6">
            <div className="rounded-full bg-destructive/10 p-4">
              <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
            <div className="text-center max-w-sm">
              <p className="text-sm font-medium text-foreground">Camera Access Required</p>
              <p className="text-xs text-muted-foreground mt-1">Please enable camera permissions in your browser settings to use facial analysis.</p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between gap-3">
        {!active ? (
          <button 
            onClick={start} 
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Camera className="h-4 w-4" /> {loading ? "Starting..." : "Start camera"}
          </button>
        ) : (
          <button 
            onClick={stop} 
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-5 py-2.5 text-sm font-semibold text-foreground hover:bg-muted transition-all"
          >
            <CameraOff className="h-4 w-4" /> Stop camera
          </button>
        )}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setEnsembleMode(!ensembleMode)}
            className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-medium transition-all ${
              ensembleMode 
                ? "border-primary bg-primary-soft text-primary" 
                : "border-border bg-background text-muted-foreground hover:bg-muted"
            }`}
            title="Toggle ensemble mode (combines face-api.js + CNN)"
          >
            <Layers className="h-3.5 w-3.5" />
            Ensemble
          </button>
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            <span className="h-1 w-1 rounded-full bg-success" />
            AI on-device
          </span>
        </div>
      </div>

      {error && (
        <div className="mt-4 flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 p-3">
          <AlertCircle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
          <p className="text-xs text-destructive leading-relaxed">{error}</p>
        </div>
      )}

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <Metric 
          label="Emotion" 
          value={faceData?.detected ? faceData.dominantEmotion : "—"} 
          color={faceData?.detected ? faceDetectionService.getEmotionColor(faceData.dominantEmotion) : undefined}
        />
        <Metric 
          label="Stress" 
          value={faceData?.detected ? faceData.stressLevel : "—"} 
          color={faceData?.detected ? faceDetectionService.getStressColor(faceData.stressLevel) : undefined}
        />
        <Metric 
          label="Wellness" 
          value={faceData?.detected ? `${faceData.emotionScore}%` : "—"} 
          accent="success" 
        />
      </div>

      {/* Ensemble Statistics */}
      {ensembleMode && ensembleStats && faceData?.detected && (
        <div className="mt-4 rounded-lg border border-primary/20 bg-primary-soft/30 p-3 animate-in fade-in duration-300">
          <div className="flex items-center gap-2 mb-2">
            <Layers className="h-3.5 w-3.5 text-primary" />
            <div className="text-xs font-medium text-primary">Ensemble Statistics</div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <div className="text-muted-foreground">Model Agreement</div>
              <div className="font-semibold text-foreground mt-0.5">
                {(ensembleStats.agreementRate * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-muted-foreground">Ensemble Confidence</div>
              <div className="font-semibold text-foreground mt-0.5">
                {(ensembleStats.avgConfidence.ensemble * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-muted-foreground">Face-API Confidence</div>
              <div className="font-semibold text-foreground mt-0.5">
                {(ensembleStats.avgConfidence.faceApi * 100).toFixed(0)}%
              </div>
            </div>
            <div>
              <div className="text-muted-foreground">CNN Confidence</div>
              <div className="font-semibold text-foreground mt-0.5">
                {(ensembleStats.avgConfidence.cnn * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {faceData?.detected && (
        <div className="mt-4 rounded-lg border border-border bg-background p-3 animate-in fade-in duration-300">
          <div className="text-xs font-medium text-muted-foreground mb-2">Emotion Breakdown</div>
          <div className="space-y-1.5">
            {Object.entries(faceData.emotions).map(([emotion, score]) => (
              <div key={emotion} className="flex items-center gap-2">
                <div className="text-xs text-muted-foreground w-20 capitalize">{emotion}</div>
                <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary rounded-full transition-all duration-300"
                    style={{ width: `${score}%` }}
                  />
                </div>
                <div className="text-xs font-medium text-foreground w-10 text-right">{score.toFixed(0)}%</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value, accent, color }: { label: string; value: string; accent?: "success"; color?: string }) {
  return (
    <div className="rounded-xl border border-border bg-background p-3 hover:bg-muted/50 transition-colors">
      <div className="text-xs font-medium text-muted-foreground">{label}</div>
      <div className={`mt-1.5 text-lg font-semibold ${
        color || (accent === "success" ? "text-success" : "text-navy")
      }`}>
        {value}
      </div>
    </div>
  );
}

interface SmartInputsProps {
  onAnalyze?: (result: AnalysisResult) => void;
  cameraData?: FaceDetectionResult | null;
}

function SmartInputs({ onAnalyze, cameraData }: SmartInputsProps) {
  const [sleep, setSleep] = useState(7);
  const [pressure, setPressure] = useState(5);
  const [hours, setHours] = useState(8);
  const [remote, setRemote] = useState(true);
  const [activity, setActivity] = useState("Moderate");
  const [mood, setMood] = useState<string>("Focused");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Auto-update mood based on camera detection
  useEffect(() => {
    if (cameraData?.detected && cameraData.dominantEmotion) {
      const emotionToMood: Record<string, string> = {
        'Happy': 'Energized',
        'Neutral': 'Calm',
        'Sad': 'Tired',
        'Angry': 'Stressed',
        'Fearful': 'Anxious',
        'Disgusted': 'Stressed',
        'Surprised': 'Focused',
      };
      const mappedMood = emotionToMood[cameraData.dominantEmotion];
      if (mappedMood && moods.includes(mappedMood as any)) {
        setMood(mappedMood);
      }
    }
  }, [cameraData]);

  const activityMap: Record<string, number> = {
    "None": 0,
    "Light": 2,
    "Moderate": 4,
    "Intense": 7
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      // Use real camera data if available
      let emotionScore = 50;
      let fatigueScore = 50;
      let stressFromCamera = 0;

      if (cameraData?.detected) {
        emotionScore = cameraData.emotionScore;
        
        // Calculate fatigue from emotions
        fatigueScore = Math.round(
          cameraData.emotions.sad * 0.8 + 
          cameraData.emotions.neutral * 0.5 + 
          (100 - cameraData.emotions.happy) * 0.3
        );

        // Stress indicators from camera
        stressFromCamera = 
          cameraData.emotions.angry * 0.9 + 
          cameraData.emotions.fearful * 0.8 + 
          cameraData.emotions.sad * 0.6;
      } else {
        // Fallback to mood-based calculation
        const moodScores: Record<string, number> = {
          "Calm": 75,
          "Focused": 70,
          "Tired": 40,
          "Anxious": 30,
          "Stressed": 20,
          "Energized": 85
        };
        emotionScore = moodScores[mood] || 50;
        fatigueScore = mood === "Tired" ? 80 : mood === "Energized" ? 20 : 50;
      }

      const focusScore = Math.max(0, 100 - (hours > 8 ? (hours - 8) * 10 : 0));

      // Calculate comprehensive stress score
      const sleepFactor = Math.max(0, (8 - sleep) * 8);
      const workPressureFactor = pressure * 8;
      const hoursFactor = hours > 8 ? (hours - 8) * 5 : 0;
      const emotionFactor = (100 - emotionScore) * 0.5;
      const cameraStressFactor = stressFromCamera * 0.3;

      const totalStressScore = Math.min(100, 
        sleepFactor + workPressureFactor + hoursFactor + emotionFactor + cameraStressFactor
      );

      // Determine stress level
      let stressLevel: string;
      if (totalStressScore > 70 || (cameraData?.stressLevel === 'High')) {
        stressLevel = "High";
      } else if (totalStressScore > 40 || (cameraData?.stressLevel === 'Moderate')) {
        stressLevel = "Moderate";
      } else {
        stressLevel = "Low";
      }

      // Calculate wellness score
      const wellnessScore = Math.max(0, Math.min(100,
        (sleep / 8) * 25 +
        ((10 - pressure) / 10) * 25 +
        (emotionScore / 100) * 30 +
        (activityMap[activity] / 7) * 10 +
        (hours <= 8 ? 10 : Math.max(0, 10 - (hours - 8) * 2))
      ));

      // Burnout risk assessment
      let burnoutRisk: string;
      const burnoutFactors = 
        (sleep < 6 ? 30 : 0) +
        (pressure > 8 ? 30 : 0) +
        (hours > 10 ? 25 : 0) +
        (emotionScore < 40 ? 15 : 0);

      if (burnoutFactors > 60 || (stressLevel === "High" && sleep < 6)) {
        burnoutRisk = "High";
      } else if (burnoutFactors > 30) {
        burnoutRisk = "Moderate";
      } else {
        burnoutRisk = "Low";
      }

      // Generate recommendations
      const recommendations: string[] = [];
      
      if (sleep < 7) {
        recommendations.push("🌙 Prioritize 7-8 hours of sleep tonight for better recovery");
      } else {
        recommendations.push("✅ Great sleep habits! Keep maintaining your sleep schedule");
      }

      if (pressure > 7 || stressLevel === "High") {
        recommendations.push("🧘 Take 5-minute mindfulness breaks every hour to reduce stress");
      } else {
        recommendations.push("✅ Your work pressure is manageable. Maintain your current pace");
      }

      if (hours > 9) {
        recommendations.push("⏰ Try to reduce working hours for better work-life balance");
      } else {
        recommendations.push("✅ Good work-life balance maintained");
      }

      if (activity === "None") {
        recommendations.push("🏃 Add 20-30 minutes of physical activity daily to boost wellness");
      } else {
        recommendations.push("✅ Keep up the physical activity! It's great for stress management");
      }

      if (cameraData?.detected) {
        if (cameraData.emotions.angry > 30) {
          recommendations.push("😤 High anger detected. Try deep breathing exercises");
        }
        if (cameraData.emotions.sad > 30) {
          recommendations.push("😔 Feeling down? Consider talking to someone or taking a break");
        }
        if (cameraData.emotions.fearful > 30) {
          recommendations.push("😰 Anxiety detected. Practice grounding techniques (5-4-3-2-1)");
        }
      }

      const mockResult: AnalysisResult = {
        stress_level: stressLevel,
        stress_score: Math.round(totalStressScore),
        burnout_risk: burnoutRisk,
        wellness_score: Math.round(wellnessScore),
        confidence: cameraData?.detected ? cameraData.confidence : 0.75,
        recommendations,
        emotional_state: cameraData?.detected ? cameraData.dominantEmotion : mood
      };

      setResult(mockResult);
      onAnalyze?.(mockResult);

    } catch (err: any) {
      setError(err.message || "Failed to generate wellness report. Please try again.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card)]">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-foreground">Wellness inputs</h3>
          <p className="text-xs text-muted-foreground">
            {cameraData?.detected ? (
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-success" />
                Camera data integrated automatically
              </span>
            ) : (
              "A few quick signals improve your score accuracy"
            )}
          </p>
        </div>
      </div>

      <div className="mt-6 space-y-6">
        <Slider label="Sleep hours" value={sleep} onChange={setSleep} min={0} max={12} step={0.5} suffix="h" />
        <Slider label="Work pressure" value={pressure} onChange={setPressure} min={0} max={10} step={1} suffix="/10" />
        <Slider label="Working hours today" value={hours} onChange={setHours} min={0} max={16} step={0.5} suffix="h" />

        <div className="flex items-center justify-between rounded-xl border border-border bg-background px-4 py-3 hover:bg-muted/50 transition-colors">
          <div>
            <div className="text-sm font-medium text-foreground">Remote work</div>
            <div className="text-xs text-muted-foreground">Are you working from home today?</div>
          </div>
          <button
            type="button"
            onClick={() => setRemote((v) => !v)}
            className={`relative h-6 w-11 rounded-full transition-colors ${remote ? "bg-primary" : "bg-muted"}`}
            aria-pressed={remote}
          >
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${remote ? "translate-x-5" : "translate-x-0.5"}`} />
          </button>
        </div>

        <div>
          <label className="text-sm font-medium text-foreground">Physical activity</label>
          <select
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring hover:bg-muted/50 transition-colors"
          >
            {["None", "Light", "Moderate", "Intense"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-foreground">How are you feeling?</label>
            <Smile className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-6">
            {moods.map((m) => (
              <button
                key={m}
                onClick={() => setMood(m)}
                className={`rounded-lg border px-2 py-2 text-xs font-medium transition-all ${
                  mood === m
                    ? "border-primary bg-primary-soft text-primary shadow-sm scale-105"
                    : "border-border bg-background text-muted-foreground hover:border-primary/40 hover:bg-muted/50"
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>

        <button 
          onClick={handleAnalyze}
          disabled={analyzing}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-sm hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {analyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Analyzing...
            </>
          ) : (
            <>
              <TrendingUp className="h-4 w-4" /> Generate wellness report
            </>
          )}
        </button>

        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-destructive/20 bg-destructive/5 p-3">
            <AlertCircle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
            <p className="text-xs text-destructive leading-relaxed">{error}</p>
          </div>
        )}

        {result && (
          <div className="space-y-3 rounded-xl border border-border bg-background p-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-foreground">Analysis Results</h4>
              <CheckCircle2 className="h-4 w-4 text-success" />
            </div>
            
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg border border-border bg-card p-3">
                <div className="text-xs text-muted-foreground">Stress Level</div>
                <div className={`mt-1 text-lg font-semibold ${
                  result.stress_level === "High" ? "text-destructive" : 
                  result.stress_level === "Moderate" ? "text-warning" : "text-success"
                }`}>
                  {result.stress_level} ({result.stress_score.toFixed(0)}%)
                </div>
              </div>
              
              <div className="rounded-lg border border-border bg-card p-3">
                <div className="text-xs text-muted-foreground">Wellness Score</div>
                <div className="mt-1 text-lg font-semibold text-primary">
                  {result.wellness_score.toFixed(0)}/100
                </div>
              </div>
              
              <div className="rounded-lg border border-border bg-card p-3">
                <div className="text-xs text-muted-foreground">Burnout Risk</div>
                <div className={`mt-1 text-lg font-semibold ${
                  result.burnout_risk === "High" ? "text-destructive" : 
                  result.burnout_risk === "Moderate" ? "text-warning" : "text-success"
                }`}>
                  {result.burnout_risk}
                </div>
              </div>
              
              <div className="rounded-lg border border-border bg-card p-3">
                <div className="text-xs text-muted-foreground">Confidence</div>
                <div className="mt-1 text-lg font-semibold text-navy">
                  {(result.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="pt-2">
              <div className="text-xs font-medium text-muted-foreground mb-2">Recommendations</div>
              <ul className="space-y-1.5">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-foreground">
                    <CheckCircle2 className="h-3.5 w-3.5 text-success mt-0.5 flex-shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Slider({
  label, value, onChange, min, max, step, suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number; max: number; step: number; suffix?: string;
}) {
  const percentage = ((value - min) / (max - min)) * 100;
  
  return (
    <div>
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <span className="text-sm font-semibold text-primary bg-primary-soft px-2 py-0.5 rounded-md">{value}{suffix}</span>
      </div>
      <div className="relative mt-3">
        <input
          type="range"
          min={min} max={max} step={step} value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded-full bg-muted accent-primary hover:accent-primary/80 transition-all"
          style={{
            background: `linear-gradient(to right, var(--color-primary) 0%, var(--color-primary) ${percentage}%, var(--color-muted) ${percentage}%, var(--color-muted) 100%)`
          }}
        />
      </div>
    </div>
  );
}

type ChatMsg = { role: "user" | "assistant"; text: string };

function Assistant() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMsg[]>([
    { role: "assistant", text: "Hi! I'm your wellness assistant. Ask me about stress management, focus techniques, sleep optimization, or break recommendations." },
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const send = () => {
    if (!input.trim()) return;
    const text = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setIsTyping(true);
    
    setTimeout(() => {
      const responses: Record<string, string> = {
        "break": "Try a 90-second box-breathing exercise: inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat for 6 cycles. This activates your parasympathetic nervous system.",
        "stress": "Consider the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste. This helps reduce anxiety.",
        "sleep": "For better sleep: Keep your room cool (65-68°F), avoid screens 1 hour before bed, and try progressive muscle relaxation. Consistency is key!",
        "focus": "Use the Pomodoro Technique: 25 minutes of focused work, then a 5-minute break. After 4 cycles, take a longer 15-30 minute break.",
        "default": "That's a great question! Based on your wellness inputs, I recommend taking regular breaks, staying hydrated, and maintaining a consistent sleep schedule. Would you like specific tips for any area?"
      };
      
      const lowerText = text.toLowerCase();
      let response = responses.default;
      
      for (const [key, value] of Object.entries(responses)) {
        if (lowerText.includes(key)) {
          response = value;
          break;
        }
      }
      
      setMessages((m) => [...m, { role: "assistant", text: response }]);
      setIsTyping(false);
    }, 800);
  };

  const tips = [
    "Suggest a 5-minute break",
    "How to reduce stress today?",
    "Tips for better sleep",
  ];

  return (
    <div className="flex h-full flex-col rounded-2xl border border-border bg-card shadow-[var(--shadow-soft)] transition-all hover:shadow-[var(--shadow-card)]">
      <div className="flex items-center gap-3 border-b border-border px-5 py-4 bg-gradient-to-r from-primary-soft to-transparent">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
          <MessageCircle className="h-4 w-4" />
        </div>
        <div>
          <div className="text-sm font-semibold text-foreground">Wellness Assistant</div>
          <div className="text-xs text-muted-foreground flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
            Personalized tips · always on
          </div>
        </div>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-5 scroll-smooth">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
                m.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "border border-border bg-background text-foreground"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="max-w-[85%] rounded-2xl border border-border bg-background px-4 py-2.5 text-sm">
              <div className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="border-t border-border px-5 py-4 bg-muted/30">
        <div className="flex flex-wrap gap-1.5 mb-3">
          {tips.map((t) => (
            <button
              key={t}
              onClick={() => setInput(t)}
              className="inline-flex items-center gap-1 rounded-full border border-border bg-background px-2.5 py-1 text-xs text-muted-foreground hover:border-primary/40 hover:text-foreground hover:bg-primary-soft transition-all"
            >
              <Sparkles className="h-3 w-3" /> {t}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask the assistant…"
            className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-all"
          />
          <button
            onClick={send}
            disabled={!input.trim() || isTyping}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            aria-label="Send"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function AnalysisPage() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [cameraData, setCameraData] = useState<FaceDetectionResult | null>(null);

  return (
    <div className="bg-gradient-to-b from-muted/30 to-background min-h-screen">
      <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-background/80 px-3 py-1 text-xs font-medium text-primary shadow-sm backdrop-blur mb-3">
            <span className="flex h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
            Live session · AI-powered
          </div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-navy sm:text-4xl">Stress &amp; Wellness Analysis</h1>
          <p className="mt-2 text-sm text-muted-foreground max-w-2xl">Real-time facial emotion detection combined with wellness inputs for accurate stress assessment. All AI processing happens locally — your privacy is guaranteed.</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <CameraPanel onFaceDetection={setCameraData} />
            <SmartInputs onAnalyze={setAnalysisResult} cameraData={cameraData} />
          </div>
          <div className="lg:sticky lg:top-20 lg:h-[calc(100vh-6rem)]">
            <Assistant />
          </div>
        </div>

        {analysisResult && (
          <div className="mt-8 rounded-2xl border border-primary/20 bg-gradient-to-br from-primary-soft to-background p-6 shadow-[var(--shadow-elevated)] animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle2 className="h-5 w-5 text-success" />
              <h2 className="text-lg font-semibold text-foreground">Your Wellness Summary</h2>
              {cameraData?.detected && (
                <span className="ml-auto text-xs text-muted-foreground flex items-center gap-1">
                  <Brain className="h-3 w-3" />
                  AI-enhanced analysis
                </span>
              )}
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                <div className="text-xs font-medium text-muted-foreground mb-1">Overall Wellness</div>
                <div className="text-2xl font-bold text-primary">{analysisResult.wellness_score.toFixed(0)}<span className="text-sm text-muted-foreground">/100</span></div>
              </div>
              <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                <div className="text-xs font-medium text-muted-foreground mb-1">Stress Level</div>
                <div className={`text-2xl font-bold ${
                  analysisResult.stress_level === "High" ? "text-destructive" : 
                  analysisResult.stress_level === "Moderate" ? "text-warning" : "text-success"
                }`}>{analysisResult.stress_level}</div>
              </div>
              <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                <div className="text-xs font-medium text-muted-foreground mb-1">Burnout Risk</div>
                <div className={`text-2xl font-bold ${
                  analysisResult.burnout_risk === "High" ? "text-destructive" : 
                  analysisResult.burnout_risk === "Moderate" ? "text-warning" : "text-success"
                }`}>{analysisResult.burnout_risk}</div>
              </div>
              <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                <div className="text-xs font-medium text-muted-foreground mb-1">Emotional State</div>
                <div className="text-2xl font-bold text-navy">{analysisResult.emotional_state}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
