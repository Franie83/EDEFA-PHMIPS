import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# Fix the self-referencing line
old = "const h = fullHazard && fullHazard.id === h.id ? fullHazard : hazard;"
new = "const h = fullHazard && fullHazard.id === hazard.id ? fullHazard : hazard;"

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Fixed self-referencing h.id -> hazard.id")
else:
    # Find whatever it currently says
    for i, line in enumerate(src.split("\n"), 1):
        if "const h = fullHazard" in line:
            print(f"Found at line {i}: {line}")
            # Try to patch with a regex
            import re
            fixed = re.sub(
                r"const h = fullHazard && fullHazard\.id === [^ ?]+ ?\? fullHazard : hazard;",
                "const h = fullHazard && fullHazard.id === hazard.id ? fullHazard : hazard;",
                line
            )
            if fixed != line:
                src = src.replace(line, fixed)
                p.write_text(src, encoding="utf-8")
                print(f"Fixed via regex: {fixed}")
                break
    else:
        print("Pattern not found. Paste lines 68-75 to debug.")