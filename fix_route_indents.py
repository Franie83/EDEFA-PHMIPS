"""
fix_route_indents.py — restore top-level route decorators in backend/app.py

After the public_report() patch, some @app.<method>(...) decorator lines
may have acquired leading spaces and are now nested inside a function.
This script finds every line that starts (after optional whitespace) with
@app.<verb>( and:
  - if it's the FIRST @app.<verb>( after a `def public_report():` block
    whose return statement is the last executable line, restore it to col 0
  - otherwise leave it alone
Actually, simpler: ensure every `@app.` line that is followed by a `def ...`
line at the SAME indentation is restored to the SAME indentation as that def.
If the def is at column 0, decorator goes to column 0.
"""

import ast
import shutil
from datetime import datetime
from pathlib import Path

APP_PY = Path(r".\backend\app.py")
src = APP_PY.read_text(encoding="utf-8").splitlines(keepends=True)

ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
shutil.copy2(APP_PY, APP_PY.with_suffix(f".py.bak_{ts}"))
print(f"Backup written: backend\\app.py.bak_{ts}")

fixed = 0
out = []
for idx, line in enumerate(src):
    stripped = line.lstrip()
    # Is this line a route decorator?
    if stripped.startswith("@app.") and "(" in stripped:
        # Find the next non-empty, non-decorator line — should be a `def`
        j = idx + 1
        while j < len(src) and (
            src[j].strip().startswith("@") or src[j].strip() == ""
        ):
            j += 1
        if j < len(src):
            def_line = src[j]
            def_indent = len(def_line) - len(def_line.lstrip())
            # Only normalize if this is clearly a top-level def (col 0)
            if def_indent == 0:
                # Decorator must also be at col 0
                if line != stripped:
                    out.append(stripped)
                    fixed += 1
                    print(f"  line {idx+1}: restored decorator to column 0: {stripped.rstrip()}")
                    continue
    out.append(line)

new_src = "".join(out)
try:
    ast.parse(new_src)
except SyntaxError as e:
    print(f"SYNTAX ERROR after fix attempt at line {e.lineno}: {e.msg}")
    print("Nothing written. Original file untouched.")
    raise SystemExit(1)

APP_PY.write_text(new_src, encoding="utf-8")
print(f"Done. {fixed} decorator line(s) corrected. Syntax OK.")