import pathlib

p = pathlib.Path("src/components/verification/VerificationWorkspace.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add useEffect to React import (needed for auto-advance)
if "useEffect" not in src.split("from 'react'")[0]:
    src = src.replace(
        "import React, { useState } from 'react';",
        "import React, { useState, useEffect } from 'react';",
        1
    )
    changes.append("added useEffect import")

# 2. Insert auto-stage effect + helper right after the selectedHazard declaration
old_sa = "  const selectedHazard = hazards.find(h => h.id === selectedHazardId) || hazards[0];"
new_sa = """  const selectedHazard = hazards.find(h => h.id === selectedHazardId) || hazards[0];

  // Determine the hazard's current workflow stage from its data
  const stageOf = (hz: any): 'VERIFICATION' | 'ASSESSMENT' | 'INTERVENTION' | 'DONE' => {
    if (!hz) return 'VERIFICATION';
    if (hz.recommended_intervention) return 'DONE';
    if (hz.assessment) return 'INTERVENTION';
    if (hz.verified_by) return 'ASSESSMENT';
    return 'VERIFICATION';
  };

  // Auto-advance to the correct tab when the hazard changes
  useEffect(() => {
    const s = stageOf(selectedHazard);
    if (s !== 'DONE') setActiveTab(s);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedHazard?.id, selectedHazard?.verified_by, selectedHazard?.assessment, selectedHazard?.recommended_intervention]);

  const stage = stageOf(selectedHazard);
  const stageLabel: Record<string, string> = {
    VERIFICATION: 'Awaiting Verification',
    ASSESSMENT: 'Verified — ready for Risk Assessment',
    INTERVENTION: 'Assessed — ready for Intervention Formulation',
    DONE: 'Intervention Approved — workflow complete',
  };"""

if old_sa in src and "stageOf" not in src:
    src = src.replace(old_sa, new_sa)
    changes.append("added stageOf helper + auto-advance effect")
else:
    changes.append("selectedHazard pattern NOT FOUND or already patched")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)