@'
import sqlite3, json, os
from pathlib import Path

UPLOADS = Path(r'.\backend\uploads')
DB = r'.\backend\instance\ef_phmips.db'

c = sqlite3.connect(DB)
cur = c.cursor()
cur.execute("SELECT id, data FROM records WHERE entity_type='evidence_files'")
orphans = []
for row_id, data in cur.fetchall():
    try: d = json.loads(data)
    except: d = {}
    h = (d.get('hazard_id') or '').strip() if isinstance(d.get('hazard_id'), str) else d.get('hazard_id')
    p = (d.get('project_id') or '').strip() if isinstance(d.get('project_id'), str) else d.get('project_id')
    v = (d.get('visit_id') or '').strip() if isinstance(d.get('visit_id'), str) else d.get('visit_id')
    s = (d.get('site_id') or '').strip() if isinstance(d.get('site_id'), str) else d.get('site_id')
    if not (h or p or v or s):
        orphans.append((row_id, d.get('id'), d.get('file_name'), d.get('file_url')))

print(f"Orphans found: {len(orphans)}")
for rid, eid, name, url in orphans:
    print(f"  {eid}  {name}  ({url})")

if orphans:
    confirm = input("\nType YES to delete these DB rows AND their disk files: ")
    if confirm == "YES":
        removed = 0
        for rid, eid, name, url in orphans:
            cur.execute("DELETE FROM records WHERE id = ?", (rid,))
            removed += 1
            # url is like "/api/evidence/file/EVD-2026-XXX_abc123.png"
            if url and "/file/" in url:
                fname = url.split("/file/", 1)[1]
                fpath = UPLOADS / fname
                if fpath.exists():
                    try: fpath.unlink()
                    except Exception as e: print(f"    could not unlink {fpath}: {e}")
        c.commit()
        print(f"Deleted {removed} DB rows and their disk files.")
    else:
        print("Aborted.")
else:
    print("Nothing to clean.")
c.close()
'@ | Out-File -Encoding utf8 cleanup_orphans.py

