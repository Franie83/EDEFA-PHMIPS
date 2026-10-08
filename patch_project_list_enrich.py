"""
patch_project_list_enrich.py
Makes GET /api/projects attach sites, site_visits, linked_hazards, evidence_files
to each project — matching what GET /api/projects/<id> already does.
"""
import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

if "sites_all   = all_(" in src or "sites_all = all_(" in src:
    print("Already patched — nothing to do.")
    raise SystemExit(0)

# Verbatim from backend/app.py lines 624-631
old = '''@app.get("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def projects():
    items = filtered("projects")
    queue = request.args.get("queue")
    if queue == "approval":
        items = [x for x in items if x.get("status") == "Pending Approval"]
    return jsonify(items)
'''

new = '''@app.get("/api/projects")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def projects():
    items = filtered("projects")
    queue = request.args.get("queue")
    if queue == "approval":
        items = [x for x in items if x.get("status") == "Pending Approval"]
    # Enrich each project with nested relations (parity with GET /api/projects/<id>)
    sites_all   = all_("sites")
    visits_all  = all_("site_visits")
    hazards_all = all_("hazards")
    evid_all    = all_("evidence_files")
    enriched = []
    for prj in items:
        pid = prj.get("id")
        enriched.append({
            **prj,
            "sites":          [s for s in sites_all   if s.get("project_id") == pid],
            "site_visits":    [v for v in visits_all  if v.get("project_id") == pid],
            "linked_hazards": [h for h in hazards_all if h.get("linked_project_id") == pid],
            "evidence_files": [e for e in evid_all    if e.get("project_id") == pid],
        })
    return jsonify(enriched)
'''

if old not in src:
    print("Exact handler NOT FOUND — paste lines 624-631 verbatim and I'll adjust.")
    raise SystemExit(1)

src = src.replace(old, new, 1)
p.write_text(src, encoding="utf-8")

print("Changes:")
print(" - enriched GET /api/projects with sites/site_visits/linked_hazards/evidence_files")
print()
print("Restart the backend to pick up the change (.\restart-backend.ps1)")