import os
import glob

def clean():
    print("  [!] CLEANING PROJECT MIGRATIONS...")
    # ONLY search in project-specific folders
    # We EXPLICITLY avoid 'venv' or any hidden folders
    project_folders = ['apps', 'core', 'users', 'quizzes']
    
    current_dir = os.getcwd()
    print(f"  [>] Working in: {current_dir}")

    for folder in project_folders:
        folder_path = os.path.join(current_dir, folder)
        if not os.path.exists(folder_path):
            continue
            
        print(f"  [>] Scanning {folder}...")
        # Find all .py files in migrations folders
        pattern = os.path.join(folder_path, "**/migrations/*.py")
        files = glob.glob(pattern, recursive=True)
        
        for f in files:
            if not f.endswith('__init__.py'):
                print(f"    - Deleting {f}")
                os.remove(f)
            
    print("[✓] Project migration files cleaned safely.")

if __name__ == "__main__":
    clean()
