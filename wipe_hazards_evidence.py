import sqlite3
c = sqlite3.connect(r'.\backend\instance\ef_phmips.db')
cur = c.cursor()
cur.execute("DELETE FROM records WHERE entity_type='evidence_files'")
ev = cur.rowcount
cur.execute("DELETE FROM records WHERE entity_type='hazards'")
h = cur.rowcount
c.commit()
print(f"Deleted {h} hazards and {ev} evidence rows.")
c.close()
