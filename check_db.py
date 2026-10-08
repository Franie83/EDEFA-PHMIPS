import os
import pathlib
import sqlite3

INSTANCE = pathlib.Path("backend/instance").resolve()
db = INSTANCE / "ef_phmips.db"

print("INSTANCE:", INSTANCE)
print("DB exists:", db.exists())
print("DB path:", db)
print("Default URI:", f"sqlite:///{db}")            # what app.py currently builds
print("Fixed URI:  ", f"sqlite:///{db.as_posix()}") # what it should build

# Try opening directly with sqlite3 using the Windows path
try:
    conn = sqlite3.connect(str(db))
    print("sqlite3 direct open: OK")
    conn.close()
except Exception as e:
    print("sqlite3 direct open FAILED:", e)