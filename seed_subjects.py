"""
Seed script to populate QuizMaster with demo subjects, chapters, and quizzes.
Run with: python manage.py shell < seed_subjects.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizMaster.settings')
django.setup()

from quizzes.models import Subject, Chapter, Quiz
from django.utils import timezone
from datetime import timedelta

subjects_data = [
    {
        "name": "Mathematics",
        "description": "Core mathematics covering algebra, calculus, geometry, and statistics.",
        "chapters": [
            {"name": "Algebra", "description": "Equations, inequalities, and polynomial expressions"},
            {"name": "Calculus", "description": "Derivatives, integrals, and limits"},
            {"name": "Geometry", "description": "Shapes, areas, volumes, and coordinate geometry"},
            {"name": "Statistics", "description": "Mean, median, mode, probability, and distributions"},
        ],
    },
    {
        "name": "Physics",
        "description": "Fundamental physics from mechanics to modern physics.",
        "chapters": [
            {"name": "Mechanics", "description": "Newton's laws, motion, energy, and momentum"},
            {"name": "Thermodynamics", "description": "Heat, temperature, entropy, and laws of thermodynamics"},
            {"name": "Electromagnetism", "description": "Electric fields, magnetism, and electromagnetic waves"},
            {"name": "Optics", "description": "Light, reflection, refraction, and wave optics"},
            {"name": "Modern Physics", "description": "Quantum mechanics and relativity"},
        ],
    },
    {
        "name": "Computer Science",
        "description": "Programming concepts, data structures, algorithms, and system design.",
        "chapters": [
            {"name": "Data Structures", "description": "Arrays, linked lists, trees, graphs, and hash tables"},
            {"name": "Algorithms", "description": "Sorting, searching, dynamic programming, and greedy algorithms"},
            {"name": "Databases", "description": "SQL, normalization, indexing, and transactions"},
            {"name": "Operating Systems", "description": "Processes, threads, memory management, and file systems"},
        ],
    },
    {
        "name": "Chemistry",
        "description": "Organic, inorganic, and physical chemistry fundamentals.",
        "chapters": [
            {"name": "Organic Chemistry", "description": "Hydrocarbons, functional groups, and reaction mechanisms"},
            {"name": "Inorganic Chemistry", "description": "Periodic table, bonding, and coordination compounds"},
            {"name": "Physical Chemistry", "description": "Thermodynamics, kinetics, and electrochemistry"},
        ],
    },
    {
        "name": "English Literature",
        "description": "Classic and modern literature, poetry, and critical analysis.",
        "chapters": [
            {"name": "Shakespeare", "description": "Plays, sonnets, and literary analysis of Shakespeare's works"},
            {"name": "Modern Fiction", "description": "20th and 21st century novels and short stories"},
            {"name": "Poetry", "description": "Poetic forms, analysis, and major poets"},
        ],
    },
]

now = timezone.now()
quiz_counter = 0

for s_data in subjects_data:
    subject, created = Subject.objects.get_or_create(
        name=s_data["name"],
        defaults={"description": s_data["description"]},
    )
    action = "Created" if created else "Exists"
    print(f"  {action}: Subject '{subject.name}'")

    for ch_data in s_data["chapters"]:
        chapter, created = Chapter.objects.get_or_create(
            subject=subject,
            name=ch_data["name"],
            defaults={"description": ch_data["description"]},
        )
        action = "Created" if created else "Exists"
        print(f"    {action}: Chapter '{chapter.name}'")

        # Create 1-2 quizzes per chapter if none exist
        if chapter.quizzes.count() == 0:
            for i in range(1, 3):
                quiz_counter += 1
                Quiz.objects.create(
                    chapter=chapter,
                    subject=subject,
                    quiz_title=f"{chapter.name} Quiz {i}",
                    date_of_quiz=now + timedelta(days=quiz_counter),
                    time_duration=15 + (quiz_counter % 3) * 5,
                    remarks=f"Auto-generated quiz for {chapter.name}",
                    is_live=(quiz_counter % 3 == 0),
                )
            print(f"      Created 2 quizzes for '{chapter.name}'")

print(f"\nDone! Total: {Subject.objects.count()} subjects, {Chapter.objects.count()} chapters, {Quiz.objects.count()} quizzes")
