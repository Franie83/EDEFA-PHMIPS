import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

old = "import React, { useState } from 'react';"
new = "import React, { useState, useEffect } from 'react';"

if old in src:
    src = src.replace(old, new, 1)
    p.write_text(src, encoding="utf-8")
    print("Added useEffect to React import")
elif new in src:
    print("useEffect already imported")
else:
    # Check what the import actually looks like
    print("Import pattern NOT FOUND. First 15 lines:")
    for i, line in enumerate(src.split("\n")[:15], 1):
        print(f"  {i}: {line}")