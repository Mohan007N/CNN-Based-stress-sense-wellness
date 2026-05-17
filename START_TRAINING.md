# Start Training - Quick Guide

## 🎯 Current Status

✅ Python 3.11.0 installed
✅ TensorFlow 2.21.0 installed
✅ Training script ready
❌ FER2013 dataset not found

---

## 📥 Option 1: Download FER2013 Dataset (Recommended)

### Method A: Kaggle API (Automatic)
```bash
# 1. Install Kaggle
pip install kaggle

# 2. Get API token
# - Go to: https://www.kaggle.com/settings
# - Click "Create New API Token"
# - Save kaggle.json to: %USERPROFILE%\.kaggle\kaggle.json

# 3. Download dataset
cd stresssense-backend
python model/train_fer2013_improved.py --download
```

### Method B: Manual Download
1. **Go to**: https://www.kaggle.com/datasets/msambare/fer2013
2. **Click**: "Download" button (requires Kaggle account)
3. **Extract**: fer2013.csv from the zip file
4. **Place**: In `stresssense-backend/data/fer2013.csv`

---

## 🚀 Option 2: Quick Test Training (No Dataset Needed)

Start with a quick test to verify everything works:

```bash
cd stresssense-backend

# Quick training with synthetic data (5 minutes)
python model/quick_train_cnn.py
```

This will:
- Generate 1,000 synthetic samples
- Train for 10 epochs (~5 minutes)
- Create `emotion_cnn_model.h5`
- Verify the pipeline works

**Note**: Accuracy will be low (~13%), but it proves the system works!

---

## 📊 Option 3: Full Training (After Dataset Download)

Once you have FER2013:

```bash
cd stresssense-backend

# Full training (2-4 hours, 65-70% accuracy)
python model/train_fer2013_improved.py

# Or quick training (30 minutes, ~60% accuracy)
python model/train_fer2013_improved.py --epochs 30
```

---

## 🎯 Recommended Approach

### Step 1: Quick Test (5 minutes)
```bash
cd stresssense-backend
python model/quick_train_cnn.py
```

### Step 2: Start Backend
```bash
python app.py
```

### Step 3: Start Frontend (New Terminal)
```bash
cd stress-sense-wellness-main
npm run dev
```

### Step 4: Test Ensemble
1. Open http://localhost:5173/analysis
2. Click "Start camera"
3. Click "Ensemble" toggle
4. Verify it works (even with low accuracy)

### Step 5: Download FER2013 & Retrain
```bash
# Download dataset (see methods above)
# Then train properly
python model/train_fer2013_improved.py
```

### Step 6: Restart Backend
```bash
python app.py
# New model will be loaded automatically
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'tensorflow'"
```bash
pip install tensorflow
```

### Issue: "No module named 'kaggle'"
```bash
pip install kaggle
```

### Issue: "Dataset not found"
- Use Option 2 (quick test) first
- Or download FER2013 manually

### Issue: Out of memory
```bash
python model/train_fer2013_improved.py --batch_size 32
```

---

## ✅ What to Expect

### Quick Test Training
```
Epoch 1/10: loss: 1.9459 - accuracy: 0.1420
Epoch 10/10: loss: 1.8234 - accuracy: 0.1357
✅ Model saved: emotion_cnn_model.h5
```

### Full FER2013 Training
```
Epoch 1/100: loss: 1.8234 - accuracy: 0.2456
Epoch 50/100: loss: 0.9876 - accuracy: 0.6234
Epoch 100/100: loss: 0.8765 - accuracy: 0.6789
✅ Test Accuracy: 67.34%
```

---

## 🎯 Next Steps

Choose your path:

**Path A: Quick Test (Recommended First)**
1. Run `python model/quick_train_cnn.py`
2. Start backend and frontend
3. Test ensemble mode
4. Download FER2013 later

**Path B: Full Training (Best Accuracy)**
1. Download FER2013 dataset
2. Run `python model/train_fer2013_improved.py`
3. Wait 2-4 hours
4. Start backend and frontend

---

**Ready to start?** Choose your path and let's go! 🚀
