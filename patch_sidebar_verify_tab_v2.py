"""
patch_sidebar_verify_tab_v2.py
1. Adds a Verification tab inside HazardReportsTabs (verbatim anchors).
2. Routes currentView === 'verification' through HazardReportsTabs.
3. Removes '8. Verification & Assessment' from the sidebar.
"""
import pathlib
import re

# =========================================================================
# PART 1 — Add Verification tab to HazardReportsTabs
# =========================================================================
hrt = pathlib.Path("src/components/hazards/HazardReportsTabs.tsx")
src = hrt.read_text(encoding="utf-8")
changes = []

# 1a. Import VerificationWorkspace
if "VerificationWorkspace" in src:
    changes.append("VerificationWorkspace already imported — skipped")
else:
    anchor = "import { InterventionPlanning } from '../interventions/InterventionPlanning.tsx';\n"
    if anchor not in src:
        print("step 1a: InterventionPlanning import anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(
        anchor,
        anchor + "import { VerificationWorkspace } from '../verification/VerificationWorkspace.tsx';\n",
        1,
    )
    changes.append("imported VerificationWorkspace")

# 1b. Add CheckSquare icon
if "CheckSquare" in src:
    changes.append("CheckSquare already imported — skipped")
else:
    anchor = "import { AlertTriangle, Compass } from 'lucide-react';\n"
    if anchor not in src:
        print("step 1b: lucide import anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(anchor, "import { AlertTriangle, Compass, CheckSquare } from 'lucide-react';\n", 1)
    changes.append("added CheckSquare icon")

# 1c. Extend Tab type
old = "type Tab = 'hazards' | 'interventions';\n"
new = "type Tab = 'hazards' | 'interventions' | 'verification';\n"
if old in src:
    src = src.replace(old, new, 1)
    changes.append("extended Tab type")
else:
    print("step 1c: Tab type anchor NOT FOUND")
    raise SystemExit(1)

# 1d. Add verification props to interface
if "onVerify?:" in src:
    changes.append("verification props already present — skipped")
else:
    anchor = """  onRefresh: () => Promise<void> | void;
  referenceData: any;

  // Optional initial tab
  initialTab?: Tab;
}"""
    new = """  onRefresh: () => Promise<void> | void;
  referenceData: any;

  // Verification tab props
  onVerify?: (hazardId: string, isValid: boolean, notes: string, requestInspection: boolean) => Promise<any>;
  onAssess?: (hazardId: string, assessmentData: any) => Promise<any>;
  onRecommendIntervention?: (hazardId: string, interventionData: any) => Promise<any>;

  // Optional initial tab
  initialTab?: Tab;
}"""
    if anchor not in src:
        print("step 1d: props interface anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(anchor, new, 1)
    changes.append("added verification props")

# 1e. Destructure new props
if "onVerify,\n  onAssess,\n  onRecommendIntervention," in src:
    changes.append("verification props already destructured — skipped")
else:
    anchor = """  onRefresh,
  referenceData,
  initialTab = 'hazards',
}) => {"""
    new = """  onRefresh,
  referenceData,
  onVerify,
  onAssess,
  onRecommendIntervention,
  initialTab = 'hazards',
}) => {"""
    if anchor not in src:
        print("step 1e: destructure anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(anchor, new, 1)
    changes.append("destructured verification props")

# 1f. Add verification entry to tabs array
if "id: 'verification'" in src:
    changes.append("verification tab entry already present — skipped")
else:
    anchor = """  const tabs: { id: Tab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'hazards', label: 'Hazard Reports', icon: <AlertTriangle className="w-4 h-4" />, count: hazards.length },
    { id: 'interventions', label: 'Interventions', icon: <Compass className="w-4 h-4" />, count: interventions.length },
  ];"""
    new = """  const pendingVerifications = hazards.filter(
    (h: any) => h.verification_status === 'Pending' || h.verification_status === 'Under Review'
  ).length;

  const tabs: { id: Tab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'hazards', label: 'Hazard Reports', icon: <AlertTriangle className="w-4 h-4" />, count: hazards.length },
    { id: 'interventions', label: 'Interventions', icon: <Compass className="w-4 h-4" />, count: interventions.length },
    { id: 'verification', label: 'Verification & Assessment', icon: <CheckSquare className="w-4 h-4" />, count: pendingVerifications },
  ];"""
    if anchor not in src:
        print("step 1f: tabs array anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(anchor, new, 1)
    changes.append("added verification tab to array")

# 1g. Render VerificationWorkspace when tab === 'verification'
# Anchor is the ENTIRE interventions render block verbatim — including hazards={hazards}
anchor = """      {tab === 'interventions' && (
        <InterventionPlanning
          interventions={interventions}
          hazards={hazards}
          projects={projects}
          onUpdateIntervention={onUpdateIntervention}
          currentUser={currentUser}
          onRefresh={onRefresh}
          referenceData={referenceData}
          hideHeader
        />
      )}"""
new = anchor + """

      {tab === 'verification' && (
        <VerificationWorkspace
          hazards={hazards}
          referenceData={referenceData}
          onVerify={onVerify}
          onAssess={onAssess}
          onRecommendIntervention={onRecommendIntervention}
          onSelectHazard={onSelectHazard}
        />
      )}"""
if anchor not in src:
    print("step 1g: render anchor NOT FOUND (unexpected — paste the block if it fails)")
    raise SystemExit(1)
src = src.replace(anchor, new, 1)
changes.append("added verification tab render block")

hrt.write_text(src, encoding="utf-8")

print("HazardReportsTabs.tsx changes:")
for c in changes:
    print(" -", c)

# =========================================================================
# PART 2 — App.tsx
# =========================================================================
app = pathlib.Path("src/App.tsx")
src = app.read_text(encoding="utf-8")
app_changes = []

# 2a. Widen the condition
old = """            {(currentView === 'hazards' || currentView === 'interventions') && (
              <HazardReportsTabs
                initialTab={currentView === 'interventions' ? 'interventions' : 'hazards'}
"""
new = """            {(currentView === 'hazards' || currentView === 'interventions' || currentView === 'verification') && (
              <HazardReportsTabs
                initialTab={
                  currentView === 'interventions' ? 'interventions' :
                  currentView === 'verification' ? 'verification' :
                  'hazards'
                }
"""
if old in src:
    src = src.replace(old, new, 1)
    app_changes.append("widened condition to include 'verification'")
else:
    print("App.tsx step 2a anchor NOT FOUND")
    raise SystemExit(1)

# 2b. Pass verification handlers
old = """                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
              />
            )}"""
new = """                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
                onVerify={handleVerifyHazard}
                onAssess={handleAssessHazard}
                onRecommendIntervention={handleRecommendIntervention}
              />
            )}"""
if old in src:
    src = src.replace(old, new, 1)
    app_changes.append("passed verification handlers")
else:
    print("App.tsx step 2b anchor NOT FOUND")
    raise SystemExit(1)

# 2c. Remove the standalone VerificationWorkspace block
old = """            {currentView === 'verification' && (
              <VerificationWorkspace
                hazards={hazards}
                referenceData={referenceData}
                onVerify={handleVerifyHazard}
                onAssess={handleAssessHazard}
                onRecommendIntervention={handleRecommendIntervention}
                onSelectHazard={h => setSelectedHazard(h)}
              />
            )}

"""
if old in src:
    src = src.replace(old, "", 1)
    app_changes.append("removed standalone VerificationWorkspace render")
else:
    print("WARN: standalone VerificationWorkspace render NOT FOUND — check manually")

# 2d. Remove unused import
imp = "import { VerificationWorkspace } from './components/verification/VerificationWorkspace.tsx';\n"
if imp in src and "VerificationWorkspace" not in src.replace(imp, ""):
    src = src.replace(imp, "", 1)
    app_changes.append("removed VerificationWorkspace import")

app.write_text(src, encoding="utf-8")

print("\nApp.tsx changes:")
for c in app_changes:
    print(" -", c)

# =========================================================================
# PART 3 — Sidebar
# =========================================================================
sb = pathlib.Path("src/components/common/Sidebar.tsx")
src = sb.read_text(encoding="utf-8")
sb_changes = []

old = "  { id: 'verification', label: '8. Verification & Assessment', icon: CheckSquare, category: 'INTERVENTIONS & WORKFLOW' },\n"
if old in src:
    src = src.replace(old, "", 1)
    sb_changes.append("removed '8. Verification & Assessment' from NAV_ITEMS")
else:
    if "id: 'verification'" not in src:
        sb_changes.append("verification nav item already absent")
    else:
        print("Sidebar: verification nav line NOT FOUND")
        raise SystemExit(1)

# Drop unused CheckSquare import if only import remains
if len(re.findall(r"\bCheckSquare\b", src)) == 1:
    src = re.sub(r"(\n\s*)CheckSquare,", "", src, count=1)
    sb_changes.append("removed unused CheckSquare import")

sb.write_text(src, encoding="utf-8")

print("\nSidebar.tsx changes:")
for c in sb_changes:
    print(" -", c)

# Brace balance
for label, path in [("HazardReportsTabs.tsx", hrt), ("App.tsx", app), ("Sidebar.tsx", sb)]:
    s = path.read_text(encoding="utf-8")
    o, c = s.count("{"), s.count("}")
    print(f"{label}: brace balance {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")