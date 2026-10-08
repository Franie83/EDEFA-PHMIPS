"""One-shot: drop counter rows so they recompute from actual records."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "instance" / "ef_phmips.db"
con = sqlite3.connect(DB)

print("Before:")
for row in con.execute("SELECT key, value FROM counters").fetchall():
    print(f"  {row[0]} = {row[1]}")

con.execute("DELETE FROM counters")
con.commit()

print("\nAfter (empty):")
print(con.execute("SELECT key, value FROM counters").fetchall())

con.close()
print("\nDone. Next hazard/project/etc. will compute max from existing records.")