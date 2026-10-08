"""
Add GET /api/contractors to backend/app.py.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "/api/contractors" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Insert right after the /api/sites GET endpoint (or anywhere in the SITES section)
anchor = '''# ==================== SITES / VISITS ====================
@app.get("/api/sites")'''

new_block = '''# ==================== CONTRACTORS ====================
@app.get("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def contractors():
    items = all_("contractors")
    active_only = request.args.get("active") in ("1", "true", "yes")
    if active_only:
        items = [x for x in items if x.get("active", True)]
    return jsonify(items)

@app.post("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def contractor_create():
    d = request.get_json(silent=True) or {}
    cid = nxt("CON", "contractors")
    c = {
        "id": cid,
        "name": d.get("name", "Unnamed Contractor"),
        "registration_no": d.get("registration_no", ""),
        "category": d.get("category", "Regional Contractor"),
        "specialties": d.get("specialties", []),
        "contact_person": d.get("contact_person", ""),
        "phone": d.get("phone", ""),
        "email": d.get("email", ""),
        "address": d.get("address", ""),
        "state": d.get("state", "Edo"),
        "active": d.get("active", True),
        "rating": float(d.get("rating") or 0),
        "created_at": now(),
    }
    put("contractors", c)
    audit("CREATE_CONTRACTOR", "CONTRACTOR", cid, None, c, details=f"Registered contractor {c['name']}")
    db.session.commit()
    return jsonify(c), 201

# ==================== SITES / VISITS ====================
@app.get("/api/sites")'''

if anchor not in text:
    raise SystemExit("SITES section anchor not found in app.py")

text = text.replace(anchor, new_block, 1)

# Update nxt() entity_map to know about CON
old_map = '"EVD":"evidence_files","INT":"interventions","ACT":"actions",'
new_map = '"EVD":"evidence_files","INT":"interventions","ACT":"actions","CON":"contractors",'
if old_map in text:
    text = text.replace(old_map, new_map, 1)
    print("  Updated nxt() entity_map to include CON")
else:
    print("  WARNING: nxt() entity_map not found")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added GET /api/contractors")
print("  Added POST /api/contractors")