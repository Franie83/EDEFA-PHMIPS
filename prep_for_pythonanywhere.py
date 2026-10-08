"""
prep_for_pythonanywhere.py

Prepares the EDEFA-PHMIPS project for a lean push to GitHub and
deployment on PythonAnywhere's free tier.

Run from the project root:
    python prep_for_pythonanywhere.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
REQUIREMENTS_PATH = PROJECT_ROOT / "backend" / "requirements.txt"
WSGI_PATH = PROJECT_ROOT / "backend" / "wsgi.py"
APP_PATH = PROJECT_ROOT / "backend" / "app.py"
ENV_EXAMPLE_PATH = PROJECT_ROOT / "backend" / ".env.example"

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def banner(msg: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {msg}")
    print("=" * 70)


def run(cmd: list[str], cwd: Path = PROJECT_ROOT) -> tuple[int, str]:
    """Run a shell command and return (returncode, output)."""
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, shell=False
        )
        return result.returncode, (result.stdout + result.stderr).strip()
    except FileNotFoundError:
        return 1, f"Command not found: {cmd[0]}"


def confirm(prompt: str) -> bool:
    """Ask the user a yes/no question."""
    while True:
        ans = input(f"{prompt} [y/N]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("", "n", "no"):
            return False


# ---------------------------------------------------------------------------
# 1. .gitignore
# ---------------------------------------------------------------------------
GITIGNORE_CONTENT = """# ===== Python =====
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
*.egg-info/
.eggs/
dist/
build/

# ===== Virtual Environments =====
.venv/
venv/
env/
ENV/

# ===== Environment / Secrets =====
.env
.env.*
!.env.example

# ===== Databases =====
*.db
*.sqlite
*.sqlite3
instance/
backend/instance/

# ===== Uploaded Files (sensitive) =====
backend/uploads/
backend/backups/
uploads/
media/

# ===== Backup Files =====
*.bak
*.bak_*
*.backup
*~

# ===== Dev Patch/Fix Scripts (not part of app) =====
patch_*.py
fix_*.py
add_*.py
migrate_*.py
revert_*.py
rewrite_*.py
append_*.py
insert_*.py
apply_*.py
wire_*.py
enforce_*.py
allow_*.py
enrich_*.py
restore_*.py
reset_*.py
cleanup_*.py
check_*.py
convert_*.py
inspect_*.py
diag_*.py
verify_*.py
bump_*.py
backfill_*.py
trim_*.py
wipe_*.py
*cleanup_orphans*
*bak_*

# ===== Node / React =====
node_modules/
dist/
.vite/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
bun.lockb

# ===== OS / Editor =====
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp

# ===== PowerShell Test Scripts =====
test_*.ps1
"""


def write_gitignore() -> None:
    banner("1. Writing .gitignore")
    if GITIGNORE_PATH.exists():
        backup = GITIGNORE_PATH.with_suffix(".gitignore.old")
        shutil.copy2(GITIGNORE_PATH, backup)
        print(f"   Backed up existing .gitignore -> {backup.name}")
    GITIGNORE_PATH.write_text(GITIGNORE_CONTENT, encoding="utf-8")
    print(f"   Wrote {GITIGNORE_PATH}")


# ---------------------------------------------------------------------------
# 2. requirements.txt
# ---------------------------------------------------------------------------
REQUIREMENTS_CONTENT = """Flask>=3.0
Flask-SQLAlchemy>=3.1
Flask-CORS>=4.0
SQLAlchemy>=2.0
gunicorn>=21.2
eventlet>=0.36
python-dotenv>=1.0
"""


def write_requirements() -> None:
    banner("2. Writing backend/requirements.txt")
    if not REQUIREMENTS_PATH.parent.exists():
        print(f"   [SKIP] {REQUIREMENTS_PATH.parent} does not exist.")
        return
    if REQUIREMENTS_PATH.exists():
        backup = REQUIREMENTS_PATH.with_suffix(".txt.old")
        shutil.copy2(REQUIREMENTS_PATH, backup)
        print(f"   Backed up existing requirements.txt -> {backup.name}")
    REQUIREMENTS_PATH.write_text(REQUIREMENTS_CONTENT, encoding="utf-8")
    print(f"   Wrote {REQUIREMENTS_PATH}")


# ---------------------------------------------------------------------------
# 3. wsgi.py
# ---------------------------------------------------------------------------
WSGI_CONTENT = '''import sys
import os

# Add backend directory to path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables (optional)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(path, ".env"))
except ImportError:
    pass

# Import the Flask app
from app import app as application
'''


def write_wsgi() -> None:
    banner("3. Writing backend/wsgi.py")
    if not WSGI_PATH.parent.exists():
        print(f"   [SKIP] {WSGI_PATH.parent} does not exist.")
        return
    if WSGI_PATH.exists():
        backup = WSGI_PATH.with_suffix(".py.old")
        shutil.copy2(WSGI_PATH, backup)
        print(f"   Backed up existing wsgi.py -> {backup.name}")
    WSGI_PATH.write_text(WSGI_CONTENT, encoding="utf-8")
    print(f"   Wrote {WSGI_PATH}")


# ---------------------------------------------------------------------------
# 4. Fix app.run() in app.py
# ---------------------------------------------------------------------------
def fix_app_run() -> None:
    banner("4. Checking backend/app.py for bare app.run()")
    if not APP_PATH.exists():
        print(f"   [SKIP] {APP_PATH} does not exist.")
        return

    text = APP_PATH.read_text(encoding="utf-8")
    original = text

    # Find lines with app.run( or socketio.run( that are NOT inside an if __main__
    lines = text.splitlines()
    fixed_lines = []
    inside_main_guard = False
    main_guard_indent = 0
    changed = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        if stripped.startswith("if __name__"):
            inside_main_guard = True
            main_guard_indent = indent
            fixed_lines.append(line)
            continue

        # Leaving the main guard if indentation drops back
        if inside_main_guard and stripped and indent <= main_guard_indent:
            inside_main_guard = False

        # If it's a run() call and NOT inside the guard, wrap it
        if re.match(r"^\s*(app|socketio)\.run\(", line) and not inside_main_guard:
            indent_str = " " * indent
            fixed_lines.append(f"{indent_str}if __name__ == '__main__':")
            fixed_lines.append(f"{indent_str}    {stripped}")
            changed = True
            continue

        fixed_lines.append(line)

    if changed:
        backup = APP_PATH.with_suffix(".py.old")
        shutil.copy2(APP_PATH, backup)
        APP_PATH.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
        print(f"   Wrapped bare run() call(s) in __main__ guard.")
        print(f"   Backed up original -> {backup.name}")
    else:
        print("   No bare run() calls found. Nothing to change.")


# ---------------------------------------------------------------------------
# 5. .env.example
# ---------------------------------------------------------------------------
ENV_EXAMPLE_CONTENT = """# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=change-me-to-a-long-random-string

# Database (SQLite for PythonAnywhere free tier)
DATABASE_URL=sqlite:////home/EDEFA/eco/backend/instance/ef_phmips.db

# CORS (comma-separated origins)
CORS_ORIGINS=https://yourusername.pythonanywhere.com

# Optional: Gemini / AI
GEMINI_API_KEY=

# Optional: Mail
MAIL_SERVER=
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
"""


def write_env_example() -> None:
    banner("5. Writing backend/.env.example")
    if not ENV_EXAMPLE_PATH.parent.exists():
        print(f"   [SKIP] {ENV_EXAMPLE_PATH.parent} does not exist.")
        return
    ENV_EXAMPLE_PATH.write_text(ENV_EXAMPLE_CONTENT, encoding="utf-8")
    print(f"   Wrote {ENV_EXAMPLE_PATH}")


# ---------------------------------------------------------------------------
# 6. Git cleanup
# ---------------------------------------------------------------------------
def git_cleanup() -> None:
    banner("6. Git cleanup (unstage everything, re-add with new .gitignore)")

    # Check if this is a git repo
    code, _ = run(["git", "rev-parse", "--is-inside-work-tree"])
    if code != 0:
        print("   [SKIP] Not a git repository.")
        return

    # Show status BEFORE
    print("\n   --- git status BEFORE ---")
    _, status_before = run(["git", "status", "--short"])
    print(status_before or "   (clean)")

    if not confirm("\n   Proceed with unstage + re-add?"):
        print("   Aborted git cleanup.")
        return

    print("\n   Unstaging everything...")
    code, out = run(["git", "rm", "-r", "--cached", "."])
    if code != 0:
        print(f"   [WARN] git rm returned {code}: {out}")

    print("   Re-adding with new .gitignore...")
    code, out = run(["git", "add", "."])
    if code != 0:
        print(f"   [ERROR] git add failed: {out}")
        return

    print("\n   --- git status AFTER ---")
    _, status_after = run(["git", "status", "--short"])
    print(status_after or "   (clean)")

    print("\n   Done. Review the list above, then commit manually:")
    print("     git commit -m \"Lean backend for PythonAnywhere testing\"")
    print("     git push -u origin main")


# ---------------------------------------------------------------------------
# 7. Summary
# ---------------------------------------------------------------------------
def print_summary() -> None:
    banner("DONE — Next steps")
    print("""
1. Review the files that were created/modified:
     - .gitignore
     - backend/requirements.txt
     - backend/wsgi.py
     - backend/app.py (if run() was wrapped)
     - backend/.env.example

2. Check git status:
     git status

3. Commit and push:
     git commit -m "Lean backend for PythonAnywhere testing"
     git push -u origin main

4. On PythonAnywhere (Bash console):
     cd ~
     git clone https://github.com/Franie83/EDEFA-PHMIPS.git eco
     cd eco/backend
     mkvirtualenv --python=/usr/bin/python3.10 eco-env
     pip install -r requirements.txt

5. Web tab -> Manual config -> Python 3.10
     Source code:       /home/EDEFA/eco/backend
     Working directory: /home/EDEFA/eco/backend
     Virtualenv:        /home/EDEFA/.virtualenvs/eco-env
     WSGI file:         paste contents of backend/wsgi.py

6. Create .env on server:
     cd ~/eco/backend && nano .env

7. Reload the web app and test:
     https://EDEFA.pythonanywhere.com
""")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    print("EDEFA-PHMIPS — Prep for PythonAnywhere")
    print(f"Project root: {PROJECT_ROOT}")

    if not (PROJECT_ROOT / "backend").exists():
        print("\n[ERROR] No 'backend' folder found. Run this from the project root.")
        sys.exit(1)

    write_gitignore()
    write_requirements()
    write_wsgi()
    fix_app_run()
    write_env_example()
    git_cleanup()
    print_summary()


if __name__ == "__main__":
    main()