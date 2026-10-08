from __future__ import annotations
import json,sys
from pathlib import Path
from app import app,db,Record,Setting,Counter,ENTITIES,put
source=Path(sys.argv[1] if len(sys.argv)>1 else "../data/ef_database.json")
if not source.exists(): raise SystemExit(f"Legacy database not found: {source}")
data=json.loads(source.read_text())
with app.app_context():
 db.session.query(Record).delete(); db.session.query(Setting).delete(); db.session.query(Counter).delete()
 for e in ENTITIES:
  for item in data.get(e,[]): put(e,item)
 db.session.add(Setting(key="reference_data",value=data["reference_data"]))
 db.session.add(Setting(key="system_settings",value=data["system_settings"]))
 db.session.commit()
print("Legacy JSON imported successfully")
