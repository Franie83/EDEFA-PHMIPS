"""
Add the filter bar to BeforeAfterMonitoring.tsx — insert it just before
the Project Selector Bar.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "monitoring" / "BeforeAfterMonitoring.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "monitor-filter-bar" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Find the marker comment for the Project Selector Bar
marker = "{/* Project Selector Bar */}"
if marker not in text:
    raise SystemExit("Project Selector Bar marker not found")

# Insert the filter bar just before it
FILTER_BAR = '''{/* Monitoring filter bar */}
      <div
        id="monitor-filter-bar"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3"
      >
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={monitorSearch}
            onChange={e => setMonitorSearch(e.target.value)}
            placeholder="Wildcard search — project ID, title, community, LGA, contractor, category…"
            className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
          />
          {monitorSearch && (
            <button
              onClick={() => setMonitorSearch('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-slate-100 text-slate-400"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Dropdown filters */}
        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Evidence Status
            </span>
            <select
              value={monitorEvidenceFilter}
              onChange={e => setMonitorEvidenceFilter(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[200px]"
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETE">✓ Complete (before + after)</option>
              <option value="MISSING_AFTER">⚠ Missing After</option>
              <option value="MISSING_BEFORE">⚠ Missing Before</option>
              <option value="NO_EVIDENCE">○ No Evidence</option>
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Sort By
            </span>
            <select
              value={monitorSort}
              onChange={e => setMonitorSort(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="id">Project ID</option>
              <option value="evidence_count">Evidence Count (high to low)</option>
              <option value="name">Project Name (A–Z)</option>
            </select>
          </label>

          {monitorHasActiveFilters && (
            <button
              onClick={resetMonitorFilters}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 inline-flex items-center gap-1.5 h-[38px]"
              title="Reset all filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        {/* Result count */}
        <div className="text-[11px] text-slate-500 border-t border-slate-100 pt-2 flex items-center gap-2">
          <Filter className="w-3.5 h-3.5" />
          Showing <strong className="text-slate-700">{filteredProjects.length}</strong> of{' '}
          <strong className="text-slate-700">{projects.length}</strong> projects
          {monitorHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      '''

text = text.replace(marker, FILTER_BAR + marker, 1)

# Ensure the icons are imported
needed_icons = ["Search", "X", "Filter", "RotateCcw"]
import_block = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
if import_block:
    existing = import_block.group(1)
    missing = [icon for icon in needed_icons if icon not in existing]
    if missing:
        new_import = "import {\n  " + existing.strip().rstrip(",") + ",\n  " + ",\n  ".join(missing) + "\n} from 'lucide-react'"
        text = text[:import_block.start()] + new_import + text[import_block.end():]
        print(f"  Added missing icons: {missing}")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Inserted filter bar (search + evidence filter + sort + reset + count)")