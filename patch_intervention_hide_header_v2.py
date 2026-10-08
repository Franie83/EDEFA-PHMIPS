import pathlib

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add hideHeader right after onRefresh prop
old_iface = """  onRefresh?: () => Promise<void> | void;

  referenceData?: any;
}"""
new_iface = """  onRefresh?: () => Promise<void> | void;

  referenceData?: any;

  hideHeader?: boolean;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("interface: added hideHeader prop")
else:
    # Try without trailing }
    import re
    pattern = re.compile(r"(onRefresh\?:\s*\(\)\s*=>\s*Promise<void>\s*\|\s*void;\s*\n\s*\n\s*referenceData\?:\s*any;\s*\n)(\})")
    new_src, n = pattern.subn(r"\1\n  hideHeader?: boolean;\n\2", src)
    if n:
        src = new_src
        changes.append("interface: added hideHeader (regex)")
    else:
        changes.append("interface pattern NOT FOUND — paste lines 43–60")

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
else:
    # Find whatever destructure exists and add hideHeader
    import re
    pattern = re.compile(r"(\n\s*referenceData\s*\n)(\}\s*\)\s*=>\s*\{)")
    new_src, n = pattern.subn(r"\1  ,hideHeader = false\n\2", src)
    if n:
        # Better: replace with proper comma
        pattern2 = re.compile(r"(\n\s*referenceData)(\s*\n\}\s*\)\s*=>\s*\{)")
        new_src, n = pattern2.subn(r"\1,\n  hideHeader = false\2", src)
        if n:
            src = new_src
            changes.append("destructured hideHeader (regex)")
    if "destructured hideHeader" not in " ".join(changes):
        changes.append("destructure pattern NOT FOUND")

# 3. Wrap the header in {!hideHeader && (...)}
old_header = """      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">"""
new_header = """      {/* Header */}
      {!hideHeader && (
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs">"""
if old_header in src:
    src = src.replace(old_header, new_header)
    changes.append("started conditional on header")
else:
    changes.append("header start pattern NOT FOUND")

# Close the conditional — find the end of the header block (Plan New Intervention button + 2 closing divs)
old_end = """            Plan New Intervention
          </button>
        </div>
      </div>"""
new_end = """            Plan New Intervention
          </button>
        </div>
      </div>
      )}"""
if old_end in src:
    src = src.replace(old_end, new_end, 1)
    changes.append("closed conditional on header")
else:
    changes.append("header end pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)

opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")