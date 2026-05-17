# StressSense Backend 🧠💼

> **Production-ready Flask REST API** for employee stress monitoring and AI-powered wellness analytics.

---

## 🗂 Project Structure

```
stresssense-backend/
├── app.py                          ← Application factory & entry point
├── config.py                       ← Dev / Test / Prod config classes
├── extensions.py                   ← Shared Flask extensions (db, jwt, cors)
├── wsgi.py                         ← Gunicorn WSGI entry point
├── Procfile                        ← Render / Railway / Heroku deployment
├── requirements.txt                ← Python dependencies
├── .env.example                    ← Environment variable template
├── .gitignore
│
├── routes/
│   ├── auth_routes.py              ← POST /register, /login, /logout, /me
│   ├── prediction_routes.py        ← POST /stress, /emotion, /emotion/image
│   ├── dashboard_routes.py         ← GET  /analytics, /history, /summary …
│   └── admin_routes.py             ← GET/DELETE /users, /stats, /predictions
│
├── models/
│   ├── user_model.py               ← users table
│   ├── prediction_model.py         ← predictions + emotion_logs tables
│   └── analytics_model.py          ← stress_analytics table
│
├── services/
│   ├── ml_service.py               ← RandomForest loader + prediction engine
│   ├── emotion_service.py          ← Emotion score processing + DeepFace opt.
│   ├── recommendation_service.py   ← Rule-based wellness recommendation engine
│   └── analytics_service.py        ← Chart.js-ready analytics aggregation
│
├── utils/
│   ├── validators.py               ← Input validation helpers
│   ├── helpers.py                  ← Response builders, chart utils
│   └── security.py                 ← File upload helpers, secure filenames
│
├── model/
│   ├── train_model.py              ← Run once to generate .pkl files
│   ├── stress_model.pkl            ← (generated — not committed)
│   └── scaler.pkl                  ← (generated — not committed)
│
├── database/
│   └── database.db                 ← SQLite DB (auto-created on first run)
└── uploads/                        ← Temp image uploads (cleared after use)
```

---

## ⚡ Quick Start

### 1. Clone & Enter Directory

```bash
git clone <your-repo-url>
cd stresssense-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY and JWT_SECRET_KEY
```

### 5. Train the ML Model (run once)

```bash
python model/train_model.py
```

> This generates `model/stress_model.pkl` and `model/scaler.pkl`.  
> If you skip this step the API falls back to a rule-based heuristic — still fully functional.

### 6. Create Admin User (optional)

```bash
flask seed-admin
# Creates: admin@stresssense.ai / Admin@123!
```

### 7. Start the Development Server

```bash
python app.py
# or:
flask run
```

API is live at: **`http://localhost:5000`**

---

## 📡 API Reference

### Auth — `/api/auth`

| Method | Endpoint              | Auth | Description             |
|--------|-----------------------|------|-------------------------|
| POST   | `/register`           | ❌   | Create new user account |
| POST   | `/login`              | ❌   | Login & get JWT tokens  |
| POST   | `/refresh`            | 🔑   | Refresh access token    |
| GET    | `/me`                 | 🔑   | Get current user profile|
| PUT    | `/profile`            | 🔑   | Update profile fields   |
| POST   | `/change-password`    | 🔑   | Change password         |
| POST   | `/logout`             | 🔑   | Logout (discard token)  |

### Prediction — `/api/predict`

| Method | Endpoint              | Auth | Description                        |
|--------|-----------------------|------|------------------------------------|
| POST   | `/stress`             | 🔑   | Run ML stress prediction           |
| POST   | `/emotion`            | 🔑   | Analyse emotion scores (JSON)      |
| POST   | `/emotion/image`      | 🔑   | Analyse face image (DeepFace)      |
| GET    | `/history`            | 🔑   | Paginated prediction history       |

### Dashboard — `/api/dashboard`

| Method | Endpoint              | Auth | Description                        |
|--------|-----------------------|------|------------------------------------|
| GET    | `/analytics`          | 🔑   | Stress & wellness trend (Chart.js) |
| GET    | `/history`            | 🔑   | Filterable prediction history      |
| GET    | `/summary`            | 🔑   | Weekly wellness summary cards      |
| GET    | `/mood-trend`         | 🔑   | Emotion trend over N days          |
| GET    | `/burnout-stats`      | 🔑   | Burnout risk distribution          |
| GET    | `/wellness-report`    | 🔑   | Full weekly wellness report        |

### Admin — `/api/admin`

| Method | Endpoint              | Auth | Description                       |
|--------|-----------------------|------|-----------------------------------|
| GET    | `/users`              | 👑   | List all users (paginated)        |
| GET    | `/users/<id>`         | 👑   | Get specific user                 |
| PUT    | `/users/<id>`         | 👑   | Update user role / status         |
| DELETE | `/user/<id>`          | 👑   | Delete user + their data          |
| GET    | `/stats`              | 👑   | Platform-wide statistics          |
| GET    | `/predictions`        | 👑   | All predictions (paginated)       |

🔑 = JWT token required &nbsp;&nbsp; 👑 = Admin JWT required

---

## 🧠 Stress Prediction Payload

**Request:**
```json
POST /api/predict/stress
Authorization: Bearer <access_token>

{
  "sleep_hours": 6.5,
  "working_hours": 10,
  "work_pressure": 8,
  "physical_activity": 1.5,
  "remote_work": true,
  "emotion_score": 35,
  "fatigue_score": 72,
  "focus_score": 45
}
```

**Response:**
```json
{
  "success": true,
  "stress_level": "High",
  "stress_score": 78.4,
  "stress_percentage": 78.4,
  "burnout_risk": "High",
  "wellness_score": 28.3,
  "confidence": 0.91,
  "model_used": "RandomForest",
  "recommendations": [
    "🚨 Your burnout risk is HIGH. Please consider speaking with HR or a counsellor.",
    "⏸️ Take a 10-minute break every 90 minutes to prevent burnout.",
    "🌙 Aim for 7–9 hours of sleep tonight.",
    "💬 Share how you're feeling with someone you trust today.",
    "💪 Do 5 minutes of desk stretches to release physical tension."
  ],
  "prediction_id": 42,
  "timestamp": "2024-07-15T14:32:10.123456"
}
```

---

## 🚀 Production Deployment

### Render / Railway

1. Push this folder to a GitHub repository
2. Connect to Render/Railway and point at the repo
3. Set environment variables from `.env.example`
4. The `Procfile` handles startup automatically

### PythonAnywhere

```bash
pip install -r requirements.txt
# In WSGI config, point to: stresssense-backend/wsgi.py
```

### Manual Gunicorn

```bash
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4 --timeout 120
```

---

## 🔒 Security Notes

- **Never commit `.env`** — it contains your secret keys
- **Rotate secrets** in production using `python -c "import secrets; print(secrets.token_hex(32))"`
- **Passwords** are hashed with Werkzeug's `generate_password_hash` (PBKDF2-SHA256)
- **JWT tokens** expire after 24 hours (access) and 30 days (refresh)
- **CORS** is restricted to `CORS_ORIGINS` in production — update `.env` accordingly

---

## 🛠 Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Framework   | Flask 3.0                               |
| Auth        | Flask-JWT-Extended (JWT Bearer tokens)  |
| Database    | SQLite → MySQL / PostgreSQL (via env)   |
| ORM         | Flask-SQLAlchemy 3.1                    |
| ML          | scikit-learn (RandomForestClassifier)   |
| Scaling     | StandardScaler (pickle)                 |
| Emotion AI  | EmotionService + optional DeepFace      |
| Server      | Gunicorn (production)                   |
| CORS        | Flask-CORS                              |

---

*Built for college projects · internship portfolios · hackathons · startup demos · GitHub showcases* 🚀
