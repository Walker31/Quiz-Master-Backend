"""
Legacy shell-entry wrapper for unified seeding.

Run with:
    python manage.py shell < seed_all.py

Preferred:
    python manage.py seed_all
"""

from django.core.management import call_command


call_command("seed_all")
