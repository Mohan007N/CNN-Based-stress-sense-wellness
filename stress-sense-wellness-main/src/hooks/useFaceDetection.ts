import { useEffect, useRef, useState } from 'react';
import * as faceapi from 'face-api.js';

export interface EmotionScores {
  happy: number;
  sad: number;
  angry: number;
  neutral: number;
  fear: number;
  disgust: number;
  surprise: number;
}

export interface FaceDetectionResult {
  emotions: EmotionScores;
  dominantEmotion: string;
  emotionScore: number;
  confidence: number;
}

export function useFaceDetection(videoRef: React.RefObject<HTMLVideoElement>, isActive: boolean) {
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [result, setResult] = useState<FaceDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const detectionIntervalRef = useRef<number | null>(null);

  // Load face-api.js models
  useEffect(() => {
    const loadModels = async () => {
      try {
        const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model';
        
        await Promise.all([
          faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
          faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
        ]);
        
        setModelsLoaded(true);
        console.log('✅ Face detection models loaded');
      } catch (err) {
        console.error('Failed to load face detection models:', err);
        setError('Failed to load face detection models');
      }
    };

    loadModels();
  }, []);

  // Start/stop detection based on isActive
  useEffect(() => {
    if (!modelsLoaded || !videoRef.current || !isActive) {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
        detectionIntervalRef.current = null;
      }
      setDetecting(false);
      return;
    }

    const detectFace = async () => {
      const video = videoRef.current;
      if (!video || video.paused || video.ended) return;

      try {
        const detections = await faceapi
          .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
          .withFaceExpressions();

        if (detections) {
          const expressions = detections.expressions;
          
          // Convert to 0-100 scale
          const emotions: EmotionScores = {
            happy: expressions.happy * 100,
            sad: expressions.sad * 100,
            angry: expressions.angry * 100,
            neutral: expressions.neutral * 100,
            fear: expressions.fearful * 100,
            disgust: expressions.disgusted * 100,
            surprise: expressions.surprised * 100,
          };

          // Find dominant emotion
          const emotionEntries = Object.entries(emotions);
          const [dominantEmotion, dominantValue] = emotionEntries.reduce((max, curr) => 
            curr[1] > max[1] ? curr : max
          );

          // Calculate emotion score (0-100, higher is better)
          const emotionScore = 
            emotions.happy * 1.0 +
            emotions.neutral * 0.7 +
            emotions.surprise * 0.2 -
            emotions.sad * 0.5 -
            emotions.angry * 0.8 -
            emotions.fear * 0.6 -
            emotions.disgust * 0.5;

          const normalizedScore = Math.max(0, Math.min(100, (emotionScore + 100) / 2));

          setResult({
            emotions,
            dominantEmotion,
            emotionScore: normalizedScore,
            confidence: dominantValue / 100,
          });

          setDetecting(true);
          setError(null);
        } else {
          setDetecting(false);
        }
      } catch (err) {
        console.error('Face detection error:', err);
        setError('Face detection failed');
      }
    };

    // Run detection every 500ms for real-time updates
    detectionIntervalRef.current = window.setInterval(detectFace, 500);

    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, [modelsLoaded, videoRef, isActive]);

  return {
    modelsLoaded,
    detecting,
    result,
    error,
  };
}
