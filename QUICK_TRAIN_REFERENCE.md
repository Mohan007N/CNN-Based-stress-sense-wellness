# Quick Training Reference Card

## 🚀 Train CNN in 3 Commands

```bash
# 1. Setup (one-time)
cd stresssense-backend && ./setup_fer2013_training.sh

# 2. Download dataset (one-time)
python model/train_fer2013_improved.py --download

# 3. Train model (2-4 hours)
python model/train_fer2013_improved.py
```

**That's it!** Model will be saved to `model/emotion_cnn_model.h5`

---

## ⚡ Quick Commands

### Training Options
```bash
# Full training (100 epochs, best accuracy)
python model/train_fer2013_improved.py

# Quick training (30 epochs, faster)
python model/train_fer2013_improved.py --epochs 30

# Custom batch size (if out of memory)
python model/train_fer2013_improved.py --batch_size 32

# Custom learning rate
python model/train_fer2013_improved.py --learning_rate 0.0005
```

### Monitoring
```bash
# Watch training progress
tensorboard --logdir=model/logs

# Check model exists
ls -lh model/emotion_cnn_model.h5
```

### Using Trained Model
```bash
# Start backend (auto-loads model)
python app.py

# You should see:
# ✅ CNN emotion model loaded from model/emotion_cnn_model.h5
```

---

## 📊 Expected Results

### Training Progress
```
Epoch 1:   Acc: 25%   (learning basics)
Epoch 20:  Acc: 52%   (learning patterns)
Epoch 50:  Acc: 62%   (fine-tuning)
Epoch 80:  Acc: 67%   (converged) ✅
```

### Final Metrics
```
Test Accuracy:     67.34%  ✅
Training Time:     2-4 hours (CPU)
Model Size:        ~50 MB
Ensemble Accuracy: ~78%    ✅
Agreement Rate:    ~75%    🟢
```

---

## 🎯 Quick Checklist

### Before Training
- [ ] Python 3.8+ installed
- [ ] TensorFlow installed
- [ ] FER2013 dataset downloaded
- [ ] ~2 GB free disk space

### After Training
- [ ] Model file exists (~50 MB)
- [ ] Test accuracy > 60%
- [ ] Training plots saved
- [ ] Backend loads model

### Using Ensemble
- [ ] Backend running
- [ ] Frontend running
- [ ] Camera started
- [ ] Ensemble toggle enabled
- [ ] Agreement rate > 70%

---

## 🐛 Quick Fixes

### Out of Memory
```bash
python model/train_fer2013_improved.py --batch_size 32
```

### Training Too Slow
```bash
python model/train_fer2013_improved.py --epochs 30
```

### Dataset Not Found
1. Download: https://www.kaggle.com/datasets/msambare/fer2013
2. Place: `stresssense-backend/data/fer2013.csv`

### Model Not Loading
```bash
# Check file exists
ls model/emotion_cnn_model.h5

# Check file size (~50 MB)
ls -lh model/emotion_cnn_model.h5
```

---

## 📁 Important Files

```
stresssense-backend/
├── model/
│   ├── train_fer2013_improved.py    ← Training script
│   ├── emotion_cnn_model.h5         ← Trained model (after training)
│   ├── training_history.png         ← Accuracy plots
│   └── confusion_matrix.png         ← Confusion matrix
├── data/
│   └── fer2013.csv                  ← Dataset (download)
└── setup_fer2013_training.sh        ← Setup script
```

---

## 🎓 Key Numbers

| Metric | Value |
|--------|-------|
| **Dataset Size** | 35,887 images |
| **Image Size** | 48×48 grayscale |
| **Emotions** | 7 classes |
| **Training Time** | 2-4 hours (CPU) |
| **Expected Accuracy** | 65-70% |
| **Model Size** | ~50 MB |
| **Ensemble Accuracy** | 75-80% |

---

## 💡 One-Liners

```bash
# Complete setup and training
./setup_fer2013_training.sh && python model/train_fer2013_improved.py

# Quick test (30 epochs)
python model/train_fer2013_improved.py --epochs 30 --batch_size 64

# Monitor training
tensorboard --logdir=model/logs &

# Verify model
python -c "from tensorflow.keras.models import load_model; m=load_model('model/emotion_cnn_model.h5'); print('✅ Model loaded')"
```

---

## 🚀 Full Workflow

```bash
# 1. Setup environment
cd stresssense-backend
./setup_fer2013_training.sh

# 2. Download dataset
python model/train_fer2013_improved.py --download

# 3. Train model
python model/train_fer2013_improved.py

# 4. Verify training
ls -lh model/emotion_cnn_model.h5

# 5. Start backend
python app.py

# 6. Start frontend (new terminal)
cd ../stress-sense-wellness-main
npm run dev

# 7. Test ensemble
# Open http://localhost:5173/analysis
# Click "Start camera" → "Ensemble"
```

---

## 📚 Documentation

- **Full Guide**: `TRAIN_WITH_REAL_DATA.md`
- **Ensemble Docs**: `ENSEMBLE_INTEGRATION_COMPLETE.md`
- **Quick Start**: `ENSEMBLE_QUICK_START.md`
- **Improvements**: `IMPROVEMENTS.md`

---

## ✅ Success Indicators

### Training Success
```
✅ Test Accuracy: 67.34%
✅ Model saved: emotion_cnn_model.h5
✅ Plots saved: training_history.png
✅ No errors during training
```

### Integration Success
```
✅ Backend loads model
✅ Ensemble toggle works
✅ Agreement rate > 70%
✅ Confidence scores high
```

---

## 🎯 Remember

1. **Train Once**: Model persists across restarts
2. **Auto-Load**: Backend loads model automatically
3. **No Code Changes**: Just train and restart
4. **Monitor Progress**: Use TensorBoard
5. **Verify Accuracy**: Check test accuracy > 60%

---

**Quick Reference Card** | **Version 1.0.0** | **2026-05-17**

**🚀 Train → Deploy → Enjoy 75-80% Accuracy!**
