# Ensemble Emotion Detection - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start Backend
```bash
cd stresssense-backend
python app.py
```
**Expected Output**: `✅ CNN emotion model loaded`

### Step 2: Start Frontend
```bash
cd stress-sense-wellness-main
npm run dev
```
**Expected Output**: Server running on `http://localhost:5173`

### Step 3: Use Ensemble
1. Navigate to `/analysis` page
2. Click **"Start camera"**
3. Click **"Ensemble"** toggle button
4. Watch the magic happen! ✨

---

## 🎯 What You'll See

### Ensemble Badge
When ensemble mode is active, you'll see a badge next to "Live facial analysis":
```
🧠 Live facial analysis [🔷 Ensemble]
```

### Statistics Panel
Real-time metrics displayed below the camera:
```
┌─────────────────────────────────────┐
│ 🔷 Ensemble Statistics              │
├─────────────────────────────────────┤
│ Model Agreement:        85%         │
│ Ensemble Confidence:    78%         │
│ Face-API Confidence:    72%         │
│ CNN Confidence:         65%         │
└─────────────────────────────────────┘
```

### Enhanced Predictions
- **Dominant Emotion**: Combined from both models
- **Confidence Score**: Boosted when models agree
- **Emotion Breakdown**: Weighted average of scores

---

## 🎮 Controls

### Ensemble Toggle
- **ON** (Blue): Using face-api.js + CNN
- **OFF** (Gray): Using face-api.js only

### When to Use Ensemble:
- ✅ Need highest accuracy
- ✅ Have backend running
- ✅ Can wait 1 second per detection

### When to Disable:
- ❌ Backend not available
- ❌ Need faster updates (0.5s)
- ❌ Testing face-api.js only

---

## 📊 Understanding the Stats

### Model Agreement
**What it means**: How often both models predict the same emotion

- **>80%**: 🟢 Excellent - Trust the prediction
- **60-80%**: 🟡 Good - Reliable prediction
- **40-60%**: 🟠 Fair - Some uncertainty
- **<40%**: 🔴 Poor - Models disagree

### Confidence Scores
**What it means**: How sure each model is about its prediction

- **Ensemble**: Combined confidence (usually highest)
- **Face-API**: Browser model confidence
- **CNN**: Backend model confidence

**Rule of Thumb**: Higher agreement = Higher ensemble confidence

---

## 🔧 Troubleshooting

### "Ensemble" button does nothing?
**Check**: Is backend running?
```bash
curl http://localhost:5000/api/health
```

### No statistics showing?
**Wait**: Stats appear after 2-3 detections
**Check**: Console for errors (F12)

### Low agreement rate?
**Normal**: 50-70% is typical
**Why**: Models trained on different data
**Fix**: Train CNN on better dataset

### Slow performance?
**Normal**: Ensemble takes ~1 second per detection
**Why**: Calling backend API + processing
**Fix**: Disable ensemble for faster updates

---

## 🎓 How It Works (Simple)

```
1. Camera captures your face
   ↓
2. Face-API.js analyzes (browser)
   ↓
3. Frame sent to CNN (backend)
   ↓
4. Both predictions combined
   ↓
5. Enhanced result displayed
```

**Key Insight**: Two models are better than one!

---

## 💡 Pro Tips

### Tip 1: Check Agreement First
- High agreement (>80%)? Trust the prediction!
- Low agreement (<50%)? Take with grain of salt

### Tip 2: Watch Confidence Trends
- Ensemble confidence rising? You're expressing clearer emotions
- Confidence dropping? Emotions might be mixed

### Tip 3: Compare Models
- Face-API better? Increase its weight
- CNN better? Increase its weight
- (See configuration below)

### Tip 4: Use for Important Decisions
- Enable ensemble for wellness reports
- Disable for quick checks

---

## ⚙️ Configuration (Advanced)

### Change Ensemble Method
Open browser console (F12) and run:
```javascript
ensembleDetector.updateConfig({
  method: 'weighted' // or 'voting', 'averaging', 'stacking'
});
```

### Adjust Model Weights
```javascript
// Give CNN more weight
ensembleDetector.updateConfig({
  weights: { faceApi: 0.4, cnn: 0.6 }
});
```

### Change Detection Speed
Edit `analysis.tsx`:
```typescript
// Faster (but more API calls)
detectionIntervalRef.current = window.setInterval(async () => {
  // ...
}, 500); // 0.5 seconds

// Slower (but less load)
}, 2000); // 2 seconds
```

---

## 📈 Expected Results

### With Good Lighting:
- Agreement: 70-85%
- Ensemble Confidence: 75-90%
- Accuracy: ~80%

### With Poor Lighting:
- Agreement: 50-65%
- Ensemble Confidence: 60-75%
- Accuracy: ~65%

### With Neutral Expression:
- Agreement: 80-90% (both see "neutral")
- Ensemble Confidence: 70-85%
- Accuracy: ~85%

---

## 🐛 Common Issues

### Issue: "CNN model not available"
**Solution**: Train the model first
```bash
cd stresssense-backend
python model/quick_train_cnn.py
```

### Issue: "Authorization failed"
**Solution**: Login first, then start camera

### Issue: "No face detected"
**Solution**: 
- Ensure good lighting
- Position face in center
- Move closer to camera

### Issue: Stats not updating
**Solution**: 
- Wait 2-3 detection cycles
- Check browser console for errors
- Verify backend is responding

---

## 🎯 Quick Test

### Test 1: Happy Face
1. Enable ensemble
2. Smile broadly
3. Check: Both models should detect "Happy"
4. Agreement should be >80%

### Test 2: Neutral Face
1. Relax your face
2. Look at camera
3. Check: Both should detect "Neutral"
4. Agreement should be >85%

### Test 3: Sad Face
1. Frown slightly
2. Look down a bit
3. Check: Both should detect "Sad"
4. Agreement might be 60-75% (harder emotion)

---

## 📚 Learn More

- **Full Documentation**: See `ENSEMBLE_INTEGRATION_COMPLETE.md`
- **Ensemble Theory**: See "Ensemble Methods Explained" section
- **API Reference**: See `ensemble-emotion.ts` source code

---

## ✅ Checklist

Before using ensemble, ensure:
- [ ] Backend is running
- [ ] CNN model is trained
- [ ] Camera permissions granted
- [ ] Good lighting conditions
- [ ] Face visible in frame

---

## 🎉 You're Ready!

Ensemble emotion detection is now at your fingertips. Enjoy more accurate emotion recognition powered by AI! 🚀

**Questions?** Check the full documentation or console logs for details.

---

**Last Updated**: 2026-05-17
**Version**: 1.0.0
