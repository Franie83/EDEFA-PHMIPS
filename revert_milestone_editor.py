import pathlib
import re

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# Remove the milestone editor handlers block (from "// --- Milestone editing ---" to the closing brace of cycleMilestoneStatus)
pattern = re.compile(
    r"\n  // --- Milestone editing ---.*?const cycleMilestoneStatus[\s\S]*?\n  \};\n",
    re.DOTALL
)
src, n = pattern.subn("", src)
if n:
    print(f"Removed milestone handlers ({n} match)")
else:
    print("Handlers pattern not found")

p.write_text(src, encoding="utf-8")
print("NOTE: You may still need to fix the JSX structure manually — check the milestone render block.")