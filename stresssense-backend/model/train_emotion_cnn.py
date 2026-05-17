"""
model/train_emotion_cnn.py — CNN-based Facial Emotion Recognition
==================================================================
Train a custom CNN model on facial emotion datasets (FER2013, CK+, etc.)
for real-time emotion detection.

Datasets supported:
    - FER2013 (Facial Expression Recognition 2013)
    - CK+ (Extended Cohn-Kanade)
    - AffectNet
    - RAF-DB (Real-world Affective Faces Database)

Usage:
    # Download FER2013 dataset first
    python model/train_emotion_cnn.py --dataset fer2013 --epochs 50
    
    # Use custom dataset
    python model/train_emotion_cnn.py --dataset custom --data_dir data/faces --epochs 50

Output:
    model/emotion_cnn_model.h5
    model/emotion_cnn_model.json
    model/emotion_labels.json
"""

import os
import sys
import json
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# TensorFlow/Keras imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, callbacks
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.utils import to_categorical
except ImportError:
    print("❌ TensorFlow not installed. Install with: pip install tensorflow")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "emotion_cnn_model.h5")
MODEL_JSON_PATH = os.path.join(SCRIPT_DIR, "emotion_cnn_model.json")
LABELS_PATH = os.path.join(SCRIPT_DIR, "emotion_labels.json")

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

IMG_SIZE = 48  # Standard size for FER2013


# ══════════════════════════════════════════════════════════════════════════════
# DATASET LOADERS
# ══════════════════════════════════════════════════════════════════════════════

def load_fer2013(csv_path: str):
    """
    Load FER2013 dataset from CSV file.
    
    Download from: https://www.kaggle.com/datasets/msambare/fer2013
    or https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data
    
    CSV format: emotion,pixels,Usage
    """
    print(f"📂 Loading FER2013 dataset from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        print("\n📥 Download FER2013 dataset:")
        print("   1. Go to: https://www.kaggle.com/datasets/msambare/fer2013")
        print("   2. Download fer2013.csv")
        print(f"   3. Place it at: {csv_path}")
        sys.exit(1)
    
    df = pd.read_csv(csv_path)
    
    # Parse pixels
    pixels = df['pixels'].tolist()
    images = []
    
    for pixel_sequence in pixels:
        face = [int(pixel) for pixel in pixel_sequence.split(' ')]
        face = np.asarray(face).reshape(IMG_SIZE, IMG_SIZE)
        images.append(face)
    
    images = np.array(images)
    images = images.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    images = images.astype('float32') / 255.0
    
    emotions = df['emotion'].values
    
    print(f"✅ Loaded {len(images)} images")
    print(f"   Shape: {images.shape}")
    print(f"   Emotions: {np.unique(emotions)}")
    
    return images, emotions


def load_custom_dataset(data_dir: str):
    """
    Load custom dataset from directory structure:
    
    data_dir/
        angry/
            img1.jpg
            img2.jpg
        happy/
            img1.jpg
            img2.jpg
        ...
    """
    print(f"📂 Loading custom dataset from {data_dir}...")
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        sys.exit(1)
    
    from tensorflow.keras.preprocessing import image
    
    images = []
    labels = []
    
    emotion_folders = sorted(os.listdir(data_dir))
    emotion_map = {folder: idx for idx, folder in enumerate(emotion_folders)}
    
    print(f"   Found emotions: {emotion_folders}")
    
    for emotion_name, emotion_id in emotion_map.items():
        emotion_path = os.path.join(data_dir, emotion_name)
        if not os.path.isdir(emotion_path):
            continue
        
        for img_name in os.listdir(emotion_path):
            img_path = os.path.join(emotion_path, img_name)
            try:
                img = image.load_img(img_path, color_mode='grayscale', target_size=(IMG_SIZE, IMG_SIZE))
                img_array = image.img_to_array(img)
                images.append(img_array)
                labels.append(emotion_id)
            except Exception as e:
                print(f"   ⚠️  Skipping {img_path}: {e}")
    
    images = np.array(images) / 255.0
    labels = np.array(labels)
    
    print(f"✅ Loaded {len(images)} images")
    print(f"   Shape: {images.shape}")
    
    # Save emotion mapping
    reverse_map = {v: k for k, v in emotion_map.items()}
    with open(LABELS_PATH, 'w') as f:
        json.dump(reverse_map, f, indent=2)
    
    return images, labels


# ══════════════════════════════════════════════════════════════════════════════
# CNN MODEL ARCHITECTURES
# ══════════════════════════════════════════════════════════════════════════════

def build_simple_cnn(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=7):
    """
    Simple CNN architecture for emotion recognition.
    Good for quick training and testing.
    """
    model = models.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def build_advanced_cnn(input_shape=(IMG_SIZE, IMG_SIZE, 1), num_classes=7):
    """
    Advanced CNN architecture with residual connections.
    Better accuracy but slower training.
    """
    inputs = layers.Input(shape=input_shape)
    
    # Block 1
    x = layers.Conv2D(64, (3, 3), padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(64, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 2
    x = layers.Conv2D(128, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(128, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 3
    x = layers.Conv2D(256, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(256, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Block 4
    x = layers.Conv2D(512, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Conv2D(512, (3, 3), padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.25)(x)
    
    # Dense layers
    x = layers.Flatten()(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = models.Model(inputs=inputs, outputs=outputs)
    
    return model


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def train_emotion_cnn(
    X_train, y_train,
    X_val, y_val,
    model_type='simple',
    epochs=50,
    batch_size=64,
    learning_rate=0.001
):
    """
    Train CNN model for emotion recognition.
    """
    print("\n🤖 Building CNN Model...")
    print("=" * 60)
    
    num_classes = len(np.unique(y_train))
    
    # Build model
    if model_type == 'simple':
        model = build_simple_cnn(num_classes=num_classes)
    else:
        model = build_advanced_cnn(num_classes=num_classes)
    
    # Compile model
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(model.summary())
    
    # Convert labels to categorical
    y_train_cat = to_categorical(y_train, num_classes)
    y_val_cat = to_categorical(y_val, num_classes)
    
    # Data augmentation
    datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        zoom_range=0.1
    )
    datagen.fit(X_train)
    
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
        patience=10,
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
    
    # Train model
    print("\n🚀 Training CNN Model...")
    print("=" * 60)
    
    history = model.fit(
        datagen.flow(X_train, y_train_cat, batch_size=batch_size),
        validation_data=(X_val, y_val_cat),
        epochs=epochs,
        callbacks=[checkpoint, early_stop, reduce_lr],
        verbose=1
    )
    
    return model, history


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATION
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_model(model, X_test, y_test):
    """Evaluate model performance."""
    print("\n📊 Evaluating Model...")
    print("=" * 60)
    
    # Predictions
    y_pred_proba = model.predict(X_test)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Accuracy
    accuracy = np.mean(y_pred == y_test)
    print(f"\n✅ Test Accuracy: {accuracy * 100:.2f}%")
    
    # Classification report
    print("\n📈 Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=[EMOTION_LABELS[i] for i in range(len(EMOTION_LABELS))]
    ))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\n📊 Confusion Matrix:")
    print(cm)
    
    return accuracy, y_pred


def plot_training_history(history, save_path='training_history.png'):
    """Plot training history."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy
    ax1.plot(history.history['accuracy'], label='Train')
    ax1.plot(history.history['val_accuracy'], label='Validation')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Loss
    ax2.plot(history.history['loss'], label='Train')
    ax2.plot(history.history['val_loss'], label='Validation')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"📊 Training history saved to {save_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Train CNN for facial emotion recognition")
    parser.add_argument(
        '--dataset',
        choices=['fer2013', 'custom'],
        default='fer2013',
        help='Dataset to use'
    )
    parser.add_argument(
        '--data_path',
        type=str,
        default='data/fer2013.csv',
        help='Path to dataset (CSV for FER2013, directory for custom)'
    )
    parser.add_argument(
        '--model_type',
        choices=['simple', 'advanced'],
        default='simple',
        help='CNN architecture'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch_size',
        type=int,
        default=64,
        help='Batch size'
    )
    parser.add_argument(
        '--learning_rate',
        type=float,
        default=0.001,
        help='Learning rate'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 CNN Facial Emotion Recognition Training")
    print("=" * 60)
    print(f"Dataset: {args.dataset}")
    print(f"Model: {args.model_type}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print("=" * 60)
    
    # Load dataset
    if args.dataset == 'fer2013':
        X, y = load_fer2013(args.data_path)
    else:
        X, y = load_custom_dataset(args.data_path)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
    )
    
    print(f"\n📊 Data Split:")
    print(f"   Train: {len(X_train)} samples")
    print(f"   Val:   {len(X_val)} samples")
    print(f"   Test:  {len(X_test)} samples")
    
    # Train model
    model, history = train_emotion_cnn(
        X_train, y_train,
        X_val, y_val,
        model_type=args.model_type,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    # Evaluate
    accuracy, y_pred = evaluate_model(model, X_test, y_test)
    
    # Plot history
    plot_training_history(history, os.path.join(SCRIPT_DIR, 'training_history.png'))
    
    # Save model architecture
    model_json = model.to_json()
    with open(MODEL_JSON_PATH, 'w') as f:
        f.write(model_json)
    print(f"💾 Model architecture saved to {MODEL_JSON_PATH}")
    
    # Save emotion labels
    with open(LABELS_PATH, 'w') as f:
        json.dump(EMOTION_LABELS, f, indent=2)
    print(f"💾 Emotion labels saved to {LABELS_PATH}")
    
    print("\n✅ Training Complete!")
    print(f"   Model: {MODEL_PATH}")
    print(f"   Accuracy: {accuracy * 100:.2f}%")
    print("\n🚀 Use this model for real-time emotion detection!")


if __name__ == "__main__":
    main()
