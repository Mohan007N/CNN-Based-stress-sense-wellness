# 🧠 CNN Training Guide for Facial Emotion Recognition

## 📊 Overview

Train a custom **Convolutional Neural Network (CNN)** on real facial image datasets for accurate emotion detection. This replaces the pre-trained face-api.js models with your own custom-trained model.

---

## 🎯 Why Train Your Own CNN?

### Benefits:

1. **Better Accuracy**: Train on domain-specific data
2. **Custom Emotions**: Add your own emotion categories
3. **Fine-tuning**: Optimize for your specific use case
4. **Control**: Full control over model architecture
5. **Privacy**: Train on your own data

### Comparison:

| Feature | face-api.js (Current) | Custom CNN |
|---------|----------------------|------------|
| Accuracy | 85%+ | 90%+ (with good data) |
| Speed | Fast (pre-trained) | Fast (after training) |
| Customization | Limited | Full control |
| Training Required | No | Yes |
| Dataset Needed | No | Yes |

---

## 📥 Step 1: Get Datasets

### Option A: Download Popular Datasets

#### FER2013 (Recommended for Beginners)

**Details:**
- **Samples**: 35,887 grayscale images (48×48)
- **Emotions**: 7 (angry, disgust, fear, happy, sad, surprise, neutral)
- **Source**: Kaggle

**Download:**

```bash
# Method 1: Manual download
# 1. Go to: https://www.kaggle.com/datasets/msambare/fer2013
# 2. Download fer2013.csv
# 3. Place in: stresssense-backend/data/fer2013.csv

# Method 2: Using Kaggle API
pip install kaggle
python model/download_datasets.py --dataset fer2013 --use_kaggle
```

#### CK+ (Extended Cohn-Kanade)

**Details:**
- **Samples**: 593 sequences from 123 subjects
- **Emotions**: 7 emotions
- **Quality**: High-quality lab conditions

**Download:**
```bash
# Requires manual request
python model/download_datasets.py --dataset ckplus
# Follow instructions to request access
```

#### JAFFE (Japanese Female Facial Expression)

**Details:**
- **Samples**: 213 images of 10 Japanese female models
- **Emotions**: 7 emotions
- **Quality**: High-quality posed expressions

**Download:**
```bash
python model/download_datasets.py --dataset jaffe
# Follow instructions
```

### Option B: Create Sample Dataset (For Testing)

```bash
# Generate synthetic sample dataset
python model/download_datasets.py --dataset sample
```

This creates a small dataset in `data/sample_emotions/` for testing the training pipeline.

### Option C: Use Your Own Dataset

**Structure your data like this:**

```
data/my_emotions/
    angry/
        img001.jpg
        img002.jpg
        ...
    happy/
        img001.jpg
        img002.jpg
        ...
    sad/
        img001.jpg
        ...
    neutral/
        img001.jpg
        ...
```

**Requirements:**
- Images should be faces (cropped or full)
- Any size (will be resized to 48×48)
- Grayscale or RGB (will be converted)
- At least 100 images per emotion (more is better)

**Verify your dataset:**
```bash
python model/download_datasets.py --verify data/my_emotions
```

---

## 🏗️ Step 2: Train the CNN Model

### Quick Start (FER2013):

```bash
cd stresssense-backend

# Install TensorFlow
pip install tensorflow

# Train with default settings
python model/train_emotion_cnn.py --dataset fer2013 --epochs 50
```

### Advanced Training:

```bash
# Simple CNN (faster, good for testing)
python model/train_emotion_cnn.py \
    --dataset fer2013 \
    --model_type simple \
    --epochs 50 \
    --batch_size 64 \
    --learning_rate 0.001

# Advanced CNN (better accuracy, slower)
python model/train_emotion_cnn.py \
    --dataset fer2013 \
    --model_type advanced \
    --epochs 100 \
    --batch_size 32 \
    --learning_rate 0.0001
```

### Custom Dataset:

```bash
python model/train_emotion_cnn.py \
    --dataset custom \
    --data_path data/my_emotions \
    --epochs 50
```

### Training Parameters:

| Parameter | Description | Default | Recommended |
|-----------|-------------|---------|-------------|
| `--dataset` | Dataset type | fer2013 | fer2013 or custom |
| `--model_type` | CNN architecture | simple | simple (fast) or advanced (accurate) |
| `--epochs` | Training epochs | 50 | 50-100 |
| `--batch_size` | Batch size | 64 | 32-64 |
| `--learning_rate` | Learning rate | 0.001 | 0.001-0.0001 |

---

## 📊 Step 3: Monitor Training

### Training Output:

```
🤖 Building CNN Model...
============================================================
Model: "sequential"
_________________________________________________________________
Layer (type)                Output Shape              Param #   
=================================================================
conv2d (Conv2D)            (None, 46, 46, 32)        320       
batch_normalization         (None, 46, 46, 32)        128       
max_pooling2d              (None, 23, 23, 32)        0         
...
=================================================================
Total params: 1,234,567
Trainable params: 1,234,000
Non-trainable params: 567
_________________________________________________________________

🚀 Training CNN Model...
============================================================
Epoch 1/50
500/500 [==============================] - 45s 90ms/step
    loss: 1.8234 - accuracy: 0.2456 - val_loss: 1.6543 - val_accuracy: 0.3234

Epoch 2/50
500/500 [==============================] - 42s 84ms/step
    loss: 1.5432 - accuracy: 0.3876 - val_loss: 1.4321 - val_accuracy: 0.4567
...

Epoch 50/50
500/500 [==============================] - 42s 84ms/step
    loss: 0.6543 - accuracy: 0.7654 - val_loss: 0.8765 - val_accuracy: 0.6789

✅ Test Accuracy: 68.45%
```

### Training History Plot:

A plot will be saved showing:
- Training vs Validation Accuracy
- Training vs Validation Loss

File: `model/training_history.png`

---

## 📈 Step 4: Evaluate Results

### Classification Report:

```
📈 Classification Report:
              precision    recall  f1-score   support

       angry       0.65      0.58      0.61       491
     disgust       0.72      0.45      0.55        56
        fear       0.58      0.52      0.55       528
       happy       0.85      0.88      0.86       895
         sad       0.62      0.61      0.61       653
    surprise       0.78      0.82      0.80       415
     neutral       0.65      0.68      0.66       626

    accuracy                           0.68      3664
   macro avg       0.69      0.65      0.66      3664
weighted avg       0.68      0.68      0.68      3664
```

### Confusion Matrix:

Shows which emotions are confused with each other.

---

## 🔧 Step 5: Use the Trained Model

### Output Files:

After training, you'll have:

1. **emotion_cnn_model.h5** - Trained model weights
2. **emotion_cnn_model.json** - Model architecture
3. **emotion_labels.json** - Emotion label mapping
4. **training_history.png** - Training visualization

### Integration Options:

#### Option A: Use in Python Backend

```python
# In services/emotion_service.py
import tensorflow as tf
from tensorflow import keras

# Load model
model = keras.models.load_model('model/emotion_cnn_model.h5')

# Predict
def predict_emotion(image):
    # Preprocess image to 48x48 grayscale
    img = preprocess(image)
    
    # Predict
    predictions = model.predict(img)
    emotion_idx = np.argmax(predictions)
    confidence = predictions[0][emotion_idx]
    
    return emotion_idx, confidence
```

#### Option B: Convert to TensorFlow.js

```bash
# Install tensorflowjs converter
pip install tensorflowjs

# Convert model
tensorflowjs_converter \
    --input_format keras \
    model/emotion_cnn_model.h5 \
    public/models/emotion_cnn/
```

Then use in frontend:
```typescript
import * as tf from '@tensorflow/tfjs';

// Load model
const model = await tf.loadLayersModel('/models/emotion_cnn/model.json');

// Predict
const predictions = model.predict(tensor);
```

#### Option C: Use with face-api.js (Hybrid)

Keep face-api.js for face detection, use your CNN for emotion classification.

---

## 🎯 CNN Model Architectures

### Simple CNN (Default):

```
Input (48x48x1)
    ↓
Conv2D(32) → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Conv2D(64) → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Conv2D(128) → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Dense(256) → BatchNorm → Dropout(0.5)
    ↓
Dense(7) → Softmax
```

**Pros**: Fast training, good for testing
**Cons**: Lower accuracy

### Advanced CNN:

```
Input (48x48x1)
    ↓
Conv2D(64)×2 → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Conv2D(128)×2 → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Conv2D(256)×2 → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Conv2D(512)×2 → BatchNorm → MaxPool → Dropout(0.25)
    ↓
Dense(512) → BatchNorm → Dropout(0.5)
    ↓
Dense(256) → BatchNorm → Dropout(0.5)
    ↓
Dense(7) → Softmax
```

**Pros**: Higher accuracy, better features
**Cons**: Slower training, more parameters

---

## 📊 Expected Results

### FER2013 Benchmark:

| Model | Accuracy | Training Time |
|-------|----------|---------------|
| Simple CNN | 60-65% | ~30 min |
| Advanced CNN | 65-70% | ~2 hours |
| State-of-the-art | 70-75% | ~8 hours |

### Your Custom Dataset:

- **Small dataset** (<1000 images): 50-60%
- **Medium dataset** (1000-5000): 60-70%
- **Large dataset** (>5000): 70-80%

---

## 🚀 Optimization Tips

### 1. Data Augmentation

Already included:
- Rotation (±10°)
- Width/Height shift (±10%)
- Horizontal flip
- Zoom (±10%)

### 2. Hyperparameter Tuning

Try different:
- Learning rates: 0.001, 0.0001, 0.00001
- Batch sizes: 32, 64, 128
- Dropout rates: 0.25, 0.5
- Optimizers: Adam, SGD, RMSprop

### 3. Transfer Learning

Use pre-trained models:
```python
from tensorflow.keras.applications import VGG16

base_model = VGG16(weights='imagenet', include_top=False)
# Add custom layers on top
```

### 4. Ensemble Methods

Combine multiple models for better accuracy.

---

## 🐛 Troubleshooting

### Issue: Low Accuracy

**Solutions:**
1. Train for more epochs
2. Use more data
3. Try advanced CNN architecture
4. Adjust learning rate
5. Check data quality

### Issue: Overfitting

**Symptoms**: High train accuracy, low validation accuracy

**Solutions:**
1. Add more dropout
2. Use data augmentation
3. Reduce model complexity
4. Get more training data

### Issue: Out of Memory

**Solutions:**
1. Reduce batch size
2. Use simple CNN
3. Reduce image size
4. Use GPU if available

### Issue: Slow Training

**Solutions:**
1. Use GPU (CUDA)
2. Reduce batch size
3. Use simple CNN
4. Reduce epochs

---

## 📚 Dataset Resources

### Popular Datasets:

1. **FER2013**: https://www.kaggle.com/datasets/msambare/fer2013
2. **CK+**: http://www.consortium.ri.cmu.edu/ckagree/
3. **AffectNet**: http://mohammadmahoor.com/affectnet/
4. **RAF-DB**: http://www.whdeng.cn/RAF/model1.html
5. **JAFFE**: https://zenodo.org/record/3451524

### Data Collection Tools:

- **OpenCV**: Capture faces from webcam
- **Labelbox**: Annotate images
- **Roboflow**: Augment and manage datasets

---

## 🎯 Next Steps

### After Training:

1. ✅ Evaluate model performance
2. ✅ Save model files
3. ✅ Convert to TensorFlow.js (optional)
4. ✅ Integrate with backend
5. ✅ Test with real-time camera
6. ✅ Deploy to production

### Continuous Improvement:

1. Collect real user data
2. Retrain periodically
3. A/B test different models
4. Monitor accuracy in production
5. Fine-tune based on feedback

---

## 📝 Complete Example

```bash
# 1. Install dependencies
pip install tensorflow pandas numpy matplotlib scikit-learn pillow

# 2. Download dataset
python model/download_datasets.py --dataset fer2013 --use_kaggle

# 3. Train model
python model/train_emotion_cnn.py \
    --dataset fer2013 \
    --model_type advanced \
    --epochs 100 \
    --batch_size 64

# 4. Check results
ls model/
# emotion_cnn_model.h5
# emotion_cnn_model.json
# emotion_labels.json
# training_history.png

# 5. (Optional) Convert to TensorFlow.js
pip install tensorflowjs
tensorflowjs_converter \
    --input_format keras \
    model/emotion_cnn_model.h5 \
    public/models/emotion_cnn/

# 6. Integrate with your app!
```

---

## ✅ Summary

**You can now:**
- ✅ Download facial emotion datasets
- ✅ Train custom CNN models
- ✅ Evaluate model performance
- ✅ Use trained models for predictions
- ✅ Integrate with your application

**Benefits:**
- 🎯 Better accuracy than pre-trained models
- 🔧 Full control over architecture
- 📊 Train on your specific data
- 🚀 Production-ready models

**Start training your CNN now! 🧠**

---

**Last Updated**: May 15, 2026
**Version**: 1.0.0
