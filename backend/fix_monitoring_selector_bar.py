"""
Rebuild the Project Selector Bar block in BeforeAfterMonitoring.tsx.
The earlier regex swallowed the onChange handler and mangled the JSX.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "monitoring" / "BeforeAfterMonitoring.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# Match the entire broken block: from "{/* Project Selector Bar */}" to the first "</div>"
pattern = r"\{/\* Project Selector Bar \*/\}[\s\S]*?</div>"

m = re.search(pattern, text)
if not m:
    raise SystemExit("Could not find Project Selector Bar block")

# The correct replacement — clean JSX with proper onChange, map, and closing tags
CORRECT = '''{/* Project Selector Bar */}
      <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-3 text-xs">
        <span className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
          Select Project:
        </span>
        <select
          value={selectedProjectId}
          onChange={e => setSelectedProjectId(e.target.value)}
          className="flex-1 min-w-[300px] py-2 px-3 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-slate-50/50 focus:bg-white"
        >
          {(filteredProjects || []).map(p => {
            const c = countByStage(p.id);
            const cls = classifyProject(p.id);
            const icon = cls === 'COMPLETE' ? '✓' : cls === 'NO_EVIDENCE' ? '○' : '⚠';
            const label =
              cls === 'COMPLETE' ? 'Complete' :
              cls === 'NO_EVIDENCE' ? 'No evidence' :
              cls === 'MISSING_AFTER' ? 'Missing after' :
              'Missing before';
            return (
              <option key={p.id} value={p.id}>
                {icon} {p.id} — {p.title} — {c.before}B/{c.during}D/{c.after}A ({label})
              </option>
            );
          })}
        </select>
        {filteredProjects.length === 0 && (
          <span className="text-[11px] text-slate-500 italic">
            No projects match the current filters.
          </span>
        )}
      </div>'''

text = text[:m.start()] + CORRECT + text[m.end():]

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  Rebuilt Project Selector Bar with clean JSX")
print("  Restored onChange handler")
print("  Added empty-state message")