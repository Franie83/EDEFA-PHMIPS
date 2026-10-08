"""
Rewrite the mangled project_create() function with a clean, properly-formatted
version that enforces the two-stage approval workflow.

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# Find the entire broken project_create function
start_marker = '@app.post("/api/projects")\n@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")\ndef project_create():'
end_marker = '@app.put("/api/projects/<id>")'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1:
    raise SystemExit("project_create start marker not found")
if end_idx == -1 or end_idx < start_idx:
    raise SystemExit("project_create end marker not found")

CLEAN = '''@app.post("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def project_create():
    d = request.get_json(silent=True) or {}
    intervention_id = d.get("intervention_id") or d.get("linked_intervention_id")

    # Enforce: project must reference an Executive-Approved intervention
    if intervention_id:
        ir = one("interventions", intervention_id)
        if not ir:
            return jsonify({"error": f"Intervention {intervention_id} not found"}), 404
        iv = dict(ir.data)
        if iv.get("approval_status") != "Executive Approved":
            return jsonify({
                "error": "Intervention must be Executive Approved before a project can be created",
                "intervention_id": intervention_id,
                "current_status": iv.get("approval_status"),
            }), 400

    n = nxt("PRJ", "PRJ")
    p = {
        "id": n,
        "intervention_id": intervention_id,
        "title": d.get("title", "New Ecological Fund Intervention Project"),
        "category": d.get("category", "Gully Erosion Control"),
        "description": d.get("description", ""),
        "state": d.get("state", "Edo"),
        "lga": d.get("lga", "Oredo"),
        "ward": d.get("ward", "Ward 1"),
        "community": d.get("community", "Community"),
        "site_name": d.get("site_name", "Primary Intervention Site"),
        "latitude": float(d.get("latitude") or 6.335),
        "longitude": float(d.get("longitude") or 5.603),
        "funding_source": d.get("funding_source", "Federal Ecological Fund Direct Allocation"),
        "approved_amount_ngn": float(d.get("approved_amount_ngn") or 1500000000),
        "contract_amount_ngn": float(d.get("contract_amount_ngn") or 1420000000),
        "contractor": d.get("contractor", "Registered Civil Engineering Contractor"),
        "implementing_agency": d.get("implementing_agency", "Ecological Project Office (EPO)"),
        "project_officer": d.get("project_officer") or user().get("name"),
        "start_date": d.get("start_date", today()),
        "expected_completion_date": d.get("expected_completion_date", ""),
        "planned_percentage": float(d.get("planned_percentage") or 10),
        "actual_percentage": float(d.get("actual_percentage") or 0),
        "status": "Pending Approval",
        "milestones": d.get("milestones", []),
        "remarks": d.get("remarks", "Project registered and assigned to field monitoring team."),
        "created_at": now(),
    }
    put("projects", p)

    # Auto-create a monitoring site for the project
    sid = f"SIT-{len(all_('sites'))+1:03d}"
    put("sites", {
        "id": sid,
        "project_id": n,
        "name": p["site_name"],
        "state": p["state"],
        "lga": p["lga"],
        "community": p["community"],
        "latitude": p["latitude"],
        "longitude": p["longitude"],
        "terrain_type": "Ecological intervention corridor",
        "ecological_zone": "Rainforest / Savannah Watershed",
        "baseline_condition": p["description"],
        "assigned_inspector": user().get("name"),
        "created_at": now(),
    })

    # Link the intervention back to the newly created project
    if intervention_id:
        ir2 = one("interventions", intervention_id)
        if ir2:
            iv2 = dict(ir2.data)
            iv2["project_id"] = n
            iv2["implementation_status"] = "Pending Project Approval"
            ir2.data = iv2

    audit("CREATE_PROJECT", "PROJECT", n, None, p)
    notify(
        f"New Project Pending Approval: {n}",
        f"{p['title']} registered by {user().get('name')}. Awaiting Executive approval.",
        "PROJECT", f"/projects/{n}", priority="HIGH",
    )
    db.session.commit()
    return jsonify(p), 201

'''

text = text[:start_idx] + CLEAN + text[end_idx:]
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Rewrote project_create() with clean multi-line formatting")
print("  - Enforced Executive-Approved intervention requirement")
print("  - Default status: Pending Approval")
print("  - Auto-creates monitoring site")
print("  - Links intervention back to project")
print("  - Notifies on project creation")