import pathlib

# Backend
p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# public_report — validate lat/lng
old_pub = """h={"id":hid,"title":d["title"],"category":d.get("category","Gully erosion"),"hazard_type":d.get("hazard_type") or d.get("category","Environmental hazard"),"description":d.get("description",""),"date_observed":d.get("date_observed",today()),"date_reported":now(),"reporter_name":d.get("reporter_name","Public Reporter"),"reporter_type":"PUBLIC","reporter_contact":d.get("reporter_contact",""),"state":d.get("state","Edo"),"lga":lga,"ward":d.get("ward","Ward 1"),"community":d.get("community","Community"),"address_description":d.get("address_description",""),"latitude":float(d.get("latitude") or 6.335),"longitude":float(d.get("longitude") or 5.603),"""

new_pub = """_lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
h={"id":hid,"title":d["title"],"category":d.get("category","Gully erosion"),"hazard_type":d.get("hazard_type") or d.get("category","Environmental hazard"),"description":d.get("description",""),"date_observed":d.get("date_observed",today()),"date_reported":now(),"reporter_name":d.get("reporter_name","Public Reporter"),"reporter_type":"PUBLIC","reporter_contact":d.get("reporter_contact",""),"state":d.get("state","Edo"),"lga":lga,"ward":d.get("ward","Ward 1"),"community":d.get("community","Community"),"address_description":d.get("address_description",""),"latitude":_lat,"longitude":_lng,"""

if old_pub in src:
    src = src.replace(old_pub, new_pub, 1)
    changes.append("public_report: added coordinate validation")
else:
    changes.append("public_report pattern NOT FOUND")

# hazard_create — validate lat/lng
old_haz = """d=request.get_json(silent=True) or {};u=user();hid=nxt("EH","HAZ");lga=d.get("lga","Oredo");h={"id":hid,"title":d.get("title","Reported Ecological Hazard"),"category":d.get("category","Gully erosion"),"""
new_haz = """d=request.get_json(silent=True) or {};u=user();hid=nxt("EH","HAZ");lga=d.get("lga","Oredo")
_lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
h={"id":hid,"title":d.get("title","Reported Ecological Hazard"),"category":d.get("category","Gully erosion"),"""
if old_haz in src:
    src = src.replace(old_haz, new_haz, 1)
    changes.append("hazard_create: added coordinate validation")
else:
    changes.append("hazard_create pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Backend changes:")
for c in changes:
    print(" -", c)

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text}")