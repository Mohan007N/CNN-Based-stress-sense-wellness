# StressSense Dataset Information

## 📊 Overview

StressSense uses **synthetic datasets** for training the stress prediction ML model. The dataset is generated programmatically to simulate realistic workplace wellness scenarios.

---

## 🎯 Dataset Location

### Current Setup:
- **Type**: Synthetic (generated on-the-fly)
- **Generator**: `model/train_model.py`
- **Samples**: 3,000 (default)
- **Features**: 8 input features
- **Target**: 3-class stress level (Low/Moderate/High)

### Trained Models:
- **Model File**: `model/stress_model.pkl` ✅ (Generated)
- **Scaler File**: `model/scaler.pkl` ✅ (Generated)
- **Accuracy**: 87.5%

---

## 📋 Dataset Features

### Input Features (8):

1. **sleep_hours** (float)
   - Range: 0-12 hours
   - Description: Hours of sleep last night
   - Impact: Higher sleep → Lower stress

2. **working_hours** (float)
   - Range: 0-16 hours
   - Description: Hours worked today
   - Impact: More hours → Higher stress

3. **work_pressure** (float)
   - Range: 1-10 scale
   - Description: Self-reported work pressure
   - Impact: Higher pressure → Higher stress

4. **physical_activity** (float)
   - Range: 0-10 hours per week
   - Description: Weekly exercise hours
   - Impact: More activity → Lower stress

5. **remote_work** (int)
   - Range: 0 or 1
   - Description: Working from home (1) or office (0)
   - Impact: Varies by individual

6. **emotion_score** (float)
   - Range: 0-100
   - Description: Emotional wellness score (higher is better)
   - Source: Facial emotion detection or manual mood
   - Impact: Higher score → Lower stress

7. **fatigue_score** (float)
   - Range: 0-100
   - Description: Fatigue level (higher is more tired)
   - Impact: Higher fatigue → Higher stress

8. **focus_score** (float)
   - Range: 0-100
   - Description: Focus/concentration level (higher is better)
   - Impact: Better focus → Lower stress

### Target Variable:

**stress_label** (int)
- **0**: Low stress (stress_score < 35)
- **1**: Moderate stress (35 ≤ stress_score < 65)
- **2**: High stress (stress_score ≥ 65)

---

## 🎲 Synthetic Data Generation

### How It Works:

The `train_model.py` script generates synthetic data using:

1. **Random distributions** for base features
2. **Realistic correlations** between features
3. **Heuristic stress calculation** based on wellness research
4. **Noise addition** for realism

### Stress Score Formula:

```python
stress_score = 
    max(0, (8 - sleep_hours) * 5) +      # Sleep deficit
    max(0, (working_hours - 8) * 3) +    # Overwork
    work_pressure * 3 +                   # Pressure
    fatigue_score * 0.4 +                 # Fatigue
    - focus_score * 0.2 +                 # Poor focus
    - physical_activity * 2 +             # Lack of exercise
    - (emotion_score / 100) * 10          # Negative emotions
```

### Label Assignment:

```python
if stress_score < 35:
    label = 0  # Low
elif stress_score < 65:
    label = 1  # Moderate
else:
    label = 2  # High
```

---

## 📈 Dataset Statistics

### Current Training Data (3,000 samples):

```
Label Distribution:
  Low (0):      2,105 samples (70%)
  Moderate (1):   843 samples (28%)
  High (2):        52 samples (2%)

Feature Ranges:
  sleep_hours:       3.0 - 10.0
  working_hours:     4.0 - 14.0
  work_pressure:     1.0 - 10.0
  physical_activity: 0.0 - 10.0
  remote_work:       0 or 1
  emotion_score:    10.0 - 95.0
  fatigue_score:     5.0 - 95.0
  focus_score:      10.0 - 95.0
```

---

## 🔧 Generating Custom Datasets

### Option 1: Use Default Synthetic Generator

```bash
cd stresssense-backend
python model/train_model.py
```

This generates 3,000 samples and trains the model.

### Option 2: Generate Custom Synthetic Dataset

```bash
# Generate 5,000 samples
python model/generate_dataset.py --type synthetic --samples 5000

# Generate and save to CSV
python model/generate_dataset.py --type synthetic --samples 5000 --save data/training_data.csv
```

### Option 3: Generate Realistic Scenarios

```bash
# Generate realistic user profiles
python model/generate_dataset.py --type realistic --samples 1000 --save data/realistic_data.csv
```

This creates 4 user profiles:
- **Healthy**: Good sleep, balanced work, active
- **Stressed**: Poor sleep, long hours, inactive
- **Burnout**: Very poor sleep, excessive hours, high pressure
- **Balanced**: Moderate in all aspects

### Option 4: Use Your Own CSV Data

```bash
# Load from CSV file
python model/generate_dataset.py --type csv --file data/my_data.csv
```

**Required CSV format:**
```csv
sleep_hours,working_hours,work_pressure,physical_activity,remote_work,emotion_score,fatigue_score,focus_score,stress_label
7.5,8.0,5.0,3.0,1,75.0,30.0,80.0,0
5.0,12.0,9.0,0.5,0,35.0,85.0,40.0,2
...
```

---

## 📊 Real-World Data Collection

### If You Want to Use Real Data:

#### 1. **Collect User Data**

Create a data collection form with these fields:
- Sleep hours (last night)
- Working hours (today)
- Work pressure (1-10 scale)
- Physical activity (hours per week)
- Remote work (yes/no)
- Current mood/emotion
- Fatigue level
- Focus level
- Self-reported stress level

#### 2. **Format as CSV**

Save collected data in the format shown above.

#### 3. **Train with Real Data**

```python
# In train_model.py, replace generate_dataset() with:
df = pd.read_csv('data/real_user_data.csv')
```

#### 4. **Retrain Model**

```bash
python model/train_model.py
```

---

## 🎯 Dataset Quality

### Current Model Performance:

```
Accuracy: 87.5%

Classification Report:
              precision    recall  f1-score   support
         Low       0.89      0.96      0.93       421
    Moderate       0.83      0.70      0.76       169
        High       0.00      0.00      0.00        10

    accuracy                           0.88       600
```

### Observations:

- ✅ **Good performance** on Low and Moderate stress
- ⚠️ **Poor performance** on High stress (only 52 samples)
- 💡 **Recommendation**: Generate more High stress samples

---

## 🔄 Improving the Dataset

### 1. **Balance Classes**

Generate more High stress samples:

```python
# In generate_dataset.py, adjust stress calculation
# to create more high-stress scenarios
```

### 2. **Add More Features**

Consider adding:
- Age
- Job role
- Team size
- Deadline pressure
- Social support
- Break frequency

### 3. **Collect Real Data**

- Deploy to users
- Collect feedback
- Retrain with real data
- Improve accuracy

### 4. **Use Pre-trained Models**

Consider using:
- Kaggle stress datasets
- Mental health datasets
- Workplace wellness surveys

---

## 📁 Dataset Files Structure

```
stresssense-backend/
├── model/
│   ├── train_model.py          # Main training script
│   ├── generate_dataset.py     # Dataset generator (NEW)
│   ├── stress_model.pkl        # Trained model ✅
│   └── scaler.pkl              # Feature scaler ✅
├── data/                       # (Optional) Real datasets
│   ├── training_data.csv
│   ├── realistic_data.csv
│   └── real_user_data.csv
└── DATASET_INFO.md             # This file
```

---

## 🚀 Quick Start

### Generate and Train:

```bash
# 1. Generate synthetic dataset and train
cd stresssense-backend
python model/train_model.py

# 2. (Optional) Generate custom dataset
python model/generate_dataset.py --type realistic --samples 2000 --save data/training.csv

# 3. Backend will auto-load the trained models
python app.py
```

---

## 📊 Example Data Samples

### Low Stress Sample:
```python
{
    "sleep_hours": 8.0,
    "working_hours": 7.5,
    "work_pressure": 3.0,
    "physical_activity": 5.0,
    "remote_work": 1,
    "emotion_score": 80.0,
    "fatigue_score": 25.0,
    "focus_score": 85.0,
    "stress_label": 0  # Low
}
```

### High Stress Sample:
```python
{
    "sleep_hours": 4.5,
    "working_hours": 13.0,
    "work_pressure": 9.5,
    "physical_activity": 0.5,
    "remote_work": 0,
    "emotion_score": 25.0,
    "fatigue_score": 90.0,
    "focus_score": 30.0,
    "stress_label": 2  # High
}
```

---

## 🔬 Research References

### Stress Factors Based On:

1. **Sleep**: National Sleep Foundation guidelines (7-9h optimal)
2. **Work Hours**: WHO recommendations (40h/week standard)
3. **Physical Activity**: CDC guidelines (150min/week)
4. **Emotional Wellness**: Positive Psychology research
5. **Fatigue**: Occupational health studies

---

## 📝 Notes

### Why Synthetic Data?

1. **Privacy**: No real user data needed initially
2. **Control**: Can generate specific scenarios
3. **Speed**: Instant dataset generation
4. **Flexibility**: Easy to adjust distributions
5. **Baseline**: Good starting point before real data

### Limitations:

1. **Not Real**: May not capture all real-world patterns
2. **Simplified**: Stress is complex, model is heuristic
3. **Bias**: Based on assumptions about stress factors
4. **Generalization**: May not work for all populations

### Recommendations:

1. ✅ Start with synthetic data (current approach)
2. ✅ Deploy to users and collect feedback
3. ✅ Gradually incorporate real data
4. ✅ Retrain periodically with new data
5. ✅ Validate with domain experts

---

## 🎯 Summary

- **Dataset**: Synthetic, 3,000 samples
- **Features**: 8 wellness indicators
- **Target**: 3-class stress level
- **Model**: RandomForest, 87.5% accuracy
- **Status**: ✅ Trained and ready
- **Location**: `model/stress_model.pkl`

**The model is trained and working! You can now use it for predictions.** 🚀

---

**Last Updated**: May 15, 2026
**Version**: 1.0.0
**Status**: ✅ TRAINED & READY
