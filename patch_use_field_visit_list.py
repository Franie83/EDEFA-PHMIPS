"""
patch_use_field_visit_list.py
Replaces the minimal inspections card list in ProjectDetailModal with the full
<FieldVisitList> component — matching Field Operations → Inspections 1:1.
"""
import pathlib
import re

p = pathlib.Path("src/components/projects/ProjectDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# --- Guard -----------------------------------------------------------------
if "FieldVisitList" in src:
    print("Already patched — nothing to do.")
    print(f"Brace balance: {'OK' if src.count('{') == src.count('}') else 'MISMATCH'}")
    raise SystemExit(0)

# --- 1. Import FieldVisitList ----------------------------------------------
import_anchor = "import { BeforeAfterMonitoring } from '../monitoring/BeforeAfterMonitoring.tsx';\n"
if import_anchor not in src:
    # Fallback: attach to the api import
    import_anchor = "import { api } from '../../services/api.ts';\n"
    if import_anchor not in src:
        print("Import anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(
        import_anchor,
        "import { FieldVisitList } from '../field/FieldVisitList.tsx';\n" + import_anchor,
        1,
    )
else:
    src = src.replace(
        import_anchor,
        "import { FieldVisitList } from '../field/FieldVisitList.tsx';\n" + import_anchor,
        1,
    )
print(" - imported FieldVisitList")

# --- 2. Replace the inspections block body ---------------------------------
# After the tabs patch, the inspections block is:
#   {activeTab === 'inspections' && (
#     <>
#       {/* Linked Field Visits */}
#       <div>
#         ... old minimal card list ...
#       </div>
#     </>
#   )}
#
# We'll match from the comment through the block's closing </div> and replace
# with a single <FieldVisitList> call.
#
# To be safe, we use a regex that stops at the block's closing `</>` `)}`.
pattern = re.compile(
    r"\{activeTab === 'inspections' && \(\n"
    r"\s*<>\n"
    r"\s*\{/\* Linked Field Visits \*/\}\n"
    r".*?"
    r"\n\s*</>\n"
    r"\s*\)\}\n",
    re.DOTALL
)

new_block = """{activeTab === 'inspections' && (
            <FieldVisitList
              visits={project.site_visits || []}
              projects={[project]}
              onOpenLogModal={() => { onClose(); onLogVisitClick(project); }}
              evidenceList={(project as any).evidence_files || []}
            />
          )}
"""

m = pattern.search(src)
if not m:
    print("Inspections block regex NOT FOUND.")
    print("Paste lines 551-640 verbatim and I'll target the exact bytes.")
    raise SystemExit(1)

src = src[:m.start()] + new_block + src[m.end():]
print(" - replaced inspections block with <FieldVisitList>")

p.write_text(src, encoding="utf-8")

print("Changes: done")
opens = src.count("{")
closes = src.count("}")
print(f"\nBrace balance: {'OK' if opens == closes else f'MISMATCH ({opens} vs {closes})'}")