import sqlite3, json
c = sqlite3.connect(r'.\backend\instance\ef_phmips.db')
cur = c.cursor()
cur.execute("SELECT entity_id, data FROM records WHERE entity_type='hazards' ORDER BY id")
rows = cur.fetchall()
print(f"Total hazards: {len(rows)}")
for entity_id, data in rows[-10:]:
    try: payload = json.loads(data)
    except: payload = {}
    print(f"  {entity_id:15}  code={payload.get('tracking_code')!r:35}  title={(payload.get('title') or '')[:40]}")
c.close()
