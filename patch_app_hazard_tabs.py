import pathlib

p = pathlib.Path("src/App.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add import
if "HazardReportsTabs" not in src:
    old_import = "import { HazardList } from './components/hazards/HazardList.tsx';"
    new_import = ("import { HazardList } from './components/hazards/HazardList.tsx';\n"
                  "import { HazardReportsTabs } from './components/hazards/HazardReportsTabs.tsx';")
    if old_import in src:
        src = src.replace(old_import, new_import, 1)
        changes.append("added HazardReportsTabs import")

# 2. Replace the HazardList block
old_hazard_block = """            {currentView === 'hazards' && (
              <HazardList
                hazards={hazards}
                statesAndLgas={referenceData?.states_and_lgas || {}}
                categories={referenceData?.hazard_categories || []}
                onSelectHazard={h => setSelectedHazard(h)}
                onNewReportClick={() => setIsReportModalOpen(true)}
                onVerifyHazard={h => {
                  setSelectedHazard(h);
                  setCurrentView('verification');
                }}
              />
            )}"""

new_hazard_block = """            {(currentView === 'hazards' || currentView === 'interventions') && (
              <HazardReportsTabs
                initialTab={currentView === 'interventions' ? 'interventions' : 'hazards'}
                hazards={hazards}
                statesAndLgas={referenceData?.states_and_lgas || {}}
                categories={referenceData?.hazard_categories || []}
                onSelectHazard={h => setSelectedHazard(h)}
                onNewReportClick={() => setIsReportModalOpen(true)}
                onVerifyHazard={h => {
                  setSelectedHazard(h);
                  setCurrentView('verification');
                }}
                interventions={interventions}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
              />
            )}"""

if old_hazard_block in src:
    src = src.replace(old_hazard_block, new_hazard_block)
    changes.append("replaced HazardList block with HazardReportsTabs")

# 3. Remove the old interventions block
old_interv_block = """            {currentView === 'interventions' && (
              <InterventionPlanning
                interventions={interventions}
                hazards={hazards}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
              />
            )}"""

if old_interv_block in src:
    src = src.replace(old_interv_block, "")
    changes.append("removed old interventions block")

# 4. Update the view title resolver
old_title = """      case 'hazards': return 'Edo State Ecological Hazard Register';
      case 'verification': return 'Hazard Verification & Triage Workspace';"""
new_title = """      case 'hazards':
      case 'interventions': return 'Hazards & Interventions';
      case 'verification': return 'Hazard Verification & Triage Workspace';"""
if old_title in src:
    src = src.replace(old_title, new_title)
    changes.append("updated getViewTitle for hazards + interventions")

# Also remove the now-duplicate case for interventions if it exists later in the switch
old_dup = "      case 'interventions': return 'Edo State Intervention Planning & Pipeline';\n"
if old_dup in src:
    src = src.replace(old_dup, "")
    changes.append("removed duplicate interventions title case")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)