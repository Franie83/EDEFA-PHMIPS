import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

if "/api/admin/backfill-evidence-project" in src:
    print("Backfill endpoint already present")
else:
    block = '''

# ==================== ADMIN: backfill evidence.project_id ====================
@app.post("/api/admin/backfill-evidence-project")
@require_tier("TIER_1_ADMIN")
def backfill_evidence_project():
    """One-shot: fill in project_id for evidence rows linked to visits/hazards that have one."""
    fixed = 0
    ev_rows = db.session.execute(select(Record).where(Record.entity_type == "evidence_files")).scalars()
    for r in ev_rows:
        d = dict(r.data)
        if d.get("project_id"):
            continue
        # Try to derive from visit
        if d.get("visit_id"):
            v = db.session.execute(select(Record).where(
                Record.entity_type == "site_visits",
                Record.entity_id == d["visit_id"]
            )).scalar_one_or_none()
            if v and v.data.get("project_id"):
                d["project_id"] = v.data["project_id"]
                r.data = d
                fixed += 1
                continue
        # Try to derive from hazard
        if d.get("hazard_id"):
            h = db.session.execute(select(Record).where(
                Record.entity_type == "hazards",
                Record.entity_id == d["hazard_id"]
            )).scalar_one_or_none()
            if h and h.data.get("linked_project_id"):
                d["project_id"] = h.data["linked_project_id"]
                r.data = d
                fixed += 1
                continue
    db.session.commit()
    audit("BACKFILL_EVIDENCE_PROJECT", "SETTINGS", "evidence_files", old=None, new={"fixed": fixed})
    return jsonify({"success": True, "fixed": fixed})

'''
    marker = "# ==================== SPA FALLBACK ===================="
    if marker in src:
        src = src.replace(marker, block + marker)
        p.write_text(src, encoding="utf-8")
        print("Added backfill endpoint")

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text}")