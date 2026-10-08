import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add hideHeader prop to interface
old_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
  referenceData?: any;
}"""
new_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
  referenceData?: any;
  hideHeader?: boolean;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("added hideHeader prop to interface")
else:
    changes.append("interface pattern NOT FOUND")

# 2. Destructure hideHeader
old_dest = """  onRefresh,
  referenceData
}) => {"""
new_dest = """  onRefresh,
  referenceData,
  hideHeader = false
}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest, 1)
    changes.append("destructured hideHeader")

# 3. Wrap the header JSX in a conditional
# The header starts with {/* Header */} and ends before the Approval Queue Tabs
# Find the outer header wrapper
old_header_start = """      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">"""
new_header_start = """      {/* Header */}
      {!hideHeader && (
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">"""
if old_header_start in src:
    src = src.replace(old_header_start, new_header_start)
    changes.append("started conditional wrapper on header")

# Find where the header div closes — the block ends with the "Plan New Intervention" button and </div>
old_header_end = """            Plan New Intervention
          </button>
        </div>
      </div>"""
new_header_end = """            Plan New Intervention
          </button>
        </div>
      </div>
      )}"""
if old_header_end in src:
    src = src.replace(old_header_end, new_header_end, 1)
    changes.append("closed conditional wrapper on header")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

# Sanity
opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")