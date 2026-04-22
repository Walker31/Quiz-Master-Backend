# Unified Seed Script Guide

## Overview

The unified seed command (`python manage.py seed_all`) is a comprehensive one-command solution to populate your database with all required entities for a fully functional QuizMaster instance.

---

## What Gets Seeded

### 1. **Admin User**
- Username: `admin`
- Password: `admin123`
- Role: `SUPERADMIN`
- Permissions: Full access to all admin features

### 2. **Test Students (3)**
- `testuser` (password: `testpass123`)
- `student1` - Aarav Sharma (password: `student123`)
- `student2` - Ananya Rao (password: `student123`)
- Role: `STUDENT`

### 3. **Batch**
- Code: `JEE26-A`
- Name: `JEE 2026 Batch A`
- Admin: `admin`
- Students: All 3 students enrolled

### 4. **Exam Type**
- Name: `JEE Mains`
- Slug: `jee-mains`
- Status: Active

### 5. **Subjects (4)**
1. **Mathematics** (MATH)
   - Algebra
   - Calculus
   - Geometry
   - Statistics

2. **Physics** (PHY)
   - Mechanics
   - Thermodynamics
   - Electromagnetism
   - Optics
   - Modern Physics

3. **Computer Science** (CS)
   - Data Structures
   - Algorithms
   - Databases
   - Operating Systems

4. **Chemistry** (CHEM)
   - Organic Chemistry
   - Inorganic Chemistry
   - Physical Chemistry

**Total: 18 chapters**

### 6. **Questions & Options**
- ~50 sample questions created across all chapters
- Each question has 4 MCQ options (A, B, C, D)
- Option A is marked as correct
- Each question:
  - Type: MCQ Single Correct
  - Difficulty: Medium
  - Marks for correct: 4
  - Marks for wrong: -1
  - Created by: admin

### 7. **Quiz**
- Title: `JEE Mains Mock Test 01`
- Status: `PUBLISHED`
- Access Type: `BATCH`
- Duration: 180 minutes
- Sections: One per subject (4 sections total)
- Quiz Questions: ~34 questions linked (10 per subject)
- Assigned to: `JEE 2026 Batch A`

---

## How to Run

### Quick Start
```bash
# Navigate to backend
cd /home/walker/Projects/QuizMaster/Backend

# Activate virtual environment
source venv/bin/activate

# Run the seed command
python manage.py seed_all
```

### What Happens During Seeding
1. ✅ Auto-applies all pending Django migrations
2. ✅ Creates/updates admin user (superuser)
3. ✅ Creates 3 test students
4. ✅ Creates batch and enrolls students
5. ✅ Creates exam type (JEE Mains)
6. ✅ Creates subjects and chapters
7. ✅ Creates sample questions with options
8. ✅ Creates quiz and links all sections/questions
9. ✅ Assigns quiz to batch

### Expected Output
```
Applying migrations...
Seeding admin and users...
Admin ready: admin / admin123
Users ready (new): 3
Batch ready: JEE 2026 Batch A
Subjects new: 4, Chapters new: 18, Questions new: ~50
Quiz ready: created, sections new: 4, quiz questions new: ~34
Seeding complete.
```

---

## Idempotent Design

The seed command is **idempotent** — you can run it multiple times safely:
- Existing records are not duplicated
- Existing users won't be recreated
- Batch won't be recreated if it exists
- Students are added to batch if not already members
- Questions are linked only if not already in quiz

---

## What's Created for Frontend Use

### Test Login Credentials
```javascript
// Signup works with any new username
// Signin with existing users:
{
  "username": "admin",
  "password": "admin123"
}

{
  "username": "testuser",
  "password": "testpass123"
}

{
  "username": "student1",
  "password": "student123"
}
```

### Available API Endpoints
```
GET  /api/v1/exams/                    # ExamTypes
GET  /api/v1/subjects/                 # Subjects
GET  /api/v1/chapters/                 # Chapters
GET  /api/v1/questions/                # Questions
GET  /api/v1/quiz/                     # Quizzes
GET  /api/v1/quiz/assignments/         # Quiz assignments
POST /api/v1/quiz/{id}/start/          # Start attempt
POST /api/v1/quiz/{id}/submit/         # Submit attempt
```

---

## Architecture Used

The seed uses the **v1 (new) architecture**:
- `apps.accounts.models.User` (custom user with roles)
- `apps.content.models.ExamType`, `Subject`, `Chapter`, `Question`
- `apps.quiz.models.Quiz`, `QuizSection`, `QuizQuestion`, `QuizAssignment`
- `apps.attempt.models.QuizAttempt`, `QuestionResponse`

Legacy tables are not used or required.

---

## Manual Seeding (If Needed)

If you want to seed specific components manually:

### 1. Just create migrations
```bash
python manage.py migrate
```

### 2. Just create admin
```bash
python manage.py createsuperuser
```

### 3. Use legacy seed scripts (deprecated)
```bash
python manage.py shell < seed_subjects.py    # Old v0 script
python manage.py seed_data                   # Old test data
python manage.py seed_questions              # Old question seed
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| PostgreSQL connection error | Check .env file, ensure `POSTGRES_*` env vars are set |
| "UndefinedTable" errors | Migrations weren't applied; command auto-applies them |
| "No module named 'apps...'" | Ensure INSTALLED_APPS in settings.py has those apps |
| Users not created | They may already exist; rerun is idempotent |
| Batch not created | Check admin user was created first |
| Questions not showing | Verify chapters exist; questions link to chapters |

---

## Performance

- **Time**: ~5-10 seconds for complete seeding
- **Database size**: ~5-10 MB after seeding
- **Operations**: ~150 database inserts/updates

---

## Post-Seeding

After seeding, you can:

1. **Test with Frontend**
   ```bash
   # Start backend server
   python manage.py runserver 8000
   
   # Start frontend (in separate terminal)
   cd ../Frontend
   npm start
   ```

2. **Login to Admin Panel**
   ```
   http://localhost:8000/admin/
   Username: admin
   Password: admin123
   ```

3. **Create More Data**
   - Add students via admin
   - Create new quizzes
   - Upload more questions
   - Create more batches

4. **Reset If Needed**
   ```bash
   python manage.py migrate zero    # Rollback all migrations
   python manage.py migrate         # Apply migrations again
   python manage.py seed_all        # Re-seed everything
   ```

---

## Questions?

Refer to:
- [README.md](README.md) - Full documentation
- [QUICKREF.md](QUICKREF.md) - Quick reference
- [FRONTEND_API_GUIDE.md](FRONTEND_API_GUIDE.md) - Frontend integration
