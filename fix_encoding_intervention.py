import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
raw = p.read_bytes()

# Try decoding as cp1252 first — if that fails, try utf-8
for enc in ("utf-8", "cp1252", "latin-1"):
    try:
        text = raw.decode(enc)
        print(f"Decoded as {enc}")
        break
    except UnicodeDecodeError:
        continue
else:
    print("Could not decode file — leaving as-is")
    exit(1)

# Fix common mojibake
fixes = [
    ("âœ“", "✓"),
    ("â€”", "—"),
    ("â‚¦", "₦"),
    ("â€¦", "…"),
    ("â€“", "–"),
    ("â€œ", "“"),
    ("â€", "\""),
]
for bad, good in fixes:
    text = text.replace(bad, good)

p.write_text(text, encoding="utf-8")
print(f"Re-encoded as UTF-8 ({len(text)} chars)")