"""
Add full filter bar + wildcard search to ActionTracking.tsx:
  - Filter state (status, priority, assignee, organization, date range, overdue-only)
  - Derived filter options from data
  - Wildcard search across 12+ fields
  - Filtered computation with all filters combined
  - Reset function
  - Result count
  - Related entity badge + days-until-due pill on each card
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "filteredActions" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# STEP 1 — Extend lucide imports
# ============================================================
needed_icons = ["RotateCcw", "Filter", "X", "Layers", "Calendar"]
m = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
if m:
    existing = m.group(1)
    missing = [ic for ic in needed_icons if ic not in existing]
    if missing:
        new_import = "import {\n  " + existing.strip().rstrip(",") + ",\n  " + ",\n  ".join(missing) + "\n} from 'lucide-react'"
        text = text[:m.start()] + new_import + text[m.end():]
        print(f"  Added icons: {missing}")

# ============================================================
# STEP 2 — Add filter state
# ============================================================
anchor = "const [isModalOpen, setIsModalOpen] = useState(false);"
if anchor not in text:
    raise SystemExit("isModalOpen anchor not found")

filter_states = anchor + """

  // Extended filter state
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [assigneeFilter, setAssigneeFilter] = useState<string>('ALL');
  const [orgFilter, setOrgFilter] = useState<string>('ALL');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [overdueOnly, setOverdueOnly] = useState<boolean>(false);"""

text = text.replace(anchor, filter_states, 1)
print("  Added filter state")

# ============================================================
# STEP 3 — Replace the filter computation with enhanced version
# ============================================================
old_filter_match = re.search(
    r"const filtered = \(actions \|\| \[\]\)\.filter\(a => \{[\s\S]*?\n  \};\n",
    text,
)
if not old_filter_match:
    raise SystemExit("Could not find the existing 'filtered' computation")

enhanced = '''// Derive filter options from actual data
  const statusOptions = Array.from(
    new Set((actions || []).map(a => a.status).filter(Boolean) as string[])
  ).sort();

  const priorityOptions = Array.from(
    new Set((actions || []).map(a => a.priority).filter(Boolean) as string[])
  ).sort();

  const assigneeOptions = Array.from(
    new Set((actions || []).map(a => a.responsible_person).filter(Boolean) as string[])
  ).sort();

  const orgOptions = Array.from(
    new Set((actions || []).map(a => a.responsible_organization).filter(Boolean) as string[])
  ).sort();

  // Classify which entity an action belongs to
  const linkedEntity = (a: any): { type: 'HAZARD' | 'PROJECT' | 'INTERVENTION' | 'NONE'; id: string } => {
    if (a.hazard_id) return { type: 'HAZARD', id: a.hazard_id };
    if (a.project_id) return { type: 'PROJECT', id: a.project_id };
    if (a.intervention_id) return { type: 'INTERVENTION', id: a.intervention_id };
    return { type: 'NONE', id: '' };
  };

  // Compute days until due (negative if overdue)
  const daysUntilDue = (dueDate: string | undefined, status: string): number | null => {
    if (!dueDate) return null;
    if (status === 'Completed' || status === 'Verified' || status === 'Closed') return null;
    const due = new Date(dueDate).getTime();
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffMs = due - today.getTime();
    return Math.round(diffMs / 86400000);
  };

  // Wildcard search across all fields
  const matchesSearch = (a: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      a.id,
      a.title,
      a.description,
      a.responsible_person,
      a.responsible_organization,
      a.hazard_id,
      a.project_id,
      a.intervention_id,
      a.status,
      a.priority,
      a.due_date,
      a.completion_date,
      a.verified_by,
      a.evidence_summary,
      a.verification_comments,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredActions = (actions || []).filter(a => {
    if (statusFilter !== 'ALL' && a.status !== statusFilter) return false;
    if (priorityFilter !== 'ALL' && a.priority !== priorityFilter) return false;
    if (assigneeFilter !== 'ALL' && a.responsible_person !== assigneeFilter) return false;
    if (orgFilter !== 'ALL' && a.responsible_organization !== orgFilter) return false;
    if (dateFrom && a.due_date && a.due_date < dateFrom) return false;
    if (dateTo && a.due_date && a.due_date > dateTo) return false;
    if (overdueOnly && !a.is_overdue) return false;
    if (!matchesSearch(a, searchTerm)) return false;
    return true;
  });

  // Header stat counts
  const totalActions = (actions || []).length;
  const overdueCount = (actions || []).filter(a => a.is_overdue).length;
  const completedCount = (actions || []).filter(a => a.status === 'Completed').length;
  const verifiedCount = (actions || []).filter(a => a.status === 'Verified').length;

  const resetActionFilters = () => {
    setSearchTerm('');
    setStatusFilter('ALL');
    setPriorityFilter('ALL');
    setAssigneeFilter('ALL');
    setOrgFilter('ALL');
    setDateFrom('');
    setDateTo('');
    setOverdueOnly(false);
  };

  const actionHasActiveFilters =
    searchTerm !== '' ||
    statusFilter !== 'ALL' ||
    priorityFilter !== 'ALL' ||
    assigneeFilter !== 'ALL' ||
    orgFilter !== 'ALL' ||
    dateFrom !== '' ||
    dateTo !== '' ||
    overdueOnly;

'''

text = text[:old_filter_match.start()] + enhanced + text[old_filter_match.end():]
print("  Replaced filter computation with enhanced version")

# ============================================================
# STEP 4 — Rewire the .map to use filteredActions
# ============================================================
if "{filtered.map(item =>" in text:
    text = text.replace("{filtered.map(item =>", "{filteredActions.map(item =>", 1)
    print("  Rewired list rendering to filteredActions")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")
print()
print("Filter logic in place. Now run add_action_filter_bar.py to insert the UI.")