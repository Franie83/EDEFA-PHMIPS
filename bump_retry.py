import pathlib

p = pathlib.Path("backend/app.py")
src = p.read_text(encoding="utf-8")

old = "for _attempt in range(1, 7):"
new = "for _attempt in range(1, 16):"

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Bumped retries to 15")
else:
    print(f"Pattern '{old}' not found — current code may differ")

# Also increase the sleep interval
old2 = "_time.sleep(3)"
new2 = "_time.sleep(5)"

if old2 in src:
    src = src.replace(old2, new2)
    p.write_text(src, encoding="utf-8")
    print("Increased sleep to 5s")