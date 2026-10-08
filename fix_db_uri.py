import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = 'url=os.getenv("DATABASE_URL",f"sqlite:///{INSTANCE/\'ef_phmips.db\'}")'
new = (
    'INSTANCE.mkdir(parents=True, exist_ok=True)\n'
    'url=os.getenv("DATABASE_URL",f"sqlite:///{(INSTANCE/\'ef_phmips.db\').as_posix()}")'
)

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched successfully.")
elif ".as_posix()" in src:
    print("Already patched.")
else:
    print("Exact line not found — open backend/app.py and edit line 225 manually.")
    print("Look for: url=os.getenv(\"DATABASE_URL\",f\"sqlite:///{INSTANCE/'ef_phmips.db'}\")")