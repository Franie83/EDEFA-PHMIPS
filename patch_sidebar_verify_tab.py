"""
patch_sidebar_verify_tab.py
1. Adds a Verification tab inside HazardReportsTabs.
2. Routes currentView === 'verification' through HazardReportsTabs (initialTab='verification').
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
if "VerificationWorkspace" not in src:
    import_anchor = "import { InterventionPlanning } from '../interventions/InterventionPlanning.tsx';\n"
    if import_anchor not in src:
        print("HazardReportsTabs: InterventionPlanning import anchor NOT FOUND")
        raise SystemExit(1)
    src = src.replace(
        import_anchor,
        import_anchor + "import { VerificationWorkspace } from '../verification/VerificationWorkspace.tsx';\n",
        1,
    )
    changes.append("imported VerificationWorkspace")

# 1b. Add CheckSquare icon to lucide import (from 'AlertTriangle, Compass' line)
icon_anchor = "import { AlertTriangle, Compass } from 'lucide-react';\n"
if icon_anchor in src:
    src = src.replace(icon_anchor, "import { AlertTriangle, Compass, CheckSquare } from 'lucide-react';\n", 1)
    changes.append("added CheckSquare icon to lucide import")
elif "CheckSquare" not in src:
    print("HazardReportsTabs: lucide icon import anchor NOT FOUND")
    raise SystemExit(1)

# 1c. Extend Tab type
old_type = "type Tab = 'hazards' | 'interventions';\n"
new_type = "type Tab = 'hazards' | 'interventions' | 'verification';\n"
if old_type in src:
    src = src.replace(old_type, new_type, 1)
    changes.append("extended Tab type with 'verification'")
else:
    print("HazardReportsTabs: Tab type anchor NOT FOUND")
    raise SystemExit(1)

# 1d. Add verification props to Props interface (after referenceData)
props_anchor = """  onRefresh: () => Promise<void> | void;
  referenceData: any;

  // Optional initial tab
  initialTab?: Tab;
}"""
props_new = """  onRefresh: () => Promise<void> | void;
  referenceData: any;

  // Verification tab props (optional — only needed when the tab is used)
  onVerify?: (hazardId: string, isValid: boolean, notes: string, requestInspection: boolean) => Promise<any>;
  onAssess?: (hazardId: string, assessmentData: any) => Promise<any>;
  onRecommendIntervention?: (hazardId: string, interventionData: any) => Promise<any>;

  // Optional initial tab
  initialTab?: Tab;
}"""
if props_anchor in src:
    src = src.replace(props_anchor, props_new, 1)
    changes.append("added verification props to interface")
else:
    print("HazardReportsTabs: props interface anchor NOT FOUND")
    raise SystemExit(1)

# 1e. Destructure new props
dest_anchor = """  onRefresh,
  referenceData,
  initialTab = 'hazards',
}) => {"""
dest_new = """  onRefresh,
  referenceData,
  onVerify,
  onAssess,
  onRecommendIntervention,
  initialTab = 'hazards',
}) => {"""
if dest_anchor in src:
    src = src.replace(dest_anchor, dest_new, 1)
    changes.append("destructured verification props")
else:
    print("HazardReportsTabs: destructure anchor NOT FOUND")
    raise SystemExit(1)

# 1f. Add verification entry to tabs array
tabs_anchor = """  const tabs: { id: Tab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'hazards', label: 'Hazard Reports', icon: <AlertTriangle className="w-4 h-4" />, count: hazards.length },
    { id: 'interventions', label: 'Interventions', icon: <Compass className="w-4 h-4" />, count: interventions.length },
  ];"""
tabs_new = """  const pendingVerifications = hazards.filter(
    (h: any) => h.verification_status === 'Pending' || h.verification_status === 'Under Review'
  ).length;

  const tabs: { id: Tab; label: string; icon: React.ReactNode; count: number }[] = [
    { id: 'hazards', label: 'Hazard Reports', icon: <AlertTriangle className="w-4 h-4" />, count: hazards.length },
    { id: 'interventions', label: 'Interventions', icon: <Compass className="w-4 h-4" />, count: interventions.length },
    { id: 'verification', label: 'Verification & Assessment', icon: <CheckSquare className="w-4 h-4" />, count: pendingVerifications },
  ];"""
if tabs_anchor in src:
    src = src.replace(tabs_anchor, tabs_new, 1)
    changes.append("added verification entry to tabs array")
else:
    print("HazardReportsTabs: tabs array anchor NOT FOUND")
    raise SystemExit(1)

# 1g. Render VerificationWorkspace when tab is 'verification'
render_anchor = """      {tab === 'interventions' && (
        <InterventionPlanning
          interventions={interventions}
          projects={projects}
          onUpdateIntervention={onUpdateIntervention}
          currentUser={currentUser}
          onRefresh={onRefresh}
          referenceData={referenceData}
          hideHeader
        />
      )}"""
render_new = render_anchor + """

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
if render_anchor in src:
    src = src.replace(render_anchor, render_new, 1)
    changes.append("added verification tab render block")
else:
    print("HazardReportsTabs: render anchor NOT FOUND")
    raise SystemExit(1)

hrt.write_text(src, encoding="utf-8")

print("HazardReportsTabs.tsx changes:")
for c in changes:
    print(" -", c)

# =========================================================================
# PART 2 — App.tsx: route verification through HazardReportsTabs
# =========================================================================
app = pathlib.Path("src/App.tsx")
src = app.read_text(encoding="utf-8")
app_changes = []

# 2a. Widen the HazardReportsTabs conditional to include 'verification'
old_cond = """            {(currentView === 'hazards' || currentView === 'interventions') && (
              <HazardReportsTabs
                initialTab={currentView === 'interventions' ? 'interventions' : 'hazards'}
"""
new_cond = """            {(currentView === 'hazards' || currentView === 'interventions' || currentView === 'verification') && (
              <HazardReportsTabs
                initialTab={
                  currentView === 'interventions' ? 'interventions' :
                  currentView === 'verification' ? 'verification' :
                  'hazards'
                }
"""
if old_cond in src:
    src = src.replace(old_cond, new_cond, 1)
    app_changes.append("widened HazardReportsTabs condition to include 'verification'")
else:
    print("App.tsx: HazardReportsTabs conditional anchor NOT FOUND")
    raise SystemExit(1)

# 2b. Pass verification handler props into HazardReportsTabs
old_props = """                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
              />
            )}"""
new_props = """                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
                onVerify={handleVerifyHazard}
                onAssess={handleAssessHazard}
                onRecommendIntervention={handleRecommendIntervention}
              />
            )}"""
if old_props in src:
    src = src.replace(old_props, new_props, 1)
    app_changes.append("passed verification handlers into HazardReportsTabs")
else:
    print("App.tsx: HazardReportsTabs props anchor NOT FOUND")
    raise SystemExit(1)

# 2c. Remove the standalone VerificationWorkspace render block
old_ver_render = """            {currentView === 'verification' && (
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
if old_ver_render in src:
    src = src.replace(old_ver_render, "", 1)
    app_changes.append("removed standalone VerificationWorkspace render block")
else:
    print("WARN: standalone VerificationWorkspace render block NOT FOUND — check manually")

# 2d. Drop the now-unused VerificationWorkspace import
if "VerificationWorkspace" not in re.sub(r"^import.*$", "", src, flags=re.MULTILINE):
    src = src.replace(
        "import { VerificationWorkspace } from './components/verification/VerificationWorkspace.tsx';\n",
        "",
        1,
    )
    app_changes.append("removed VerificationWorkspace import from App.tsx")

app.write_text(src, encoding="utf-8")

print("\nApp.tsx changes:")
for c in app_changes:
    print(" -", c)

# =========================================================================
# PART 3 — Remove '8. Verification & Assessment' from sidebar
# =========================================================================
sb = pathlib.Path("src/components/common/Sidebar.tsx")
src = sb.read_text(encoding="utf-8")
sb_changes = []

old_nav = "  { id: 'verification', label: '8. Verification & Assessment', icon: CheckSquare, category: 'INTERVENTIONS & WORKFLOW' },\n"
if old_nav in src:
    src = src.replace(old_nav, "", 1)
    sb_changes.append("removed '8. Verification & Assessment' from NAV_ITEMS")
else:
    if "id: 'verification'" not in src:
        sb_changes.append("verification nav item already absent")
    else:
        print("Sidebar: verification nav line NOT FOUND")
        raise SystemExit(1)

# Drop unused CheckSquare import
if len(re.findall(r"\bCheckSquare\b", src)) == 1:
    src = re.sub(r"(\n\s*)CheckSquare,", "", src, count=1)
    sb_changes.append("removed unused CheckSquare import")

sb.write_text(src, encoding="utf-8")

print("\nSidebar.tsx changes:")
for c in sb_changes:
    print(" -", c)

# Sanity
for label, path in [("HazardReportsTabs.tsx", hrt), ("App.tsx", app), ("Sidebar.tsx", sb)]:
    s = path.read_text(encoding="utf-8")
    o, c = s.count("{"), s.count("}")
    print(f"{label}: brace balance {'OK' if o == c else f'MISMATCH ({o} vs {c})'}")