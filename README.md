# StressSense - AI-Powered Workplace Wellness Platform

StressSense is an intelligent workplace wellness platform that uses facial emotion recognition and machine learning to help organizations monitor and improve employee wellbeing.

## 🚀 Features

- **Real-time Emotion Detection**: CNN-based facial emotion recognition
- **Stress Prediction**: ML model predicting stress levels from wellness indicators
- **Ensemble Learning**: Combines multiple emotion detection methods for higher accuracy
- **Privacy-First**: On-device processing, no data leaves your infrastructure
- **Analytics Dashboard**: Track wellness trends and insights
- **User Authentication**: Secure JWT-based authentication system

## 📁 Project Structure

```
.
├── stress-sense-wellness-main/    # Frontend (React + TanStack Router + Vite)
│   ├── src/
│   │   ├── routes/               # Page routes
│   │   ├── components/           # React components
│   │   ├── lib/                  # Utilities and API client
│   │   └── hooks/                # Custom React hooks
│   └── public/                   # Static assets
│
└── stresssense-backend/          # Backend (Flask + Python)
    ├── routes/                   # API endpoints
    ├── models/                   # Database models
    ├── services/                 # Business logic
    ├── model/                    # ML models
    │   ├── emotion_cnn_model.h5  # Trained CNN model
    │   ├── stress_model.pkl      # Stress prediction model
    │   └── scaler.pkl            # Feature scaler
    └── data/                     # Training datasets
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19
- **Router**: TanStack Router
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **ML**: TensorFlow.js, face-api.js

### Backend
- **Framework**: Flask
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Authentication**: Flask-JWT-Extended
- **ML**: TensorFlow, scikit-learn
- **Image Processing**: OpenCV, PIL

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd stresssense-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install CNN dependencies (optional, for training)
pip install -r requirements-cnn.txt

# Run the backend
python app.py
```

Backend will run on `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd stress-sense-wellness-main

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will run on `http://localhost:8080`

## 🔑 Authentication

### Test User Credentials
```
Email: test@stresssense.ai
Password: test123
```

### Create New User
Use the registration page at `/register` or use the API:

```bash
POST /api/auth/register
{
  "full_name": "John Doe",
  "email": "john@company.com",
  "password": "secure123",
  "department": "Engineering",
  "position": "Developer"
}
```

## 🧠 ML Models

### 1. CNN Emotion Recognition Model
- **Architecture**: Custom CNN with 3 convolutional blocks
- **Input**: 48×48 grayscale facial images
- **Output**: 7 emotions (angry, disgust, fear, happy, sad, surprise, neutral)
- **Location**: `stresssense-backend/model/emotion_cnn_model.h5`
- **Status**: ✅ Trained and ready

### 2. Stress Prediction Model
- **Algorithm**: Random Forest Classifier
- **Features**: 8 wellness indicators (sleep, work hours, pressure, etc.)
- **Output**: 3 stress levels (Low, Moderate, High)
- **Location**: `stresssense-backend/model/stress_model.pkl`
- **Accuracy**: 87.5%

### 3. Ensemble System
Combines multiple emotion detection methods:
- CNN model (custom trained)
- face-api.js (pre-trained)
- Weighted voting for final prediction

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout user

### Predictions
- `POST /api/predict/stress` - Predict stress level
- `POST /api/predict/emotion` - Detect emotion from image
- `GET /api/predict/history` - Get prediction history

### Dashboard
- `GET /api/dashboard/stats` - Get user statistics
- `GET /api/dashboard/trends` - Get wellness trends

## 🎯 Training Your Own CNN Model

### Using Sample Data (Quick Test)
```bash
cd stresssense-backend
python model/download_datasets.py --dataset sample
python model/train_emotion_cnn.py --dataset custom --data_path data/sample_emotions --epochs 20
```

### Using FER2013 Dataset (Production)
```bash
# 1. Install Kaggle API
pip install kaggle

# 2. Setup Kaggle credentials
# Download kaggle.json from https://www.kaggle.com/account
# Place in ~/.kaggle/ (Linux/Mac) or C:\Users\<username>\.kaggle\ (Windows)

# 3. Download FER2013
python model/download_datasets.py --dataset fer2013 --use_kaggle

# 4. Train CNN (1-2 hours)
python model/train_emotion_cnn.py --dataset fer2013 --epochs 50

# Expected accuracy: 65-70%
```

## 🔧 Configuration

### Backend Environment Variables
Create `.env` file in `stresssense-backend/`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///database/database.db
CORS_ORIGINS=*
```

### Frontend Environment Variables
Create `.env` file in `stress-sense-wellness-main/`:
```env
VITE_API_URL=http://localhost:5000/api
```

## 🚀 Deployment

### Backend (Production)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

### Frontend (Production)
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📝 Development

### Backend Development
```bash
# Run with auto-reload
FLASK_ENV=development python app.py

# Create admin user
flask seed-admin
```

### Frontend Development
```bash
# Run dev server with hot reload
npm run dev

# Lint code
npm run lint

# Format code
npm run format
```

## 🧪 Testing

### Test Login API
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@stresssense.ai","password":"test123"}'
```

### Test Stress Prediction
```bash
curl -X POST http://localhost:5000/api/predict/stress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "sleep_hours": 7,
    "working_hours": 8,
    "work_pressure": 5,
    "physical_activity": 3,
    "remote_work": 1,
    "emotion_score": 75,
    "fatigue_score": 30,
    "focus_score": 80
  }'
```

## 📚 Documentation

- **Backend API**: See `stresssense-backend/README.md`
- **Dataset Info**: See `stresssense-backend/DATASET_INFO.md`
- **Model Training**: See training scripts in `stresssense-backend/model/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FER2013 Dataset**: Facial Expression Recognition dataset
- **face-api.js**: Face detection and recognition library
- **TensorFlow**: Machine learning framework
- **Flask**: Python web framework
- **React**: Frontend library

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@stresssense.ai

---

**Built with ❤️ for healthier workplaces**

**Version**: 1.0.0  
**Last Updated**: May 2026
