import sqlite3

DB = r'.\backend\instance\ef_phmips.db'
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
cur = c.cursor()

for t in ('records', 'counters', 'settings'):
    print(f"=== {t} ===")
    cur.execute(f"PRAGMA table_info({t})")
    for r in cur.fetchall():
        print(f"  {r['name']:20} {r['type']}")
    cur.execute(f"SELECT COUNT(*) AS n FROM {t}")
    print(f"  ROWS: {cur.fetchone()['n']}")
    print()

print("=== ALL RECORDS ===")
cur.execute("SELECT * FROM records")
rows = cur.fetchall()
print(f"Total records: {len(rows)}")
for r in rows:
    keys = r.keys()
    line = {}
    for k in keys:
        v = r[k]
        if isinstance(v, str) and len(v) > 200:
            v = v[:200] + '...'
        line[k] = v
    print(line)
    print()

c.close()