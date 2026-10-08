"""Check PRJ-2026-007 status and approval."""
import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

print("=== PRJ-2026-007 ===")
row = con.execute(
    "SELECT data FROM records WHERE entity_type='projects' AND entity_id='PRJ-2026-007'"
).fetchone()

if not row:
    print("Not found.")
else:
    d = json.loads(row["data"])
    print(f"  Title:    {d.get('title')}")
    print(f"  Status:   {d.get('status')}")
    print(f"  Approved: {d.get('approved_amount_ngn')}")
    print(f"  Contract: {d.get('contract_amount_ngn')}")
    print()
    print("  approval object:")
    print(json.dumps(d.get("approval"), indent=4))

print()
print("=== Last 10 audit entries ===")
for row in con.execute(
    "SELECT data FROM records WHERE entity_type='audit_logs' ORDER BY id DESC LIMIT 10"
).fetchall():
    d = json.loads(row["data"])
    print(f"  {d.get('timestamp', '')[:19]}  {d.get('action', ''):<35}  {d.get('user_name', '')}")

con.close()