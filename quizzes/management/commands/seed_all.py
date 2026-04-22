from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Batch
from apps.content.models import ExamType, Subject, Chapter, Question, QuestionOption
from apps.quiz.models import Quiz, QuizSection, QuizQuestion, QuizAssignment


class Command(BaseCommand):
    help = "Seed admin, users, subjects, chapters, questions, quizzes, and assignments"

    SUBJECTS_DATA = [
        {
            "name": "Mathematics",
            "code": "MATH",
            "chapters": [
                "Algebra",
                "Calculus",
                "Geometry",
                "Statistics",
            ],
        },
        {
            "name": "Physics",
            "code": "PHY",
            "chapters": [
                "Mechanics",
                "Thermodynamics",
                "Electromagnetism",
                "Optics",
                "Modern Physics",
            ],
        },
        {
            "name": "Computer Science",
            "code": "CS",
            "chapters": [
                "Data Structures",
                "Algorithms",
                "Databases",
                "Operating Systems",
            ],
        },
        {
            "name": "Chemistry",
            "code": "CHEM",
            "chapters": [
                "Organic Chemistry",
                "Inorganic Chemistry",
                "Physical Chemistry",
            ],
        },
    ]

    USERS_DATA = [
        {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "role": "STUDENT",
        },
        {
            "username": "student1",
            "email": "student1@example.com",
            "first_name": "Aarav",
            "last_name": "Sharma",
            "password": "student123",
            "role": "STUDENT",
        },
        {
            "username": "student2",
            "email": "student2@example.com",
            "first_name": "Ananya",
            "last_name": "Rao",
            "password": "student123",
            "role": "STUDENT",
        },
    ]

    def handle(self, *args, **options):
        user_model = get_user_model()
        now = timezone.now()

        self.stdout.write(self.style.NOTICE("Applying migrations..."))
        call_command("migrate", interactive=False, verbosity=0)

        with transaction.atomic():
            self.stdout.write(self.style.NOTICE("Seeding admin and users..."))
            admin_user, admin_created = user_model.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@example.com",
                    "first_name": "Admin",
                    "last_name": "User",
                    "is_staff": True,
                    "is_superuser": True,
                    "role": "SUPERADMIN",
                    "is_verified": True,
                },
            )
            if admin_created:
                admin_user.set_password("admin123")
                admin_user.save()
            else:
                updated = []
                if not admin_user.is_staff:
                    admin_user.is_staff = True
                    updated.append("is_staff")
                if not admin_user.is_superuser:
                    admin_user.is_superuser = True
                    updated.append("is_superuser")
                if getattr(admin_user, "role", None) != "SUPERADMIN":
                    admin_user.role = "SUPERADMIN"
                    updated.append("role")
                if hasattr(admin_user, "is_verified") and not admin_user.is_verified:
                    admin_user.is_verified = True
                    updated.append("is_verified")
                if updated:
                    admin_user.save(update_fields=updated)

            self.stdout.write(self.style.SUCCESS("Admin ready: admin / admin123"))

            created_users = 0
            students = []
            for user_data in self.USERS_DATA:
                user, created = user_model.objects.get_or_create(
                    username=user_data["username"],
                    defaults={
                        "email": user_data["email"],
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"],
                        "role": user_data["role"],
                        "is_verified": True,
                    },
                )
                if created:
                    user.set_password(user_data["password"])
                    user.save()
                    created_users += 1
                students.append(user)

            self.stdout.write(self.style.SUCCESS(f"Users ready (new): {created_users}"))

            batch, _ = Batch.objects.get_or_create(
                code="JEE26-A",
                defaults={
                    "name": "JEE 2026 Batch A",
                    "admin": admin_user,
                    "start_date": date.today(),
                },
            )
            if batch.admin_id != admin_user.id:
                batch.admin = admin_user
                batch.save(update_fields=["admin"])
            for student in students:
                batch.students.add(student)

            self.stdout.write(self.style.SUCCESS("Batch ready: JEE 2026 Batch A"))

            exam, _ = ExamType.objects.get_or_create(
                slug="jee-mains",
                defaults={
                    "name": "JEE Mains",
                    "description": "National level engineering entrance exam.",
                    "is_active": True,
                },
            )

            created_subjects = 0
            created_chapters = 0
            created_questions = 0
            subjects = []

            for subject_index, subject_data in enumerate(self.SUBJECTS_DATA):
                subject, subject_created = Subject.objects.get_or_create(
                    exam_type=exam,
                    name=subject_data["name"],
                    defaults={
                        "code": subject_data["code"],
                        "order": subject_index,
                    },
                )
                if subject_created:
                    created_subjects += 1
                subjects.append(subject)

                for chapter_index, chapter_name in enumerate(subject_data["chapters"]):
                    chapter, chapter_created = Chapter.objects.get_or_create(
                        subject=subject,
                        name=chapter_name,
                        defaults={"order": chapter_index},
                    )
                    if chapter_created:
                        created_chapters += 1

                    for q_index in range(1, 4):
                        question, question_created = Question.objects.get_or_create(
                            chapter=chapter,
                            text=f"[{subject.name}] {chapter.name} sample question {q_index}: What is the correct option?",
                            defaults={
                                "q_type": "MCQ_SINGLE",
                                "difficulty": "MEDIUM",
                                "marks_correct": 4,
                                "marks_wrong": -1,
                                "marks_partial": 0,
                                "solution": "This is a seeded demo solution.",
                                "created_by": admin_user,
                                "is_verified": True,
                            },
                        )
                        if question_created:
                            created_questions += 1
                            QuestionOption.objects.get_or_create(
                                question=question,
                                label="A",
                                defaults={"text": "Option A", "is_correct": True, "order": 0},
                            )
                            QuestionOption.objects.get_or_create(
                                question=question,
                                label="B",
                                defaults={"text": "Option B", "is_correct": False, "order": 1},
                            )
                            QuestionOption.objects.get_or_create(
                                question=question,
                                label="C",
                                defaults={"text": "Option C", "is_correct": False, "order": 2},
                            )
                            QuestionOption.objects.get_or_create(
                                question=question,
                                label="D",
                                defaults={"text": "Option D", "is_correct": False, "order": 3},
                            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Subjects new: {created_subjects}, Chapters new: {created_chapters}, Questions new: {created_questions}"
                )
            )

            quiz, quiz_created = Quiz.objects.get_or_create(
                title="JEE Mains Mock Test 01",
                defaults={
                    "exam_type": exam,
                    "created_by": admin_user,
                    "status": "PUBLISHED",
                    "access_type": "BATCH",
                    "start_time": now,
                    "end_time": now + timedelta(days=7),
                    "duration_mins": 180,
                    "shuffle_questions": False,
                    "shuffle_options": False,
                    "show_solution_after": "SUBMIT",
                    "max_attempts": 1,
                    "pass_percentage": 35,
                    "instructions": "Attempt all sections carefully.",
                    "is_proctored": False,
                },
            )

            section_count = 0
            linked_question_count = 0
            for order, subject in enumerate(subjects):
                section, section_created = QuizSection.objects.get_or_create(
                    quiz=quiz,
                    name=f"{subject.name} Section",
                    defaults={
                        "subject": subject,
                        "order": order,
                    },
                )
                if section.subject_id != subject.id:
                    section.subject = subject
                    section.save(update_fields=["subject"])
                if section_created:
                    section_count += 1

                subject_questions = Question.objects.filter(chapter__subject=subject).order_by("id")[:10]
                for q_order, question in enumerate(subject_questions):
                    _, created = QuizQuestion.objects.get_or_create(
                        section=section,
                        question=question,
                        defaults={"order": q_order},
                    )
                    if created:
                        linked_question_count += 1

            QuizAssignment.objects.get_or_create(
                quiz=quiz,
                batch=batch,
                defaults={
                    "assigned_by": admin_user,
                    "is_mandatory": True,
                    "deadline": now + timedelta(days=5),
                },
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Quiz ready: {'created' if quiz_created else 'exists'}, sections new: {section_count}, quiz questions new: {linked_question_count}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
