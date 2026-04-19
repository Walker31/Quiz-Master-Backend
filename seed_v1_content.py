"""
seed_v1_content.py
Populates the new v1 content architecture: ExamType -> Subject -> Chapter -> Question.
Run with: python manage.py shell < seed_v1_content.py
"""
import os
import django
from django.utils.text import slugify

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizMaster.settings.dev')
django.setup()

from apps.accounts.models import User
from apps.content.models import ExamType, Subject, Chapter, Question, QuestionOption

def seed():
    # 1. Get or create a superuser
    admin, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@quizmaster.com',
            'role': 'SUPERADMIN',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if _: admin.set_password('admin123'); admin.save()

    # 2. Create Exam Types
    exam_data = [
        {"name": "JEE Mains", "slug": "jee-mains", "desc": "National level engineering entrance exam in India."},
        {"name": "NEET UG", "slug": "neet-ug", "desc": "National Eligibility cum Entrance Test for medical studies."},
        {"name": "GATE CS", "slug": "gate-cs", "desc": "Graduate Aptitude Test in Engineering for Computer Science."},
    ]

    exams = []
    for ed in exam_data:
        et, created = ExamType.objects.get_or_create(
            slug=ed['slug'],
            defaults={'name': ed['name'], 'description': ed['desc']}
        )
        exams.append(et)
        print(f"{'[Created]' if created else '[Exists]'} ExamType: {et.name}")

    # 3. Create Subjects & Chapters for JEE
    jee = exams[0]
    jee_subjects = [
        {
            "name": "Physics", "code": "PHY",
            "chapters": ["Electrostatics", "Current Electricity", "Ray Optics", "Modern Physics"]
        },
        {
            "name": "Mathematics", "code": "MATH",
            "chapters": ["Coordinate Geometry", "Calculus", "Vectors & 3D", "Algebra"]
        }
    ]

    for sd in jee_subjects:
        sub, _ = Subject.objects.get_or_create(
            exam_type=jee, name=sd['name'],
            defaults={'code': sd['code']}
        )
        print(f"  -> Subject: {sub.name}")
        
        for i, ch_name in enumerate(sd['chapters']):
            ch, _ = Chapter.objects.get_or_create(
                subject=sub, name=ch_name,
                defaults={'order': i}
            )
            print(f"    - Chapter: {ch.name}")
            
            # Create a dummy question for each chapter
            if ch.questions.count() == 0:
                q = Question.objects.create(
                    chapter=ch,
                    q_type='MCQ_SINGLE',
                    difficulty='MEDIUM',
                    text=f"Sample question for {ch_name}: What is the SI unit of power?",
                    marks_correct=4,
                    marks_wrong=-1,
                    created_by=admin
                )
                QuestionOption.objects.create(question=q, label='A', text='Watt', is_correct=True, order=0)
                QuestionOption.objects.create(question=q, label='B', text='Joule', is_correct=False, order=1)
                QuestionOption.objects.create(question=q, label='C', text='Newton', is_correct=False, order=2)
                QuestionOption.objects.create(question=q, label='D', text='Pascal', is_correct=False, order=3)

    print("\n[✓] Seeding complete!")

if __name__ == "__main__":
    seed()
