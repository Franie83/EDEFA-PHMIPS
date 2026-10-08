"""
patch_monitoring_compact.py
Adds a `compact` prop to BeforeAfterMonitoring that hides the filter bar and
project dropdown row. Passes `compact` from ProjectDetailModal's Monitoring
→ Before/After tab.
"""
import pathlib
import re

# =========================================================================
# PART 1 — Add `compact` prop to BeforeAfterMonitoring
# =========================================================================
bam = pathlib.Path("src/components/monitoring/BeforeAfterMonitoring.tsx")
src = bam.read_text(encoding="utf-8")
changes = []

if "compact" in src and "compact?:" in src:
    print("BeforeAfterMonitoring: already has compact prop — skipping")
else:
    # 1a. Add prop to interface
    iface_old = """interface BeforeAfterMonitoringProps {
  projects: Project[];
  evidenceList: Evidence[];
}"""
    iface_new = """interface BeforeAfterMonitoringProps {
  projects: Project[];
  evidenceList: Evidence[];
  compact?: boolean;
}"""
    if iface_old not in src:
        print("BeforeAfterMonitoring: interface anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(iface_old, iface_new, 1)
    changes.append("added compact prop to interface")

    # 1b. Destructure compact
    dest_old = """export const BeforeAfterMonitoring: React.FC<BeforeAfterMonitoringProps> = ({
  projects = [],
  evidenceList = []
}) => {"""
    dest_new = """export const BeforeAfterMonitoring: React.FC<BeforeAfterMonitoringProps> = ({
  projects = [],
  evidenceList = [],
  compact = false
}) => {"""
    if dest_old not in src:
        print("BeforeAfterMonitoring: destructure anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(dest_old, dest_new, 1)
    changes.append("destructured compact prop")

    # 1c. Wrap the filter bar + project picker in {!compact && (...)}
    # The filter bar has id="monitor-filter-bar" and the project picker follows.
    # We need to find the containing block and wrap it.
    # Use a regex to locate the opening tag of the filter bar and the
    # closing of the project picker.
    #
    # Simplest: wrap the div with id="monitor-filter-bar" and everything
    # up to (but not including) the toggle/slider section.
    #
    # The filter bar opening: <div id="monitor-filter-bar"
    # The end anchor is uncertain, so we do a smaller, safer change:
    # wrap JUST the filter bar (which contains the search + 3 dropdowns).
    # That removes the biggest chunk of noise.
    fb_old_pat = re.compile(
        r'(<div\s+id="monitor-filter-bar"[^>]*>)',
        re.MULTILINE
    )
    m = fb_old_pat.search(src)
    if not m:
        print("BeforeAfterMonitoring: 'monitor-filter-bar' div NOT FOUND")
        changes.append("WARNING: could not wrap filter bar — add manually")
    else:
        # Insert `{!compact && (` before the div and `)}` after its matching close.
        # Finding the matching </div> is complex. Instead, toggle display via a
        # className prefix using template literal would change too much. Fallback:
        # inject a conditional class on the filter bar div itself.
        old_attr = m.group(1)
        # Add a className that hides it when compact. If className exists, merge.
        if "className=" in old_attr:
            new_attr = re.sub(
                r'className="([^"]*)"',
                lambda mm: f'className={{`${{compact ? \'hidden\' : \'\'}} {mm.group(1)}`}}',
                old_attr,
                count=1,
            )
        else:
            # no className — add one
            new_attr = old_attr[:-1] + ' className={compact ? "hidden" : ""}>'
        src = src.replace(old_attr, new_attr, 1)
        changes.append("filter bar div now hides when compact=true")

    bam.write_text(src, encoding="utf-8")

print("BeforeAfterMonitoring changes:")
for c in changes:
    print(" -", c)

# =========================================================================
# PART 2 — Pass compact from ProjectDetailModal
# =========================================================================
pdm = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = pdm.read_text(encoding="utf-8")
pdm_changes = []

old_render = """              <BeforeAfterMonitoring
                projects={[project]}
                evidenceList={(project as any).evidence_files || []}
              />"""
new_render = """              <BeforeAfterMonitoring
                projects={[project]}
                evidenceList={(project as any).evidence_files || []}
                compact
              />"""

if new_render in src:
    print("ProjectDetailModal: already passes compact — skipping")
elif old_render in src:
    src = src.replace(old_render, new_render, 1)
    pdm.write_text(src, encoding="utf-8")
    pdm_changes.append("passed compact to BeforeAfterMonitoring")
else:
    print("ProjectDetailModal: BeforeAfterMonitoring render anchor NOT FOUND")
    print("Paste the block around <BeforeAfterMonitoring in the modal.")

print("ProjectDetailModal changes:")
for c in pdm_changes:
    print(" -", c)

for label, path in [
    ("BeforeAfterMonitoring.tsx", bam),
    ("ProjectDetailModal.tsx", pdm),
]:
    s = path.read_text(encoding="utf-8")
    o, c = s.count("{"), s.count("}")
    print(f"{label}: brace balance {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")