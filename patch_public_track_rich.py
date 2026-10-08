import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old_track = '''@app.get("/api/public/track/<code>")
def track(code):
 h=next((x for x in all_("hazards") if x.get("tracking_code")==code),None)
 if not h:return jsonify({"error":"Tracking code not found"}),404
 return jsonify({"tracking_code":code,"hazard_id":h["id"],"title":h["title"],"status":h["status"],"date_reported":h["date_reported"],"state":h["state"],"lga":h["lga"],"community":h["community"]})'''

new_track = '''@app.get("/api/public/track/<code>")
def track(code):
 h=next((x for x in all_("hazards") if x.get("tracking_code")==code),None)
 if not h:return jsonify({"error":"Tracking code not found"}),404
 hid=h["id"]
 # Public-safe evidence (photos/videos only, no uploader name/gps)
 ev=[{"id":e.get("id"),"media_type":e.get("media_type"),"file_url":e.get("file_url"),"file_name":e.get("file_name"),"description":e.get("description",""),"stage_tag":e.get("stage_tag",""),"upload_date":e.get("upload_date")} for e in all_("evidence_files") if e.get("hazard_id")==hid and e.get("media_type") in ("photo","video")]
 # Intervention (public-safe fields)
 iv=next((x for x in all_("interventions") if x.get("hazard_id")==hid),None)
 public_intervention=None
 if iv:
  public_intervention={
   "id":iv.get("id"),"title":iv.get("title"),"scope":iv.get("estimated_scope") or iv.get("technical_description",""),
   "estimated_cost_ngn":iv.get("estimated_cost_ngn"),"proposed_funding":iv.get("proposed_funding"),
   "responsible_department":iv.get("responsible_department"),
   "proposed_start_date":iv.get("proposed_start_date"),"proposed_completion_date":iv.get("proposed_completion_date"),
   "expected_outcome":iv.get("expected_outcome"),
   "approval_status":iv.get("approval_status"),
  }
 # Project (public-safe fields)
 pr=None
 if iv and iv.get("project_id"):
  proj=one("projects",iv["project_id"])
  if proj:
   pdata=dict(proj.data)
   pr={
    "id":pdata.get("id"),"title":pdata.get("title"),"status":pdata.get("status"),
    "community":pdata.get("community"),"lga":pdata.get("lga"),"state":pdata.get("state"),
    "contractor":pdata.get("contractor"),"implementing_agency":pdata.get("implementing_agency"),
    "approved_amount_ngn":pdata.get("approved_amount_ngn"),"contract_amount_ngn":pdata.get("contract_amount_ngn"),
    "funding_source":pdata.get("funding_source"),
    "start_date":pdata.get("start_date"),"expected_completion_date":pdata.get("expected_completion_date"),
    "planned_percentage":pdata.get("planned_percentage"),"actual_percentage":pdata.get("actual_percentage"),
    "description":pdata.get("description",""),
   }
 # Project evidence (photos linked to the project, tagged during/after)
 project_evidence=[]
 if pr:
  project_evidence=[{"id":e.get("id"),"media_type":e.get("media_type"),"file_url":e.get("file_url"),"file_name":e.get("file_name"),"description":e.get("description",""),"stage_tag":e.get("stage_tag",""),"upload_date":e.get("upload_date")} for e in all_("evidence_files") if e.get("project_id")==pr["id"] and e.get("media_type") in ("photo","video")]
 # Merge and dedupe by id
 seen=set(); merged=[]
 for e in ev+project_evidence:
  if e["id"] in seen: continue
  seen.add(e["id"]); merged.append(e)
 # Timeline of public-facing stages
 timeline=[]
 timeline.append({"stage":"Reported","date":h.get("date_reported"),"done":True})
 timeline.append({"stage":"Verified","date":h.get("verified_at"),"done":bool(h.get("verified_by"))})
 timeline.append({"stage":"Assessed","date":(h.get("assessment") or {}).get("assessed_at"),"done":bool(h.get("assessment"))})
 timeline.append({"stage":"Intervention Planned","date":(iv or {}).get("created_at"),"done":bool(iv)})
 timeline.append({"stage":"Intervention Approved","date":((iv or {}).get("executive_approval") or {}).get("approved_at"),"done":(iv or {}).get("approval_status")=="Executive Approved"})
 timeline.append({"stage":"Project Registered","date":(pr or {}).get("start_date") if pr else None,"done":bool(pr)})
 timeline.append({"stage":"Completed","date":(pr or {}).get("expected_completion_date") if pr and pr.get("actual_percentage",0)>=100 else None,"done":bool(pr and pr.get("actual_percentage",0)>=100)})
 return jsonify({
  "tracking_code":code,
  "hazard_id":hid,
  "title":h["title"],
  "category":h.get("category",""),
  "description":h.get("description",""),
  "status":h["status"],
  "severity":h.get("severity",""),
  "date_reported":h["date_reported"],
  "state":h["state"],
  "lga":h["lga"],
  "community":h.get("community",""),
  "evidence":merged,
  "intervention":public_intervention,
  "project":pr,
  "timeline":timeline,
 })'''

if old_track in src:
    src = src.replace(old_track, new_track)
    p.write_text(src, encoding="utf-8")
    print("Extended public track endpoint with evidence + intervention + project + timeline")
else:
    print("Pattern not found — paste the current def track() block")

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text}")