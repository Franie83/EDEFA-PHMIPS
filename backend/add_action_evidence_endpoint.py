"""Add POST /api/actions/:id/evidence to backend/app.py."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "/api/actions/<id>/evidence" in text:
    print("Already present — skipping.")
    raise SystemExit(0)

anchor = '@app.delete("/api/actions/<id>")'
if anchor not in text:
    raise SystemExit("Could not find DELETE /api/actions/<id> anchor")

NEW_ENDPOINT = '''@app.post("/api/actions/<id>/evidence")
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

    try:
        ev = evidence_create(d, {"action_id": id})
    except Exception as e:
        return jsonify({"error": f"Evidence upload failed: {e}"}), 400

    ev_files = list(current.get("evidence_files") or [])
    ev_files.append(ev)
    current["evidence_files"] = ev_files
    r.data = current

    audit("UPLOAD_ACTION_EVIDENCE", "ACTION", id, old=None, new=ev,
          details=f"Uploaded evidence for action {id}: {ev.get('file_name')}")
    db.session.commit()
    return jsonify({"success": True, "evidence": ev, "action": current}), 201


'''

text = text.replace(anchor, NEW_ENDPOINT + anchor, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Added POST /api/actions/<id>/evidence")