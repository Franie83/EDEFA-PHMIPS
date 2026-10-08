"""
fix_public_report.py — repair the indentation of public_report() in backend/app.py

Problem: the try/except block was inserted at column 0, breaking the function body.
Solution: replace the whole public_report preamble with a correctly-indented block,
then re-parse the file with ast to guarantee it compiles.
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

# ============================================================
# Replace the entire public_report() function body with a
# correctly-indented version (1-space indent inside the function,
# 2 spaces inside try/except). Matches the compact style used
# throughout the rest of the file.
# ============================================================

NEW_FUNC = '''@app.post("/api/public/report")
def public_report():
 d=request.get_json(silent=True) or {};d["reporter_type"]="PUBLIC";
 d["title"]=d.get("title","Public Ecological Hazard Report");hid=nxt("EH","HAZ");lga=d.get("lga","Oredo")
 try:
  _lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
 except (TypeError,ValueError):
  return jsonify({"error":"latitude and longitude must be numeric"}),400
 if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
 if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
 h={"id":hid,"title":d["title"],"category":d.get("category","Gully erosion"),"hazard_type":d.get("hazard_type") or d.get("category","Environmental hazard"),"description":d.get("description",""),"date_observed":d.get("date_observed",today()),"date_reported":now(),"reporter_name":d.get("reporter_name","Public Reporter"),"reporter_type":"PUBLIC","reporter_contact":d.get("reporter_contact",""),"state":d.get("state","Edo"),"lga":lga,"ward":d.get("ward","Ward 1"),"community":d.get("community","Community"),"address_description":d.get("address_description",""),"latitude":_lat,"longitude":_lng,"estimated_affected_area_sqm":float(d.get("estimated_affected_area_sqm") or 0),"estimated_affected_population":int(d.get("estimated_affected_population") or 0),"estimated_affected_assets":d.get("estimated_affected_assets",""),"potential_impact":d.get("potential_impact",""),"severity":d.get("severity","MEDIUM"),"urgency":d.get("urgency","NORMAL"),"status":"Submitted","tracking_code":f"EF-HAZ-{today().replace('-','')}-{re.sub(r'[^A-Za-z0-9]','',lga)[:4].upper()}"}
 put("hazards",h)
 for ev in d.get("evidence") or []:
  evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})
 audit("PUBLIC_SUBMIT_HAZARD","HAZARD",hid,None,{"title":h["title"],"tracking_code":h["tracking_code"]},"Public anonymous report")
 db.session.commit()
 return jsonify({"success":True,"tracking_code":h["tracking_code"],"hazard_id":hid,"message":"Ecological hazard report submitted successfully."}),201
'''

# Match the whole public_report block: from its decorator to the return jsonify line
PATTERN = re.compile(
    r'@app\.post\("/api/public/report"\)\s*\n'
    r'def public_report\(\):\s*\n'
    r'(?:.*\n)*?'                                     # anything (including the broken lines)
    r'\s*return jsonify\(\{"success":True,"tracking_code":h\["tracking_code"\],"hazard_id":hid,"message":"Ecological hazard report submitted successfully\."\}\),201\s*\n',
    re.MULTILINE,
)

m = PATTERN.search(src)
if not m:
    raise SystemExit("FAILED: could not locate public_report() block. Aborting (no changes written).")

src = src[:m.start()] + NEW_FUNC + src[m.end():]
print("public_report() replaced with correctly-indented version.")

# ============================================================
# Syntax check — ast.parse will raise if the file is still broken.
# ============================================================
try:
    ast.parse(src)
except SyntaxError as e:
    print()
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
    print(f"  {(e.text or '').rstrip()}")
    print()
    print("Nothing written to disk. Original file untouched.")
    raise SystemExit(1)

# ---------- write ----------
APP_PY.write_text(src, encoding="utf-8")
print(f"Syntax OK. Patched: {APP_PY.resolve()}")
print()
print("Next: restart Flask and reload the browser.")