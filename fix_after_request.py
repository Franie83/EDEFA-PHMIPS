"""fix_after_request.py — repair the after_request block and glued return line."""
import ast
import re
import shutil
from datetime import datetime
from pathlib import Path

APP_PY = Path(r".\backend\app.py")
if not APP_PY.exists():
    raise SystemExit(f"Not found: {APP_PY.resolve()}")

src = APP_PY.read_text(encoding="utf-8")

ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
backup = APP_PY.with_suffix(f".py.bak_{ts}")
shutil.copy2(APP_PY, backup)
print(f"Backup written: {backup}")

changes = []

# PATCH 1 — remove trailing " @app.after_request" glued to "return e"
before = src
src = re.sub(r'(put\("evidence_files",e\);return e)\s+@app\.after_request\b', r'\1', src)
if src != before:
    changes.append("PATCH 1: removed trailing '@app.after_request' glued after 'return e'")
else:
    changes.append("PATCH 1: no glued line — skipped")

# PATCH 2 — ensure @app.after_request decorator exists at column 0 above def sec
if re.search(r'^@app\.after_request\s*$', src, re.MULTILINE):
    changes.append("PATCH 2: decorator already present — skipped")
else:
    # Insert @app.after_request right before 'def sec(r):'
    new_src, n = re.subn(
        r'^def sec\(r\):',
        '@app.after_request\ndef sec(r):',
        src,
        count=1,
        flags=re.MULTILINE,
    )
    if n:
        src = new_src
        changes.append("PATCH 2: inserted '@app.after_request' above def sec()")
    else:
        changes.append("PATCH 2: could not locate 'def sec(r):' — skipped")

# syntax check
try:
    ast.parse(src)
except SyntaxError as e:
    print()
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
    print(f"  {(e.text or '').rstrip()}")
    print("Nothing written.")
    raise SystemExit(1)

APP_PY.write_text(src, encoding="utf-8")
print()
for c in changes:
    print(" -", c)
print()
print(f"Syntax OK. Patched: {APP_PY.resolve()}")
print("Next:  .\\restart-backend.ps1")