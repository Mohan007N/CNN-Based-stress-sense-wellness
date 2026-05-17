"""
model/train_fer2013_improved.py — Improved CNN Training with FER2013
=====================================================================
Automatically downloads FER2013 dataset and trains CNN with optimized
hyperparameters for maximum accuracy.

Features:
    - Automatic dataset download from Kaggle
    - Optimized CNN architecture
    - Advanced data augmentation
    - Learning rate scheduling
    - Early stopping
    - Model checkpointing
    - Comprehensive evaluation

Usage:
    # With Kaggle API configured
    python model/train_fer2013_improved.py
    
    # With manual dataset
    python model/train_fer2013_improved.py --data_path data/fer2013.csv

Expected Accuracy: 65-70% on FER2013 test set
"""

import os
import sys
import json
import argparse
from datetime import datetime
import zipfile
import urllib.request

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# TensorFlow/Keras imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.utils import to_categorical
    print(f"✅ TensorFlow {tf.__version__} loaded")
except ImportError:
    print("❌ TensorFlow not installed. Install with: pip install tensorflow")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
MODEL_PATH = os.path.join(SCRIPT_DIR, "emotion_cnn_model.h5")
MODEL_JSON_PATH = os.path.join(SCRIPT_DIR, "emotion_cnn_model.json")
LABELS_PATH = os.path.join(SCRIPT_DIR, "emotion_labels.json")
HISTORY_PATH = os.path.join(SCRIPT_DIR, "training_history.png")
CONFUSION_PATH = os.path.join(SCRIPT_DIR, "confusion_matrix.png")

# Standard emotion labels (7 emotions)
EMOTION_LABELS = {
    0: "angry",
    1: "disgust",
    2: "fear",
    3: "happy",
    4: "sad",
    5: "surprise",
    6: "neutral"
}

IMG_SIZE = 48


# ══════════════════════════════════════════════════════════════════════════════
# DATASET DOWNLOAD & LOADING
# ══════════════════════════════════════════════════════════════════════════════

def download_fer2013_kaggle():
    """
    Download FER2013 dataset using Kaggle API.
    
    Setup:
        1. Install kaggle: pip install kaggle
        2. Get API token from https://www.kaggle.com/settings
        3. Place kaggle.json in ~/.kaggle/
    """
    print("📥 Downloading FER2013 from Kaggle...")
    
    try:
        import kaggle
    except ImportError:
        print("❌ Kaggle API not installed. Install with: pip install kaggle")
        return False
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        # Download dataset
        kaggle.api.dataset_download_files(
            'msambare/fer2013',
            path=DATA_DIR,
            unzip=True
        )
        print("✅ FER2013 dataset downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        print("\n📝 Manual download instructions:")
        print("   1. Go to: https://www.kaggle.com/datasets/msambare/fer2013")
        print("   2. Download fer2013.csv")
        print(f"   3. Place it in: {DATA_DIR}/fer2013.csv")
        return False


def load_fer2013(csv_path: str):
    """
    Load FER2013 dataset from CSV file.
    
    CSV format: emotion,pixels,Usage
    """
    print(f"📂 Loading FER2013 dataset from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        
        # Try to download
        if download_fer2013_kaggle():
            # Check again
            csv_path = os.path.join(DATA_DIR, 'fer2013.csv')
            if not os.path.exists(csv_path):
                print("❌ Download succeeded but file not found")
                sys.exit(1)
        else:
            sys.exit(1)
    
    df = pd.read_csv(csv_path)
    
    print(f"   Total samples: {len(df)}")
    print(f"   Columns: {df.columns.tolist()}")
    
    # Parse pixels
    pixels = df['pixels'].tolist()
    images = []
    
    print("   Parsing pixel data...")
    for i, pixel_sequence in enumerate(pixels):
        if i % 5000 == 0:
            print(f"   Progress: {i}/{len(pixels)}")
        face = [int(pixel) for pixel in pixel_sequence.split(' ')]
        face = np.asarray(face).reshape(IMG_SIZE, IMG_SIZE)
        images.append(face)
    
    images = np.array(images)
    images = images.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    images = images.astype('float32') / 255.0
    
    emotions = df['emotion'].values
    
    # Print distribution
    print(f"\n✅ Loaded {len(images)} images")
    print(f"   Shape: {images.shape}")
    print(f"   Emotion distribution:")
    for emotion_id, emotion_name in EMOTION_LABELS.items():
        count = np.sum(emotions == emotion_id)
        percentage = (count / len(emotions)) * 100
        print(f"      {emotion_name:10s}: {count:5d} ({percentage:5.2f}%)")
    
    return images, emotions


# ══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED CNN ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════

def build_optimized_cnn(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=7):
    """
    Optimized CNN architecture for FER2013.
    
    Based on research and best practices:
    - Deeper network with residual-like connections
    - Batch normalization for faster training
    - Dropout for regularization
    - Global average pooling to reduce parameters
    
    Expected accuracy: 65-70% on FER2013
    """
    inputs = layers.Input(shape=input_shape)
    
    # Block 1: Initial feature extraction
    x = layers.Conv2D(64, (3, 3), padding='same', kernel_initializer='he_normal')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(64, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 2: Deeper features
    x = layers.Conv2D(128, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(128, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 3: High-level features
    x = layers.Conv2D(256, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(256, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 4: Abstract features
    x = layers.Conv2D(512, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(512, (3, 3), padding='same', kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Global average pooling (reduces overfitting)
    x = layers.GlobalAveragePooling2D()(x)
    
    # Dense layers
    x = layers.Dense(512, kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Dropout(0.5)(x)
    
    x = layers.Dense(256, kernel_initializer='he_normal')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Dropout(0.5)(x)
    
    # Output layer
    outputs = layers.Dense(num_classes, activation='softmax', kernel_initializer='he_normal')(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name='EmotionCNN')
    
    return model


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def create_data_generators(X_train, y_train, X_val, y_val, batch_size=64):
    """
    Create data generators with augmentation.
    """
    # Training data augmentation (aggressive for better generalization)
    train_datagen = ImageDataGenerator(
        rotation_range=15,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        zoom_range=0.15,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Validation data (no augmentation)
    val_datagen = ImageDataGenerator()
    
    # Convert labels to categorical
    num_classes = len(np.unique(y_train))
    y_train_cat = to_categorical(y_train, num_classes)
    y_val_cat = to_categorical(y_val, num_classes)
    
    # Create generators
    train_generator = train_datagen.flow(
        X_train, y_train_cat,
        batch_size=batch_size,
        shuffle=True
    )
    
    val_generator = val_datagen.flow(
        X_val, y_val_cat,
        batch_size=batch_size,
        shuffle=False
    )
    
    return train_generator, val_generator, num_classes


def train_model(
    X_train, y_train,
    X_val, y_val,
    epochs=100,
    batch_size=64,
    initial_lr=0.001
):
    """
    Train CNN model with optimized hyperparameters.
    """
    print("\n🤖 Building Optimized CNN Model...")
    print("=" * 70)
    
    # Create data generators
    train_gen, val_gen, num_classes = create_data_generators(
        X_train, y_train, X_val, y_val, batch_size
    )
    
    # Build model
    model = build_optimized_cnn(num_classes=num_classes)
    
    # Compile with Adam optimizer
    model.compile(
        optimizer=optimizers.Adam(learning_rate=initial_lr),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    print(f"\n📊 Total parameters: {model.count_params():,}")
    
    # Callbacks
    checkpoint = callbacks.ModelCheckpoint(
        MODEL_PATH,
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )
    
    early_stop = callbacks.EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
    
    # Cosine annealing for learning rate
    cosine_decay = callbacks.LearningRateScheduler(
        lambda epoch: initial_lr * 0.5 * (1 + np.cos(np.pi * epoch / epochs))
    )
    
    # TensorBoard logging
    log_dir = os.path.join(SCRIPT_DIR, 'logs', datetime.now().strftime("%Y%m%d-%H%M%S"))
    tensorboard = callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
    
    # Train model
    print("\n🚀 Training CNN Model...")
    print("=" * 70)
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Initial LR: {initial_lr}")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Validation samples: {len(X_val)}")
    print("=" * 70)
    
    history = model.fit(
        train_gen,
        steps_per_epoch=len(X_train) // batch_size,
        validation_data=val_gen,
        validation_steps=len(X_val) // batch_size,
        epochs=epochs,
        callbacks=[checkpoint, early_stop, reduce_lr, tensorboard],
        verbose=1
    )
    
    return model, history


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATION & VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_model(model, X_test, y_test):
    """Comprehensive model evaluation."""
    print("\n📊 Evaluating Model...")
    print("=" * 70)
    
    # Predictions
    y_pred_proba = model.predict(X_test, verbose=1)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Overall accuracy
    accuracy = np.mean(y_pred == y_test)
    print(f"\n✅ Test Accuracy: {accuracy * 100:.2f}%")
    
    # Per-class accuracy
    print("\n📈 Per-Class Accuracy:")
    for emotion_id, emotion_name in EMOTION_LABELS.items():
        mask = y_test == emotion_id
        if np.sum(mask) > 0:
            class_acc = np.mean(y_pred[mask] == y_test[mask])
            print(f"   {emotion_name:10s}: {class_acc * 100:5.2f}%")
    
    # Classification report
    print("\n📋 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=[EMOTION_LABELS[i] for i in range(len(EMOTION_LABELS))],
        digits=4
    ))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    return accuracy, y_pred, cm


def plot_training_history(history):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy
    ax1.plot(history.history['accuracy'], label='Train', linewidth=2)
    ax1.plot(history.history['val_accuracy'], label='Validation', linewidth=2)
    ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Accuracy', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Loss
    ax2.plot(history.history['loss'], label='Train', linewidth=2)
    ax2.plot(history.history['val_loss'], label='Validation', linewidth=2)
    ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Loss', fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(HISTORY_PATH, dpi=150, bbox_inches='tight')
    print(f"📊 Training history saved to {HISTORY_PATH}")
    plt.close()


def plot_confusion_matrix(cm):
    """Plot confusion matrix."""
    plt.figure(figsize=(10, 8))
    
    # Normalize confusion matrix
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Plot
    sns.heatmap(
        cm_normalized,
        annot=True,
        fmt='.2f',
        cmap='Blues',
        xticklabels=[EMOTION_LABELS[i] for i in range(len(EMOTION_LABELS))],
        yticklabels=[EMOTION_LABELS[i] for i in range(len(EMOTION_LABELS))],
        cbar_kws={'label': 'Accuracy'},
        square=True
    )
    
    plt.title('Confusion Matrix (Normalized)', fontsize=14, fontweight='bold', pad=20)
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(CONFUSION_PATH, dpi=150, bbox_inches='tight')
    print(f"📊 Confusion matrix saved to {CONFUSION_PATH}")
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Train optimized CNN on FER2013")
    parser.add_argument(
        '--data_path',
        type=str,
        default=os.path.join(DATA_DIR, 'fer2013.csv'),
        help='Path to FER2013 CSV file'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        help='Number of training epochs (default: 100)'
    )
    parser.add_argument(
        '--batch_size',
        type=int,
        default=64,
        help='Batch size (default: 64)'
    )
    parser.add_argument(
        '--learning_rate',
        type=float,
        default=0.001,
        help='Initial learning rate (default: 0.001)'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download FER2013 from Kaggle'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧠 IMPROVED CNN TRAINING FOR EMOTION RECOGNITION")
    print("=" * 70)
    print(f"Dataset: FER2013")
    print(f"Architecture: Optimized CNN (4 blocks + GAP)")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Expected Accuracy: 65-70%")
    print("=" * 70)
    
    # Download dataset if requested
    if args.download:
        download_fer2013_kaggle()
    
    # Load dataset
    X, y = load_fer2013(args.data_path)
    
    # Split data (70% train, 15% val, 15% test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    print(f"\n📊 Data Split:")
    print(f"   Train:      {len(X_train):6d} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"   Validation: {len(X_val):6d} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"   Test:       {len(X_test):6d} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Train model
    model, history = train_model(
        X_train, y_train,
        X_val, y_val,
        epochs=args.epochs,
        batch_size=args.batch_size,
        initial_lr=args.learning_rate
    )
    
    # Evaluate
    accuracy, y_pred, cm = evaluate_model(model, X_test, y_test)
    
    # Plot results
    plot_training_history(history)
    plot_confusion_matrix(cm)
    
    # Save model artifacts
    model_json = model.to_json()
    with open(MODEL_JSON_PATH, 'w') as f:
        f.write(model_json)
    print(f"💾 Model architecture saved to {MODEL_JSON_PATH}")
    
    with open(LABELS_PATH, 'w') as f:
        json.dump(EMOTION_LABELS, f, indent=2)
    print(f"💾 Emotion labels saved to {LABELS_PATH}")
    
    # Save training summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'dataset': 'FER2013',
        'architecture': 'Optimized CNN',
        'total_samples': len(X),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'test_samples': len(X_test),
        'epochs_trained': len(history.history['accuracy']),
        'batch_size': args.batch_size,
        'initial_lr': args.learning_rate,
        'final_train_acc': float(history.history['accuracy'][-1]),
        'final_val_acc': float(history.history['val_accuracy'][-1]),
        'test_accuracy': float(accuracy),
        'model_path': MODEL_PATH,
    }
    
    summary_path = os.path.join(SCRIPT_DIR, 'training_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"💾 Training summary saved to {summary_path}")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print(f"📁 Model saved: {MODEL_PATH}")
    print(f"📊 Test Accuracy: {accuracy * 100:.2f}%")
    print(f"📈 Training history: {HISTORY_PATH}")
    print(f"📊 Confusion matrix: {CONFUSION_PATH}")
    print("\n🚀 Ready for ensemble emotion detection!")
    print("   The model will be automatically loaded by the backend.")
    print("=" * 70)


if __name__ == "__main__":
    main()
