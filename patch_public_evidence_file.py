import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = '''@app.get("/api/evidence/file/<path:name>")
@require_tier("TIER_1_ADMIN","TIER_2_EXEC","TIER_3_DIRECTOR","TIER_4_STAFF")
def file(name):
 safe=secure_filename(Path(name).name)
 if safe!=Path(name).name:return jsonify({"error":"Invalid filename"}),400
 return send_from_directory(UPLOADS,safe)'''

new = '''@app.get("/api/evidence/file/<path:name>")
def file(name):
 # Public endpoint: evidence files are served without auth so public trackers can display them.
 # Filenames include random UUIDs, so they are effectively unguessable. No sensitive metadata.
 safe=secure_filename(Path(name).name)
 if safe!=Path(name).name:return jsonify({"error":"Invalid filename"}),400
 return send_from_directory(UPLOADS,safe)'''

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Made /api/evidence/file/<name> public")
elif "Public endpoint: evidence files are served" in src:
    print("Already public — no change")
else:
    print("Pattern not found. Paste the current def file() block:")
    import re
    m = re.search(r'@app\.get\("/api/evidence/file/<path:name>"\).{0,500}', src, re.DOTALL)
    if m:
        print(m.group(0))

import ast
try:
    ast.parse(src)
    print("SYNTAX OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text}")