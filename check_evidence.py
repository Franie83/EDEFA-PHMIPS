import sqlite3, json
c = sqlite3.connect(r'.\backend\instance\ef_phmips.db')
cur = c.cursor()
cur.execute("SELECT entity_id, data FROM records WHERE entity_type='evidence_files' ORDER BY id")
rows = cur.fetchall()
print(f"Total evidence rows: {len(rows)}\n")
for eid, data in rows:
    try: d = json.loads(data)
    except: d = {}
    print(f"{eid}")
    print(f"  file_name  = {d.get('file_name')}")
    print(f"  file_size  = {d.get('file_size')}")
    print(f"  hazard_id  = {d.get('hazard_id')}")
    print(f"  stage_tag  = {d.get('stage_tag')}")
    print(f"  upload_date= {d.get('upload_date')}")
    print()
c.close()
