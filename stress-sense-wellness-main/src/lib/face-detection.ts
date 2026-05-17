/**
 * Face Detection & Emotion Recognition Service
 * Uses face-api.js with TensorFlow.js for real-time facial analysis
 */

import * as faceapi from 'face-api.js';

export interface EmotionScores {
  neutral: number;
  happy: number;
  sad: number;
  angry: number;
  fearful: number;
  disgusted: number;
  surprised: number;
}

export interface FaceDetectionResult {
  detected: boolean;
  emotions: EmotionScores;
  dominantEmotion: string;
  emotionScore: number; // 0-100, higher is better
  stressLevel: 'Low' | 'Moderate' | 'High';
  confidence: number;
}

class FaceDetectionService {
  private modelsLoaded = false;
  private modelPath = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';

  /**
   * Load face-api.js models (only once)
   */
  async loadModels(): Promise<void> {
    if (this.modelsLoaded) return;

    try {
      console.log('Loading face detection models...');
      
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(this.modelPath),
        faceapi.nets.faceExpressionNet.loadFromUri(this.modelPath),
        faceapi.nets.faceLandmark68Net.loadFromUri(this.modelPath),
      ]);

      this.modelsLoaded = true;
      console.log('✅ Face detection models loaded successfully');
    } catch (error) {
      console.error('Failed to load face detection models:', error);
      throw new Error('Failed to initialize face detection. Please refresh the page.');
    }
  }

  /**
   * Detect face and analyze emotions from video element
   */
  async detectFace(videoElement: HTMLVideoElement): Promise<FaceDetectionResult | null> {
    if (!this.modelsLoaded) {
      await this.loadModels();
    }

    try {
      // Detect face with expressions
      const detection = await faceapi
        .detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks()
        .withFaceExpressions();

      if (!detection) {
        return null;
      }

      const expressions = detection.expressions;
      
      // Convert to our format (0-100 scale)
      const emotions: EmotionScores = {
        neutral: expressions.neutral * 100,
        happy: expressions.happy * 100,
        sad: expressions.sad * 100,
        angry: expressions.angry * 100,
        fearful: expressions.fearful * 100,
        disgusted: expressions.disgusted * 100,
        surprised: expressions.surprised * 100,
      };

      // Find dominant emotion
      const dominantEmotion = this.getDominantEmotion(emotions);
      
      // Calculate emotion score (0-100, higher is better)
      const emotionScore = this.calculateEmotionScore(emotions);
      
      // Determine stress level
      const stressLevel = this.calculateStressLevel(emotions, emotionScore);
      
      // Calculate confidence based on detection score
      const confidence = detection.detection.score;

      return {
        detected: true,
        emotions,
        dominantEmotion,
        emotionScore,
        stressLevel,
        confidence,
      };
    } catch (error) {
      console.error('Face detection error:', error);
      return null;
    }
  }

  /**
   * Get the dominant emotion from scores
   */
  private getDominantEmotion(emotions: EmotionScores): string {
    const entries = Object.entries(emotions);
    const [emotion] = entries.reduce((max, entry) => 
      entry[1] > max[1] ? entry : max
    );
    
    // Capitalize first letter
    return emotion.charAt(0).toUpperCase() + emotion.slice(1);
  }

  /**
   * Calculate overall emotion score (0-100, higher is better)
   * Positive emotions increase score, negative emotions decrease it
   */
  private calculateEmotionScore(emotions: EmotionScores): number {
    const positiveWeight = 
      emotions.happy * 1.0 + 
      emotions.surprised * 0.5 + 
      emotions.neutral * 0.3;
    
    const negativeWeight = 
      emotions.sad * 0.7 + 
      emotions.angry * 0.9 + 
      emotions.fearful * 0.8 + 
      emotions.disgusted * 0.6;
    
    // Calculate score (0-100)
    const rawScore = positiveWeight - negativeWeight;
    const normalizedScore = Math.max(0, Math.min(100, 50 + rawScore / 2));
    
    return Math.round(normalizedScore);
  }

  /**
   * Calculate stress level based on emotions
   */
  private calculateStressLevel(emotions: EmotionScores, emotionScore: number): 'Low' | 'Moderate' | 'High' {
    // High stress indicators
    const stressIndicators = 
      emotions.angry * 1.0 + 
      emotions.fearful * 0.9 + 
      emotions.sad * 0.7 + 
      emotions.disgusted * 0.5;
    
    // Calm indicators
    const calmIndicators = 
      emotions.happy * 1.0 + 
      emotions.neutral * 0.6;
    
    const stressScore = stressIndicators - calmIndicators;
    
    if (stressScore > 30 || emotionScore < 40) {
      return 'High';
    } else if (stressScore > 10 || emotionScore < 60) {
      return 'Moderate';
    } else {
      return 'Low';
    }
  }

  /**
   * Get emotion color for UI display
   */
  getEmotionColor(emotion: string): string {
    const colors: Record<string, string> = {
      Happy: 'text-success',
      Neutral: 'text-muted-foreground',
      Sad: 'text-warning',
      Angry: 'text-destructive',
      Fearful: 'text-warning',
      Disgusted: 'text-warning',
      Surprised: 'text-primary',
    };
    return colors[emotion] || 'text-foreground';
  }

  /**
   * Get stress level color for UI display
   */
  getStressColor(level: string): string {
    const colors: Record<string, string> = {
      Low: 'text-success',
      Moderate: 'text-warning',
      High: 'text-destructive',
    };
    return colors[level] || 'text-foreground';
  }

  /**
   * Check if models are loaded
   */
  isReady(): boolean {
    return this.modelsLoaded;
  }
}

// Export singleton instance
export const faceDetectionService = new FaceDetectionService();
