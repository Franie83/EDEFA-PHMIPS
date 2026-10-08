import pathlib

p = pathlib.Path("src/App.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add import
if "import { FieldOperations }" not in src:
    needle = "import { AuditLogsModule } from './components/audit/AuditLogsModule.tsx';"
    if needle in src:
        src = src.replace(
            needle,
            needle + "\nimport { FieldOperations } from './components/field-ops/FieldOperations.tsx';"
        )
        changes.append("added FieldOperations import")
    else:
        changes.append("import anchor NOT FOUND")
else:
    changes.append("FieldOperations import already present")

# 2. Replace the three render blocks
old_block = """            {currentView === 'sites' && (
              <SiteList
                sites={sites}
                projects={projects}
                onCreateSite={handleCreateSite}
                onNavigateToMap={navigateToMapCoordinate}
              />
            )}

            {currentView === 'visits' && (
              <FieldVisitList
                visits={visits}
                projects={projects}
                onOpenLogModal={() => {
                  setVisitDefaultProject(null);
                  setIsVisitModalOpen(true);
                }}
              />
            )}

            {currentView === 'monitoring' && (
              <BeforeAfterMonitoring
                projects={projects}
                evidenceList={evidenceList}
              />
            )}"""

new_block = """            {(currentView === 'field-ops' ||
              currentView === 'sites' ||
              currentView === 'visits' ||
              currentView === 'field_visits' ||
              currentView === 'monitoring') && (
              <FieldOperations
                initialTab={
                  currentView === 'visits' || currentView === 'field_visits' ? 'inspections' :
                  currentView === 'monitoring' ? 'monitoring' :
                  'sites'
                }
                sites={sites}
                projects={projects}
                onCreateSite={handleCreateSite}
                onNavigateToMap={navigateToMapCoordinate}
                visits={visits}
                onOpenLogModal={() => {
                  setVisitDefaultProject(null);
                  setIsVisitModalOpen(true);
                }}
                evidenceList={evidenceList}
              />
            )}"""

if old_block in src:
    src = src.replace(old_block, new_block)
    changes.append("render blocks merged into <FieldOperations>")
elif "currentView === 'field-ops'" in src:
    changes.append("render blocks already merged")
else:
    changes.append("render blocks NOT FOUND — manual edit needed")

# 3. Consolidate getViewTitle
old_title = """      case 'sites': return 'Project Sites & Baseline Coordinates';
      case 'visits': return 'Physical Field Inspection Visits Register';
      case 'monitoring': return 'Before & After Longitudinal Monitoring';"""

new_title = """      case 'field-ops':
      case 'sites':
      case 'visits':
      case 'field_visits':
      case 'monitoring': return 'Field Operations — Sites, Inspections & Monitoring';"""

if old_title in src:
    src = src.replace(old_title, new_title)
    changes.append("getViewTitle() consolidated")
elif "Field Operations — Sites" in src:
    changes.append("getViewTitle() already consolidated")
else:
    changes.append("getViewTitle() pattern NOT FOUND — manual edit needed")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)