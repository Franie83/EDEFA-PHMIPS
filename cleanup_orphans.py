import sqlite3, json
c = sqlite3.connect(r'.\backend\instance\ef_phmips.db')
cur = c.cursor()
cur.execute("SELECT id, data FROM records WHERE entity_type='evidence_files'")
orphans = []
for row_id, data in cur.fetchall():
    try: d = json.loads(data)
    except: d = {}
    h = (d.get('hazard_id') or '').strip()
    p = (d.get('project_id') or '').strip()
    v = (d.get('visit_id') or '').strip()
    s = (d.get('site_id') or '').strip()
    if not (h or p or v or s):
        orphans.append((row_id, d.get('id'), d.get('file_name')))
print(f"Orphans found: {len(orphans)}")
for rid, eid, name in orphans:
    print(f"  {eid}  {name}")
confirm = input("\nType YES to delete these rows: ")
if confirm == "YES":
    for rid, _, _ in orphans:
        cur.execute("DELETE FROM records WHERE id = ?", (rid,))
    c.commit()
    print(f"Deleted {len(orphans)} rows.")
else:
    print("Aborted.")
c.close()
