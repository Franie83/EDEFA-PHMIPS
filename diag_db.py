import os, pathlib, sqlalchemy

ROOT = pathlib.Path("backend").resolve()
INSTANCE = ROOT / "instance"
db = INSTANCE / "ef_phmips.db"

print("ROOT exists:", ROOT.exists(), "->", ROOT)
print("INSTANCE exists:", INSTANCE.exists(), "->", INSTANCE)
print("DB exists:", db.exists(), "->", db)
print("DB size:", db.stat().st_size if db.exists() else "N/A")

# Build the exact URI the app builds
posix = db.as_posix().lstrip("/")
uri = f"sqlite:////{posix}"
print("URI:", uri)

# Try three different URI styles
for label, u in [
    ("four-slash posix", uri),
    ("three-slash posix", f"sqlite:///{db.as_posix()}"),
    ("plain as_posix", str(db.as_posix())),
]:
    try:
        eng = sqlalchemy.create_engine(u)
        c = eng.connect()
        c.close()
        print(f"  [{label}] OK -> {u}")
    except Exception as e:
        print(f"  [{label}] FAIL -> {u}  :: {e}")

# Also try raw sqlite3 with the plain path
import sqlite3
try:
    c = sqlite3.connect(str(db))
    c.close()
    print("raw sqlite3 plain path: OK")
except Exception as e:
    print("raw sqlite3 plain path FAIL:", e)