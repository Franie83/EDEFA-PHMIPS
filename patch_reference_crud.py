import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

if "@app.post(\"/api/reference-data/categories\")" in src:
    print("Reference CRUD endpoints already present")
else:
    block = '''

# ==================== REFERENCE DATA CRUD ====================
# Super-Admin-only endpoints for managing the app's dropdown values.

def _ref_setting():
    s = db.session.get(Setting, "reference_data")
    if not s:
        s = Setting(key="reference_data", value={
            "hazard_categories": ["Gully erosion","Flooding","Landslide","Soil instability","Coastal erosion","Deforestation","Illegal dumping","Desertification","Other"],
            "states_and_lgas": {"Edo":["Akoko Edo","Egor","Esan Central","Esan North-East","Esan South-East","Esan West","Etsako Central","Etsako East","Etsako West","Igueben","Ikpoba-Okha","Oredo","Orhionmwon","Ovia North-East","Ovia South-West","Owan East","Owan West","Uhunmwonde"]},
            "priority_weights": {"severity_weight":0.25,"urgency_weight":0.2,"exposure_weight":0.2,"impact_weight":0.2,"escalation_weight":0.15,"critical_threshold":8.0,"high_threshold":6.5,"medium_threshold":4.0}
        })
        db.session.add(s)
    return s

# ---- Categories ----
@app.get("/api/reference-data/categories")
@require_tier("TIER_1_ADMIN")
def ref_cats_list():
    return jsonify(_ref_setting().value.get("hazard_categories", []))

@app.post("/api/reference-data/categories")
@require_tier("TIER_1_ADMIN")
def ref_cats_add():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    s = _ref_setting()
    cats = list(s.value.get("hazard_categories", []))
    if name in cats:
        return jsonify({"error": "category already exists"}), 409
    cats.append(name)
    s.value = {**s.value, "hazard_categories": cats}
    audit("ADD_REFERENCE_CATEGORY", "SETTINGS", "hazard_categories", old=None, new={"name": name})
    db.session.commit()
    return jsonify({"success": True, "hazard_categories": cats})

@app.delete("/api/reference-data/categories/<path:name>")
@require_tier("TIER_1_ADMIN")
def ref_cats_del(name):
    s = _ref_setting()
    cats = list(s.value.get("hazard_categories", []))
    if name not in cats:
        return jsonify({"error": "category not found"}), 404
    cats = [c for c in cats if c != name]
    s.value = {**s.value, "hazard_categories": cats}
    audit("DELETE_REFERENCE_CATEGORY", "SETTINGS", "hazard_categories", old={"name": name}, new=None)
    db.session.commit()
    return jsonify({"success": True, "hazard_categories": cats})

@app.put("/api/reference-data/categories/<path:old_name>")
@require_tier("TIER_1_ADMIN")
def ref_cats_update(old_name):
    d = request.get_json(silent=True) or {}
    new_name = (d.get("name") or "").strip()
    if not new_name:
        return jsonify({"error": "new name required"}), 400
    s = _ref_setting()
    cats = list(s.value.get("hazard_categories", []))
    if old_name not in cats:
        return jsonify({"error": "category not found"}), 404
    if new_name in cats and new_name != old_name:
        return jsonify({"error": "another category already uses that name"}), 409
    cats = [new_name if c == old_name else c for c in cats]
    s.value = {**s.value, "hazard_categories": cats}
    audit("UPDATE_REFERENCE_CATEGORY", "SETTINGS", "hazard_categories", old={"name": old_name}, new={"name": new_name})
    db.session.commit()
    return jsonify({"success": True, "hazard_categories": cats})

# ---- States ----
@app.post("/api/reference-data/states")
@require_tier("TIER_1_ADMIN")
def ref_states_add():
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "state name required"}), 400
    s = _ref_setting()
    states = dict(s.value.get("states_and_lgas", {}))
    if name in states:
        return jsonify({"error": "state already exists"}), 409
    states[name] = []
    s.value = {**s.value, "states_and_lgas": states}
    audit("ADD_REFERENCE_STATE", "SETTINGS", "states_and_lgas", old=None, new={"name": name})
    db.session.commit()
    return jsonify({"success": True, "states_and_lgas": states})

@app.delete("/api/reference-data/states/<path:name>")
@require_tier("TIER_1_ADMIN")
def ref_states_del(name):
    s = _ref_setting()
    states = dict(s.value.get("states_and_lgas", {}))
    if name not in states:
        return jsonify({"error": "state not found"}), 404
    del states[name]
    s.value = {**s.value, "states_and_lgas": states}
    audit("DELETE_REFERENCE_STATE", "SETTINGS", "states_and_lgas", old={"name": name}, new=None)
    db.session.commit()
    return jsonify({"success": True, "states_and_lgas": states})

# ---- LGAs (nested under a state) ----
@app.post("/api/reference-data/states/<path:state>/lgas")
@require_tier("TIER_1_ADMIN")
def ref_lga_add(state):
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "LGA name required"}), 400
    s = _ref_setting()
    states = dict(s.value.get("states_and_lgas", {}))
    if state not in states:
        return jsonify({"error": f"state '{state}' not found"}), 404
    lgas = list(states.get(state, []))
    if name in lgas:
        return jsonify({"error": "LGA already exists"}), 409
    lgas.append(name)
    states[state] = lgas
    s.value = {**s.value, "states_and_lgas": states}
    audit("ADD_REFERENCE_LGA", "SETTINGS", "states_and_lgas", old=None, new={"state": state, "lga": name})
    db.session.commit()
    return jsonify({"success": True, "states_and_lgas": states})

@app.delete("/api/reference-data/states/<path:state>/lgas/<path:name>")
@require_tier("TIER_1_ADMIN")
def ref_lga_del(state, name):
    s = _ref_setting()
    states = dict(s.value.get("states_and_lgas", {}))
    if state not in states:
        return jsonify({"error": f"state '{state}' not found"}), 404
    lgas = list(states.get(state, []))
    if name not in lgas:
        return jsonify({"error": "LGA not found"}), 404
    lgas = [l for l in lgas if l != name]
    states[state] = lgas
    s.value = {**s.value, "states_and_lgas": states}
    audit("DELETE_REFERENCE_LGA", "SETTINGS", "states_and_lgas", old={"state": state, "lga": name}, new=None)
    db.session.commit()
    return jsonify({"success": True, "states_and_lgas": states})

'''
    # Insert before SPA FALLBACK
    marker = "# ==================== SPA FALLBACK ===================="
    if marker in src:
        src = src.replace(marker, block + marker)
        p.write_text(src, encoding="utf-8")
        print("Added reference-data CRUD endpoints")
    else:
        print("SPA FALLBACK marker not found — paste the last 40 lines of app.py")

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")