"""
Enforce action permissions:
  1. GET /api/actions → role-scoped (T1/T2/Auditor see all; T3/T4 see only their own)
  2. PUT /api/actions/:id → T1/T2 can edit any; T3/T4 can only mark complete + upload evidence
  3. DELETE /api/actions/:id → Super Admin only
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "def _visible_actions" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# 1. Replace the GET /api/actions handler with role-scoped version
# ============================================================
old_get = re.search(
    r'@app\.get\("/api/actions"\)\s*@require_tier\([^\)]+\)\s*def actions\(\):[\s\S]*?return jsonify\(out\)',
    text,
)
if not old_get:
    raise SystemExit("Could not find the existing GET /api/actions handler")

new_get = '''def _visible_actions():
    """Return actions visible to the current user, scoped by role."""
    role = session.get("role", "")
    me = user()
    my_name = me.get("name", "")
    my_id = me.get("id", "")
    all_items = all_("actions")

    # T1, T2, Auditor see everything
    if role in ("SUPER_ADMIN", "EXECUTIVE", "AUDITOR"):
        return all_items, "all"

    # T3, T4 see only their own
    mine = [
        a for a in all_items
        if a.get("responsible_person") == my_name
        or a.get("created_by_id") == my_id
    ]
    return mine, "own"


@app.get("/api/actions")
@require_tier("TIER_1_ADMIN", "TIER_2_EXEC", "TIER_3_DIRECTOR", "TIER_4_STAFF")
def actions():
    items, scope = _visible_actions()
    out = []
    for a in items:
        a = dict(a)
        overdue = (
            a.get("status") not in {"Completed", "Verified", "Closed"}
            and a.get("due_date", "9999") < today()
        )
        a["is_overdue"] = overdue
        a["status"] = "Overdue" if overdue else a.get("status")
        out.append(a)
    return jsonify(out)'''

text = text[:old_get.start()] + new_get + text[old_get.end():]
print("  Rewrote GET /api/actions with role-scoped visibility")

# ============================================================
# 2. Replace the PUT /api/actions/:id handler with permission-enforced version
# ============================================================
old_put = re.search(
    r'@app\.put\("/api/actions/<id>"\)[\s\S]*?return jsonify\(a\)',
    text,
)
if not old_put:
    raise SystemExit("Could not find the existing PUT /api/actions handler")

new_put = '''@app.put("/api/actions/<id>")
@require_tier("TIER_1_ADMIN", "TIER_2_EXEC", "TIER_3_DIRECTOR", "TIER_4_STAFF")
def action_update(id):
    r = one("actions", id)
    if not r:
        return jsonify({"error": "Action not found"}), 404

    role = session.get("role", "")
    me = user()
    my_name = me.get("name", "")
    my_id = me.get("id", "")
    current = dict(r.data)

    # Determine permission level
    can_edit_metadata = role in ("SUPER_ADMIN", "EXECUTIVE")
    is_mine = (
        current.get("responsible_person") == my_name
        or current.get("created_by_id") == my_id
    )

    # Read-only users cannot write at all
    if is_readonly(role):
        return jsonify({"error": "Read-only role"}), 403

    # Enforce: only T1/T2 can edit metadata; T3/T4 can only complete + upload evidence
    if not can_edit_metadata and not is_mine:
        return jsonify({
            "error": "You can only modify your own actions",
            "your_role": role,
        }), 403

    d = request.get_json(silent=True) or {}

    # Metadata fields that only T1/T2 may change
    metadata_fields = {
        "title", "description", "responsible_person", "responsible_organization",
        "priority", "due_date", "status", "intervention_id", "hazard_id", "project_id",
    }

    if not can_edit_metadata:
        # T3/T4 can only set status to Completed/Verified and add evidence
        allowed = {"status", "progress_percentage", "completion_date", "evidence_summary",
                   "verification_comments", "verified_by", "evidence_files"}
        attempted = set(d.keys())
        forbidden = attempted - allowed
        if forbidden:
            return jsonify({
                "error": "Staff and Director can only mark complete and upload evidence",
                "attempted_fields": sorted(forbidden),
                "allowed_fields": sorted(allowed),
            }), 403

    # Merge
    new_data = {**current, **d}

    # Auto-fill completion fields
    if new_data.get("status") == "Completed" and not new_data.get("completion_date"):
        new_data["completion_date"] = today()
        new_data["progress_percentage"] = 100

    if new_data.get("status") == "Verified" and not new_data.get("verified_by"):
        new_data["verified_by"] = my_name

    # Enforce evidence-required-when-completed
    if new_data.get("status") == "Completed":
        ev = new_data.get("evidence_files") or []
        if not ev:
            return jsonify({
                "error": "Evidence is required when marking an action complete",
                "hint": "Upload at least one file via POST /api/actions/<id>/evidence",
            }), 400

    r.data = new_data
    audit("EDIT_ACTION", "ACTION", id, old=current, new=new_data,
          details=f"Edited action {id} — status {new_data.get('status')}")
    db.session.commit()
    return jsonify(new_data)'''

text = text[:old_put.start()] + new_put + text[old_put.end():]
print("  Rewrote PUT /api/actions/:id with permission enforcement")

# ============================================================
# 3. Replace DELETE /api/actions/:id — Super Admin only
# ============================================================
old_del = re.search(
    r'@app\.delete\("/api/actions/<id>"\)[\s\S]*?return jsonify\(\{"success":True,"deleted_id":id\}\)',
    text,
)
if old_del:
    new_del = '''@app.delete("/api/actions/<id>")
@require_tier("TIER_1_ADMIN")
def action_delete(id):
    r = one("actions", id)
    if not r:
        return jsonify({"error": "Action not found"}), 404
    deleted = dict(r.data)
    db.session.delete(r)
    audit("DELETE_ACTION", "ACTION", id, old=deleted, new=None,
          details=f"Deleted action {id} — {deleted.get('title', '')}")
    db.session.commit()
    return jsonify({"success": True, "deleted_id": id})'''
    text = text[:old_del.start()] + new_del + text[old_del.end():]
    print("  Tightened DELETE /api/actions/:id to Super Admin only")

# ============================================================
# 4. Add POST /api/actions/:id/evidence endpoint
# ============================================================
if "/api/actions/<id>/evidence" not in text:
    anchor = '@app.delete("/api/actions/<id>")'
    if anchor not in text:
        raise SystemExit("Could not find anchor to insert evidence endpoint")

    evidence_endpoint = '''@app.post("/api/actions/<id>/evidence")
@require_tier("TIER_1_ADMIN", "TIER_2_EXEC", "TIER_3_DIRECTOR", "TIER_4_STAFF")
def action_evidence_upload(id):
    """Upload a photo or document as evidence for an action."""
    r = one("actions", id)
    if not r:
        return jsonify({"error": "Action not found"}), 404

    role = session.get("role", "")
    me = user()
    my_name = me.get("name", "")
    my_id = me.get("id", "")
    current = dict(r.data)

    if is_readonly(role):
        return jsonify({"error": "Read-only role"}), 403

    # T3/T4 can only upload evidence to their own actions
    if role not in ("SUPER_ADMIN", "EXECUTIVE"):
        is_mine = (
            current.get("responsible_person") == my_name
            or current.get("created_by_id") == my_id
        )
        if not is_mine:
            return jsonify({"error": "You can only upload evidence to your own actions"}), 403

    d = request.get_json(silent=True) or {}
    file_name = d.get("file_name")
    if not file_name:
        return jsonify({"error": "file_name is required"}), 400

    # Use the existing evidence_create helper to store the file
    try:
        ev = evidence_create(d, {"action_id": id})
    except Exception as e:
        return jsonify({"error": f"Evidence upload failed: {e}"}), 400

    # Append to the action's evidence_files array
    ev_files = list(current.get("evidence_files") or [])
    ev_files.append(ev)
    current["evidence_files"] = ev_files
    r.data = current

    audit("UPLOAD_ACTION_EVIDENCE", "ACTION", id, old=None, new=ev,
          details=f"Uploaded evidence for action {id}: {ev.get('file_name')}")
    db.session.commit()
    return jsonify({"success": True, "evidence": ev, "action": current}), 201


@app.delete("/api/actions/<id>")'''

    text = text.replace(anchor, evidence_endpoint, 1)
    print("  Added POST /api/actions/:id/evidence endpoint")

TARGET.write_text(text, encoding="utf-8")
print()
print(f"Patched {TARGET.name}")