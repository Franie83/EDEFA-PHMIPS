"""
apply_geo_patch.py — one-shot patch for backend/app.py

Fixes:
  1. hazard_update (PUT /api/hazards/<id>) — add latitude/longitude validation
     and fix the broken audit() call (was passing kwargs, needs positional).
  2. hazard_create (POST /api/hazards) — wrap the float() casts in try/except.
  3. public_report (POST /api/public/report) — same safe-cast wrapper.

Creates a timestamped .bak file before touching the original.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

APP_PY = Path(r".\backend\app.py")

if not APP_PY.exists():
    raise SystemExit(f"Not found: {APP_PY.resolve()}")

src = APP_PY.read_text(encoding="utf-8")

# ---------- backup ----------
ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
backup = APP_PY.with_suffix(f".py.bak_{ts}")
shutil.copy2(APP_PY, backup)
print(f"Backup written: {backup}")

# ============================================================
# PATCH 1 — replace hazard_update body (the PUT handler)
# ============================================================
# We match from the decorator line up to the closing of the function,
# identified by the 'return jsonify(new)' that ends it.
# The whole block is compact (single line body) in this file.

PUT_PATTERN = re.compile(
    r'@app\.put\("/api/hazards/<id>"\)\s*\n'
    r'@require_edit\(\)\s*\n'
    r'def hazard_update\(id\):\s*\n'
    r'(?P<body>(?:[ \t]+.*\n)+?)'          # body lines
    r'(?=\n@|\Z)',                           # stop at next decorator or EOF
    re.MULTILINE,
)

NEW_PUT = '''@app.put("/api/hazards/<id>")
@require_edit()
def hazard_update(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 d=request.get_json(silent=True) or {};old=dict(r.data)
 # --- Geo validation (blocks corrupt coordinates from being merged) ---
 if "latitude" in d:
  try:lat=float(d["latitude"])
  except (TypeError,ValueError):return jsonify({"error":"latitude must be numeric","field":"latitude"}),400
  if not (-90.0<=lat<=90.0):return jsonify({"error":f"latitude {lat} out of range (-90..90)","field":"latitude"}),400
 if "longitude" in d:
  try:lon=float(d["longitude"])
  except (TypeError,ValueError):return jsonify({"error":"longitude must be numeric","field":"longitude"}),400
  if not (-180.0<=lon<=180.0):return jsonify({"error":f"longitude {lon} out of range (-180..180)","field":"longitude"}),400
 immutable={"id","date_reported","tracking_code"}
 new={**old,**{k:v for k,v in d.items() if k not in immutable}}
 r.data=new
 audit("EDIT_HAZARD","HAZARD",id,old,new,f"Edited hazard {id} - {new.get('title','')}")
 db.session.commit();return jsonify(new)
'''

m = PUT_PATTERN.search(src)
if not m:
    raise SystemExit("PATCH 1 FAILED: could not locate hazard_update block.")
src = src[:m.start()] + NEW_PUT + src[m.end():]
print("PATCH 1 applied — hazard_update hardened.")

# ============================================================
# PATCH 2 — wrap float() casts in hazard_create and public_report
# ============================================================
CAST_PATTERN = re.compile(
    r'^(?P<indent>[ \t]*)'
    r'(?P<var1>_lat)=float\(d\.get\("latitude"\) or 6\.335\);'
    r'(?P<var2>_lng)=float\(d\.get\("longitude"\) or 5\.603\)\s*$',
    re.MULTILINE,
)

def wrap_cast(match):
    ind = match.group("indent")
    v1 = match.group("var1")
    v2 = match.group("var2")
    return (
        f"{ind}try:\n"
        f"{ind} {v1}=float(d.get(\"latitude\") or 6.335);{v2}=float(d.get(\"longitude\") or 5.603)\n"
        f"{ind}except (TypeError,ValueError):\n"
        f"{ind} return jsonify({{\"error\":\"latitude and longitude must be numeric\"}}),400"
    )

src, n = CAST_PATTERN.subn(wrap_cast, src)
print(f"PATCH 2 applied — wrapped {n} float cast line(s) in try/except.")
if n == 0:
    print("  (warning: no cast lines matched; they may already be wrapped)")

# ---------- write ----------
APP_PY.write_text(src, encoding="utf-8")
print(f"Patched: {APP_PY.resolve()}")
print()
print("Verify with:  Get-Content .\\backend\\app.py | Select-String 'longitude must be' -Context 1,1")