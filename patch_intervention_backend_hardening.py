import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- Guard A: PUT /api/interventions/<id> cannot change hazard_id ----------
old_int_update = """def int_update(id):
 r=one("interventions",id)
 if not r:return jsonify({"error":"Intervention not found"}),404
 d=request.get_json(silent=True) or {};old=dict(r.data)
 new={**old,**{k:v for k,v in d.items() if k!="id"}}
 r.data=new
 audit("EDIT_INTERVENTION","INTERVENTION",id,old=old,new=new,details=f"Edited intervention {id}")
 db.session.commit();return jsonify(new)"""

new_int_update = """def int_update(id):
 r=one("interventions",id)
 if not r:return jsonify({"error":"Intervention not found"}),404
 d=request.get_json(silent=True) or {};old=dict(r.data)
 # Guard: hazard_id cannot be changed to a different value or cleared
 if "hazard_id" in d and d["hazard_id"] != old.get("hazard_id"):
  return jsonify({"error":"hazard_id cannot be changed — an intervention is permanently linked to its source hazard"}),400
 # Guard: if hazard_id somehow missing, refuse
 if not old.get("hazard_id"):
  return jsonify({"error":"Intervention is not linked to a hazard — data integrity violation"}),400
 new={**old,**{k:v for k,v in d.items() if k not in ("id","hazard_id")}}
 r.data=new
 audit("EDIT_INTERVENTION","INTERVENTION",id,old=old,new=new,details=f"Edited intervention {id}")
 db.session.commit();return jsonify(new)"""

if old_int_update in src:
    src = src.replace(old_int_update, new_int_update)
    changes.append("PUT /api/interventions/<id> — hazard_id is now immutable")
else:
    changes.append("int_update() pattern NOT FOUND")

# ---------- Guard B: reject if hazard_id is missing in recommend() ----------
old_rec = """ h=dict(r.data)
 if not h.get("verified_by"):
  return jsonify({"error":"Hazard must be verified before an intervention can be planned"}),400"""

new_rec = """ h=dict(r.data)
 if not h.get("id"):
  return jsonify({"error":"Invalid hazard record — missing id"}),400
 if not h.get("verified_by"):
  return jsonify({"error":"Hazard must be verified before an intervention can be planned"}),400"""

if old_rec in src:
    src = src.replace(old_rec, new_rec)
    changes.append("recommend() — added missing-id guard")
elif 'if not h.get("id"):' in src:
    changes.append("recommend() already has id guard")
else:
    changes.append("recommend() id-guard pattern NOT FOUND")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSYNTAX ERROR at line {e.lineno}: {e.text}")