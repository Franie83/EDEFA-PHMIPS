import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = 'url=os.getenv("DATABASE_URL",f"sqlite:////{(INSTANCE/\'ef_phmips.db\').as_posix().lstrip(\'/\')}")'
new = 'url=os.getenv("DATABASE_URL",f"sqlite:///{(INSTANCE/\'ef_phmips.db\').as_posix()}")'

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched successfully.")
elif new in src:
    print("Already correct.")
else:
    print("Pattern not found. Edit line 226 manually to:")
    print(" ", new)