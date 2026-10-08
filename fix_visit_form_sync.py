import pathlib

p = pathlib.Path("src/components/field/FieldVisitForm.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add useEffect to sync projectId/siteId when lists load or modal opens
old_states = """  const [projectId, setProjectId] = useState(defaultProject?.id || projects[0]?.id || '');
  const [siteId, setSiteId] = useState(sites[0]?.id || '');"""

new_states = """  const [projectId, setProjectId] = useState(defaultProject?.id || projects[0]?.id || '');
  const [siteId, setSiteId] = useState(sites[0]?.id || '');

  // Sync project/site selections whenever the modal opens or the lists change
  useEffect(() => {
    if (!isOpen) return;
    const targetProject = defaultProject?.id || projects[0]?.id || '';
    if (!projectId || !projects.some(p => p.id === projectId)) {
      setProjectId(targetProject);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projects.length, defaultProject?.id]);

  useEffect(() => {
    if (!isOpen) return;
    // Prefer sites belonging to the chosen project
    const candidates = sites.filter(s => !projectId || s.project_id === projectId);
    const target = candidates[0]?.id || sites[0]?.id || '';
    if (!siteId || !sites.some(s => s.id === siteId)) {
      setSiteId(target);
    } else if (projectId && !candidates.some(s => s.id === siteId)) {
      setSiteId(target);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, projectId, sites.length]);"""

if old_states in src and "Sync project/site selections" not in src:
    src = src.replace(old_states, new_states)
    changes.append("added useEffect sync for project/site")
else:
    changes.append("state pattern NOT FOUND or already patched")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)