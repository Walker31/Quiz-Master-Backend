from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from quizzes.models import Subject, Chapter, Quiz, Question, Score
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Seed the database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to seed data...')

        # Create test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create subjects
        subjects = []
        subject_names = ['Mathematics', 'Science', 'English', 'History']
        for name in subject_names:
            subject, created = Subject.objects.get_or_create(
                name=name,
                defaults={'description': f'Learn {name}'}
            )
            subjects.append(subject)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created subject: {name}'))

        # Create chapters
        chapters = []
        for subject in subjects:
            for i in range(1, 4):
                chapter, created = Chapter.objects.get_or_create(
                    subject=subject,
                    name=f'{subject.name} - Chapter {i}',
                    defaults={'description': f'Chapter {i} of {subject.name}'}
                )
                chapters.append(chapter)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created chapter: {chapter.name}'))

        # Create quizzes
        quizzes = []
        for chapter in chapters[:5]:
            for i in range(1, 3):
                quiz, created = Quiz.objects.get_or_create(
                    chapter=chapter,
                    subject=chapter.subject,
                    quiz_title=f'{chapter.name} - Quiz {i}',
                    defaults={
                        'date_of_quiz': timezone.now() + timedelta(days=i),
                        'time_duration': 30 + (i * 10),
                        'remarks': f'Quiz {i} for {chapter.name}',
                        'is_live': i == 1
                    }
                )
                quizzes.append(quiz)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created quiz: {quiz.quiz_title}'))

        # Create questions
        question_count = 0
        for quiz in quizzes:
            for q_num in range(1, 6):
                question, created = Question.objects.get_or_create(
                    quiz=quiz,
                    question_statement=f'What is the answer to question {q_num} in {quiz.quiz_title}?',
                    defaults={
                        'option_1': 'Option A',
                        'option_2': 'Option B',
                        'option_3': 'Option C',
                        'option_4': 'Option D',
                        'correct_option': (q_num % 4) + 1,
                        'remarks': f'Question {q_num}'
                    }
                )
                if created:
                    question_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {question_count} questions'))

        # Create scores
        score_count = 0
        for quiz in quizzes[:3]:
            score, created = Score.objects.get_or_create(
                quiz=quiz,
                user=user,
                defaults={
                    'time_taken': 1200,
                    'max_marks': 50,
                    'total_scored': 35
                }
            )
            if created:
                score_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {score_count} scores'))
        self.stdout.write(self.style.SUCCESS('Data seeding completed!'))
