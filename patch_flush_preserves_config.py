import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- FIX 1: clear_seed_data preserves reference_data + system_settings + branding ----------
old_clear = """def clear_seed_data():
 quick_ids={u.get("id") for u in _raw("users") if u.get("quick_access")}
 if not quick_ids:
  ensure_quick_access_users(); quick_ids={u.get("id") for u in _raw("users") if u.get("quick_access")}
 for r in db.session.query(Record).all():
  if r.entity_type=="users" and r.entity_id in quick_ids: continue
  db.session.delete(r)
 db.session.query(Setting).delete(); db.session.query(Counter).delete(); db.session.commit(); ensure_quick_access_users()"""

new_clear = """def clear_seed_data():
 quick_ids={u.get("id") for u in _raw("users") if u.get("quick_access")}
 if not quick_ids:
  ensure_quick_access_users(); quick_ids={u.get("id") for u in _raw("users") if u.get("quick_access")}
 # Preserve configuration settings before wiping records
 preserved_settings={}
 for s in db.session.query(Setting).all():
  preserved_settings[s.key]=s.value
 for r in db.session.query(Record).all():
  if r.entity_type=="users" and r.entity_id in quick_ids: continue
  db.session.delete(r)
 # Only delete Setting rows that are NOT config
 CONFIG_KEYS={"reference_data","system_settings","branding"}
 db.session.query(Setting).filter(~Setting.key.in_(CONFIG_KEYS)).delete(synchronize_session=False)
 db.session.query(Counter).delete()
 # Re-add any missing config rows from what we captured (in case flush happened before this fix)
 for k,v in preserved_settings.items():
  if k in CONFIG_KEYS and not db.session.get(Setting,k):
   db.session.add(Setting(key=k, value=v))
 db.session.commit(); ensure_quick_access_users()"""

if old_clear in src:
    src = src.replace(old_clear, new_clear)
    changes.append("clear_seed_data: preserves reference_data / system_settings / branding")
else:
    changes.append("clear_seed_data pattern NOT FOUND")

# ---------- FIX 2: reference-data endpoint self-heals ----------
old_ref = """@app.get("/api/reference-data")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def ref():return jsonify(db.session.get(Setting,"reference_data").value)"""

new_ref = """@app.get("/api/reference-data")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def ref():
 s=db.session.get(Setting,"reference_data")
 if not s:
  s=Setting(key="reference_data",value={"hazard_categories":["Gully erosion","Flooding","Landslide","Soil instability","Coastal erosion","Deforestation","Illegal dumping","Desertification","Other"],"states_and_lgas":{"Edo":["Akoko Edo","Egor","Esan Central","Esan North-East","Esan South-East","Esan West","Etsako Central","Etsako East","Etsako West","Igueben","Ikpoba-Okha","Oredo","Orhionmwon","Ovia North-East","Ovia South-West","Owan East","Owan West","Uhunmwonde"]},"priority_weights":{"severity_weight":0.25,"urgency_weight":0.2,"exposure_weight":0.2,"impact_weight":0.2,"escalation_weight":0.15,"critical_threshold":8.0,"high_threshold":6.5,"medium_threshold":4.0}})
  db.session.add(s);db.session.commit()
 return jsonify(s.value)"""

if old_ref in src:
    src = src.replace(old_ref, new_ref)
    changes.append("GET /api/reference-data: self-heals with defaults")
else:
    changes.append("reference-data GET pattern NOT FOUND")

# ---------- FIX 3: settings endpoint self-heals ----------
old_set = """@app.get("/api/settings")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC")
def settings():return jsonify(db.session.get(Setting,"system_settings").value)"""

new_set = """@app.get("/api/settings")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC")
def settings():
 s=db.session.get(Setting,"system_settings")
 if not s:
  s=Setting(key="system_settings",value={"organization_name":"Edo State Ecological Fund Agency (EDEFA)","department_name":"Ecological Hazard Management & GIS"})
  db.session.add(s);db.session.commit()
 return jsonify(s.value)"""

if old_set in src:
    src = src.replace(old_set, new_set)
    changes.append("GET /api/settings: self-heals with defaults")
else:
    changes.append("settings GET pattern NOT FOUND")

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