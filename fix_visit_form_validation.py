import pathlib

p = pathlib.Path("src/components/field/FieldVisitForm.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# Find the submit handler and add validation at the top
old_submit = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);"""

new_submit = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) {
      alert('Please select a project before saving the visit.');
      return;
    }
    if (!siteId) {
      alert('Please select a site before saving the visit. If no sites exist yet, create one from the Sites tab.');
      return;
    }
    setIsSubmitting(true);"""

if old_submit in src:
    src = src.replace(old_submit, new_submit)
    changes.append("added validation for project/site")
else:
    changes.append("submit handler pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)