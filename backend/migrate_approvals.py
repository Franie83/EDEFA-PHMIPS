"""
Apply the two-stage approval flow to backend/app.py.

Adds:
  - POST /api/interventions/:id/director-approve
  - POST /api/interventions/:id/executive-approve
  - POST /api/interventions/:id/reject
  - POST /api/projects/:id/executive-approve

Modifies:
  - GET /api/interventions — add ?queue= filter
  - GET /api/projects      — add ?queue= filter
  - POST /api/projects     — require Executive-Approved intervention

Idempotent.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "director_approve_intervention" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# PATCH A — import line
# ============================================================
print("PATCH A: import line")
old_import = """from permissions import (
    TIER_MAP, READONLY_ROLES, TIER_LABELS, LOGIN_GROUPS,
    tier_of, is_readonly, require_tier,
    require_edit, require_delete, can_edit_or_delete,
)"""
new_import = """from permissions import (
    TIER_MAP, READONLY_ROLES, TIER_LABELS, LOGIN_GROUPS,
    tier_of, is_readonly, require_tier,
    require_edit, require_delete, can_edit_or_delete,
    require_director_approve, require_exec_approve,
)"""
if old_import in text:
    text = text.replace(old_import, new_import, 1)
    print("  Updated permissions import.")
elif "require_director_approve" in text:
    print("  Already present.")
else:
    print("  WARNING: import block not found")

# ============================================================
# PATCH B — insert approval endpoints after recommend()
# ============================================================
print("\nPATCH B: approval endpoints")

APPROVAL_ENDPOINTS = '''

# ==================== APPROVAL FLOW ====================

@app.post("/api/interventions/<id>/director-approve")
@require_director_approve()
def director_approve_intervention(id):
    r = one("interventions", id)
    if not r:
        return jsonify({"error": "Intervention not found"}), 404
    d = request.get_json(silent=True) or {}
    i = dict(r.data)
    if i.get("approval_status") not in ("Proposed", "Rejected", None):
        return jsonify({
            "error": "Cannot director-approve from current status",
            "current_status": i.get("approval_status"),
        }), 400
    u = user()
    i["director_approval"] = {
        "approved_by": u.get("name"),
        "approved_by_id": u.get("id"),
        "approved_at": now(),
        "notes": d.get("notes", ""),
    }
    i["approval_status"] = "Director Approved"
    i.pop("rejection_reason", None)
    i.pop("rejected_by", None)
    i.pop("rejected_at", None)
    r.data = i
    audit("DIRECTOR_APPROVE_INTERVENTION", "INTERVENTION", id, old=None, new=i,
          details=f"Director approved intervention {id}")
    notify(f"Intervention {id} awaiting Executive approval",
           f"{id} was approved by Director {u.get('name')}. Awaiting Executive sign-off.",
           "INTERVENTION", f"/interventions/{id}", priority="HIGH")
    db.session.commit()
    return jsonify({"success": True, "intervention": i})


@app.post("/api/interventions/<id>/executive-approve")
@require_exec_approve()
def exec_approve_intervention(id):
    r = one("interventions", id)
    if not r:
        return jsonify({"error": "Intervention not found"}), 404
    d = request.get_json(silent=True) or {}
    i = dict(r.data)
    if i.get("approval_status") != "Director Approved":
        return jsonify({
            "error": "Intervention must be Director Approved before Executive approval",
            "current_status": i.get("approval_status"),
        }), 400
    u = user()
    i["executive_approval"] = {
        "approved_by": u.get("name"),
        "approved_by_id": u.get("id"),
        "approved_at": now(),
        "notes": d.get("notes", ""),
        "approved_amount_ngn": d.get("approved_amount_ngn"),
    }
    i["approval_status"] = "Executive Approved"
    r.data = i
    h_r = one("hazards", i.get("hazard_id", ""))
    if h_r:
        h = dict(h_r.data)
        h["status"] = "Intervention Approved"
        h_r.data = h
    audit("EXECUTIVE_APPROVE_INTERVENTION", "INTERVENTION", id, old=None, new=i,
          details=f"Executive approved intervention {id}")
    notify(f"Intervention {id} fully approved",
           f"{id} was approved by Executive {u.get('name')}. Director may now create the project.",
           "INTERVENTION", f"/interventions/{id}", priority="HIGH")
    db.session.commit()
    return jsonify({"success": True, "intervention": i})


@app.post("/api/interventions/<id>/reject")
@require_tier("TIER_1_ADMIN", "TIER_2_EXEC", "TIER_3_DIRECTOR")
def reject_intervention(id):
    r = one("interventions", id)
    if not r:
        return jsonify({"error": "Intervention not found"}), 404
    d = request.get_json(silent=True) or {}
    reason = d.get("rejection_reason", "").strip()
    if not reason:
        return jsonify({"error": "rejection_reason is required"}), 400
    i = dict(r.data)
    u = user()
    i["approval_status"] = "Proposed"
    i["rejection_reason"] = reason
    i["rejected_by"] = u.get("name")
    i["rejected_at"] = now()
    i.pop("director_approval", None)
    i.pop("executive_approval", None)
    r.data = i
    audit("REJECT_INTERVENTION", "INTERVENTION", id, old=None, new=i,
          details=f"Rejected by {u.get('name')}: {reason}")
    db.session.commit()
    return jsonify({"success": True, "intervention": i})


@app.post("/api/projects/<id>/executive-approve")
@require_exec_approve()
def exec_approve_project(id):
    r = one("projects", id)
    if not r:
        return jsonify({"error": "Project not found"}), 404
    d = request.get_json(silent=True) or {}
    p = dict(r.data)
    if p.get("status") != "Pending Approval":
        return jsonify({
            "error": "Project must be in Pending Approval status",
            "current_status": p.get("status"),
        }), 400
    u = user()
    p["approval"] = {
        "approved_by": u.get("name"),
        "approved_by_id": u.get("id"),
        "approved_at": now(),
        "notes": d.get("notes", ""),
        "approved_amount_ngn": d.get("approved_amount_ngn") or p.get("approved_amount_ngn"),
    }
    p["status"] = "Active"
    r.data = p
    audit("EXECUTIVE_APPROVE_PROJECT", "PROJECT", id, old=None, new=p,
          details=f"Executive approved project {id}")
    notify(f"Project {id} activated",
           f"{id} was approved by Executive {u.get('name')}. Civil works may commence.",
           "PROJECT", f"/projects/{id}", priority="HIGH")
    db.session.commit()
    return jsonify({"success": True, "project": p})
'''

# Find the end of the bulk-verify function (the closest "return jsonify({"success":True,"updated_count":n})")
anchor = 'return jsonify({"success":True,"updated_count":n})'
idx = text.find(anchor)
if idx == -1:
    raise SystemExit("bulk-verify end anchor not found — aborting")

# Insert right after the bulk function's body
insert_at = idx + len(anchor)
text = text[:insert_at] + "\n" + APPROVAL_ENDPOINTS + text[insert_at:]
print("  Inserted 4 approval endpoints.")

# ============================================================
# PATCH C — interventions() — add queue filter
# ============================================================
print("\nPATCH C: interventions queue filter")

old_interventions = '''@app.get("/api/interventions")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def interventions():return jsonify(all_("interventions"))'''

new_interventions = '''@app.get("/api/interventions")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def interventions():
    items = all_("interventions")
    queue = request.args.get("queue")
    if queue == "director":
        items = [x for x in items if x.get("approval_status") in ("Proposed", "Rejected", None)]
    elif queue == "executive":
        items = [x for x in items if x.get("approval_status") == "Director Approved"]
    elif queue == "approved":
        items = [x for x in items if x.get("approval_status") == "Executive Approved"]
    return jsonify(items)'''

if old_interventions in text:
    text = text.replace(old_interventions, new_interventions, 1)
    print("  Added ?queue= filter to /api/interventions")
else:
    print("  WARNING: interventions() not found in expected form")

# ============================================================
# PATCH D — projects() — add queue filter
# ============================================================
print("\nPATCH D: projects queue filter")

old_projects = '''@app.get("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def projects():return jsonify(filtered("projects"))'''

new_projects = '''@app.get("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def projects():
    items = filtered("projects")
    queue = request.args.get("queue")
    if queue == "approval":
        items = [x for x in items if x.get("status") == "Pending Approval"]
    return jsonify(items)'''

if old_projects in text:
    text = text.replace(old_projects, new_projects, 1)
    print("  Added ?queue= filter to /api/projects")
else:
    print("  WARNING: projects() not found in expected form")

# ============================================================
# PATCH E — project_create() — require Exec-Approved intervention + Pending status
# ============================================================
print("\nPATCH E: project_create() rules")

# E1: restrict tier + require intervention
old_pc_head = '''@app.post("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def project_create():
 d=request.get_json(silent=True) or {};n=nxt("PRJ","PRJ");p={"id":n,'''

new_pc_head = '''@app.post("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_3_DIRECTOR")
def project_create():
 d=request.get_json(silent=True) or {}
 intervention_id = d.get("intervention_id") or d.get("linked_intervention_id")
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
 n=nxt("PRJ","PRJ");p={"id":n,"intervention_id":intervention_id,'''

if old_pc_head in text:
    text = text.replace(old_pc_head, new_pc_head, 1)
    print("  Restricted project_create to T1+T3 and require Exec-Approved intervention")
else:
    print("  WARNING: project_create() header not found in expected form")

# E2: change default status from "Active" to "Pending Approval"
old_status = '"status":d.get("status","Active"),"milestones"'
new_status = '"status":"Pending Approval","milestones"'
if old_status in text:
    text = text.replace(old_status, new_status, 1)
    print("  New projects now default to Pending Approval status")
else:
    print("  WARNING: project_create status field not found in expected form")

# E3: after audit, link back intervention to project
old_audit = 'audit("CREATE_PROJECT","PROJECT",n,None,p);db.session.commit();return jsonify(p),201'
new_audit = '''if intervention_id:
     ir2 = one("interventions", intervention_id)
     if ir2:
         iv2 = dict(ir2.data)
         iv2["project_id"] = n
         iv2["implementation_status"] = "Pending Project Approval"
         ir2.data = iv2
 audit("CREATE_PROJECT","PROJECT",n,None,p);db.session.commit();return jsonify(p),201'''
if old_audit in text:
    text = text.replace(old_audit, new_audit, 1)
    print("  Project creation now links back to its intervention")
else:
    print("  WARNING: audit anchor in project_create not found")

# ============================================================
# Save
# ============================================================
TARGET.write_text(text, encoding="utf-8")

print()
print("=" * 60)
print("MIGRATION COMPLETE")
print("=" * 60)
print(f"  {TARGET}")
print()
print("Next: verify syntax, then restart Flask.")