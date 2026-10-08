import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = 'url=os.getenv("DATABASE_URL",f"sqlite:///{(INSTANCE/\'ef_phmips.db\').as_posix()}")'
new = 'url=os.getenv("DATABASE_URL",f"sqlite:////{(INSTANCE/\'ef_phmips.db\').as_posix().lstrip(\'/\')}")'

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched successfully.")
elif "sqlite:////" in src:
    print("Already patched.")
else:
    print("Pattern not found. Manual edit needed on line 226.")
    print("Replace:")
    print(" ", old)
    print("With:")
    print(" ", new)