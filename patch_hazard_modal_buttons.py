import pathlib

p = pathlib.Path("src/components/hazards/HazardDetailModal.tsx")
src = p.read_text(encoding="utf-8")

old = """            {!hazard.verified_by && (
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

new = """            {(!hazard.verified_by || !hazard.assessment) && (
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

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Patched: merged two early-stage buttons into one 'Verification & Assessment'")
elif "Verification &amp; Assessment" in src:
    print("Already patched")
else:
    print("Pattern not found — manual edit needed around line 396")