import pathlib

p = pathlib.Path("src/components/field-ops/FieldOperations.tsx")
src = p.read_text(encoding="utf-8")
changes = []

old = """        {tab === 'inspections' && (
          <FieldVisitList
            visits={visits}
            projects={projects}
            onOpenLogModal={onOpenLogModal}
          />
        )}"""
new = """        {tab === 'inspections' && (
          <FieldVisitList
            visits={visits}
            projects={projects}
            onOpenLogModal={onOpenLogModal}
            evidenceList={evidenceList}
          />
        )}"""
if old in src:
    src = src.replace(old, new)
    changes.append("passed evidenceList to FieldVisitList")
else:
    changes.append("FieldVisitList block pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)