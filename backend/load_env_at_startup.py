"""Add load_dotenv() to app.py so .env is read at startup."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "backend" / "app.py"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "load_dotenv" in text:
    print("load_dotenv already present — skipping.")
    raise SystemExit(0)

# Anchor on the BASE line
anchor = "BASE=Path(__file__).resolve().parent.parent"
if anchor not in text:
    raise SystemExit("Could not find BASE anchor. Paste the first 30 lines of app.py.")

insertion = "from dotenv import load_dotenv\nload_dotenv()\n\n"

text = text.replace(anchor, insertion + anchor, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Inserted load_dotenv() before BASE")