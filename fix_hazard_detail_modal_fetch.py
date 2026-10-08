import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add import for api if missing
if "import { api } from" not in src:
    # Insert after the existing imports
    lines = src.split("\n")
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("} from") or line.startswith("import "):
            insert_at = i + 1
    lines.insert(insert_at, "import { api } from '../../services/api.ts';")
    src = "\n".join(lines)
    changes.append("added api import")
else:
    changes.append("api import already present")

# 2. Change state to hold the full hazard
old_state = "  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);"
new_state = """  const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);
  const [fullHazard, setFullHazard] = useState<Hazard | null>(null);"""
if old_state in src and "fullHazard" not in src:
    src = src.replace(old_state, new_state)
    changes.append("added fullHazard state")

# 3. Add useEffect to fetch full hazard with evidence_files
old_guard = "  if (!hazard) return null;"
new_guard = """  // Fetch the full hazard (with evidence_files, actions, intervention) when modal opens
  useEffect(() => {
    if (!hazard?.id) {
      setFullHazard(null);
      return;
    }
    let cancelled = false;
    api.getHazardById(hazard.id)
      .then(full => { if (!cancelled) setFullHazard(full); })
      .catch(() => { if (!cancelled) setFullHazard(hazard); });
    return () => { cancelled = true; };
  }, [hazard?.id]);

  if (!hazard) return null;

  // Prefer the fully-hydrated hazard (with evidence), fall back to the list item
  const h = fullHazard && fullHazard.id === hazard.id ? fullHazard : hazard;"""
if old_guard in src:
    src = src.replace(old_guard, new_guard, 1)
    changes.append("added full hazard fetch + alias `h`")
else:
    changes.append("if (!hazard) return null; guard NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)