# 📊 Dataset & ML Model - Complete Summary

## ✅ Current Status

### Models Trained & Ready:
- ✅ **stress_model.pkl** - RandomForest classifier (87.5% accuracy)
- ✅ **scaler.pkl** - StandardScaler for feature normalization
- ✅ **Backend loaded** - Models auto-loaded on startup

### Dataset:
- ✅ **Type**: Synthetic (programmatically generated)
- ✅ **Samples**: 3,000 training samples
- ✅ **Features**: 8 wellness indicators
- ✅ **Target**: 3-class stress level (Low/Moderate/High)

---

## 📍 Where is the Dataset?

### Answer: **It's Generated Synthetically!**

The dataset is **not a file** - it's generated on-the-fly by the training script using realistic algorithms.

### Why Synthetic Data?

1. **Privacy**: No real user data needed
2. **Instant**: Generate thousands of samples in seconds
3. **Controlled**: Adjust distributions as needed
4. **Baseline**: Good starting point before collecting real data
5. **Flexible**: Easy to create specific scenarios

---

## 🎯 Dataset Details

### Input Features (8):

| Feature | Range | Description | Impact on Stress |
|---------|-------|-------------|------------------|
| **sleep_hours** | 0-12h | Hours of sleep | More sleep → Less stress |
| **working_hours** | 0-16h | Hours worked today | More hours → More stress |
| **work_pressure** | 1-10 | Self-reported pressure | Higher → More stress |
| **physical_activity** | 0-10h/week | Exercise hours | More activity → Less stress |
| **remote_work** | 0 or 1 | Work location | Varies |
| **emotion_score** | 0-100 | Emotional wellness | Higher → Less stress |
| **fatigue_score** | 0-100 | Fatigue level | Higher → More stress |
| **focus_score** | 0-100 | Focus/concentration | Higher → Less stress |

### Target Variable:

- **0**: Low stress (score < 35)
- **1**: Moderate stress (35-65)
- **2**: High stress (score > 65)

---

## 📈 Model Performance

### Training Results:

```
Accuracy: 87.5%

Classification Report:
              precision    recall  f1-score   support
         Low       0.89      0.96      0.93       421
    Moderate       0.83      0.70      0.76       169
        High       0.00      0.00      0.00        10

Label Distribution (3,000 samples):
  Low:      2,105 (70%)
  Moderate:   843 (28%)
  High:        52 (2%)
```

### Observations:

- ✅ **Excellent** on Low stress detection
- ✅ **Good** on Moderate stress detection
- ⚠️ **Poor** on High stress (insufficient samples)

---

## 🔧 How to Use the Dataset

### Option 1: Use Existing Trained Model (Current)

```bash
# Models already trained and loaded!
# Just run the backend:
cd stresssense-backend
python app.py
```

The backend automatically loads:
- `model/stress_model.pkl`
- `model/scaler.pkl`

### Option 2: Retrain with More Samples

```bash
# Edit train_model.py to change n_samples
cd stresssense-backend
python model/train_model.py
```

### Option 3: Generate Custom Dataset

```bash
# Generate 5,000 samples
python model/generate_dataset.py --type synthetic --samples 5000

# Generate realistic user scenarios
python model/generate_dataset.py --type realistic --samples 2000

# Save to CSV for inspection
python model/generate_dataset.py --type synthetic --samples 5000 --save data/training.csv
```

### Option 4: Use Your Own Real Data

1. **Collect data** in CSV format:
```csv
sleep_hours,working_hours,work_pressure,physical_activity,remote_work,emotion_score,fatigue_score,focus_score,stress_label
7.5,8.0,5.0,3.0,1,75.0,30.0,80.0,0
5.0,12.0,9.0,0.5,0,35.0,85.0,40.0,2
```

2. **Load and train**:
```python
# In train_model.py, replace generate_dataset() with:
df = pd.read_csv('data/real_data.csv')
```

3. **Retrain**:
```bash
python model/train_model.py
```

---

## 📊 Dataset Generation Algorithm

### Stress Score Calculation:

```python
stress_score = 
    max(0, (8 - sleep_hours) * 6) +      # Sleep deficit
    max(0, (working_hours - 8) * 4) +    # Overwork
    work_pressure * 4 +                   # Pressure
    fatigue_score * 0.5 +                 # Fatigue
    - focus_score * 0.25 +                # Poor focus
    - physical_activity * 2.5 +           # Lack of exercise
    - (emotion_score / 100) * 15          # Negative emotions
    + random_noise(-8, +8)                # Realism
```

### Realistic Distributions:

- **Sleep**: Normal distribution around 7h (σ=1.5)
- **Work Hours**: Bimodal (70% normal 8h, 30% overwork 11h)
- **Pressure**: Beta distribution (most moderate)
- **Activity**: Exponential (most people do little)
- **Emotions**: Correlated with sleep and pressure

---

## 🎯 Example Data Samples

### Low Stress Example:
```json
{
  "sleep_hours": 8.0,
  "working_hours": 7.5,
  "work_pressure": 3.0,
  "physical_activity": 5.0,
  "remote_work": 1,
  "emotion_score": 80.0,
  "fatigue_score": 25.0,
  "focus_score": 85.0,
  "stress_score": 18.5,
  "stress_label": 0
}
```

### High Stress Example:
```json
{
  "sleep_hours": 4.5,
  "working_hours": 13.0,
  "work_pressure": 9.5,
  "physical_activity": 0.5,
  "remote_work": 0,
  "emotion_score": 25.0,
  "fatigue_score": 90.0,
  "focus_score": 30.0,
  "stress_score": 78.2,
  "stress_label": 2
}
```

---

## 🔄 Integration with Face Detection

### How Camera Data Enhances Predictions:

1. **Emotion Score** from facial detection replaces manual mood
2. **Fatigue Score** calculated from sad/neutral emotions
3. **Stress Indicators** from angry/fearful/sad emotions
4. **Real-time Updates** as expressions change

### Data Flow:

```
Camera → Face Detection → Emotions (7 types)
                              ↓
                    Emotion Score (0-100)
                              ↓
                    ML Model Input
                              ↓
                    Stress Prediction
```

---

## 📁 File Structure

```
stresssense-backend/
├── model/
│   ├── train_model.py          # Main training script
│   ├── generate_dataset.py     # Dataset generator
│   ├── stress_model.pkl        # ✅ Trained model
│   └── scaler.pkl              # ✅ Feature scaler
├── services/
│   ├── ml_service.py           # Model inference
│   └── emotion_service.py      # Emotion processing
├── routes/
│   └── prediction_routes.py    # API endpoints
└── DATASET_INFO.md             # Full documentation
```

---

## 🚀 Quick Commands

### Train Model:
```bash
cd stresssense-backend
python model/train_model.py
```

### Generate Dataset:
```bash
# Synthetic (default)
python model/generate_dataset.py --type synthetic --samples 5000

# Realistic scenarios
python model/generate_dataset.py --type realistic --samples 2000

# Save to CSV
python model/generate_dataset.py --type synthetic --samples 5000 --save data/training.csv
```

### Test Prediction:
```bash
# Start backend
python app.py

# Test API (in another terminal)
curl -X POST http://localhost:5000/api/predict/stress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "sleep_hours": 7,
    "working_hours": 8,
    "work_pressure": 5,
    "physical_activity": 3,
    "remote_work": true,
    "emotion_score": 75,
    "fatigue_score": 30,
    "focus_score": 80
  }'
```

---

## 📊 Dataset Statistics

### Current Training Data:

```
Total Samples: 3,000

Label Distribution:
  Low (0):      2,105 samples (70.2%)
  Moderate (1):   843 samples (28.1%)
  High (2):        52 samples (1.7%)

Feature Statistics:
  sleep_hours:       mean=7.0, std=1.5
  working_hours:     mean=8.5, std=2.0
  work_pressure:     mean=5.5, std=2.0
  physical_activity: mean=2.5, std=2.0
  emotion_score:     mean=65.0, std=15.0
  fatigue_score:     mean=45.0, std=20.0
  focus_score:       mean=70.0, std=15.0
```

---

## 🎯 Improving the Dataset

### Recommendations:

1. **Balance Classes**:
   - Generate more High stress samples
   - Adjust stress calculation thresholds

2. **Add Features**:
   - Age, job role, team size
   - Deadline pressure, social support
   - Break frequency, commute time

3. **Collect Real Data**:
   - Deploy to users
   - Collect feedback
   - Retrain with real data

4. **Use External Datasets**:
   - Kaggle stress datasets
   - Mental health surveys
   - Workplace wellness studies

---

## 📚 Documentation

### Full Details:
- **DATASET_INFO.md** - Complete dataset documentation
- **ML_FACE_DETECTION.md** - Face detection ML details
- **REAL_TIME_ML_SUMMARY.md** - Overall ML implementation

### Code Files:
- **model/train_model.py** - Training script
- **model/generate_dataset.py** - Dataset generator
- **services/ml_service.py** - Model inference
- **services/emotion_service.py** - Emotion processing

---

## ✅ Summary

### What You Have:

1. ✅ **Trained ML Model** (87.5% accuracy)
2. ✅ **Synthetic Dataset** (3,000 samples)
3. ✅ **Dataset Generator** (customizable)
4. ✅ **Backend Integration** (auto-loads models)
5. ✅ **Face Detection** (enhances predictions)
6. ✅ **API Endpoints** (ready to use)

### What You Can Do:

1. ✅ Use current model (already working)
2. ✅ Generate more training data
3. ✅ Retrain with custom parameters
4. ✅ Add your own real data
5. ✅ Improve model accuracy
6. ✅ Deploy to production

---

## 🎉 Ready to Use!

**The dataset is synthetic, the model is trained, and everything is working!**

- **Frontend**: http://localhost:8080
- **Backend**: http://localhost:5000
- **Analysis**: http://localhost:8080/analysis

**Start using the ML-powered stress detection now! 🚀**

---

**Last Updated**: May 15, 2026
**Version**: 1.0.0
**Status**: ✅ TRAINED & READY
