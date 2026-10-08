import pathlib

p = pathlib.Path("src/components/field/FieldVisitList.tsx")
src = p.read_text(encoding="utf-8")

# Show the current broken region so we can see exactly what's there
idx = src.find("{/* Lightbox for evidence preview */}")
if idx == -1:
    print("Lightbox not found — nothing to fix")
else:
    print("=== Lightbox location (200 chars before + full block) ===")
    print(src[max(0, idx-300):idx+1800])