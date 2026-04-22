"""
seed_students.py
Creates dummy student accounts and a sample batch for testing.
Run with: python manage.py shell < seed_students.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizMaster.settings.dev')
django.setup()

from apps.accounts.models import User, Batch

def seed():
    # 1. Get an admin to be the batch mentor
    admin = User.objects.filter(role='SUPERADMIN').first()
    if not admin:
        admin = User.objects.create_superuser('admin', 'admin@quizmaster.com', 'admin123')
        admin.role = 'SUPERADMIN'
        admin.save()
        print(f"Created Superadmin: {admin.username}")

    # 2. Create a Sample Batch
    batch, created = Batch.objects.get_or_create(
        code="ENG2024",
        defaults={
            "name": "Engineering Batch 2024",
            "admin": admin
        }
    )
    print(f"{'[Created]' if created else '[Exists]'} Batch: {batch.name}")

    # 3. Create Dummy Students
    students_data = [
        {"username": "arjun", "first": "Arjun", "last": "Kumar", "email": "arjun@example.com"},
        {"username": "priya", "first": "Priya", "last": "Sharma", "email": "priya@example.com"},
        {"username": "rahul", "first": "Rahul", "last": "Verma", "email": "rahul@example.com"},
        {"username": "sneha", "first": "Sneha", "last": "Reddy", "email": "sneha@example.com"},
        {"username": "vikram", "first": "Vikram", "last": "Singh", "email": "vikram@example.com"},
    ]

    for data in students_data:
        student, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                "email": data['email'],
                "first_name": data['first'],
                "last_name": data['last'],
                "role": "STUDENT",
                "is_verified": True
            }
        )
        if created:
            student.set_password("password123")
            student.save()
            print(f"Created Student: {student.username}")
        
        # Add to batch
        if not batch.students.filter(id=student.id).exists():
            batch.students.add(student)
            print(f"  -> Added {student.username} to {batch.name}")

    print("\n[✓] Student seeding complete! All passwords set to: password123")

if __name__ == "__main__":
    seed()
