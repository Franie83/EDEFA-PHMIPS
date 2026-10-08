"""
Patch src/App.tsx to:
  1. Import canEdit, canDelete helpers
  2. Add editingHazard state
  3. Add handleEditHazard, handleDeleteHazard
  4. Pass onEdit/onDelete/currentRole to HazardDetailModal
  5. Pass editHazard to HazardReportModal

Idempotent.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "App.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "handleEditHazard" in text and "handleDeleteHazard" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# --- Patch 1: import canEdit, canDelete ---
old_import = "import { api } from './services/api.ts';"
new_import = "import { api } from './services/api.ts';\nimport { canEdit as canEditFn, canDelete as canDeleteFn } from './types/tiers.ts';"
if old_import not in text:
    raise SystemExit("api import not found — aborting.")
text = text.replace(old_import, new_import, 1)

# --- Patch 2: add editingHazard state ---
old_state = "  const [selectedHazard, setSelectedHazard] = useState<Hazard | null>(null);"
new_state = "  const [selectedHazard, setSelectedHazard] = useState<Hazard | null>(null);\n  const [editingHazard, setEditingHazard] = useState<Hazard | null>(null);"
if old_state not in text:
    raise SystemExit("selectedHazard state not found — aborting.")
text = text.replace(old_state, new_state, 1)

# --- Patch 3: add handlers right after handleCreateHazard ---
old_handler_anchor = """    await loadData();
    setIsReportModalOpen(false);
  };"""
new_handler_anchor = """    await loadData();
    setIsReportModalOpen(false);
  };

  const handleEditHazard = async (id: string, data: Partial<Hazard>) => {
    await api.updateHazard(id, data);
    await loadData();
    setEditingHazard(null);
    setSelectedHazard(null);
  };

  const handleDeleteHazard = async (hazard: Hazard) => {
    try {
      await api.deleteHazard(hazard.id);
      await loadData();
      setSelectedHazard(null);
    } catch (err: any) {
      alert(`Delete failed: ${err.message || 'Unknown error'}`);
    }
  };"""
if old_handler_anchor not in text:
    raise SystemExit("handleCreateHazard anchor not found — aborting.")
text = text.replace(old_handler_anchor, new_handler_anchor, 1)

# --- Patch 4: HazardReportModal — pass editHazard + route onSubmit ---
old_report_modal = """      <HazardReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        onSubmit={handleCreateHazard}
        statesAndLgas={referenceData?.states_and_lgas || {}}
        categories={referenceData?.hazard_categories || []}
      />"""
new_report_modal = """      <HazardReportModal
        isOpen={isReportModalOpen || Boolean(editingHazard)}
        onClose={() => { setIsReportModalOpen(false); setEditingHazard(null); }}
        onSubmit={editingHazard
          ? (data: any) => handleEditHazard(editingHazard.id, data)
          : handleCreateHazard}
        statesAndLgas={referenceData?.states_and_lgas || {}}
        categories={referenceData?.hazard_categories || []}
        editHazard={editingHazard}
      />"""
if old_report_modal not in text:
    raise SystemExit("HazardReportModal JSX not found — aborting.")
text = text.replace(old_report_modal, new_report_modal, 1)

# --- Patch 5: HazardDetailModal — add onEdit, onDelete, currentRole ---
old_detail_modal = """      <HazardDetailModal
        hazard={selectedHazard}
        onClose={() => setSelectedHazard(null)}
        onVerifyClick={() => {
          setSelectedHazard(null);
          setCurrentView('verification');
        }}
        onAssessClick={() => {
          setSelectedHazard(null);
          setCurrentView('verification');
        }}
        onInterventionClick={() => {
          setSelectedHazard(null);
          setCurrentView('interventions');
        }}
        onNavigateToMap={navigateToMapCoordinate}
      />"""
new_detail_modal = """      <HazardDetailModal
        hazard={selectedHazard}
        onClose={() => setSelectedHazard(null)}
        onVerifyClick={() => {
          setSelectedHazard(null);
          setCurrentView('verification');
        }}
        onAssessClick={() => {
          setSelectedHazard(null);
          setCurrentView('verification');
        }}
        onInterventionClick={() => {
          setSelectedHazard(null);
          setCurrentView('interventions');
        }}
        onNavigateToMap={navigateToMapCoordinate}
        onEdit={canEditFn(currentUser?.role) ? (h) => { setEditingHazard(h); setSelectedHazard(null); } : undefined}
        onDelete={canDeleteFn(currentUser?.role) ? handleDeleteHazard : undefined}
        currentRole={currentUser?.role}
      />"""
if old_detail_modal not in text:
    raise SystemExit("HazardDetailModal JSX not found — aborting.")
text = text.replace(old_detail_modal, new_detail_modal, 1)

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Imported canEdit / canDelete")
print("  - Added editingHazard state")
print("  - Added handleEditHazard / handleDeleteHazard")
print("  - Wired edit mode into HazardReportModal")
print("  - Wired onEdit / onDelete / currentRole into HazardDetailModal")