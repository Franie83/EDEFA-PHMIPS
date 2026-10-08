"""
Insert the "Manage Contractors" button and the ManageContractorsModal
render into ProjectModal.tsx.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# ============================================================
# 1. Ensure the import is there
# ============================================================
if "from './ManageContractorsModal.tsx'" not in text:
    # Look for any existing import of ContractorModal (old) and swap it
    if "from './ContractorModal.tsx'" in text:
        text = text.replace(
            "import { ContractorModal } from './ContractorModal.tsx';",
            "import { ManageContractorsModal } from './ManageContractorsModal.tsx';",
            1,
        )
        print("  Swapped ContractorModal import for ManageContractorsModal")
    else:
        old = "import { api } from '../../services/api.ts';"
        if old in text:
            text = text.replace(
                old,
                old + "\nimport { ManageContractorsModal } from './ManageContractorsModal.tsx';",
                1,
            )
            print("  Added ManageContractorsModal import")
        else:
            raise SystemExit("Could not find api import anchor")
else:
    print("  Import already present")

# ============================================================
# 2. Ensure the state variable is there
# ============================================================
if "showManageContractors" not in text:
    anchor = "const [contractorsLoading, setContractorsLoading] = useState(false);"
    if anchor not in text:
        raise SystemExit("contractorsLoading anchor not found")
    text = text.replace(
        anchor,
        anchor + "\n  const [showManageContractors, setShowManageContractors] = useState(false);",
        1,
    )
    print("  Added showManageContractors state")
else:
    print("  State already present")

# ============================================================
# 3. Add the "Manage Contractors" button below the dropdown
# ============================================================
# Find the contractor select's closing </select>
marker = "— Select a registered contractor —"
idx = text.find(marker)
if idx == -1:
    raise SystemExit("Could not find contractor dropdown marker")

close_select = text.find("</select>", idx)
if close_select == -1:
    raise SystemExit("Could not find </select> after contractor dropdown")

# Check if the button already exists
window = text[close_select:close_select + 500]
if "Manage Contractors" not in window:
    insert_at = close_select + len("</select>")
    add_button = """

                <button
                  type="button"
                  onClick={() => setShowManageContractors(true)}
                  className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 hover:text-emerald-900"
                >
                  ⚙️ Manage Contractors
                </button>"""
    text = text[:insert_at] + add_button + text[insert_at:]
    print("  Inserted 'Manage Contractors' button")
else:
    print("  Button already present")

# ============================================================
# 4. Render the ManageContractorsModal at the end of the component
# ============================================================
if "<ManageContractorsModal" not in text:
    # Find the last closing of the outer modal: the pattern is:
    #     </div>
    #   </div>
    #   );
    # };
    # We look for the final `);` followed by `};` at the end of the file
    closing = "\n  );\n};"
    if closing not in text:
        # try with different whitespace
        closing = ");\n};"
        if closing not in text:
            raise SystemExit("Could not find component-closing pattern")

    modal_jsx = """      <ManageContractorsModal
        isOpen={showManageContractors}
        onClose={() => setShowManageContractors(false)}
        onChanged={async () => {
          try {
            const list = await api.getContractors();
            setContractorList(list || []);
          } catch (err) {
            console.error('Failed to refresh contractors:', err);
          }
        }}
      />

  );
};"""

    text = text.replace(closing, "\n" + modal_jsx, 1)
    print("  Rendered ManageContractorsModal at end of component")
else:
    print("  ManageContractorsModal render already present")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")