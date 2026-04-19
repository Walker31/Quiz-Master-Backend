# QuizMaster Backend - Quick Reference

## Quick Test (No Auth Needed!)

```bash
# Get all subjects
curl http://localhost:8000/api/quizzes/subjects/

# Get math questions (subject 1)
curl "http://localhost:8000/api/quizzes/questions/?subject=1"

# Get hard questions (difficulty 7)
curl "http://localhost:8000/api/quizzes/questions/?difficulty=7"

# Get all questions (190 total)
curl http://localhost:8000/api/quizzes/questions/
```
```bash
# Setup
cd /home/walker/Projects/QuizMaster/Backend
source venv/bin/activate
pip install -r requirements.txt

# Configure .env with PostgreSQL credentials
nano .env

# Run migrations and seed data
python manage.py migrate
python manage.py shell < seed_subjects.py
python manage.py seed_questions

# Start server
python manage.py runserver
# OR with Uvicorn
uvicorn quizMaster.asgi:application --host 0.0.0.0 --port 8000
```

## API Quick Reference

### Base URL: `http://localhost:8000/api/`

### Public Endpoints (No Auth Required!)
- `GET /quizzes/subjects/` - List all subjects
- `GET /quizzes/chapters/` - List all chapters
- `GET /quizzes/quizzes/` - List all quizzes
- `GET /quizzes/quizzes/live/` - Get live quizzes
- `GET /quizzes/questions/` - List all questions (190 total)
- `GET /quizzes/questions/?subject=1` - Questions for subject
- `GET /quizzes/questions/?chapter=5` - Questions for chapter
- `GET /quizzes/questions/?difficulty=7` - Questions by difficulty
- `GET /quizzes/questions/?quiz=1` - Questions for quiz

### Authentication Endpoints
- `POST /auth/signup/` - Register user
- `POST /auth/signin/` - Login user
- `GET /auth/me/` - Get current user (auth required)
- `POST /token/refresh/` - Refresh access token

### Query Parameters
```
/quizzes/questions/
  ?quiz=1                 # Filter by quiz ID (ignores 'undefined')
  &difficulty=7           # Filter by difficulty (1-10)
  &chapter=5              # Filter by chapter
  &subject=1              # Filter by subject
  
# All params optional and validate safely
# Invalid values like 'undefined' or 'abc' are ignored
```

## Database Structure

### 5 Subjects
1. Mathematics (4 chapters, 8 quizzes, 40 questions)
2. Physics (5 chapters, 10 quizzes, 50 questions)
3. Computer Science (4 chapters, 8 quizzes, 40 questions)
4. Chemistry (3 chapters, 6 quizzes, 30 questions)
5. English Literature (3 chapters, 6 quizzes, 30 questions)

### Total Statistics
- **Subjects:** 5
- **Chapters:** 19
- **Quizzes:** 38
- **Questions:** 190 (JEE-level with difficulty 1-10)
- **Users:** 2 (test + admin)

## Test Credentials
```
Username: testuser
Password: testpass123

Admin Username: admin
Admin Password: admin123
```

## Difficulty Levels
- **1-3:** Very Easy to Easy (Fundamentals)
- **4-5:** Medium (Standard difficulty)
- **6-7:** Hard to Very Hard (Advanced)
- **8-9:** Extremely Hard to JEE Advanced
- **10:** Expert Level

## Key Models

### Question Model
```python
quiz           # ForeignKey to Quiz
chapter        # ForeignKey to Chapter
subject        # ForeignKey to Subject
question_statement  # TextField
option_1/2/3/4     # TextFields
correct_option     # Integer (1-4)
difficulty_level   # Integer (1-10)
created_at/updated_at  # DateTime
```

### JWT Configuration
- Access Token Lifetime: 30 minutes
- Refresh Token Lifetime: 1 day
- Auth Header Type: Bearer

## Useful Commands

```bash
# Django Shell
python manage.py shell

# Check database
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# List all URLs
python manage.py show_urls

# Check for issues
python manage.py check

# Create superuser
python manage.py createsuperuser

# Seed commands
python manage.py shell < seed_subjects.py  # Load initial data
python manage.py seed_questions             # Load JEE questions
python manage.py seed_data                  # Load dummy data
```

## Common Responses

### Success (200/201)
```json
{
  "id": 1,
  "field": "value"
}
```

### Errors
- **400:** Bad Request (validation error)
- **401:** Unauthorized (missing token)
- **403:** Forbidden (insufficient permissions)
- **404:** Not Found
- **500:** Server Error

## Environment Variables
```env
DJANGO_SECRET_KEY      # Secret key for sessions
DJANGO_DEBUG          # True for dev, False for prod
DJANGO_ALLOWED_HOSTS  # Comma-separated hosts

POSTGRES_DB           # Database name
POSTGRES_USER         # Database user
POSTGRES_PASSWORD     # Database password
POSTGRES_HOST         # Database host (localhost)
POSTGRES_PORT         # Database port (5432)
```

## File Structure
```
Backend/
├── README.md                      # Full documentation
├── QUICKREF.md                    # This file
├── requirements.txt               # Dependencies
├── manage.py                      # Django CLI
├── .env                          # Configuration
├── seed_subjects.py              # Initial data script
├── quizMaster/                   # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── users/                        # Authentication
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
└── quizzes/                      # Quizzes & questions
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    └── management/commands/
        ├── seed_data.py
        └── seed_questions.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PostgreSQL connection failed | Check `.env` credentials |
| "Field 'id' expected a number but got 'undefined'" | Fixed - backend now ignores invalid params |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Port 8000 in use | Use `--port 8001` or kill the process |
| No database | Run `python manage.py migrate` |
| No data | Run seeding commands |
| Token invalid | Check token expiry (30 min), use refresh endpoint |

---
**Last Updated:** April 19, 2026
