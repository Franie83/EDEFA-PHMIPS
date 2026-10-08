import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

if "@app.post(\"/api/reference-data/lists/" in src:
    print("Generic list endpoints already present")
else:
    block = '''

# ==================== GENERIC REFERENCE LIST CRUD ====================
# Allows the CMS to manage ANY list in reference_data by key.
# e.g. severities, urgencies, reporter_types, hazard_types,
#      funding_sources, departments, implementing_agencies,
#      priorities, inspection_stages

@app.get("/api/reference-data/lists")
@require_tier("TIER_1_ADMIN")
def ref_list_keys():
    s = _ref_setting()
    # Return only keys that are simple string arrays (not dicts)
    out = {}
    for k, v in s.value.items():
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            out[k] = v
    return jsonify(out)

@app.post("/api/reference-data/lists/<path:key>")
@require_tier("TIER_1_ADMIN")
def ref_list_add(key):
    d = request.get_json(silent=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    if not key.replace("_", "").isalnum():
        return jsonify({"error": "invalid key"}), 400
    s = _ref_setting()
    current = list(s.value.get(key, []))
    if name in current:
        return jsonify({"error": "value already exists"}), 409
    current.append(name)
    s.value = {**s.value, key: current}
    audit(f"ADD_REFERENCE_{key.upper()}", "SETTINGS", key, old=None, new={"name": name})
    db.session.commit()
    return jsonify({"success": True, "key": key, "values": current})

@app.delete("/api/reference-data/lists/<path:key>/<path:name>")
@require_tier("TIER_1_ADMIN")
def ref_list_del(key, name):
    s = _ref_setting()
    current = list(s.value.get(key, []))
    if name not in current:
        return jsonify({"error": "value not found"}), 404
    current = [x for x in current if x != name]
    s.value = {**s.value, key: current}
    audit(f"DELETE_REFERENCE_{key.upper()}", "SETTINGS", key, old={"name": name}, new=None)
    db.session.commit()
    return jsonify({"success": True, "key": key, "values": current})

@app.put("/api/reference-data/lists/<path:key>/<path:old_name>")
@require_tier("TIER_1_ADMIN")
def ref_list_update(key, old_name):
    d = request.get_json(silent=True) or {}
    new_name = (d.get("name") or "").strip()
    if not new_name:
        return jsonify({"error": "new name required"}), 400
    s = _ref_setting()
    current = list(s.value.get(key, []))
    if old_name not in current:
        return jsonify({"error": "value not found"}), 404
    if new_name in current and new_name != old_name:
        return jsonify({"error": "another value already uses that name"}), 409
    current = [new_name if x == old_name else x for x in current]
    s.value = {**s.value, key: current}
    audit(f"UPDATE_REFERENCE_{key.upper()}", "SETTINGS", key, old={"name": old_name}, new={"name": new_name})
    db.session.commit()
    return jsonify({"success": True, "key": key, "values": current})

# Seed default lists if they don't exist yet
def _seed_default_lists():
    s = db.session.get(Setting, "reference_data")
    if not s:
        return
    defaults = {
        "hazard_types": [
            "Gully head advance", "Ravine expansion", "Riverbank scour",
            "Drainage blockage", "Flash flooding", "Slope failure",
            "Illegal dumping", "Deforestation", "Other"
        ],
        "severities": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "urgencies": ["NORMAL", "HIGH", "IMMEDIATE"],
        "reporter_types": ["PUBLIC", "FIELD_OFFICER", "LGA_OFFICIAL", "COMMUNITY_LEADER"],
        "priorities": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        "funding_sources": [
            "Federal Ecological Fund Direct Allocation",
            "Federal Ecological Fund (EPO)",
            "State-Federal Ecological Matching Grant",
            "State Government Counterpart Fund",
            "Ecological Fund Emergency Intervention Envelope"
        ],
        "departments": [
            "Engineering Directorate",
            "Urban Drainage & Flood Mitigation Unit",
            "Engineering & Ecological Risk Directorate",
            "Soil Erosion and Flood Control Department",
            "Ecological Project Office (EPO)"
        ],
        "implementing_agencies": [
            "Ecological Project Office (EPO)",
            "State Ministry of Environment",
            "Federal Ministry of Environment"
        ],
        "inspection_stages": ["Initial", "Visit 1", "Visit 2", "Visit 3", "Current", "Follow-up"]
    }
    changed = False
    for k, v in defaults.items():
        if k not in s.value:
            s.value = {**s.value, k: v}
            changed = True
    if changed:
        db.session.commit()

# Run the seeder once at import time
with app.app_context():
    try:
        _seed_default_lists()
    except Exception as _e:
        print("[reference_data seeder] skipped:", _e)

'''
    marker = "# ==================== SPA FALLBACK ===================="
    if marker in src:
        src = src.replace(marker, block + marker)
        p.write_text(src, encoding="utf-8")
        print("Added generic reference list CRUD + default seeder")
    else:
        print("SPA FALLBACK marker not found")

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text}")