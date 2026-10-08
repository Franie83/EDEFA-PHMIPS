import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

# The merged version we just applied
merged = """            {(!hazard.verified_by || !hazard.assessment) && (
              <button
                onClick={() => {
                  onClose();
                  if (!hazard.verified_by) {
                    onVerifyClick(hazard);
                  } else {
                    onAssessClick(hazard);
                  }
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-700 text-white hover:bg-emerald-800"
                title={
                  !hazard.verified_by
                    ? 'Stage 1: Verify the report is a genuine hazard'
                    : 'Stage 2: Score the hazard to calculate priority'
                }
              >
                Verification &amp; Assessment
              </button>
            )}
"""

# The original two-button version
original = """            {!hazard.verified_by && (
              <button
                onClick={() => {
                  onClose();
                  onVerifyClick(hazard);
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-700 text-white hover:bg-emerald-800"
              >
                Perform Technical Verification
              </button>
            )}

            {!hazard.assessment && hazard.verified_by && (
              <button
                onClick={() => {
                  onClose();
                  onAssessClick(hazard);
                }}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-amber-600 text-white hover:bg-amber-700"
              >
                Conduct Technical Assessment
              </button>
            )}
"""

if merged in src:
    src = src.replace(merged, original)
    p.write_text(src, encoding="utf-8")
    print("Reverted: two-button form restored")
elif "Perform Technical Verification" in src and "Conduct Technical Assessment" in src:
    print("Already reverted — two-button form is already in place")
else:
    print("Pattern not found. Manual edit needed.")
    # Show the current button block to help debug
    import re
    m = re.search(r'\{!hazard\.verified_by.{0,800}', src, re.DOTALL)
    if m:
        print("\nCurrent block:")
        print(m.group(0))