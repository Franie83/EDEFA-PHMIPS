import pathlib

p = pathlib.Path("src/components/monitoring/BeforeAfterMonitoring.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. New state
if "const [filterProject, setFilterProject]" not in src:
    src = src.replace(
        "const [monitorSort, setMonitorSort] = useState<'id' | 'evidence_count' | 'name'>('id');",
        "const [monitorSort, setMonitorSort] = useState<'id' | 'evidence_count' | 'name'>('id');\n"
        "  const [filterProject, setFilterProject] = useState<string>('ALL');"
    )
    changes.append("added filterProject state")

# 2. Filter chain
old_chain = """  const filteredProjects = (projects || [])
    .filter(p => {
      if (!matchesMonitorSearch(p, monitorSearch)) return false;
      if (monitorEvidenceFilter !== 'ALL') {
        if (classifyProject(p.id) !== monitorEvidenceFilter) return false;
      }
      return true;
    })"""

new_chain = """  const filteredProjects = (projects || [])
    .filter(p => {
      if (filterProject !== 'ALL' && p.id !== filterProject) return false;
      if (!matchesMonitorSearch(p, monitorSearch)) return false;
      if (monitorEvidenceFilter !== 'ALL') {
        if (classifyProject(p.id) !== monitorEvidenceFilter) return false;
      }
      return true;
    })"""

if old_chain in src:
    src = src.replace(old_chain, new_chain)
    changes.append("added filterProject to filter chain")

# 3. Reset
old_reset = """  const resetMonitorFilters = () => {
    setMonitorSearch('');
    setMonitorEvidenceFilter('ALL');
    setMonitorSort('id');
  };"""
new_reset = """  const resetMonitorFilters = () => {
    setMonitorSearch('');
    setMonitorEvidenceFilter('ALL');
    setMonitorSort('id');
    setFilterProject('ALL');
  };"""
if old_reset in src:
    src = src.replace(old_reset, new_reset)
    changes.append("reset now clears filterProject")

# 4. hasActiveFilters
old_active = """  const monitorHasActiveFilters =
    monitorSearch !== '' || monitorEvidenceFilter !== 'ALL' || monitorSort !== 'id';"""
new_active = """  const monitorHasActiveFilters =
    monitorSearch !== '' ||
    monitorEvidenceFilter !== 'ALL' ||
    monitorSort !== 'id' ||
    filterProject !== 'ALL';"""
if old_active in src:
    src = src.replace(old_active, new_active)
    changes.append("hasActiveFilters includes filterProject")

# 5. Auto-select slider
if "React.useEffect(() => {\n    if (filterProject !== 'ALL')" not in src:
    marker = "  const resetMonitorFilters = () => {"
    inject = """  React.useEffect(() => {
    if (filterProject !== 'ALL') {
      setSelectedProjectId(filterProject);
    }
  }, [filterProject]);

  const resetMonitorFilters = () => {"""
    if marker in src:
        src = src.replace(marker, inject)
        changes.append("auto-select slider on filter change")

# 6. Insert Project dropdown in the filter bar
project_dropdown = """          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Project
            </span>
            <select
              value={filterProject}
              onChange={e => setFilterProject(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[240px]"
            >
              <option value="ALL">All Projects ({projects.length})</option>
              {projects.map(p => {
                const c = countByStage(p.id);
                return (
                  <option key={p.id} value={p.id}>
                    {p.id} — {p.title.slice(0, 40)}{p.title.length > 40 ? '…' : ''} ({c.total})
                  </option>
                );
              })}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Evidence Status
            </span>"""

anchor = """          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Evidence Status
            </span>"""

if "All Projects ({projects.length})" not in src and anchor in src:
    src = src.replace(anchor, project_dropdown, 1)
    changes.append("Project dropdown inserted in filter bar")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)
print(f"\nWrote {p}")