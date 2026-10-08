import pathlib

p = pathlib.Path("src/components/projects/ProjectModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add referenceData AFTER prefillInterventionId
old_iface = """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  prefillInterventionId?: string;
}"""
new_iface = """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  prefillInterventionId?: string;
  referenceData?: any;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("interface: added referenceData")
else:
    changes.append("interface pattern NOT FOUND")

# 2. Destructure — need to see actual destructure block
old_dest = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  prefillInterventionId
}) => {"""
new_dest = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  prefillInterventionId,
  referenceData
}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured referenceData")
else:
    # Try without prefillInterventionId
    old_dest2 = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories
}) => {"""
    new_dest2 = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  referenceData
}) => {"""
    if old_dest2 in src:
        src = src.replace(old_dest2, new_dest2)
        changes.append("destructured referenceData (fallback)")
    else:
        changes.append("destructure pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)