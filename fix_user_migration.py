"""
fix_user_migration.py
Surgically migrates existing django.contrib.auth.User to apps.accounts.User.
Run with: python manage.py shell < fix_user_migration.py
"""
import os
import django
from django.db import connection, transaction

def fix_migration():
    with connection.cursor() as cursor:
        # 1. Check if accounts_user already exists
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'accounts_user'")
        if cursor.fetchone()[0] > 0:
            print("  [!] accounts_user table already exists. Checking migration records...")
        else:
            # 2. Rename auth_user to accounts_user
            print("  [>] Renaming auth_user to accounts_user...")
            cursor.execute("ALTER TABLE auth_user RENAME TO accounts_user")
            
            # 3. Add missing columns for the custom User model
            print("  [>] Adding custom columns (role, phone, avatar, is_verified)...")
            cursor.execute("ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS role varchar(12) DEFAULT 'STUDENT'")
            cursor.execute("ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS phone varchar(15) DEFAULT ''")
            cursor.execute("ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS avatar varchar(100) DEFAULT ''")
            cursor.execute("ALTER TABLE accounts_user ADD COLUMN IF NOT EXISTS is_verified boolean DEFAULT FALSE")

        # 4. Insert migration record for accounts.0001_initial
        print("  [>] Recording accounts.0001_initial as applied...")
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) "
            "VALUES ('accounts', '0001_initial', NOW()) "
            "ON CONFLICT (app, name) DO NOTHING"
        )

        # 5. Fix ContentTypes
        print("  [>] Updating ContentTypes from auth.user to accounts.user...")
        cursor.execute(
            "UPDATE django_content_type SET app_label = 'accounts' "
            "WHERE app_label = 'auth' AND model = 'user'"
        )

        # 6. Fix user_groups and user_permissions tables
        # These are usually auth_user_groups, etc. but they reference auth_user.
        # Since we renamed the table, they might need adjustment depending on FK names.
        # Postgres usually handles FKs even if the table is renamed, but the table name itself might be auth_user_groups.
        
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'auth_user_groups'")
        if cursor.fetchone()[0] > 0:
            print("  [>] Renaming auth_user_groups to accounts_user_groups...")
            cursor.execute("ALTER TABLE auth_user_groups RENAME TO accounts_user_groups")
            
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'auth_user_user_permissions'")
        if cursor.fetchone()[0] > 0:
            print("  [>] Renaming auth_user_user_permissions to accounts_user_user_permissions...")
            cursor.execute("ALTER TABLE auth_user_user_permissions RENAME TO accounts_user_user_permissions")

    print("\n[✓] Migration fixed surgically. You can now run: python manage.py migrate")

if __name__ == "__main__":
    fix_migration()
