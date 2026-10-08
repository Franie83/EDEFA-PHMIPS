import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

# The broken chain produced by the previous patch
broken = (
    '"tracking_code":f"EF-HAZ-{today().replace(\'-\',\'\')}-{re.sub(r\'[^A-Za-z0-9]\',\'\',lga)[:4].upper()}"};'
    'put("hazards",h);'
    'for ev in d.get("evidence") or []: evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"});'
    'audit("PUBLIC_SUBMIT_HAZARD","HAZARD",hid,None,{"title":h["title"],"tracking_code":h["tracking_code"]},"Public anonymous report");'
    'db.session.commit();'
    'return jsonify({"success":True,"tracking_code":h["tracking_code"],"hazard_id":hid,"message":"Ecological hazard report submitted successfully."}),201'
)

# Correct version — `for` body on its own line
fixed = (
    '"tracking_code":f"EF-HAZ-{today().replace(\'-\',\'\')}-{re.sub(r\'[^A-Za-z0-9]\',\'\',lga)[:4].upper()}"}\n'
    ' put("hazards",h)\n'
    ' for ev in d.get("evidence") or []:\n'
    '  evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})\n'
    ' audit("PUBLIC_SUBMIT_HAZARD","HAZARD",hid,None,{"title":h["title"],"tracking_code":h["tracking_code"]},"Public anonymous report")\n'
    ' db.session.commit()\n'
    ' return jsonify({"success":True,"tracking_code":h["tracking_code"],"hazard_id":hid,"message":"Ecological hazard report submitted successfully."}),201'
)

if broken in src:
    src = src.replace(broken, fixed)
    p.write_text(src, encoding="utf-8")
    print("Fixed: for-loop now on its own line")
elif 'for ev in d.get("evidence") or []:\n' in src:
    print("Already fixed")
else:
    print("Pattern not found. Paste the current line 1343 below.")

# Verify syntax
import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print("STILL BROKEN:", e)
    print("Line", e.lineno, ":", e.text)