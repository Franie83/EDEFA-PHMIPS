"""
Insert the Action Tracking filter bar above the cards list.
The old toolbar was removed by an earlier patch, so we insert fresh.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "actions" / "ActionTracking.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "action-filter-bar" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# Insert just before the "Action cards list" comment
MARKER = "{/* Action cards list */}"
if MARKER not in text:
    raise SystemExit("Marker '{/* Action cards list */}' not found")

NEW_BAR = '''{/* Action filter bar */}
      <div
        id="action-filter-bar"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3"
      >
        {/* Stat pills */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={resetActionFilters}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              !actionHasActiveFilters
                ? 'bg-emerald-800 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            All ({totalActions})
          </button>
          <button
            onClick={() => { resetActionFilters(); setOverdueOnly(true); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              overdueOnly
                ? 'bg-rose-700 text-white'
                : 'bg-rose-100 text-rose-800 hover:bg-rose-200'
            }`}
          >
            Overdue ({overdueCount})
          </button>
          <button
            onClick={() => { resetActionFilters(); setStatusFilter('Completed'); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              statusFilter === 'Completed'
                ? 'bg-blue-700 text-white'
                : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
            }`}
          >
            Completed ({completedCount})
          </button>
          <button
            onClick={() => { resetActionFilters(); setStatusFilter('Verified'); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              statusFilter === 'Verified'
                ? 'bg-teal-700 text-white'
                : 'bg-teal-100 text-teal-800 hover:bg-teal-200'
            }`}
          >
            Verified ({verifiedCount})
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Wildcard search — ID, title, description, assignee, organization, linked IDs..."
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

        {/* Dropdown filters */}
        <div className="flex flex-wrap items-end gap-3 text-xs">
          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Status</span>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[160px]"
            >
              <option value="ALL">All Statuses ({statusOptions.length})</option>
              {statusOptions.map(s => (<option key={s} value={s}>{s}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Priority</span>
            <select
              value={priorityFilter}
              onChange={e => setPriorityFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[140px]"
            >
              <option value="ALL">All Priorities</option>
              {priorityOptions.map(p => (<option key={p} value={p}>{p}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Assignee</span>
            <select
              value={assigneeFilter}
              onChange={e => setAssigneeFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[180px]"
            >
              <option value="ALL">All Assignees ({assigneeOptions.length})</option>
              {assigneeOptions.map(a => (<option key={a} value={a}>{a}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Organization</span>
            <select
              value={orgFilter}
              onChange={e => setOrgFilter(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600 min-w-[220px]"
            >
              <option value="ALL">All Organizations ({orgOptions.length})</option>
              {orgOptions.map(o => (<option key={o} value={o}>{o}</option>))}
            </select>
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Due From</span>
            <input
              type="date"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex flex-col">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Due To</span>
            <input
              type="date"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              className="py-2 px-3 rounded-lg border border-slate-300 bg-slate-50/50 focus:bg-white outline-none focus:border-emerald-600"
            />
          </label>

          <label className="flex items-center gap-2 pb-2">
            <input
              type="checkbox"
              checked={overdueOnly}
              onChange={e => setOverdueOnly(e.target.checked)}
              className="w-4 h-4"
            />
            <span className="text-xs font-semibold text-slate-700">Overdue only</span>
          </label>

          {actionHasActiveFilters && (
            <button
              onClick={resetActionFilters}
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
          Showing <strong className="text-slate-700">{filteredActions.length}</strong> of{' '}
          <strong className="text-slate-700">{totalActions}</strong> action directives
          {actionHasActiveFilters && (
            <span className="text-emerald-700 font-semibold">— filters active</span>
          )}
        </div>
      </div>

      '''

text = text.replace(MARKER, NEW_BAR + MARKER, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Inserted filter bar above the action cards list")