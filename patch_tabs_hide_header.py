import pathlib

p = pathlib.Path("src/components/hazards/HazardReportsTabs.tsx")
src = p.read_text(encoding="utf-8")

old = """        <InterventionPlanning
          interventions={interventions}
          hazards={hazards}
          projects={projects}
          onUpdateIntervention={onUpdateIntervention}
          currentUser={currentUser}
          onRefresh={onRefresh}
          referenceData={referenceData}
        />"""
new = """        <InterventionPlanning
          interventions={interventions}
          hazards={hazards}
          projects={projects}
          onUpdateIntervention={onUpdateIntervention}
          currentUser={currentUser}
          onRefresh={onRefresh}
          referenceData={referenceData}
          hideHeader
        />"""

if old in src:
    src = src.replace(old, new)
    p.write_text(src, encoding="utf-8")
    print("Added hideHeader to InterventionPlanning in HazardReportsTabs")
elif "hideHeader" in src:
    print("Already added")
else:
    print("InterventionPlanning block NOT FOUND — paste the current block")