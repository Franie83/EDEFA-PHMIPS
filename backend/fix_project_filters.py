"""
Make the ProjectList filter dropdowns derive their options from actual data
instead of hardcoded lists.

Applies to: Status, State, Category filters.
Also applies to the same filters in HazardList if present.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectList.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "availableStatuses" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# 1. Add derived lists right after the filtered/filter logic
#    Find the existing searchTerm/selectedState/selectedStatus state definitions
anchor = "const [selectedStatus, setSelectedStatus] = useState('');"
if anchor in text:
    derived = anchor + """

  // Derive filter options from actual project data so nothing is ever missing
  const availableStatuses = Array.from(
    new Set(projects.map(p => p.status).filter(Boolean) as string[])
  ).sort((a, b) => {
    // Custom order: Active first, then Pending Approval, then others alphabetically
    const order = ['Active', 'Pending Approval', 'Procurement', 'Delayed', 'Suspended', 'Completed', 'Rejected', 'Cancelled', 'Proposed'];
    const ai = order.indexOf(a);
    const bi = order.indexOf(b);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.localeCompare(b);
  });

  const availableStates = Array.from(
    new Set(projects.map(p => p.state).filter(Boolean) as string[])
  ).sort();

  const availableCategories = Array.from(
    new Set(projects.map(p => p.category).filter(Boolean) as string[])
  ).sort();
"""
    text = text.replace(anchor, derived, 1)
    print("  Added derived availableStatuses / availableStates / availableCategories")
else:
    raise SystemExit("Could not find selectedStatus state anchor")

# 2. Replace the hardcoded status dropdown options
old_status_options = re.search(
    r'<option value="">All Statuses</option>\s*'
    r'<option value="Active">Active</option>\s*'
    r'<option value="Completed">Completed</option>\s*'
    r'<option value="Procurement">Procurement</option>\s*'
    r'<option value="Delayed">Delayed</option>',
    text,
)
if old_status_options:
    new_status_options = '''<option value="">All Statuses</option>
          {availableStatuses.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}'''
    text = text[:old_status_options.start()] + new_status_options + text[old_status_options.end():]
    print("  Replaced hardcoded status options with derived list")
else:
    print("  WARNING: could not find hardcoded status options block")

# 3. Replace hardcoded state options if present
#    Look for a select whose options start with states
state_block = re.search(
    r'<option value="">All States[^<]*</option>\s*(<option value="[^"]+">[^<]+</option>\s*){3,}',
    text,
)
if state_block:
    new_state_options = '''<option value="">All States ({availableStates.length})</option>
          {availableStates.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
          '''
    text = text[:state_block.start()] + new_state_options + text[state_block.end():]
    print("  Replaced hardcoded state options with derived list")

# 4. Replace hardcoded category options if present
cat_block = re.search(
    r'<option value="">All Categories</option>\s*(<option value="[^"]+">[^<]+</option>\s*){3,}',
    text,
)
if cat_block:
    new_cat_options = '''<option value="">All Categories</option>
          {availableCategories.map(c => (
            <option key={c} value={c}>{c}</option>
          ))}
          '''
    text = text[:cat_block.start()] + new_cat_options + text[cat_block.end():]
    print("  Replaced hardcoded category options with derived list")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")