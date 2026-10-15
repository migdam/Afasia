# 🗣️ Aphasia Speech Therapy App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> **A production-ready speech therapy web application designed for aphasia patients, supporting Polish and English languages.**

[🇵🇱 **Polish Version** / Wersja Polska →](README.pl.md)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🌟 Overview

Aphasia Speech Therapy App is a comprehensive web-based platform designed to help individuals with aphasia improve their communication skills through interactive exercises and progress tracking. Built with modern technologies and best practices, it provides a seamless experience for both patients and therapists.

### What is Aphasia?

Aphasia is a communication disorder that affects a person's ability to speak, understand, read, and write. It typically occurs after a stroke or brain injury. This application helps patients practice and improve their language skills through structured therapy sessions.

### Who is this for?

- **Patients**: Individuals with aphasia seeking to improve their communication skills
- **Speech Therapists**: Professionals monitoring patient progress and managing therapy plans
- **Caregivers**: Family members supporting aphasia patients in their recovery
- **Healthcare Facilities**: Clinics and hospitals providing speech therapy services

---

## ✨ Features

### Core Functionality

#### 🎯 **Interactive Therapy Sessions**
- **Word Naming**: Visual recognition and naming exercises with images
- **Sentence Completion**: Fill-in-the-blank exercises with multiple choice options
- **Image Recognition**: Match images to correct words
- **Pronunciation Practice**: Record and evaluate speech patterns

#### 📊 **Progress Tracking**
- Real-time performance monitoring
- Visual progress charts and analytics
- Accuracy rate tracking over time
- Session history with detailed statistics

#### 👤 **User Management**
- Secure authentication with JWT tokens
- Personal profile customization
- Language preference settings (English/Polish)
- Role-based access control (Patient, Therapist, Admin)

### 🚀 12 Enhanced Features

#### 1. **🎤 Voice Recording for Pronunciation Practice**
Record your pronunciation attempts using your device's microphone. The system stores recordings for later review and evaluation.

**Benefits:**
- Practice at your own pace
- Review past attempts
- Track pronunciation improvement
- Get feedback from therapists

#### 2. **🖼️ Image-Based Word Recognition**
Visual learning through high-quality images paired with word exercises.

**Benefits:**
- Enhanced memory association
- Visual context for better learning
- Suitable for various aphasia types
- Engaging and interactive

#### 3. **📈 Difficulty Levels (Easy, Medium, Hard)**
Adaptive learning with three difficulty tiers to match your skill level.

**Easy**: Simple, common words and basic sentences
**Medium**: Moderate vocabulary and complex sentences
**Hard**: Advanced words and challenging exercises

#### 4. **🎮 Gamification System**
Stay motivated with game-like elements:

- **Points**: Earn points based on accuracy and difficulty
- **Badges**: Unlock achievements (First Session, Week Streak, Month Streak, Perfectionist, Dedicated, Master)
- **Streaks**: Build daily practice habits with streak tracking
- **Leaderboards**: (Admin view) See platform-wide progress

#### 5. **📊 Progress Analytics Dashboard**
Visualize your improvement with:

- Interactive line charts showing accuracy over time
- Total sessions completed
- Average accuracy percentage
- Total practice time
- Streak information
- Badge collection display

#### 6. **🔊 Audio Playback for Pronunciation**
Listen to correct pronunciations before attempting exercises.

**Features:**
- Native speaker recordings
- Slow/normal speed options
- Repeat playback
- Multi-language support

#### 7. **🌙 Dark Mode Theme**
Eye-friendly dark theme for comfortable extended use.

**Features:**
- Smooth theme transitions
- Persistent preference saving
- Reduced eye strain
- Better contrast ratios
- Toggle with one click

#### 8. **📅 Session Scheduling System**
Plan your therapy sessions in advance.

**Features:**
- Calendar integration
- Set preferred time and date
- Reminder notifications (upcoming)
- View all scheduled sessions
- Manage and reschedule easily

#### 9. **📄 Export Progress Reports (PDF/CSV)**
Generate comprehensive reports for therapists or personal records.

**CSV Export**: Detailed data for spreadsheet analysis
**PDF Export**: Professional formatted reports

**Report Contents:**
- Session history
- Accuracy trends
- Time spent practicing
- Points and achievements
- Exercise breakdown by type

#### 10. **👨‍⚕️ Admin Dashboard for Therapists**
Comprehensive tools for healthcare professionals.

**Features:**
- Platform-wide statistics
- Patient management
- View all user progress
- Activate/deactivate accounts
- Monitor engagement metrics
- Export patient reports

#### 11. **📱 Offline Mode (Progressive Web App)**
Practice even without internet connection.

**Features:**
- Install to home screen
- Offline caching
- Background synchronization
- App-like experience
- No app store required

#### 12. **🎙️ Speech-to-Text Evaluation**
Automatic pronunciation accuracy assessment.

**Features:**
- Real-time transcription
- Accuracy scoring
- Confidence metrics
- Multi-language support (EN/PL)
- Detailed feedback

---

## 📸 Screenshots

### Login & Dashboard
```
┌─────────────────────────────────────┐
│  🗣️ Aphasia Therapy        🌙 EN ⚙️ │
├─────────────────────────────────────┤
│                                     │
│     Welcome to Aphasia Therapy      │
│   Interactive speech therapy        │
│           exercises                 │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Username: ____________      │   │
│  │ Password: ____________      │   │
│  │                             │   │
│  │      [Login Button]         │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### Dashboard View
```
┌─────────────────────────────────────┐
│ Dashboard                           │
├─────────────────────────────────────┤
│ ⭐ Points  🔥 Streak  🏆 Badges     │
│    1,250       14        6          │
├─────────────────────────────────────┤
│ Start New Session                   │
│ Type: [Word Naming ▼]               │
│ Difficulty: [Medium ▼]              │
│ Exercises: [10]                     │
│ [Start]                             │
├─────────────────────────────────────┤
│ Recent Sessions                     │
│ ✓ Word Naming - Medium | 85%       │
│ ✓ Pronunciation - Easy | 92%       │
│ ✓ Sentence Complete - Hard | 78%   │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Node.js** (optional, for development tools)

### Clone the Repository

```bash
git clone https://github.com/yourusername/aphasia-therapy-app.git
cd aphasia-therapy-app
```

### Start Backend Server

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.template ../.env
# Edit .env and set SECRET_KEY (generate with: openssl rand -hex 32)

# Run the server
python -m app.main
```

The API will be available at: **http://localhost:8000**

### Start Frontend Server

```bash
# Open a new terminal
cd frontend

# Serve with Python's built-in server
python -m http.server 3000

# Or use Node.js
npx serve -p 3000
```

The app will be available at: **http://localhost:3000**

### Access the Application

1. Open your browser and navigate to **http://localhost:3000**
2. Click "Register" to create a new account
3. Log in with your credentials
4. Start your first therapy session!

---

## 📥 Installation

### Method 1: Docker (Recommended for Production)

```bash
# Make sure Docker and Docker Compose are installed

# Start all services
docker-compose up --build

# The application will be available at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Method 2: Manual Installation

#### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp ../.env.template ../.env
   ```

   Edit `.env` and configure:
   ```env
   SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
   DATABASE_URL=sqlite:///./aphasia_app.db
   BACKEND_CORS_ORIGINS=http://localhost:3000
   ```

4. **Run Server**
   ```bash
   python -m app.main
   ```

#### Frontend Setup

1. **Navigate to Frontend**
   ```bash
   cd frontend
   ```

2. **Serve Static Files**
   ```bash
   # Option 1: Python
   python -m http.server 3000

   # Option 2: Node.js
   npx serve -p 3000
   ```

---

## 💡 Usage

### For Patients

#### 1. **Create an Account**
- Click "Register" on the login page
- Fill in your email, username, and password
- Select your preferred language (English or Polish)
- Click "Register"

#### 2. **Start a Therapy Session**
- From the dashboard, select "Start New Session"
- Choose exercise type (Word Naming, Sentence Completion, etc.)
- Select difficulty level (Easy, Medium, or Hard)
- Set number of exercises (5-50)
- Click "Start"

#### 3. **Complete Exercises**
- Read the question carefully
- For multiple choice: Click the correct answer
- For text input: Type your answer
- For pronunciation: Click the record button and speak
- Click "Submit" when ready
- Get immediate feedback

#### 4. **Track Your Progress**
- Click "Progress" in the navigation menu
- View your statistics and charts
- See earned badges
- Export reports for your therapist

#### 5. **Schedule Future Sessions**
- Click "Add Schedule" on the dashboard
- Select date and time
- Choose exercise type and difficulty
- Click "Schedule"

### For Therapists/Admins

#### 1. **Access Admin Dashboard**
- Log in with admin credentials
- Click "Admin" in the navigation menu

#### 2. **Monitor Patients**
- View total users and active users
- See platform-wide statistics
- Check individual patient progress

#### 3. **Manage Users**
- View all registered patients
- Activate or deactivate accounts
- Access patient session histories

#### 4. **Generate Reports**
- Export platform statistics
- Download patient progress reports
- Analyze therapy effectiveness

---

## 📚 API Documentation

### Interactive Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

#### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login user |

**Example Login Request:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "total_points": 0,
    "current_streak": 0
  }
}
```

#### Therapy Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/therapy/sessions` | Create new session |
| GET | `/api/v1/therapy/sessions` | List user's sessions |
| GET | `/api/v1/therapy/sessions/{id}` | Get session details |
| GET | `/api/v1/therapy/sessions/{id}/exercises` | Get session exercises |
| POST | `/api/v1/therapy/exercises/{id}/answer` | Submit an exercise's answer (one per exercise; the last one completes the session) |
| POST | `/api/v1/therapy/sessions/{id}/complete` | Get a finished session's result (scored by the server) |

**Example Create Session:**
```json
{
  "title": "Morning Practice",
  "exercise_type": "word_naming",
  "difficulty": "medium",
  "language": "en",
  "num_exercises": 10
}
```

#### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/profile` | Get user profile |
| PUT | `/api/v1/users/profile` | Update profile |
| GET | `/api/v1/users/progress` | Get progress statistics |
| GET | `/api/v1/users/badges` | Get earned badges |
| GET | `/api/v1/users/scheduled-sessions` | Get scheduled sessions |
| POST | `/api/v1/users/scheduled-sessions` | Schedule new session |
| GET | `/api/v1/users/progress/export/csv` | Export CSV report |
| GET | `/api/v1/users/progress/export/pdf` | Export PDF report |

#### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/stats` | Get platform statistics |
| GET | `/api/v1/admin/users` | List all users |
| GET | `/api/v1/admin/users/{id}/sessions` | Get user's sessions |
| PUT | `/api/v1/admin/users/{id}/activate` | Activate user |
| PUT | `/api/v1/admin/users/{id}/deactivate` | Deactivate user |

### Authentication

All endpoints (except register and login) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token-here>
```

---

## 🏗️ Architecture

### Tech Stack

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT tokens with passlib/bcrypt
- **Validation**: Pydantic models
- **Logging**: Structlog
- **Documentation**: OpenAPI/Swagger

#### Frontend
- **HTML5**: Semantic, accessible markup
- **CSS3**: Modern styling with Grid and Flexbox
- **JavaScript**: Vanilla ES6+ with modules
- **PWA**: Service Workers for offline support
- **Charts**: Custom Canvas API implementation
- **Audio**: Web Audio API, MediaRecorder API
- **Speech**: Web Speech API for recognition

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (for frontend)
- **Database**: PostgreSQL (production)
- **Caching**: Service Worker cache

### Project Structure

```
aphasia-therapy-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/  # API route handlers
│   │   │       │   ├── auth.py
│   │   │       │   ├── therapy.py
│   │   │       │   ├── users.py
│   │   │       │   └── admin.py
│   │   │       └── schemas.py  # Pydantic models
│   │   ├── core/               # Core utilities
│   │   │   ├── config.py       # Settings
│   │   │   ├── security.py     # Auth logic
│   │   │   └── logging.py      # Logging config
│   │   ├── db/                 # Database layer
│   │   │   ├── database.py     # DB connection
│   │   │   └── models.py       # SQLAlchemy models
│   │   └── main.py             # Application entry
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Static frontend
│   ├── css/
│   │   ├── styles.css          # Main styles
│   │   └── dark-mode.css       # Dark theme
│   ├── js/
│   │   ├── api.js              # API client
│   │   ├── i18n.js             # Translations
│   │   ├── chart.js            # Charts
│   │   ├── audio.js            # Audio handling
│   │   ├── ui.js               # UI management
│   │   └── app.js              # Main app
│   ├── index.html              # Single-page app
│   ├── manifest.json           # PWA manifest
│   ├── sw.js                   # Service worker
│   ├── nginx.conf
│   └── Dockerfile
├── docs/                       # Documentation
│   ├── USER_GUIDE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── docker-compose.yml
├── .env.template
├── .gitignore
├── README.md                   # This file
└── README.pl.md               # Polish version
```

### Database Schema

```mermaid
erDiagram
    USER ||--o{ THERAPY_SESSION : has
    USER ||--o{ USER_BADGE : earns
    USER ||--o{ SCHEDULED_SESSION : schedules
    USER ||--o{ PROGRESS : tracks
    THERAPY_SESSION ||--o{ EXERCISE : contains
    EXERCISE ||--o{ AUDIO_RECORDING : has

    USER {
        int id PK
        string email
        string username
        string hashed_password
        string role
        int total_points
        int current_streak
    }

    THERAPY_SESSION {
        int id PK
        int user_id FK
        string title
        string exercise_type
        string difficulty
        float score
        bool is_completed
    }

    EXERCISE {
        int id PK
        int session_id FK
        string question
        string correct_answer
        string user_answer
        bool is_correct
    }
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory (use `.env.template` as a reference):

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./aphasia_app.db
# Production: postgresql://user:password@localhost/aphasia_db

# CORS (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=./uploads

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@aphasia-therapy.app
```

### Database Configuration

#### Development (SQLite)
```env
DATABASE_URL=sqlite:///./aphasia_app.db
```

#### Production (PostgreSQL)
```env
DATABASE_URL=postgresql://username:password@localhost:5432/aphasia_db
```

### CORS Configuration

Add your frontend URL to allowed origins:

```env
BACKEND_CORS_ORIGINS=http://localhost:3000,https://yourapp.com
```

---

## 🚢 Deployment

### Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aphasia-therapy-app.git
   cd aphasia-therapy-app
   ```

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with production values
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://your-domain.com
   - Backend: http://your-domain.com:8000

### Manual Deployment

#### Backend (FastAPI)

1. **Set up server** (Ubuntu/Debian example)
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv postgresql nginx
   ```

2. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/aphasia-therapy-app.git
   cd aphasia-therapy-app/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure PostgreSQL**
   ```bash
   sudo -u postgres createdb aphasia_db
   sudo -u postgres createuser aphasia_user
   # Set password and grant privileges
   ```

4. **Run with systemd**
   Create `/etc/systemd/system/aphasia-api.service`:
   ```ini
   [Unit]
   Description=Aphasia Therapy API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/path/to/aphasia-therapy-app/backend
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable aphasia-api
   sudo systemctl start aphasia-api
   ```

#### Frontend (Nginx)

1. **Configure Nginx**
   Create `/etc/nginx/sites-available/aphasia-therapy`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       root /path/to/aphasia-therapy-app/frontend;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/aphasia-therapy /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Set up SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Production Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Use strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper CORS origins
- [ ] Set up backup strategy
- [ ] Configure monitoring and logging
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CDN for static assets

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/aphasia-therapy-app.git
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write meaningful commit messages
- Add tests for new features
- Run `scripts/check.sh` before you commit; it must pass
- Update documentation

### Pull Request Process

1. Update the README.md with details of changes
2. Update the documentation if needed
3. Ensure all tests pass
4. Get approval from maintainers
5. Squash commits before merging

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain professional communication

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Aphasia Therapy App

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 💬 Support

### Getting Help

- **Documentation**: Check the [docs](docs/) folder
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/aphasia-therapy-app/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/yourusername/aphasia-therapy-app/discussions)

### Contact

- **Email**: support@aphasia-therapy.app
- **Website**: https://aphasia-therapy.app
- **Twitter**: @AphasiaTherapy

---

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- Speech therapy professionals who provided guidance
- Open source community for valuable tools
- All contributors and supporters

---

## 📊 Project Status

- ✅ **Version**: 1.0.0
- ✅ **Status**: Production Ready
- ✅ **Last Updated**: 2024
- ✅ **Maintained**: Yes

---

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Video therapy sessions
- [ ] Group therapy rooms
- [ ] Mobile native apps
- [ ] Enhanced AI speech analysis

### Version 1.2 (Future)
- [ ] Custom exercise creation
- [ ] Family/caregiver portal
- [ ] Multi-language content expansion
- [ ] EHR integration

---

## 📈 Statistics

- **Languages**: Python, JavaScript, HTML, CSS
- **Backend**: FastAPI, SQLAlchemy
- **Frontend**: Vanilla JS, Web APIs
- **Database**: PostgreSQL, SQLite
- **Deployment**: Docker, Nginx

---

**Made with ❤️ for the aphasia community**

[⬆ Back to top](#-aphasia-speech-therapy-app)
