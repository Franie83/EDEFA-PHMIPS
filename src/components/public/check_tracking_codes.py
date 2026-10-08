import sqlite3, json

DB = r'.\backend\instance\ef_phmips.db'
c = sqlite3.connect(DB)
cur = c.cursor()

cur.execute("SELECT entity_id, data FROM records WHERE entity_type='hazards' ORDER BY id")
rows = cur.fetchall()
print(f"Total hazards: {len(rows)}\n")

print("Last 10 hazards:")
for entity_id, data in rows[-10:]:
    try:
        payload = json.loads(data)
    except Exception:
        payload = {}
    code = payload.get('tracking_code')
    title = payload.get('title', '')[:40]
    status = payload.get('status', '')
    print(f"  {entity_id:15}  code={code!r:35}  status={status:20}  title={title}")

c.close()