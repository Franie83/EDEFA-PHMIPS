import pathlib

# ============================================================
# PATCH 1: ProjectModal.tsx — accept prefillInterventionId prop
# ============================================================
pm = pathlib.Path("src/components/projects/ProjectModal.tsx")
src = pm.read_text(encoding="utf-8")
changes = []

# 1. Add prop to interface
if "prefillInterventionId" not in src:
    src = src.replace(
        """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
}""",
        """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  prefillInterventionId?: string;
}"""
    )
    changes.append("ProjectModal: added prefillInterventionId prop to interface")

    # 2. Destructure the new prop
    src = src.replace(
        """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories
}) => {""",
        """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  prefillInterventionId
}) => {"""
    )
    changes.append("ProjectModal: destructured prefillInterventionId")

    # 3. Add useEffect that pre-fills once interventions are loaded
    marker = """  // Auto-fill project fields when an intervention is selected
  const handleInterventionSelect = (interventionId: string) => {"""
    new_block = """  // Prefill from an externally supplied intervention (e.g. from Intervention Planning "Create Project" button)
  useEffect(() => {
    if (!isOpen) return;
    if (!prefillInterventionId) return;
    if (approvedInterventions.length === 0) return;
    const iv = approvedInterventions.find(i => i.id === prefillInterventionId);
    if (!iv) return;
    if (formData.intervention_id === prefillInterventionId) return;
    setFormData(prev => ({
      ...prev,
      intervention_id: prefillInterventionId,
      title: prev.title || `Project for ${iv.title}`,
      description: prev.description || iv.technical_description || iv.estimated_scope || '',
      approved_amount_ngn: iv.estimated_cost_ngn || prev.approved_amount_ngn,
      contract_amount_ngn: iv.estimated_cost_ngn
        ? Math.round(iv.estimated_cost_ngn * 0.95)
        : prev.contract_amount_ngn,
    }));
  }, [isOpen, prefillInterventionId, approvedInterventions]);

  // Auto-fill project fields when an intervention is selected
  const handleInterventionSelect = (interventionId: string) => {"""
    if marker in src:
        src = src.replace(marker, new_block)
        changes.append("ProjectModal: added prefill useEffect")

    pm.write_text(src, encoding="utf-8")

# ============================================================
# PATCH 2: InterventionPlanning.tsx — add "Create Project" button + modal
# ============================================================
ip = pathlib.Path("src/components/interventions/InterventionPlanning.tsx")
isrc = ip.read_text(encoding="utf-8")
ichanges = []

# 1. Import ProjectModal
if "ProjectModal" not in isrc:
    isrc = isrc.replace(
        "import { InterventionModal } from './InterventionModal.tsx';",
        "import { InterventionModal } from './InterventionModal.tsx';\n"
        "import { ProjectModal } from '../projects/ProjectModal.tsx';"
    )
    ichanges.append("InterventionPlanning: imported ProjectModal")

# 2. Import FolderGit2 icon
if "FolderGit2" not in isrc:
    isrc = isrc.replace(
        "  Search,\n  X,\n  AlertCircle",
        "  Search,\n  X,\n  AlertCircle,\n  FolderGit2"
    )
    ichanges.append("InterventionPlanning: imported FolderGit2 icon")

# 3. Add state for project modal
if "isProjectModalOpen" not in isrc:
    isrc = isrc.replace(
        "  const [pickerSelectedHazard, setPickerSelectedHazard] = useState<Hazard | null>(null);",
        "  const [pickerSelectedHazard, setPickerSelectedHazard] = useState<Hazard | null>(null);\n"
        "  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);\n"
        "  const [projectSourceIntervention, setProjectSourceIntervention] = useState<any | null>(null);"
    )
    ichanges.append("InterventionPlanning: added project modal state")

# 4. Add handler for creating project
handler_code = """
  const handleCreateProjectFromIntervention = async (data: any) => {
    await api.createProject(data);
    await onRefresh?.();
    setIsProjectModalOpen(false);
    setProjectSourceIntervention(null);
    alert('Project created — pending Executive approval.\\n\\nOpen the Projects Register to review or approve.');
  };
"""
if "handleCreateProjectFromIntervention" not in isrc:
    marker = "  const queueOf = (i: any): 'director' | 'executive' | 'approved' | 'other' => {"
    isrc = isrc.replace(marker, handler_code + "\n" + marker)
    ichanges.append("InterventionPlanning: added handleCreateProjectFromIntervention")

# 5. Add "Create Project" button in the fully-approved card footer
old_footer = """                  {isFullyApproved && (
                    <span className="text-[11px] font-semibold text-emerald-700">
                      Ready for project registration
                    </span>
                  )}"""
new_footer = """                  {isFullyApproved && (
                    <button
                      onClick={() => {
                        setProjectSourceIntervention(item);
                        setIsProjectModalOpen(true);
                      }}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold bg-blue-700 hover:bg-blue-800 text-white inline-flex items-center gap-1.5"
                    >
                      <FolderGit2 className="w-3.5 h-3.5" />
                      Create Project
                    </button>
                  )}"""
if old_footer in isrc:
    isrc = isrc.replace(old_footer, new_footer)
    ichanges.append("InterventionPlanning: added Create Project button")

# 6. Render ProjectModal at the end
old_render = """      {/* Step 2: intervention form, prefilled with the picked hazard */}
      <InterventionModal"""
new_render = """      {/* Create Project from an Executive-Approved intervention */}
      <ProjectModal
        isOpen={isProjectModalOpen}
        onClose={() => {
          setIsProjectModalOpen(false);
          setProjectSourceIntervention(null);
        }}
        onSubmit={handleCreateProjectFromIntervention}
        statesAndLgas={{}}
        categories={[]}
        prefillInterventionId={projectSourceIntervention?.id}
      />

      {/* Step 2: intervention form, prefilled with the picked hazard */}
      <InterventionModal"""
if "prefillInterventionId={projectSourceIntervention?.id}" not in isrc:
    isrc = isrc.replace(old_render, new_render)
    ichanges.append("InterventionPlanning: rendered ProjectModal")

ip.write_text(isrc, encoding="utf-8")

# ============================================================
print("\nProjectModal.tsx changes:")
for c in changes:
    print(" -", c)
print("\nInterventionPlanning.tsx changes:")
for c in ichanges:
    print(" -", c)

# Syntax check on both files by counting braces as a sanity check
for label, path in [("ProjectModal.tsx", pm), ("InterventionPlanning.tsx", ip)]:
    content = path.read_text(encoding="utf-8")
    opens = content.count("{")
    closes = content.count("}")
    status = "OK" if opens == closes else f"MISMATCH ({opens} {{ vs {closes} }})"
    print(f"\n{label} brace balance: {status}")