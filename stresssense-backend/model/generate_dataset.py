"""
model/generate_dataset.py — Dataset Generation & Management
============================================================
Generate synthetic or load real stress/wellness datasets for training.

Usage:
    # Generate synthetic dataset
    python model/generate_dataset.py --type synthetic --samples 5000
    
    # Load from CSV
    python model/generate_dataset.py --type csv --file data/stress_data.csv
    
    # Generate and save to CSV
    python model/generate_dataset.py --type synthetic --samples 5000 --save data/training_data.csv
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ── Feature columns ───────────────────────────────────────────────────────────
FEATURES = [
    "sleep_hours",       # 0-12 hours
    "working_hours",     # 0-16 hours
    "work_pressure",     # 1-10 scale
    "physical_activity", # 0-10 hours per week
    "remote_work",       # 0 or 1
    "emotion_score",     # 0-100 (higher is better)
    "fatigue_score",     # 0-100 (higher is more fatigued)
    "focus_score",       # 0-100 (higher is better focus)
]

TARGET = "stress_label"  # 0=Low, 1=Moderate, 2=High


# ══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC DATA GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_synthetic_dataset(n_samples: int = 3000, seed: int = 42) -> pd.DataFrame:
    """
    Generate realistic synthetic stress/wellness data.
    
    Parameters
    ----------
    n_samples : int
        Number of samples to generate
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    pd.DataFrame with features and stress_label
    """
    np.random.seed(seed)
    
    print(f"🎲 Generating {n_samples} synthetic samples...")
    
    # ── Generate base features ────────────────────────────────────────────────
    
    # Sleep hours (normal distribution around 7h, range 3-10)
    sleep = np.clip(np.random.normal(7, 1.5, n_samples), 3, 10)
    
    # Working hours (bimodal: normal 8h workers + overworkers)
    work_normal = np.random.normal(8, 1, int(n_samples * 0.7))
    work_over = np.random.normal(11, 1.5, int(n_samples * 0.3))
    work_h = np.concatenate([work_normal, work_over])
    np.random.shuffle(work_h)
    work_h = np.clip(work_h, 4, 16)[:n_samples]
    
    # Work pressure (uniform with slight bias toward moderate)
    press = np.random.beta(2, 2, n_samples) * 9 + 1  # Beta distribution scaled to 1-10
    
    # Physical activity (exponential distribution, most people do little)
    activity = np.clip(np.random.exponential(2, n_samples), 0, 10)
    
    # Remote work (60% remote, 40% office)
    remote = np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    
    # Emotion score (influenced by sleep and pressure)
    emotion_base = 70 - (8 - sleep) * 5 - press * 2
    emotion = np.clip(emotion_base + np.random.normal(0, 10, n_samples), 10, 95)
    
    # Fatigue score (influenced by sleep and work hours)
    fatigue_base = (8 - sleep) * 8 + (work_h - 8) * 3
    fatigue = np.clip(fatigue_base + np.random.normal(0, 10, n_samples), 5, 95)
    
    # Focus score (influenced by sleep and fatigue)
    focus_base = 80 - (8 - sleep) * 5 - fatigue * 0.3
    focus = np.clip(focus_base + np.random.normal(0, 10, n_samples), 10, 95)
    
    # ── Calculate stress score ────────────────────────────────────────────────
    
    stress_raw = (
        np.maximum(0, (8 - sleep) * 6) +      # Sleep deficit
        np.maximum(0, (work_h - 8) * 4) +     # Overwork
        press * 4 +                            # Work pressure
        fatigue * 0.5 +                        # Fatigue
        - focus * 0.25 +                       # Poor focus
        - activity * 2.5 +                     # Lack of exercise
        - (emotion / 100) * 15                 # Negative emotions
    )
    
    # Add realistic noise
    stress_score = np.clip(stress_raw + np.random.normal(0, 8, n_samples), 0, 100)
    
    # ── Assign labels ──────────────────────────────────────────────────────────
    
    # 0=Low (<35), 1=Moderate (35-65), 2=High (>65)
    labels = np.where(
        stress_score < 35, 0,
        np.where(stress_score < 65, 1, 2)
    )
    
    # ── Create DataFrame ───────────────────────────────────────────────────────
    
    df = pd.DataFrame({
        "sleep_hours":       sleep,
        "working_hours":     work_h,
        "work_pressure":     press,
        "physical_activity": activity,
        "remote_work":       remote.astype(float),
        "emotion_score":     emotion,
        "fatigue_score":     fatigue,
        "focus_score":       focus,
        "stress_score":      stress_score,  # For reference
        "stress_label":      labels,
    })
    
    print(f"✅ Generated {len(df)} samples")
    print(f"\n📊 Label Distribution:")
    print(df['stress_label'].value_counts().sort_index())
    print(f"\n📈 Stress Score Stats:")
    print(df['stress_score'].describe())
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
# REALISTIC SCENARIO GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_realistic_scenarios(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate realistic user scenarios with temporal patterns.
    Simulates different user profiles over time.
    """
    np.random.seed(42)
    
    print(f"👥 Generating {n_samples} realistic user scenarios...")
    
    scenarios = []
    
    # Define user profiles
    profiles = {
        "healthy": {
            "sleep": (7, 8.5, 0.5),
            "work": (7, 9, 1),
            "pressure": (2, 5, 1),
            "activity": (3, 7, 2),
            "remote": 0.7,
        },
        "stressed": {
            "sleep": (5, 6.5, 0.8),
            "work": (9, 12, 1.5),
            "pressure": (6, 9, 1),
            "activity": (0, 2, 1),
            "remote": 0.5,
        },
        "burnout": {
            "sleep": (4, 5.5, 0.5),
            "work": (10, 14, 1),
            "pressure": (8, 10, 0.5),
            "activity": (0, 1, 0.5),
            "remote": 0.4,
        },
        "balanced": {
            "sleep": (7, 8, 0.5),
            "work": (7, 9, 1),
            "pressure": (3, 6, 1.5),
            "activity": (2, 5, 1.5),
            "remote": 0.6,
        },
    }
    
    # Generate samples for each profile
    samples_per_profile = n_samples // len(profiles)
    
    for profile_name, params in profiles.items():
        for _ in range(samples_per_profile):
            sleep = np.clip(np.random.normal(
                (params["sleep"][0] + params["sleep"][1]) / 2,
                params["sleep"][2]
            ), params["sleep"][0], params["sleep"][1])
            
            work = np.clip(np.random.normal(
                (params["work"][0] + params["work"][1]) / 2,
                params["work"][2]
            ), params["work"][0], params["work"][1])
            
            pressure = np.clip(np.random.normal(
                (params["pressure"][0] + params["pressure"][1]) / 2,
                params["pressure"][2]
            ), params["pressure"][0], params["pressure"][1])
            
            activity = np.clip(np.random.normal(
                (params["activity"][0] + params["activity"][1]) / 2,
                params["activity"][2]
            ), params["activity"][0], params["activity"][1])
            
            remote = 1 if np.random.random() < params["remote"] else 0
            
            # Calculate derived features
            emotion = 80 - (8 - sleep) * 6 - pressure * 3 + np.random.normal(0, 10)
            emotion = np.clip(emotion, 10, 95)
            
            fatigue = (8 - sleep) * 10 + (work - 8) * 4 + np.random.normal(0, 10)
            fatigue = np.clip(fatigue, 5, 95)
            
            focus = 85 - (8 - sleep) * 6 - fatigue * 0.4 + np.random.normal(0, 10)
            focus = np.clip(focus, 10, 95)
            
            # Calculate stress
            stress = (
                max(0, (8 - sleep) * 6) +
                max(0, (work - 8) * 4) +
                pressure * 4 +
                fatigue * 0.5 -
                focus * 0.25 -
                activity * 2.5 -
                (emotion / 100) * 15
            )
            stress = np.clip(stress + np.random.normal(0, 8), 0, 100)
            
            label = 0 if stress < 35 else (1 if stress < 65 else 2)
            
            scenarios.append({
                "sleep_hours": sleep,
                "working_hours": work,
                "work_pressure": pressure,
                "physical_activity": activity,
                "remote_work": float(remote),
                "emotion_score": emotion,
                "fatigue_score": fatigue,
                "focus_score": focus,
                "stress_score": stress,
                "stress_label": label,
                "profile": profile_name,
            })
    
    df = pd.DataFrame(scenarios)
    
    print(f"✅ Generated {len(df)} scenarios")
    print(f"\n📊 Profile Distribution:")
    print(df['profile'].value_counts())
    print(f"\n📊 Label Distribution:")
    print(df['stress_label'].value_counts().sort_index())
    
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CSV LOADING
# ══════════════════════════════════════════════════════════════════════════════

def load_from_csv(filepath: str) -> pd.DataFrame:
    """
    Load dataset from CSV file.
    
    Expected columns: all FEATURES + stress_label
    """
    print(f"📂 Loading dataset from {filepath}...")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Validate columns
    required_cols = FEATURES + [TARGET]
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    print(f"✅ Loaded {len(df)} samples")
    print(f"\n📊 Label Distribution:")
    print(df[TARGET].value_counts().sort_index())
    
    return df[required_cols]


# ══════════════════════════════════════════════════════════════════════════════
# SAVE TO CSV
# ══════════════════════════════════════════════════════════════════════════════

def save_to_csv(df: pd.DataFrame, filepath: str):
    """Save dataset to CSV file."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"💾 Dataset saved to {filepath}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate or load stress/wellness dataset")
    parser.add_argument(
        "--type",
        choices=["synthetic", "realistic", "csv"],
        default="synthetic",
        help="Dataset type to generate or load"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=3000,
        help="Number of samples to generate (for synthetic/realistic)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="CSV file path (for type=csv)"
    )
    parser.add_argument(
        "--save",
        type=str,
        help="Save generated dataset to CSV file"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 StressSense Dataset Generator")
    print("=" * 60)
    
    # Generate or load dataset
    if args.type == "synthetic":
        df = generate_synthetic_dataset(n_samples=args.samples, seed=args.seed)
    elif args.type == "realistic":
        df = generate_realistic_scenarios(n_samples=args.samples)
    elif args.type == "csv":
        if not args.file:
            print("❌ Error: --file required for type=csv")
            sys.exit(1)
        df = load_from_csv(args.file)
    
    # Save if requested
    if args.save:
        save_to_csv(df, args.save)
    
    print("\n✅ Dataset generation complete!")
    print(f"   Shape: {df.shape}")
    print(f"   Features: {len(FEATURES)}")
    print(f"   Samples: {len(df)}")


if __name__ == "__main__":
    main()
