import pathlib
import re

p = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# --- Guard: if already wrapped, bail ---
if "{!hideHeader && (" in src and "Plan New Intervention" in src:
    # Check whether the wrapping actually surrounds the header (crude but effective)
    idx_wrap = src.find("{!hideHeader && (")
    idx_btn  = src.find("Plan New Intervention")
    if 0 < idx_wrap < idx_btn:
        print("Already wrapped — nothing to do.")
        print(f"Brace balance: {'OK' if src.count('{') == src.count('}') else 'MISMATCH'}")
        raise SystemExit(0)

# --- Step 1: header START ---
start_pattern = re.compile(
    r"(\{/\*\s*Header\s*\*/\}\s*\n)(\s*)(<div[^>]*className=\"flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-xs\">)"
)
m = start_pattern.search(src)
if not m:
    print("Header START pattern NOT FOUND — paste lines around '{/* Header */}'")
    raise SystemExit(1)
indent = m.group(2)
new_start = f"{m.group(1)}{indent}{{!hideHeader && (\n{indent}{m.group(3)}"
src = src[:m.start()] + new_start + src[m.end():]
changes.append("wrapped header start in {!hideHeader && (…)}")

# --- Step 2: header END ---
# The header block ends with: ...Plan New Intervention</button> then two closing </div>s.
end_pattern = re.compile(
    r"(Plan New Intervention\s*\n\s*</button>\s*\n)(\s*)(</div>\s*\n)(\s*)(</div>)",
    re.MULTILINE
)
m2 = end_pattern.search(src)
if not m2:
    print("Header END pattern NOT FOUND — paste the block around 'Plan New Intervention'")
    raise SystemExit(1)
# Insert ')}' after the second closing </div>, matching the div's indentation
close_indent = m2.group(5) if False else m2.group(2)
new_end = f"{m2.group(1)}{m2.group(2)}{m2.group(3)}{m2.group(4)}{m2.group(5)}\n{indent})}}"
src = src[:m2.start()] + new_end + src[m2.end():]
changes.append("closed the {!hideHeader && (…)} wrapper")

p.write_text(src, encoding="utf-8")

print("Changes:")
for c in changes:
    print(" -", c)

opens  = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")