import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = (
    '"tracking_code":f"EF-HAZ-{today().replace(\'-\',\'\')}-{re.sub(r\'[^A-Za-z0-9]\',\'\',lga)[:4].upper()}"};'
    'put("hazards",h);'
    'audit("PUBLIC_SUBMIT_HAZARD","HAZARD",hid,None,{"title":h["title"],"tracking_code":h["tracking_code"]},"Public anonymous report");'
    'db.session.commit();'
    'return jsonify({"success":True,"tracking_code":h["tracking_code"],"hazard_id":hid,"message":"Ecological hazard report submitted successfully."}),201'
)

new = (
    '"tracking_code":f"EF-HAZ-{today().replace(\'-\',\'\')}-{re.sub(r\'[^A-Za-z0-9]\',\'\',lga)[:4].upper()}"};'
    'put("hazards",h)'
    ';'
    'for ev in d.get("evidence") or []:'
    ' evidence_create(ev,{"hazard_id":hid,"latitude":h["latitude"],"longitude":h["longitude"],"stage_tag":"before"})'
    ';'
    'audit("PUBLIC_SUBMIT_HAZARD","HAZARD",hid,None,{"title":h["title"],"tracking_code":h["tracking_code"]},"Public anonymous report");'
    'db.session.commit();'
    'return jsonify({"success":True,"tracking_code":h["tracking_code"],"hazard_id":hid,"message":"Ecological hazard report submitted successfully."}),201'
)

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched public_report() to accept evidence array")
elif 'for ev in d.get("evidence") or []:' in src and 'PUBLIC_SUBMIT_HAZARD' in src:
    print("Already patched — evidence already handled in public_report()")
else:
    print("Pattern not found. Manual edit needed.")
    # Print the current public_report block to help debug
    import re
    m = re.search(r'def public_report\(\):.{0,800}', src, re.DOTALL)
    if m:
        print("\nCurrent public_report body:")
        print(m.group(0))