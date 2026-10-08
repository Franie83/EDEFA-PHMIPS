import pathlib
import re

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# The auto-detect useEffect block I added
auto_effect = """  // Auto-trigger GPS detection when the modal opens in create-mode
  useEffect(() => {
    if (!isOpen || isEditMode) return;
    // Only auto-detect if we don't already have coordinates
    if (formData.latitude !== '' && formData.latitude !== null) return;
    // Give the modal a moment to mount, then auto-detect
    const timer = setTimeout(() => {
      handleDetectGps({ auto: true });
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);"""

# 1. Remove it from its current (broken) location
if auto_effect in src:
    src = src.replace(auto_effect, "")
    changes.append("removed useEffect from after early-return")
else:
    # Try a looser match in case whitespace differs
    pattern = re.compile(
        r"\n\s*// Auto-trigger GPS detection.*?\}, \[isOpen\]\);",
        re.DOTALL
    )
    src, n = pattern.subn("", src)
    if n:
        changes.append("removed useEffect via regex")
    else:
        changes.append("auto-detect useEffect NOT FOUND")

# 2. Insert it just BEFORE the "if (!isOpen) return null;" line
insert_marker = "  if (!isOpen) return null;"
if insert_marker in src and auto_effect not in src:
    # Find the last useEffect before the marker to insert right after it
    # Simplest: insert right before the marker
    src = src.replace(
        insert_marker,
        auto_effect + "\n\n" + insert_marker,
        1
    )
    changes.append("inserted useEffect before early return")
else:
    if auto_effect in src:
        changes.append("skipped insert — useEffect still in place")
    else:
        changes.append("early-return marker NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# Sanity check: count hooks
hook_count = len(re.findall(r"\buse(State|Effect|Ref|Memo|Callback|Context)\b", src))
print(f"\nTotal hook calls in file: {hook_count}")