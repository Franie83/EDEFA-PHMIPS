"""Add PUT and DELETE endpoints for contractors."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "/api/contractors/<id>" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

anchor = '''@app.post("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def contractor_create():'''

new_endpoints = '''@app.put("/api/contractors/<id>")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR")
def contractor_update(id):
    r = one("contractors", id)
    if not r:
        return jsonify({"error": "Contractor not found"}), 404
    d = request.get_json(silent=True) or {}
    old = dict(r.data)
    immutable = {"id", "created_at"}
    new = {**old, **{k: v for k, v in d.items() if k not in immutable}}
    r.data = new
    audit("EDIT_CONTRACTOR", "CONTRACTOR", id, old=old, new=new,
          details=f"Edited contractor {new.get('name', '')}")
    db.session.commit()
    return jsonify(new)


@app.delete("/api/contractors/<id>")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR")
def contractor_delete(id):
    """Soft-delete: sets active=False so historical project references stay intact."""
    r = one("contractors", id)
    if not r:
        return jsonify({"error": "Contractor not found"}), 404
    d = dict(r.data)
    old_active = d.get("active", True)
    d["active"] = False
    d["deactivated_at"] = now()
    r.data = d
    audit("DEACTIVATE_CONTRACTOR", "CONTRACTOR", id, old={"active": old_active}, new={"active": False},
          details=f"Deactivated contractor {d.get('name', '')}")
    db.session.commit()
    return jsonify({"success": True, "deactivated_id": id})


@app.post("/api/contractors")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def contractor_create():'''

if anchor not in text:
    raise SystemExit("contractor_create anchor not found in app.py")

text = text.replace(anchor, new_endpoints, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added PUT /api/contractors/<id>")
print("  Added DELETE /api/contractors/<id>")