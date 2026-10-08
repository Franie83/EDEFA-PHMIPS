import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")
changes = []

# Fix hazard_create — indent the three inserted lines by one space
old_haz = """ d=request.get_json(silent=True) or {};u=user();hid=nxt("EH","HAZ");lga=d.get("lga","Oredo")
_lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
h={"id":hid,"title":d.get("title","Reported Ecological Hazard")"""

new_haz = """ d=request.get_json(silent=True) or {};u=user();hid=nxt("EH","HAZ");lga=d.get("lga","Oredo")
 _lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
 if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
 if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
 h={"id":hid,"title":d.get("title","Reported Ecological Hazard")"""

if old_haz in src:
    src = src.replace(old_haz, new_haz)
    changes.append("hazard_create: indented validation lines")
else:
    changes.append("hazard_create pattern NOT FOUND")

# Also update the leftover float() calls inside the h dict to use _lat/_lng
src = src.replace(
    '"latitude":float(d.get("latitude") or 6.335),"longitude":float(d.get("longitude") or 5.603),"estimated_affected_area_sqm"',
    '"latitude":_lat,"longitude":_lng,"estimated_affected_area_sqm"',
    1
)

# Fix public_report — indent the three inserted lines by one space
old_pub = """ d=request.get_json(silent=True) or {};d["reporter_type"]="PUBLIC"; 
 d["title"]=d.get("title","Public Ecological Hazard Report");hid=nxt("EH","HAZ");lga=d.get("lga","Oredo");_lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
h={"id":hid,"title":d["title"]"""

new_pub = """ d=request.get_json(silent=True) or {};d["reporter_type"]="PUBLIC"; 
 d["title"]=d.get("title","Public Ecological Hazard Report");hid=nxt("EH","HAZ");lga=d.get("lga","Oredo");_lat=float(d.get("latitude") or 6.335);_lng=float(d.get("longitude") or 5.603)
 if not (-90<=_lat<=90):return jsonify({"error":"Latitude must be between -90 and 90"}),400
 if not (-180<=_lng<=180):return jsonify({"error":"Longitude must be between -180 and 180"}),400
 h={"id":hid,"title":d["title"]"""

if old_pub in src:
    src = src.replace(old_pub, new_pub)
    changes.append("public_report: indented validation lines")
else:
    changes.append("public_report pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

import ast
try:
    ast.parse(src)
    print("\nSYNTAX OK")
except SyntaxError as e:
    print(f"\nSTILL BROKEN at line {e.lineno}: {e.text}")