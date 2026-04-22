# QuizMaster Backend - API Documentation

## Overview
QuizMaster is a comprehensive quiz platform backend built with Django REST Framework, featuring JWT authentication, PostgreSQL integration, and multi-subject quiz management with JEE-level questions.

**Version:** 1.0.0  
**Last Updated:** April 19, 2026  
**Python:** 3.14+  
**Django:** 6.0.4  

---

## Table of Contents
1. [Project Setup](#project-setup)
2. [Database Configuration](#database-configuration)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Models](#models)
6. [Authentication](#authentication)
7. [Management Commands](#management-commands)
8. [Testing](#testing)
9. [Deployment](#deployment)

---

## Project Setup

### Prerequisites
- Python 3.14+
- PostgreSQL 12+
- pip/pipenv

### Installation

1. **Clone and navigate to project:**
   ```bash
   cd /home/walker/Projects/QuizMaster/Backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Update `.env` with your PostgreSQL credentials:
     ```env
     DJANGO_SECRET_KEY=your-secret-key-here
     DJANGO_DEBUG=True
     DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

     POSTGRES_DB=quizmaster_db
     POSTGRES_USER=quizmaster_user
     POSTGRES_PASSWORD=your-secure-password
     POSTGRES_HOST=localhost
     POSTGRES_PORT=5432
     ```

5. **Run migrations:**
   ```bash
   ./venv/bin/python manage.py migrate
   ```

6. **Seed database (optional):**
   ```bash
  ./venv/bin/python manage.py seed_all  # Users/admin + subjects/chapters/quizzes + questions + scores
   ```

7. **Create superuser:**
   ```bash
   ./venv/bin/python manage.py createsuperuser
   ```

8. **Run development server:**
   ```bash
   ./venv/bin/python manage.py runserver
   # OR with Uvicorn (ASGI):
   ./venv/bin/uvicorn quizMaster.asgi:application --host 0.0.0.0 --port 8000
   ```

---

## Database Configuration

### PostgreSQL Setup

If PostgreSQL is not already set up:

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE quizmaster_db;
CREATE USER quizmaster_user WITH PASSWORD 'quizmaster_password';
ALTER ROLE quizmaster_user SET client_encoding TO 'utf8';
ALTER ROLE quizmaster_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE quizmaster_user SET default_transaction_deferrable TO on;
ALTER ROLE quizmaster_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE quizmaster_db TO quizmaster_user;
ALTER SCHEMA public OWNER TO quizmaster_user;
GRANT USAGE, CREATE ON SCHEMA public TO quizmaster_user;
\q
```

---

## Architecture

### Tech Stack
- **Framework:** Django 6.0.4
- **API:** Django REST Framework 3.17.1
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** PostgreSQL with psycopg3
- **Server:** Uvicorn 0.44.0 (ASGI)
- **Python Version:** 3.14

### Permission Model
- **Public Read (GET):** Anyone can read subjects, chapters, quizzes, and questions without authentication
- **Protected Write:** Only authenticated staff/admin users can create/edit/delete content
- **User Accounts:** Users must authenticate to access profile, scores, and other user-specific features
- **Admin Panel:** `/admin/` requires superuser authentication

### Project Structure
```
Backend/
├── manage.py                          # Django management script
├── requirements.txt                   # Dependencies
├── .env                              # Environment configuration
├── .env.example                      # Environment template
├── seed_all.py                       # Shell wrapper for unified seed command
├── seed_subjects.py                  # Legacy subject/chapter/quiz seed script
│
├── quizMaster/                       # Main project settings
│   ├── settings.py                  # Django configuration
│   ├── urls.py                      # Project URL routing
│   ├── asgi.py                      # ASGI application
│   └── wsgi.py                      # WSGI application
│
├── users/                            # User authentication app
│   ├── models.py                    # UserProfile model
│   ├── views.py                     # Auth views (SignUp, SignIn, Me)
│   ├── serializers.py               # User serializers
│   ├── urls.py                      # Auth routes
│   ├── admin.py                     # Admin configuration
│   └── migrations/
│
├── quizzes/                          # Quiz management app
│   ├── models.py                    # Quiz-related models
│   ├── views.py                     # ViewSets for API endpoints
│   ├── serializers.py               # Quiz serializers
│   ├── urls.py                      # Quiz routes
│   ├── admin.py                     # Admin configuration
│   ├── management/
│   │   └── commands/
│   │       ├── seed_all.py         # Unified seed command
│   │       ├── seed_data.py        # Seed dummy data command
│   │       └── seed_questions.py   # Seed JEE-level questions
│   └── migrations/
│
├── venv/                             # Virtual environment
└── staticfiles/                      # Static files (admin)
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Authentication Endpoints

#### 1. User Sign Up
- **Endpoint:** `POST /auth/signup/`
- **Description:** Register a new user
- **Permissions:** Allow Any
- **Request Body:**
  ```json
  {
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```
- **Response (201):**
  ```json
  {
    "user": {
      "id": 1,
      "username": "newuser",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tokens": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
  ```

#### 2. User Sign In
- **Endpoint:** `POST /auth/signin/`
- **Description:** Authenticate user and receive JWT tokens
- **Permissions:** Allow Any
- **Request Body:**
  ```json
  {
    "username": "newuser",
    "password": "securepass123"
  }
  ```
- **Response (200):** Same as Sign Up

#### 3. Get Current User
- **Endpoint:** `GET /auth/me/`
- **Description:** Get current authenticated user info
- **Permissions:** IsAuthenticated
- **Headers:** `Authorization: Bearer <access_token>`
- **Response (200):**
  ```json
  {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
  ```

#### 4. Refresh Access Token
- **Endpoint:** `POST /token/refresh/`
- **Description:** Get new access token using refresh token
- **Request Body:**
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```
- **Response (200):**
  ```json
  {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
  ```

### Quiz Endpoints

#### 5. List Subjects
- **Endpoint:** `GET /quizzes/subjects/`
- **Permissions:** Public (no auth required)
- **Response:** Array of subjects with IDs, names, and descriptions

#### 6. List Chapters
- **Endpoint:** `GET /quizzes/chapters/`
- **Permissions:** Public (no auth required)
- **Query Parameters:**
  - `subject`: Filter by subject ID
- **Response:** Array of chapters with related subject info

#### 7. List Quizzes
- **Endpoint:** `GET /quizzes/quizzes/`
- **Permissions:** Public (no auth required)
- **Query Parameters:**
  - `chapter`: Filter by chapter ID
  - `is_live`: Filter by live status (true/false)
- **Response:** Array of quizzes with timing and status

#### 8. Get Live Quizzes
- **Endpoint:** `GET /quizzes/quizzes/live/`
- **Permissions:** Public (no auth required)
- **Response:** Array of currently live quizzes only

#### 9. List Questions
- **Endpoint:** `GET /quizzes/questions/`
- **Permissions:** Public (no auth required)
- **Query Parameters:**
  - `quiz`: Filter by quiz ID (optional, ignores 'undefined')
  - `difficulty`: Filter by difficulty level 1-10 (optional)
  - `chapter`: Filter by chapter ID (optional)
  - `subject`: Filter by subject ID (optional)
- **Note:** All parameters are optional. 'undefined' values are safely ignored.
- **Response:** Array of questions with difficulty levels and relationships
- **Example Response:**
  ```json
  {
    "id": 381,
    "quiz": 1,
    "chapter": 5,
    "subject": "Mathematics",
    "text": "If α and β are roots of x² - 5x + 6 = 0, then α³ + β³ equals...",
    "question_statement": "If α and β are roots of x² - 5x + 6 = 0, then α³ + β³ equals",
    "option_1": "35",
    "option_2": "30",
    "option_3": "25",
    "option_4": "40",
    "options": [
      {"id": 1, "text": "35"},
      {"id": 2, "text": "30"},
      {"id": 3, "text": "25"},
      {"id": 4, "text": "40"}
    ],
    "correct_option": 1,
    "difficulty_level": 4,
    "difficulty_label": "Medium",
    "remarks": "JEE-level question 1 for Algebra (Difficulty: 4/10)",
    "created_at": "2026-04-19T10:30:00Z",
    "updated_at": "2026-04-19T10:30:00Z"
  }
  ```
- **Frontend Fields:**
  - `text`: Alias for question_statement (for frontend compatibility)
  - `options`: Array format of options `[{id, text}, ...]`
  - Individual fields `option_1` through `option_4` also available

#### 10. List Scores
- **Endpoint:** `GET /quizzes/scores/`
- **Description:** Get user scores (all scores if admin, own scores if user)
- **Permissions:** IsAuthenticated
- **Response:** Array of score records with user and quiz details

#### 11. Submit Quiz Score
- **Endpoint:** `POST /quizzes/scores/`
- **Permissions:** IsAuthenticated
- **Request Body:**
  ```json
  {
    "quiz": 1,
    "time_taken": 1200,
    "max_marks": 50,
    "total_scored": 42
  }
  ```
- **Response (201):** Saved score object

---

## Models

### 1. User (Django Built-in)
- Extends: `django.contrib.auth.models.User`
- Fields:
  - `username` (String, unique)
  - `email` (Email)
  - `password` (Hashed)
  - `first_name`, `last_name`
  - `is_staff`, `is_active`, `is_superuser`

### 2. UserProfile
- **Purpose:** Extended user information
- **Fields:**
  - `user` (OneToOne → User)
  - `created_at` (DateTime, auto)
  - `updated_at` (DateTime, auto)
- **Admin:** Registered with search by username/email

### 3. Subject
- **Fields:**
  - `name` (CharField, max 150)
  - `description` (TextField, optional)
  - `created_at`, `updated_at` (DateTime, auto)
- **Relations:** Has many Chapters and Quizzes
- **Subjects in DB:**
  - Mathematics
  - Physics
  - Chemistry
  - Computer Science
  - English Literature

### 4. Chapter
- **Fields:**
  - `subject` (ForeignKey → Subject)
  - `name` (CharField, max 150)
  - `description` (TextField, optional)
  - `created_at`, `updated_at` (DateTime, auto)
- **Relations:** Belongs to Subject, has many Quizzes and Questions
- **Sample Chapters:**
  - Mathematics: Algebra, Calculus, Geometry, Statistics
  - Physics: Mechanics, Thermodynamics, Electromagnetism, Optics, Modern Physics
  - Chemistry: Organic, Inorganic, Physical
  - CS: Data Structures, Algorithms, Databases, OS
  - English: Shakespeare, Modern Fiction, Poetry

### 5. Quiz
- **Fields:**
  - `chapter` (ForeignKey → Chapter)
  - `subject` (ForeignKey → Subject)
  - `quiz_title` (CharField, max 150)
  - `date_of_quiz` (DateTime)
  - `time_duration` (Integer, in minutes)
  - `remarks` (TextField, optional)
  - `is_live` (Boolean, default False)
  - `created_at`, `updated_at` (DateTime, auto)
- **Relations:** Has many Questions and Scores
- **Total:** 38 quizzes (2 per chapter)

### 6. Question
- **Fields:**
  - `quiz` (ForeignKey → Quiz)
  - `chapter` (ForeignKey → Chapter, optional but recommended)
  - `subject` (ForeignKey → Subject, optional but recommended)
  - `question_statement` (TextField)
  - `option_1`, `option_2`, `option_3`, `option_4` (TextField)
  - `correct_option` (Integer: 1, 2, 3, or 4)
  - `difficulty_level` (Integer: 1-10)
  - `remarks` (TextField, optional)
  - `created_at`, `updated_at` (DateTime, auto)
- **Difficulty Levels:**
  - 1-3: Easy (Basic concepts)
  - 4-5: Medium (Standard difficulty)
  - 6-7: Hard (Advanced topics)
  - 8-9: Very Hard (Expert level)
  - 10: Expert Level (Competitive exams)
- **Indexes:** On (subject, difficulty_level) and (chapter, difficulty_level)
- **Ordering:** By quiz and difficulty level
- **Total:** 190 questions with JEE-level content

### 7. Score
- **Fields:**
  - `quiz` (ForeignKey → Quiz)
  - `user` (ForeignKey → User)
  - `time_taken` (Integer, in seconds, optional)
  - `max_marks` (Integer)
  - `total_scored` (Integer)
  - `created_at`, `updated_at` (DateTime, auto)
- **Relations:** User scores on quizzes
- **Permissions:** Users can view only their scores; staff can view all

---

## Authentication

### JWT Token Flow

1. **User Signs Up/In** → Receives `access` and `refresh` tokens
2. **Include Access Token** in requests:
   ```
   Authorization: Bearer <access_token>
   ```
3. **Access Token Expires** in 30 minutes
4. **Refresh Token Expires** in 1 day
5. **Refresh Access Token** using `POST /api/token/refresh/`

### Default Test Credentials (after seeding)
- **Username:** `testuser`
- **Password:** `testpass123`
- **Admin Username:** `admin`
- **Admin Password:** `admin123`

### Token Configuration (in settings.py)
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## Management Commands

### 1. Unified Seed (Recommended)
```bash
./venv/bin/python manage.py seed_all
```
**Creates:**
- Admin user (username: admin, password: admin123)
- Test/sample users and profiles
- 5 subjects, 19 chapters, and chapter quizzes
- JEE-level questions via `seed_questions`
- Sample scores for test user
- Idempotent (safe to run multiple times)

### 2. Seed Subjects, Chapters, and Quizzes (Legacy)
```bash
./venv/bin/python manage.py shell < seed_subjects.py
```
**Creates:**
- 5 subjects
- 19 chapters
- 38 quizzes
- Idempotent (won't duplicate)

### 3. Seed Test Data
```bash
./venv/bin/python manage.py seed_data
```
**Creates:**
- Test user (username: testuser, password: testpass123)
- Admin user (username: admin, password: admin123)
- Sample subjects, chapters, quizzes, questions, and scores

### 4. Seed JEE-Level Questions
```bash
./venv/bin/python manage.py seed_questions
```
**Creates:**
- 190 JEE-level questions across all quizzes
- Assigns difficulty levels (1-10) per chapter
- Links questions to subject and chapter
- Replaces existing questions if any

**Difficulty Assignment by Chapter:**
- Algebra: Level 6 (Hard)
- Calculus: Level 7 (Very Hard)
- Geometry: Level 5 (Medium-Hard)
- Statistics: Level 4 (Medium)
- Mechanics: Level 7 (Very Hard)
- Thermodynamics: Level 6 (Hard)
- Electromagnetism: Level 8 (Extremely Hard)
- Optics: Level 6 (Hard)
- Modern Physics: Level 9 (JEE Advanced)
- And more...

---

## Testing

### Manual API Testing

1. **Get All Subjects (no auth needed):**
   ```bash
   curl -X GET http://localhost:8000/api/quizzes/subjects/
   ```

2. **Get Questions by Subject (no auth needed):**
   ```bash
   curl -X GET "http://localhost:8000/api/quizzes/questions/?subject=1"
   ```

3. **Get Questions by Chapter (no auth needed):**
   ```bash
   curl -X GET "http://localhost:8000/api/quizzes/questions/?chapter=5"
   ```

4. **Get Questions by Difficulty (no auth needed):**
   ```bash
   curl -X GET "http://localhost:8000/api/quizzes/questions/?difficulty=7"
   ```

5. **Get All Questions (no auth needed):**
   ```bash
   curl -X GET http://localhost:8000/api/quizzes/questions/
   ```

6. **Sign Up (create account):**
   ```bash
   curl -X POST http://localhost:8000/api/auth/signup/ \
     -H "Content-Type: application/json" \
     -d '{"username":"newuser","email":"user@example.com","password":"securepass123"}'
   ```

7. **Sign In (get JWT token):**
   ```bash
   curl -X POST http://localhost:8000/api/auth/signin/ \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass123"}'
   ```

8. **Get Current User (auth required):**
   ```bash
   curl -X GET http://localhost:8000/api/auth/me/ \
     -H "Authorization: Bearer <access_token>"
   ```

### Using Django Shell
```bash
./venv/bin/python manage.py shell
```
```python
from quizzes.models import Question, Quiz
from django.contrib.auth.models import User

# Check questions
qs = Question.objects.filter(difficulty_level__gte=6)
print(f"Hard questions: {qs.count()}")

# Check user
user = User.objects.get(username='testuser')
print(f"User: {user.username} ({user.email})")

# Check quiz questions
quiz = Quiz.objects.first()
print(f"Quiz: {quiz.quiz_title}")
print(f"Questions: {quiz.questions.count()}")
```

---

## Deployment

### Production Checklist

1. **Update .env:**
   ```env
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=<generate-strong-key>
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   POSTGRES_PASSWORD=<strong-password>
   ```

2. **Run migrations:**
   ```bash
   ./venv/bin/python manage.py migrate
   ```

3. **Collect static files:**
   ```bash
   ./venv/bin/python manage.py collectstatic --noinput
   ```

4. **Start with Gunicorn (recommended):**
   ```bash
   pip install gunicorn
   gunicorn --workers 4 --bind 0.0.0.0:8000 quizMaster.wsgi:application
   ```

5. **Or Uvicorn (for ASGI):**
   ```bash
   ./venv/bin/uvicorn quizMaster.asgi:application --host 0.0.0.0 --port 8000 --workers 4
   ```

6. **Setup Nginx as reverse proxy**
7. **Enable HTTPS with SSL certificate**
8. **Configure firewall and security headers**

### Docker Deployment (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.14
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "quizMaster.wsgi:application"]
```

---

## Dependencies

### Core
- `Django==6.0.4`
- `djangorestframework>=3.15`
- `djangorestframework-simplejwt>=5.3`

### Database
- `psycopg[binary]>=3.2` (PostgreSQL driver)

### Server
- `uvicorn>=0.30` (ASGI server)

### Development
- `pytest-django` (for testing)
- `django-extensions` (utilities)

See `requirements.txt` for complete list.

---

## Troubleshooting

### PostgreSQL Connection Error
```
FATAL: password authentication failed for user "quizmaster_user"
```
**Solution:**
1. Verify credentials in `.env`
2. Reset PostgreSQL user password:
   ```sql
   ALTER USER quizmaster_user WITH PASSWORD 'new-password';
   ```

### "Field 'id' expected a number but got 'undefined'" Error
**Cause:** Frontend sending `?quiz=undefined` or similar invalid parameter  
**Solution:** The backend now safely ignores 'undefined' string values
- `?quiz=undefined` → Returns all questions (ignores param)
- `?quiz=abc` → Returns all questions (ignores invalid int)
- `?quiz=1` → Returns only quiz 1's questions (valid)

**Note:** All query parameters are now optional and validate before filtering.

### ModuleNotFoundError: No module named 'rest_framework'
**Solution:**
```bash
./venv/bin/python -m pip install -r requirements.txt
```

### Migration Errors
**Solution:**
```bash
./venv/bin/python manage.py migrate --noinput
```

### Port Already in Use
**Solution:**
```bash
./venv/bin/python manage.py runserver 8001
# OR
./venv/bin/uvicorn quizMaster.asgi:application --port 8001
```

---

## Support & Contact

For issues or questions:
- Check existing API documentation above
- Review Django/DRF official docs
- Check `.env` configuration
- Verify PostgreSQL is running

**Last Updated:** April 19, 2026
**Maintainer:** QuizMaster Development Team
