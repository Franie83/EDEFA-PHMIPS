import pathlib

# ============================================================
# Fix 1: InterventionModal closes on success
# ============================================================
ip = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
isrc = ip.read_text(encoding="utf-8")
ichanges = []

old_success = """        onSuccess={async () => {
          setPickerSelectedHazard(null);
          await onRefresh?.();
        }}"""
new_success = """        onSuccess={async () => {
          setIsNewModalOpen(false);
          setPickerSelectedHazard(null);
          await onRefresh?.();
        }}"""
if old_success in isrc:
    isrc = isrc.replace(old_success, new_success)
    ichanges.append("InterventionModal closes on success")
else:
    ichanges.append("InterventionModal onSuccess pattern NOT FOUND")

# Add referenceData to props interface
old_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
}"""
new_iface = """interface InterventionPlanningProps {
  interventions: Intervention[];
  hazards: Hazard[];
  projects: Project[];
  onUpdateIntervention: (id: string, data: Partial<Intervention>) => Promise<void>;
  currentUser?: { role?: string; name?: string } | null;
  onRefresh?: () => Promise<void> | void;
  referenceData?: any;
}"""
if old_iface in isrc:
    isrc = isrc.replace(old_iface, new_iface)
    ichanges.append("InterventionPlanning interface: added referenceData")

# Destructure referenceData
old_dest = """export const InterventionPlanning: React.FC<InterventionPlanningProps> = ({
  interventions = [],
  hazards = [],
  projects = [],
  onUpdateIntervention,
  currentUser,
  onRefresh
}) => {"""
new_dest = """export const InterventionPlanning: React.FC<InterventionPlanningProps> = ({
  interventions = [],
  hazards = [],
  projects = [],
  onUpdateIntervention,
  currentUser,
  onRefresh,
  referenceData
}) => {"""
if old_dest in isrc:
    isrc = isrc.replace(old_dest, new_dest)
    ichanges.append("InterventionPlanning destructure: added referenceData")

# Pass to inner ProjectModal — fix the empty props
old_pm = """      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setProjectSourceIntervention(null);
        }}
        onSubmit={handleCreateProjectFromIntervention}
        statesAndLgas={{}}
        categories={[]}
        prefillInterventionId={projectSourceIntervention?.id}
      />"""
new_pm = """      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setProjectSourceIntervention(null);
        }}
        onSubmit={handleCreateProjectFromIntervention}
        statesAndLgas={referenceData?.states_and_lgas || {}}
        categories={referenceData?.hazard_categories || []}
        prefillInterventionId={projectSourceIntervention?.id}
        referenceData={referenceData}
      />"""
if old_pm in isrc:
    isrc = isrc.replace(old_pm, new_pm)
    ichanges.append("inner ProjectModal now receives reference data")
else:
    ichanges.append("inner ProjectModal pattern NOT FOUND")

ip.write_text(isrc, encoding="utf-8")

# ============================================================
# Fix 2: App.tsx passes referenceData to InterventionPlanning
# ============================================================
ap = pathlib.Path("src/App.tsx")
asrc = ap.read_text(encoding="utf-8")
achanges = []

old_ip = """              <InterventionPlanning
                interventions={interventions}
                hazards={hazards}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
              />"""
new_ip = """              <InterventionPlanning
                interventions={interventions}
                hazards={hazards}
                projects={projects}
                onUpdateIntervention={handleUpdateIntervention}
                currentUser={currentUser}
                onRefresh={loadData}
                referenceData={referenceData}
              />"""
if old_ip in asrc:
    asrc = asrc.replace(old_ip, new_ip)
    achanges.append("App.tsx: passes referenceData to InterventionPlanning")
else:
    achanges.append("App.tsx InterventionPlanning pattern NOT FOUND")

ap.write_text(asrc, encoding="utf-8")

print("InterventionPlanning.tsx changes:")
for c in ichanges:
    print(" -", c)
print("\nApp.tsx changes:")
for c in achanges:
    print(" -", c)