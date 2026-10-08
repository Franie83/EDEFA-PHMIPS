"""Diagnostic — show what's in the interventions table right now."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
con = sqlite3.connect(DB)

print("=== Interventions in DB ===")
rows = con.execute(
    "SELECT id, entity_id, data FROM records WHERE entity_type='interventions' ORDER BY id"
).fetchall()
for row_id, eid, data in rows:
    d = json.loads(data)
    print(f"  {eid:<14} status={d.get('approval_status','?'):<20} title={d.get('title','')[:50]}")

print(f"\nTotal: {len(rows)} interventions")

print("\n=== Recent audit entries for interventions ===")
audit = con.execute(
    "SELECT data FROM records WHERE entity_type='audit_logs' ORDER BY id DESC LIMIT 30"
).fetchall()
for (raw,) in audit:
    d = json.loads(raw)
    if 'INTERVENTION' in (d.get('entity_type','') + d.get('action','')):
        print(f"  {d.get('id','')} {d.get('action',''):<35} {d.get('entity_id',''):<15} by {d.get('user_name','')}")

con.close()