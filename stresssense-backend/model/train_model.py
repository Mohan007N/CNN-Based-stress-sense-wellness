"""
model/train_model.py — ML Model Training Script
================================================
Run this script ONCE to generate stress_model.pkl and scaler.pkl.
These files are loaded by services/ml_service.py at runtime.

Usage:
    python model/train_model.py

Output:
    model/stress_model.pkl
    model/scaler.pkl
"""

import os
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

# ── Resolve model output directory ───────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(SCRIPT_DIR, "stress_model.pkl")
SCALER_PATH = os.path.join(SCRIPT_DIR, "scaler.pkl")

# Feature columns — must match FEATURE_COLUMNS in services/ml_service.py
FEATURES = [
    "sleep_hours",
    "working_hours",
    "work_pressure",
    "physical_activity",
    "remote_work",
    "emotion_score",
    "fatigue_score",
    "focus_score",
]

# ── Synthetic dataset generation ──────────────────────────────────────────────
def generate_dataset(n_samples: int = 2000) -> pd.DataFrame:
    """
    Generate a realistic synthetic training dataset.

    Stress label mapping:
        0 → Low  (stress_score < 35)
        1 → Moderate (35 ≤ stress_score < 65)
        2 → High (stress_score ≥ 65)
    """
    np.random.seed(42)

    sleep    = np.random.uniform(3, 10, n_samples)
    work_h   = np.random.uniform(4, 14, n_samples)
    press    = np.random.uniform(1, 10, n_samples)
    activity = np.random.uniform(0, 10, n_samples)
    remote   = np.random.randint(0, 2, n_samples).astype(float)
    emotion  = np.random.uniform(10, 95, n_samples)
    fatigue  = np.random.uniform(5, 95, n_samples)
    focus    = np.random.uniform(10, 95, n_samples)

    # Composite stress score (heuristic)
    stress_raw = (
        np.maximum(0, (8 - sleep) * 5)
        + np.maximum(0, (work_h - 8) * 3)
        + press * 3
        + fatigue * 0.4
        - focus * 0.2
        - activity * 2
        - (emotion / 100) * 10
    )
    stress_score = np.clip(stress_raw, 0, 100)

    # Add noise
    stress_score += np.random.normal(0, 5, n_samples)
    stress_score = np.clip(stress_score, 0, 100)

    # Labels
    labels = np.where(stress_score < 35, 0, np.where(stress_score < 65, 1, 2))

    df = pd.DataFrame({
        "sleep_hours":       sleep,
        "working_hours":     work_h,
        "work_pressure":     press,
        "physical_activity": activity,
        "remote_work":       remote,
        "emotion_score":     emotion,
        "fatigue_score":     fatigue,
        "focus_score":       focus,
        "stress_label":      labels,
    })

    return df


# ── Training pipeline ─────────────────────────────────────────────────────────
def train():
    print("🤖 StressSense — ML Model Training")
    print("=" * 45)

    # 1. Generate data
    print("📊 Generating synthetic training data...")
    df = generate_dataset(n_samples=3000)
    print(f"   Dataset shape: {df.shape}")
    print(f"   Label distribution:\n{df['stress_label'].value_counts().to_string()}")

    X = df[FEATURES].values
    y = df["stress_label"].values

    # 2. Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Scale features
    print("\n⚙️  Fitting StandardScaler...")
    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    # 4. Train RandomForest
    print("🌲 Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # 5. Evaluate
    y_pred   = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✅ Accuracy: {accuracy * 100:.2f}%")
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Low", "Moderate", "High"]))

    # 6. Save artefacts
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"💾 Model saved  → {MODEL_PATH}")

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print(f"💾 Scaler saved → {SCALER_PATH}")

    print("\n🚀 Training complete! The backend will auto-load these files on startup.")


if __name__ == "__main__":
    train()
