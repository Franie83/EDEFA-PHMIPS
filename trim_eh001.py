import sqlite3, json
c = sqlite3.connect(r'.\backend\instance\ef_phmips.db')
cur = c.cursor()
cur.execute("SELECT id, data FROM records WHERE entity_type='evidence_files'")
rows = []
for row_id, data in cur.fetchall():
    try: d = json.loads(data)
    except: d = {}
    if d.get('hazard_id') == 'EH-2026-001':
        rows.append((row_id, d.get('id'), d.get('file_name'), d.get('upload_date')))
rows.sort(key=lambda r: r[3] or '')
print("Evidence rows for EH-2026-001:")
for rid, eid, name, date in rows:
    print(f"  {eid}  {date}  {(name or '')[:50]}")
print()
keep_id = rows[-1][1] if rows else None
print(f"Keeping newest: {keep_id}")
confirm = input("\nType YES to delete all but the newest: ")
if confirm == "YES":
    deleted = 0
    for rid, eid, _, _ in rows:
        if eid == keep_id: continue
        cur.execute("DELETE FROM records WHERE id = ?", (rid,))
        deleted += 1
    c.commit()
    print(f"Deleted {deleted} old rows.")
else:
    print("Aborted.")
c.close()
