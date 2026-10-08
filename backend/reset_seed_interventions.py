"""Reset the two seed interventions to 'Proposed' so they can flow through
the new Director -> Executive approval chain."""

import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
if not DB.exists():
    raise SystemExit(f"Database not found: {DB}")

con = sqlite3.connect(DB)

SEED_INT_IDS = ["INT-2026-001", "INT-2026-002"]

for iid in SEED_INT_IDS:
    row = con.execute(
        "SELECT id, data FROM records WHERE entity_type='interventions' AND entity_id=?",
        (iid,)
    ).fetchone()
    if not row:
        print(f"  {iid}: not found — skipping")
        continue
    d = json.loads(row[1])
    old_status = d.get("approval_status")
    d["approval_status"] = "Proposed"
    d.pop("approved_by", None)
    d.pop("approved_at", None)
    d.pop("director_approval", None)
    d.pop("executive_approval", None)
    d.pop("project_id", None)
    con.execute("UPDATE records SET data=? WHERE id=?", (json.dumps(d), row[0]))
    print(f"  {iid}: {old_status} -> Proposed")

for pid in ["PRJ-2026-004", "PRJ-2026-005"]:
    row = con.execute(
        "SELECT id, data FROM records WHERE entity_type='projects' AND entity_id=?",
        (pid,)
    ).fetchone()
    if not row:
        print(f"  {pid}: not found — skipping")
        continue
    d = json.loads(row[1])
    old_status = d.get("status")
    d["status"] = "Pending Approval"
    con.execute("UPDATE records SET data=? WHERE id=?", (json.dumps(d), row[0]))
    print(f"  {pid}: {old_status} -> Pending Approval")

con.execute("DELETE FROM counters")
con.commit()
con.close()
print("\nDone. Restart Flask, then re-run the tests.")