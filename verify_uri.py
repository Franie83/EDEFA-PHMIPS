import pathlib, sqlalchemy

ROOT = pathlib.Path("backend").resolve()
INSTANCE = ROOT / "instance"
INSTANCE.mkdir(parents=True, exist_ok=True)
uri = f"sqlite:////{(INSTANCE/'ef_phmips.db').as_posix().lstrip('/')}"
print("URI:", uri)

engine = sqlalchemy.create_engine(uri)
try:
    conn = engine.connect()
    print("SQLAlchemy connect: OK")
    conn.close()
except Exception as e:
    print("FAILED:", e)