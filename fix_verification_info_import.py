import pathlib

p = pathlib.Path("src/components/verification/VerificationWorkspace.tsx")
src = p.read_text(encoding="utf-8")

# Find the lucide-react import block
old = """  Sliders
} from 'lucide-react';"""
new = """  Sliders,
  Info
} from 'lucide-react';"""

if "Info" not in src.split("from 'lucide-react'")[0]:
    if old in src:
        src = src.replace(old, new, 1)
        p.write_text(src, encoding="utf-8")
        print("Added Info to lucide-react imports")
    else:
        print("Import anchor NOT FOUND — paste the import block")
else:
    print("Info already imported")