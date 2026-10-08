"""
fix_backend_final.py — restores the Flask init block and fixes stage_tag priority.
Run from the eco/ folder:  python fix_backend_final.py
"""
import ast
import re
import shutil
from datetime import datetime
from pathlib import Path

APP_PY = Path(r".\backend\app.py")
if not APP_PY.exists():
    raise SystemExit(f"Not found: {APP_PY.resolve()}")

src = APP_PY.read_text(encoding="utf-8")

# ---------- backup ----------
ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
backup = APP_PY.with_suffix(f".py.bak_{ts}")
shutil.copy2(APP_PY, backup)
print(f"Backup written: {backup}")

changes = []

# ============================================================
# PATCH 1 — ensure Flask init block is present
# ============================================================
FLASK_INIT = 'app=Flask(__name__,static_folder=str(BASE/"dist"),static_url_path="")\n'
FLASK_INIT += 'app.secret_key=os.getenv("SECRET_KEY", "dev-only-change-this-secret")\n'
FLASK_INIT += 'app.config["SESSION_COOKIE_HTTPONLY"]=True\n'
FLASK_INIT += 'app.config["SESSION_COOKIE_SAMESITE"]="Lax"\n'
FLASK_INIT += 'app.config["SESSION_COOKIE_SECURE"]=os.getenv("SESSION_COOKIE_SECURE","0").lower() in {"1","true","yes"}\n'
FLASK_INIT += 'INSTANCE.mkdir(parents=True, exist_ok=True)\n'
FLASK_INIT += 'url=os.getenv("DATABASE_URL",f"sqlite:///{(INSTANCE/\'ef_phmips.db\').as_posix()}")\n'
FLASK_INIT += 'if url.startswith("postgres://"):url="postgresql+psycopg://"+url[11:]\n'
FLASK_INIT += 'elif url.startswith("postgresql://"):url="postgresql+psycopg://"+url[13:]\n'
FLASK_INIT += 'app.config.update(SQLALCHEMY_DATABASE_URI=url,SQLALCHEMY_TRACK_MODIFICATIONS=False,MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH",50))*1024*1024,SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping":True,"pool_recycle":280} if url.startswith("postgres") else {})\n'
FLASK_INIT += 'db.init_app(app)\n'
FLASK_INIT += 'with app.app_context():db.create_all();seed()\n'

has_app_flask = bool(re.search(r"app\s*=\s*Flask\(", src))
has_db_init = "db.init_app(app)" in src

if not has_app_flask or not has_db_init:
    inserted = False
    # Anchor 1: end of evidence_create
    m = re.search(r'(evidence_files",e\);\s*return e[^\n]*\n)', src)
    if m:
        src = src[:m.end()] + "\n" + FLASK_INIT + src[m.end():]
        inserted = True
    # Anchor 2: just before @app.after_request
    if not inserted:
        m2 = re.search(r'(\n@app\.after_request)', src)
        if m2:
            src = src[:m2.start()] + "\n\n" + FLASK_INIT + src[m2.start():]
            inserted = True
    # Anchor 3: right after the last def before any @app.<verb> route
    if not inserted:
        m3 = re.search(r'(\n@app\.(get|post|put|delete|route)\()', src)
        if m3:
            src = src[:m3.start()] + "\n\n" + FLASK_INIT + src[m3.start():]
            inserted = True
    if not inserted:
        raise SystemExit("Cannot find insertion point for Flask init block.")
    changes.append("PATCH 1: inserted Flask init block")
else:
    changes.append("PATCH 1: Flask init block already present — skipped")

# ============================================================
# PATCH 2 — evidence_create stage_tag priority
# ============================================================
OLD_STAGE = '"stage_tag":links.get("stage_tag",d.get("stage_tag","evidence"))'
NEW_STAGE = '"stage_tag":d.get("stage_tag") or links.get("stage_tag") or "evidence"'

if OLD_STAGE in src:
    src = src.replace(OLD_STAGE, NEW_STAGE, 1)
    changes.append("PATCH 2: evidence_create stage_tag priority fixed")
elif NEW_STAGE in src:
    changes.append("PATCH 2: evidence_create already fixed — skipped")
else:
    changes.append("PATCH 2: could not locate evidence_create stage_tag line")

# ============================================================
# PATCH 3 — visit_create evidence loop stage_tag priority
# ============================================================
OLD_LOOP = '"stage_tag":d.get("stage_tag","during")})'
NEW_LOOP = '"stage_tag":ev.get("stage_tag") or d.get("stage_tag") or "during"})'

if OLD_LOOP in src:
    src = src.replace(OLD_LOOP, NEW_LOOP, 1)
    changes.append("PATCH 3: visit_create evidence loop fixed")
elif NEW_LOOP in src:
    changes.append("PATCH 3: visit_create already fixed — skipped")
else:
    changes.append("PATCH 3: could not locate visit_create loop")

# ============================================================
# Syntax check
# ============================================================
try:
    ast.parse(src)
except SyntaxError as e:
    print()
    print(f"SYNTAX ERROR after patch at line {e.lineno}: {e.msg}")
    print(f"  {(e.text or '').rstrip()}")
    print()
    print("Nothing written. Original file untouched.")
    raise SystemExit(1)

APP_PY.write_text(src, encoding="utf-8")
print()
for c in changes:
    print(" -", c)
print()
print(f"Syntax OK. Patched: {APP_PY.resolve()}")
print("Next: restart Flask with .\\restart-backend.ps1")