"""
Replace the old Filter Toolbar in EvidenceRepository.tsx with the enhanced
one that uses the new filter state (entity, uploader, date range, reset).
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "evidence" / "EvidenceRepository.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "evidence-filter-bar" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Find the old Filter Toolbar block: from "{/* Filter Toolbar */}" to the
# matching closing </div> of that section.
marker = "{/* Filter Toolbar */}"
idx = text.find(marker)
if idx == -1:
    raise SystemExit("'Filter Toolbar' marker not found")

# Walk forward, tracking <div> depth
pos = idx + len(marker)
depth = 0
opened = False
end = None
while pos < len(text):
    ch = text[pos]
    if text.startswith("<div", pos) and (pos + 4 >= len(text) or text[pos+4] in " \t\n>"):
        depth += 1
        opened = True
        pos += 4
        continue
    if text.startswith("</div>", pos):
        depth -= 1
        pos += len("</div>")
        if opened and depth == 0:
            end = pos
            break
        continue
    pos += 1

if end is None:
    raise SystemExit("Could not find end of Filter Toolbar block")

# Build the replacement filter bar
NEW_FILTER_BAR = '''{/* Evidence filter bar */}
      <div
        id="evidence-filter-bar"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3"
      >
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Wildcard search — file name, description, uploader, IDs, dates, stage…"
            className="w-full pl-9 pr-9 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 text-xs"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-slate-100 text-slate-400"
              title="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Media
            </span>
            <select
              value={mediaFilter}
              onChange={e => setMediaFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[150px]"
            >
              <option value="ALL">All Types ({mediaOptions.length})</option>
              {mediaOptions.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Stage
            </span>
            <select
              value={stageFilter}
              onChange={e => setStageFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[150px]"
            >
              <option value="ALL">All Stages ({stageOptions.length})</option>
              {stageOptions.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Related Entity
            </span>
            <select
              value={entityFilter}
              onChange={e => setEntityFilter(e.target.value as any)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[160px]"
            >
              <option value="ALL">All Entities</option>
              <option value="HAZARD">Hazard-linked</option>
              <option value="PROJECT">Project-linked</option>
              <option value="SITE">Site-linked</option>
              <option value="VISIT">Visit-linked</option>
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              Uploader
            </span>
            <select
              value={uploaderFilter}
              onChange={e => setUploaderFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="ALL">All Uploaders ({uploaderOptions.length})</option>
              {uploaderOptions.map(u => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              From Date
            </span>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">
              To Date
            </span>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          {evidenceHasActiveFilters && (
            <button
              onClick={resetEvidenceFilters}
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
          Showing <strong className="text-slate-700">{filteredEvidence.length}</strong> of{' '}
          <strong className="text-slate-700">{evidenceList.length}</strong> files
          {evidenceHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>'''

text = text[:idx] + NEW_FILTER_BAR + text[end:]

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Replaced Filter Toolbar with enhanced bar")
print("  Added: Media, Stage, Related Entity, Uploader, From Date, To Date, Reset, Count")