import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- Guard 1: verify() ----------
old_verify = """def verify(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 d=request.get_json(silent=True) or {};h=dict(r.data);old=h.get("status");"""

new_verify = """def verify(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 h_check=dict(r.data)
 if h_check.get("status") in ("Verified","Assessed","Intervention Recommended","Intervention Approved"):
  return jsonify({"error":f"Hazard is already in '{h_check.get('status')}' state — cannot re-verify"}),400
 if h_check.get("status")=="Rejected/Invalid":
  return jsonify({"error":"Hazard was rejected as invalid — cannot verify"}),400
 d=request.get_json(silent=True) or {};h=dict(r.data);old=h.get("status");"""

if old_verify in src:
    src = src.replace(old_verify, new_verify)
    changes.append("verify(): added state guards")
else:
    changes.append("verify() pattern NOT FOUND")

# ---------- Guard 2: assess() ----------
old_assess = """def assess(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 d=request.get_json(silent=True) or {};h=dict(r.data);w=db.session.get(Setting,"reference_data").value["priority_weights"];"""

new_assess = """def assess(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 h_check=dict(r.data)
 if not h_check.get("verified_by"):
  return jsonify({"error":"Hazard must be verified before it can be assessed"}),400
 if h_check.get("status") in ("Assessed","Intervention Recommended","Intervention Approved"):
  return jsonify({"error":f"Hazard is already in '{h_check.get('status')}' state — cannot re-assess"}),400
 if h_check.get("status")=="Rejected/Invalid":
  return jsonify({"error":"Rejected hazards cannot be assessed"}),400
 d=request.get_json(silent=True) or {};h=dict(r.data);w=db.session.get(Setting,"reference_data").value["priority_weights"];"""

if old_assess in src:
    src = src.replace(old_assess, new_assess)
    changes.append("assess(): added verified+state guards")
else:
    changes.append("assess() pattern NOT FOUND")

# ---------- Guard 3: recommend() ----------
old_recommend = """def recommend(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 h=dict(r.data);d=request.get_json(silent=True) or {};iid=nxt("INT","INT");"""

new_recommend = """def recommend(id):
 r=one("hazards",id)
 if not r:return jsonify({"error":"Hazard not found"}),404
 h=dict(r.data)
 if not h.get("verified_by"):
  return jsonify({"error":"Hazard must be verified before an intervention can be planned"}),400
 if not h.get("assessment"):
  return jsonify({"error":"Hazard must be assessed before an intervention can be planned"}),400
 if h.get("recommended_intervention"):
  return jsonify({"error":f"Intervention already exists for this hazard: {h['recommended_intervention'].get('intervention_id')}"}),400
 if h.get("status") in ("Rejected/Invalid",):
  return jsonify({"error":"Cannot plan intervention for a rejected hazard"}),400
 d=request.get_json(silent=True) or {};iid=nxt("INT","INT");"""

if old_recommend in src:
    src = src.replace(old_recommend, new_recommend)
    changes.append("recommend(): added verified+assessed guards")
else:
    changes.append("recommend() pattern NOT FOUND")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

# Syntax check
import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSYNTAX ERROR at line {e.lineno}: {e.text}")