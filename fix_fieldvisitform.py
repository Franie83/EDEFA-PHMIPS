"""
fix_fieldvisitform.py — fixes FieldVisitForm.tsx so opening the modal
from a different project resets project/site/evidence cleanly.

- Always sets projectId from defaultProject (or first project) on open.
- Clears evidence on open.
- Resets GPS to the default project's coordinates.
- Always resets siteId to a site belonging to the current project.

Creates a timestamped .bak before modifying the file.
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

TARGET = Path(r".\src\components\field\FieldVisitForm.tsx")
if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET.resolve()}")

src = TARGET.read_text(encoding="utf-8")

ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
backup = TARGET.with_suffix(f".tsx.bak_{ts}")
shutil.copy2(TARGET, backup)
print(f"Backup written: {backup}")

# The two original useEffect blocks (as they appear in the file you pasted).
OLD_BLOCK = '''  // Sync project/site selections whenever the modal opens or the lists change
  useEffect(() => {
    if (!isOpen) return;
    const targetProject = defaultProject?.id || projects[0]?.id || '';
    if (!projectId || !projects.some(p => p.id === projectId)) {
      setProjectId(targetProject);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projects.length, defaultProject?.id]);

  useEffect(() => {
    if (!isOpen) return;
    // Prefer sites belonging to the chosen project
    const candidates = sites.filter(s => !projectId || s.project_id === projectId);
    const target = candidates[0]?.id || sites[0]?.id || '';
    if (!siteId || !sites.some(s => s.id === siteId)) {
      setSiteId(target);
    } else if (projectId && !candidates.some(s => s.id === siteId)) {
      setSiteId(target);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projectId, sites.length]);'''

NEW_BLOCK = '''  // Whenever the modal opens, force the project to the default (or first project).
  // Also clear evidence + reset GPS so nothing leaks from a previous session.
  useEffect(() => {
    if (!isOpen) return;
    const targetProject = defaultProject?.id || projects[0]?.id || '';
    setProjectId(targetProject);
    setEvidenceFiles([]);
    setGpsLatitude(defaultProject?.latitude || 6.2209);
    setGpsLongitude(defaultProject?.longitude || 7.0722);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, defaultProject?.id]);

  // Whenever the project changes (or the modal opens), reset siteId to a site
  // that belongs to the current project. Prevents a stale site_id from another
  // project leaking into this visit.
  useEffect(() => {
    if (!isOpen) return;
    const candidates = sites.filter(s => s.project_id === projectId);
    const target = candidates[0]?.id || '';
    setSiteId(target);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projectId, sites.length]);'''

if OLD_BLOCK in src:
    src = src.replace(OLD_BLOCK, NEW_BLOCK, 1)
    print(" - PATCH 1: replaced the two useEffect blocks")
else:
    # Try a more tolerant regex-based replacement in case whitespace differs
    pattern = re.compile(
        r"// Sync project/site selections whenever the modal opens or the lists change\s*\n"
        r"\s*useEffect\(\(\) => \{\s*\n"
        r".*?"
        r"\}, \[isOpen, projectId, sites\.length\]\);",
        re.DOTALL,
    )
    m = pattern.search(src)
    if not m:
        print("ERROR: could not locate the two useEffect blocks.")
        print("Nothing written. Original file untouched.")
        raise SystemExit(1)
    src = src[:m.start()] + NEW_BLOCK + src[m.end():]
    print(" - PATCH 1 (regex): replaced the two useEffect blocks")

TARGET.write_text(src, encoding="utf-8")
print()
print(f"Patched: {TARGET.resolve()}")
print("Next: hard-refresh the browser (Ctrl+Shift+R twice).")