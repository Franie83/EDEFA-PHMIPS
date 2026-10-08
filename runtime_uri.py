import os, pathlib, re
from dotenv import load_dotenv
load_dotenv()

print("DATABASE_URL in env:", repr(os.getenv("DATABASE_URL")))

# Read app.py and evaluate just the URI construction logic
src = pathlib.Path("backend/app.py").read_text(encoding="utf-8")

# Extract lines 24, 25, 225, 226 for inspection
lines = src.splitlines()
for n in (24, 25, 225, 226):
    if n <= len(lines):
        print(f"{n}: {lines[n-1]}")