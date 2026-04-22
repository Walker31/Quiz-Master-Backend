# 🎯 Quick Seed Command Reference

## One Command to Seed Everything

```bash
python manage.py seed_all
```

That's it! This single command creates:

### Users & Access
- ✅ Admin account (admin / admin123)
- ✅ 3 test students
- ✅ JEE 2026 Batch A (all students enrolled)

### Content
- ✅ 4 Subjects: Math, Physics, CS, Chemistry
- ✅ 18 Chapters across all subjects
- ✅ ~50 sample MCQ questions with 4 options each
- ✅ 1 Published Quiz with all sections
- ✅ Quiz assigned to batch

### Settings
- ✅ Auto-applies all migrations
- ✅ Idempotent (safe to run multiple times)
- ✅ Ready for development/testing

---

## Login Credentials

```
Admin:
  Username: admin
  Password: admin123

Students:
  testuser / testpass123
  student1 / student123
  student2 / student123
```

---

## What Gets Created

```
Admin User
 └─ SUPERADMIN (full access)

Students (3)
 └─ STUDENT role
 └─ Enrolled in JEE 2026 Batch A

Exam Type
 └─ JEE Mains

Subjects (4)
 ├─ Mathematics (4 chapters)
 ├─ Physics (5 chapters)
 ├─ Computer Science (4 chapters)
 └─ Chemistry (3 chapters)

Questions (~50)
 ├─ Type: MCQ Single Correct
 ├─ Difficulty: Medium
 ├─ Each has 4 options (A-D)
 └─ Option A = Correct answer

Quiz
 ├─ Title: JEE Mains Mock Test 01
 ├─ Duration: 180 minutes
 ├─ Sections: 4 (one per subject)
 ├─ Questions: ~34 linked
 └─ Assigned to: JEE 2026 Batch A
```

---

## After Seeding

### Start Development Server
```bash
python manage.py runserver
# Access at http://localhost:8000
```

### Admin Panel
```
http://localhost:8000/admin/
Login with admin credentials
```

### Test the API
```bash
# Get all quizzes
curl http://localhost:8000/api/v1/quiz/

# Get all subjects
curl http://localhost:8000/api/v1/subjects/

# Get all questions
curl http://localhost:8000/api/v1/questions/
```

---

## When to Use

✅ **Use seed_all when:**
- Starting fresh development
- Resetting test database
- Demo/presentation setup
- Testing with sample data

❌ **Don't use when:**
- Production deployment (create users manually)
- You have real user data
- You want to preserve existing data

---

## Troubleshooting

**Error: "relation quizzes_quiz does not exist"**
→ Migrations are auto-applied; should be resolved on next run

**Error: "column doesn't exist"**
→ Ensure `.env` PostgreSQL credentials are correct

**Users already exist?**
→ Script is idempotent; it won't recreate them

**Need to reset?**
```bash
# Delete all data and recreate
python manage.py migrate zero  # Rollback
python manage.py migrate       # Re-apply
python manage.py seed_all      # Re-seed
```

---

## Documentation Links

- 📖 [SEED_GUIDE.md](SEED_GUIDE.md) - Detailed seeding guide
- 📋 [QUICKREF.md](QUICKREF.md) - API quick reference
- 📚 [README.md](README.md) - Full documentation
- 🔌 [FRONTEND_API_GUIDE.md](FRONTEND_API_GUIDE.md) - Frontend integration

---

**Created:** April 22, 2026  
**Command:** `python manage.py seed_all`  
**Status:** ✅ Production Ready
