import sqlite3
import json

DB = r'.\backend\instance\ef_phmips.db'
HAZARD_ID = 'EH-2026-002'

c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
cur = c.cursor()

cur.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type='hazards' AND entity_id=?",
    (HAZARD_ID,)
)
row = cur.fetchone()
if not row:
    print("Not found")
    raise SystemExit(1)

payload = json.loads(row['data'])
print("BEFORE:")
print(f"  id           = {payload.get('id')}")
print(f"  title        = {payload.get('title')}")
print(f"  latitude     = {payload.get('latitude')}")
print(f"  longitude    = {payload.get('longitude')}")
print(f"  community    = {payload.get('community')}")
print(f"  lga          = {payload.get('lga')}")
print(f"  state        = {payload.get('state')}")
print()

# Fix: EH-2026-002 is "Ugbogui, Oredo, Edo". Ugbogui is roughly at
# lat 6.3350, lon 5.6250 (just outside Benin City to the northwest).
OLD_LON = payload.get('longitude')
payload['longitude'] = 5.6250

# Also sanity-check latitude while we're here
if not (-90 <= float(payload['latitude']) <= 90):
    print(f"WARNING: latitude also invalid: {payload['latitude']}")
if not (-180 <= payload['longitude'] <= 180):
    print(f"WARNING: new longitude still invalid: {payload['longitude']}")

cur.execute(
    "UPDATE records SET data=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
    (json.dumps(payload), row['id'])
)
c.commit()

print("AFTER:")
print(f"  latitude     = {payload.get('latitude')}  (unchanged)")
print(f"  longitude    = {OLD_LON}  →  {payload.get('longitude')}")
print()
print("Saved.")
c.close()