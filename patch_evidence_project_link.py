import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# Fix A — visit_create: derive project_id from the visit and pass to evidence_create
old_visit = """ for ev in d.get("evidence") or []:evidence_create(ev,{"project_id":v["project_id"],"site_id":v["site_id"],"visit_id":vid,"latitude":v["gps_latitude"],"longitude":v["gps_longitude"],"stage_tag":d.get("stage_tag","during")})"""

new_visit = """ for ev in d.get("evidence") or []:evidence_create(ev,{"project_id":v.get("project_id") or d.get("project_id") or "","site_id":v.get("site_id") or "","visit_id":vid,"latitude":v["gps_latitude"],"longitude":v["gps_longitude"],"stage_tag":d.get("stage_tag","during")})"""

if old_visit in src:
    src = src.replace(old_visit, new_visit)
    changes.append("visit_create: evidence now inherits project_id")
else:
    changes.append("visit_create evidence pattern NOT FOUND")

# Fix B — hazard_create: if hazard has linked_project_id, propagate to evidence
old_haz = """ for ev in d.get("evidence") or []:evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

new_haz = """ for ev in d.get("evidence") or []:evidence_create(ev,{"hazard_id":hid,"project_id":h.get("linked_project_id") or "","latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})"""

if old_haz in src:
    src = src.replace(old_haz, new_haz)
    changes.append("hazard_create: evidence carries linked project_id")
else:
    changes.append("hazard_create evidence pattern NOT FOUND")

# Fix C — evidence_create: ensure project_id defaults to ""
old_ev = """e={"id":eid,"file_name":name,"file_type":d.get("file_type") or ("video/mp4" if media=="video" else "image/jpeg"),"file_size":int(d.get("file_size") or 0),"media_type":media,"file_url":url or "","uploader_name":user().get("name"),"uploader_id":user().get("id"),"upload_date":now(),"description":d.get("description","Field evidence record"),"gps_latitude":links.get("latitude",d.get("gps_latitude")),"gps_longitude":links.get("longitude",d.get("gps_longitude")),"stage_tag":links.get("stage_tag",d.get("stage_tag","evidence"))};"""

new_ev = """e={"id":eid,"file_name":name,"file_type":d.get("file_type") or ("video/mp4" if media=="video" else "image/jpeg"),"file_size":int(d.get("file_size") or 0),"media_type":media,"file_url":url or "","uploader_name":user().get("name"),"uploader_id":user().get("id"),"upload_date":now(),"description":d.get("description","Field evidence record"),"gps_latitude":links.get("latitude",d.get("gps_latitude")),"gps_longitude":links.get("longitude",d.get("gps_longitude")),"stage_tag":links.get("stage_tag",d.get("stage_tag","evidence")),"project_id":links.get("project_id") or d.get("project_id") or "","site_id":links.get("site_id") or d.get("site_id") or "","visit_id":links.get("visit_id") or d.get("visit_id") or "","hazard_id":links.get("hazard_id") or d.get("hazard_id") or ""};"""

if old_ev in src:
    src = src.replace(old_ev, new_ev)
    changes.append("evidence_create: defaults all foreign keys to ''")
else:
    changes.append("evidence_create pattern NOT FOUND")

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