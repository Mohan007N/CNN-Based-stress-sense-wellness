/**
 * Ensemble Emotion Detection
 * Combines face-api.js and CNN predictions for better accuracy
 */

export interface EmotionScores {
  neutral: number;
  happy: number;
  sad: number;
  angry: number;
  fearful: number;
  disgusted: number;
  surprised: number;
}

export interface EmotionPrediction {
  emotions: EmotionScores;
  dominantEmotion: string;
  confidence: number;
  source: 'face-api' | 'cnn' | 'ensemble';
}

export interface EnsembleConfig {
  method: 'voting' | 'weighted' | 'averaging' | 'stacking';
  weights?: {
    faceApi: number;
    cnn: number;
  };
  threshold?: number; // Minimum confidence to trust a prediction
}

/**
 * Ensemble Emotion Detector
 * Combines multiple models for better accuracy
 */
export class EnsembleEmotionDetector {
  private config: EnsembleConfig;

  constructor(config: Partial<EnsembleConfig> = {}) {
    this.config = {
      method: config.method || 'weighted',
      weights: config.weights || { faceApi: 0.6, cnn: 0.4 }, // face-api.js is more accurate
      threshold: config.threshold || 0.3,
    };
  }

  /**
   * Combine predictions from multiple models
   */
  combine(
    faceApiPrediction: EmotionPrediction | null,
    cnnPrediction: EmotionPrediction | null
  ): EmotionPrediction {
    // If only one model available, use it
    if (!faceApiPrediction && !cnnPrediction) {
      return this.getDefaultPrediction();
    }
    if (!faceApiPrediction) return cnnPrediction!;
    if (!cnnPrediction) return faceApiPrediction!;

    // Both models available - ensemble!
    switch (this.config.method) {
      case 'voting':
        return this.votingEnsemble(faceApiPrediction, cnnPrediction);
      case 'weighted':
        return this.weightedEnsemble(faceApiPrediction, cnnPrediction);
      case 'averaging':
        return this.averagingEnsemble(faceApiPrediction, cnnPrediction);
      case 'stacking':
        return this.stackingEnsemble(faceApiPrediction, cnnPrediction);
      default:
        return this.weightedEnsemble(faceApiPrediction, cnnPrediction);
    }
  }

  /**
   * Method 1: Voting Ensemble
   * Each model votes, majority wins
   */
  private votingEnsemble(
    pred1: EmotionPrediction,
    pred2: EmotionPrediction
  ): EmotionPrediction {
    // If both agree, high confidence
    if (pred1.dominantEmotion === pred2.dominantEmotion) {
      const avgConfidence = (pred1.confidence + pred2.confidence) / 2;
      return {
        emotions: this.averageEmotions(pred1.emotions, pred2.emotions),
        dominantEmotion: pred1.dominantEmotion,
        confidence: Math.min(0.95, avgConfidence * 1.2), // Boost confidence when models agree
        source: 'ensemble',
      };
    }

    // Models disagree - use the one with higher confidence
    const winner = pred1.confidence > pred2.confidence ? pred1 : pred2;
    return {
      ...winner,
      confidence: winner.confidence * 0.8, // Reduce confidence when models disagree
      source: 'ensemble',
    };
  }

  /**
   * Method 2: Weighted Ensemble
   * Models with higher accuracy get more weight
   */
  private weightedEnsemble(
    pred1: EmotionPrediction,
    pred2: EmotionPrediction
  ): EmotionPrediction {
    const w1 = this.config.weights!.faceApi;
    const w2 = this.config.weights!.cnn;

    // Weighted average of emotion scores
    const emotions: EmotionScores = {
      neutral: pred1.emotions.neutral * w1 + pred2.emotions.neutral * w2,
      happy: pred1.emotions.happy * w1 + pred2.emotions.happy * w2,
      sad: pred1.emotions.sad * w1 + pred2.emotions.sad * w2,
      angry: pred1.emotions.angry * w1 + pred2.emotions.angry * w2,
      fearful: pred1.emotions.fearful * w1 + pred2.emotions.fearful * w2,
      disgusted: pred1.emotions.disgusted * w1 + pred2.emotions.disgusted * w2,
      surprised: pred1.emotions.surprised * w1 + pred2.emotions.surprised * w2,
    };

    // Find dominant emotion
    const entries = Object.entries(emotions) as [keyof EmotionScores, number][];
    const [dominantEmotion, dominantScore] = entries.reduce((max, entry) =>
      entry[1] > max[1] ? entry : max
    );

    // Calculate confidence
    const confidence = dominantScore / 100;

    // Boost confidence if models agree
    const agreement = pred1.dominantEmotion === pred2.dominantEmotion ? 1.15 : 0.9;

    return {
      emotions,
      dominantEmotion: this.capitalizeFirst(dominantEmotion),
      confidence: Math.min(0.95, confidence * agreement),
      source: 'ensemble',
    };
  }

  /**
   * Method 3: Averaging Ensemble
   * Simple average of all predictions
   */
  private averagingEnsemble(
    pred1: EmotionPrediction,
    pred2: EmotionPrediction
  ): EmotionPrediction {
    const emotions = this.averageEmotions(pred1.emotions, pred2.emotions);
    const entries = Object.entries(emotions) as [keyof EmotionScores, number][];
    const [dominantEmotion, dominantScore] = entries.reduce((max, entry) =>
      entry[1] > max[1] ? entry : max
    );

    return {
      emotions,
      dominantEmotion: this.capitalizeFirst(dominantEmotion),
      confidence: dominantScore / 100,
      source: 'ensemble',
    };
  }

  /**
   * Method 4: Stacking Ensemble
   * Use a meta-model to combine predictions
   * (Simplified version - in production, train a real meta-model)
   */
  private stackingEnsemble(
    pred1: EmotionPrediction,
    pred2: EmotionPrediction
  ): EmotionPrediction {
    // Meta-features: combine raw predictions with agreement signals
    const agreement = pred1.dominantEmotion === pred2.dominantEmotion ? 1 : 0;
    const avgConfidence = (pred1.confidence + pred2.confidence) / 2;
    const confidenceDiff = Math.abs(pred1.confidence - pred2.confidence);

    // Simple meta-model rules (in production, use trained model)
    let finalConfidence = avgConfidence;

    if (agreement === 1) {
      // Models agree - boost confidence
      finalConfidence = Math.min(0.95, avgConfidence * 1.25);
    } else if (confidenceDiff > 0.3) {
      // One model very confident - trust it more
      finalConfidence = Math.max(pred1.confidence, pred2.confidence) * 0.9;
    } else {
      // Models disagree with similar confidence - reduce confidence
      finalConfidence = avgConfidence * 0.75;
    }

    // Use weighted average for final emotions
    return this.weightedEnsemble(pred1, pred2);
  }

  /**
   * Average emotion scores from two predictions
   */
  private averageEmotions(
    emotions1: EmotionScores,
    emotions2: EmotionScores
  ): EmotionScores {
    return {
      neutral: (emotions1.neutral + emotions2.neutral) / 2,
      happy: (emotions1.happy + emotions2.happy) / 2,
      sad: (emotions1.sad + emotions2.sad) / 2,
      angry: (emotions1.angry + emotions2.angry) / 2,
      fearful: (emotions1.fearful + emotions2.fearful) / 2,
      disgusted: (emotions1.disgusted + emotions2.disgusted) / 2,
      surprised: (emotions1.surprised + emotions2.surprised) / 2,
    };
  }

  /**
   * Get default prediction when no models available
   */
  private getDefaultPrediction(): EmotionPrediction {
    return {
      emotions: {
        neutral: 100,
        happy: 0,
        sad: 0,
        angry: 0,
        fearful: 0,
        disgusted: 0,
        surprised: 0,
      },
      dominantEmotion: 'Neutral',
      confidence: 0,
      source: 'ensemble',
    };
  }

  /**
   * Capitalize first letter
   */
  private capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Update ensemble configuration
   */
  updateConfig(config: Partial<EnsembleConfig>) {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current configuration
   */
  getConfig(): EnsembleConfig {
    return { ...this.config };
  }
}

/**
 * Analyze ensemble performance
 */
export class EnsembleAnalyzer {
  private predictions: Array<{
    faceApi: EmotionPrediction;
    cnn: EmotionPrediction;
    ensemble: EmotionPrediction;
    timestamp: number;
  }> = [];

  /**
   * Record a prediction for analysis
   */
  record(
    faceApi: EmotionPrediction,
    cnn: EmotionPrediction,
    ensemble: EmotionPrediction
  ) {
    this.predictions.push({
      faceApi,
      cnn,
      ensemble,
      timestamp: Date.now(),
    });

    // Keep only last 100 predictions
    if (this.predictions.length > 100) {
      this.predictions.shift();
    }
  }

  /**
   * Calculate agreement rate between models
   */
  getAgreementRate(): number {
    if (this.predictions.length === 0) return 0;

    const agreements = this.predictions.filter(
      (p) => p.faceApi.dominantEmotion === p.cnn.dominantEmotion
    ).length;

    return agreements / this.predictions.length;
  }

  /**
   * Get average confidence by source
   */
  getAverageConfidence(): {
    faceApi: number;
    cnn: number;
    ensemble: number;
  } {
    if (this.predictions.length === 0) {
      return { faceApi: 0, cnn: 0, ensemble: 0 };
    }

    const sum = this.predictions.reduce(
      (acc, p) => ({
        faceApi: acc.faceApi + p.faceApi.confidence,
        cnn: acc.cnn + p.cnn.confidence,
        ensemble: acc.ensemble + p.ensemble.confidence,
      }),
      { faceApi: 0, cnn: 0, ensemble: 0 }
    );

    return {
      faceApi: sum.faceApi / this.predictions.length,
      cnn: sum.cnn / this.predictions.length,
      ensemble: sum.ensemble / this.predictions.length,
    };
  }

  /**
   * Get statistics
   */
  getStats() {
    return {
      totalPredictions: this.predictions.length,
      agreementRate: this.getAgreementRate(),
      averageConfidence: this.getAverageConfidence(),
    };
  }

  /**
   * Clear recorded predictions
   */
  clear() {
    this.predictions = [];
  }
}

// Export singleton instances
export const ensembleDetector = new EnsembleEmotionDetector({
  method: 'weighted',
  weights: { faceApi: 0.6, cnn: 0.4 },
});

export const ensembleAnalyzer = new EnsembleAnalyzer();
