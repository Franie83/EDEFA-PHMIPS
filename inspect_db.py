import sqlite3

DB = r'.\backend\instance\ef_phmips.db'
c = sqlite3.connect(DB)
cur = c.cursor()

# 1) List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
print()

# 2) For each table that looks hazard-related, print schema + row count
for t in tables:
    low = t.lower()
    if 'hazard' in low or 'report' in low:
        print(f"--- TABLE: {t} ---")
        cur.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in cur.fetchall()]
        print("  COLUMNS:", cols)
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print("  ROW COUNT:", cur.fetchone()[0])
        print()

c.close()