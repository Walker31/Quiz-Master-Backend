import os
import django
from django.db import connection

def reset():
    print("  [!] RESETTING DATABASE...")
    with connection.cursor() as cursor:
        # Drop everything in the public schema
        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        cursor.execute("COMMENT ON SCHEMA public IS 'standard public schema';")
    print("[✓] Database has been wiped clean. You can now run migrations from scratch.")

if __name__ == "__main__":
    # Ensure Django is setup
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizMaster.settings.dev')
    django.setup()
    reset()
