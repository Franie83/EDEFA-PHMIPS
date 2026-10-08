"""
Fix the JSX parent error in ProjectModal.tsx — wrap the outer div and the
ManageContractorsModal in a React fragment.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "<>\\n      <div id=\"project-create-modal\"" in text or "return (\n    <>\n" in text:
    print("Already wrapped in fragment — skipping.")
    raise SystemExit(0)

# 1. Change `return (` followed by the outer div into `return ( <> ... <div`
old_open = '''  return (
    <div id="project-create-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">'''

new_open = '''  return (
    <>
    <div id="project-create-modal" className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4">'''

if old_open not in text:
    # try with different spacing
    old_open = '  return (\n    <div id="project-create-modal"'
    if old_open not in text:
        raise SystemExit("Could not find the return ( + outer div. Paste the file section.")
    # Insert fragment opening right after `return (`
    text = text.replace('  return (\n', '  return (\n    <>\n', 1)
    print("  Added fragment opening")
else:
    text = text.replace(old_open, new_open, 1)
    print("  Added fragment opening")

# 2. Close the fragment before `);` at the very end
old_close = '''      <ManageContractorsModal
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
};'''

new_close = '''      <ManageContractorsModal
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
    </>
  );
};'''

if old_close not in text:
    # Try looser match
    marker = "<ManageContractorsModal"
    idx = text.find(marker)
    if idx == -1:
        raise SystemExit("Could not find ManageContractorsModal in the file")
    # Find the `);` after it
    end_idx = text.find(");\n};", idx)
    if end_idx == -1:
        end_idx = text.find(");", idx)
        if end_idx == -1:
            raise SystemExit("Could not find `);` after the modal render")
    # Insert `</>` right before `);`
    text = text[:end_idx] + "    </>\n  " + text[end_idx:]
    print("  Added fragment closing")
else:
    text = text.replace(old_close, new_close, 1)
    print("  Added fragment closing")

TARGET.write_text(text, encoding="utf-8")
print(f"\nPatched {TARGET.name}")