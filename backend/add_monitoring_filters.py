"""
Add filter bar + search + evidence-status filter to BeforeAfterMonitoring.tsx.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "monitoring" / "BeforeAfterMonitoring.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "filteredProjects" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# STEP 1 — Add filter state after comparisonMode
# ============================================================
anchor = "const [comparisonMode, setComparisonMode] = useState<'slider' | 'side-by-side'>('slider');"
if anchor not in text:
    raise SystemExit("comparisonMode anchor not found")

filter_states = anchor + """

  // --- Filter state ---
  const [monitorSearch, setMonitorSearch] = useState('');
  const [monitorEvidenceFilter, setMonitorEvidenceFilter] = useState<
    'ALL' | 'COMPLETE' | 'MISSING_AFTER' | 'MISSING_BEFORE' | 'NO_EVIDENCE'
  >('ALL');
  const [monitorSort, setMonitorSort] = useState<'id' | 'evidence_count' | 'name'>('id');"""

text = text.replace(anchor, filter_states, 1)
print("  Added filter state (search, evidence filter, sort)")

# ============================================================
# STEP 2 — Add derivation logic after the existing evidence grouping
# ============================================================
anchor2 = "const afterItems = (projectEvidence || []).filter(e => e.stage_tag === 'after' || e.stage_tag === 'evidence');"
if anchor2 not in text:
    raise SystemExit("afterItems anchor not found")

derivation = anchor2 + """

  // --- Filtering helpers ---

  // Count evidence by stage for any project
  const countByStage = (projectId: string) => {
    const ev = (evidenceList || []).filter(e => e.project_id === projectId);
    return {
      before: ev.filter(e => e.stage_tag === 'before').length,
      during: ev.filter(e => e.stage_tag === 'during').length,
      after: ev.filter(e => e.stage_tag === 'after' || e.stage_tag === 'evidence').length,
      total: ev.length,
    };
  };

  // Classify a project by evidence completeness
  const classifyProject = (projectId: string): 'COMPLETE' | 'MISSING_AFTER' | 'MISSING_BEFORE' | 'NO_EVIDENCE' => {
    const c = countByStage(projectId);
    if (c.total === 0) return 'NO_EVIDENCE';
    if (c.before > 0 && c.after > 0) return 'COMPLETE';
    if (c.before > 0 && c.after === 0) return 'MISSING_AFTER';
    if (c.before === 0 && c.after > 0) return 'MISSING_BEFORE';
    return 'NO_EVIDENCE';
  };

  // Wildcard search across project fields
  const matchesMonitorSearch = (p: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      p.id,
      p.title,
      p.community,
      p.lga,
      p.state,
      p.contractor,
      p.category,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  // Filter and sort the projects
  const filteredProjects = (projects || [])
    .filter(p => {
      if (!matchesMonitorSearch(p, monitorSearch)) return false;
      if (monitorEvidenceFilter !== 'ALL') {
        if (classifyProject(p.id) !== monitorEvidenceFilter) return false;
      }
      return true;
    })
    .sort((a, b) => {
      if (monitorSort === 'evidence_count') {
        return countByStage(b.id).total - countByStage(a.id).total;
      }
      if (monitorSort === 'name') {
        return (a.title || '').localeCompare(b.title || '');
      }
      return a.id.localeCompare(b.id);
    });

  const resetMonitorFilters = () => {
    setMonitorSearch('');
    setMonitorEvidenceFilter('ALL');
    setMonitorSort('id');
  };

  const monitorHasActiveFilters =
    monitorSearch !== '' || monitorEvidenceFilter !== 'ALL' || monitorSort !== 'id';"""

text = text.replace(anchor2, derivation, 1)
print("  Added countByStage, classifyProject, filteredProjects, reset")

# ============================================================
# STEP 3 — Replace the project selector dropdown to use filteredProjects
# ============================================================
# Find the existing select dropdown in the Project Selector Bar
# Pattern: <select ... value={selectedProjectId} onChange={...}> ... </select>
pattern = r'(<span className="font-bold text-slate-700 uppercase tracking-wider text-\[11px\]">Select Project:</span>\s*<select[^>]*>\s*)([\s\S]*?)(</select>)'
m = re.search(pattern, text)
if not m:
    print("  WARNING: could not find the project selector dropdown — will skip dropdown enrichment")
else:
    before = m.group(1)
    options = m.group(2)
    after = m.group(3)

    # Replace the options with enriched versions that show evidence counts
    new_options = """{(filteredProjects || []).map(p => {
            const c = countByStage(p.id);
            const cls = classifyProject(p.id);
            const icon = cls === 'COMPLETE' ? '✓' : cls === 'NO_EVIDENCE' ? '○' : '⚠';
            const label = cls === 'COMPLETE' ? 'Complete' : cls === 'NO_EVIDENCE' ? 'No evidence' : cls === 'MISSING_AFTER' ? 'Missing after' : 'Missing before';
            return (
              <option key={p.id} value={p.id}>
                {icon} {p.id} — {p.title} — {c.before}B/{c.during}D/{c.after}A ({label})
              </option>
            );
          })}"""

    text = text[:m.start(2)] + new_options + text[m.end(2):]
    print("  Enriched project dropdown with evidence indicators")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")
print()
print("NOTE: The filter bar UI still needs to be placed manually. Paste the")
print("      first 100 lines of the file and I'll give you the exact JSX.")