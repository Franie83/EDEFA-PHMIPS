import pathlib

p = pathlib.Path("src/components/projects/ProjectModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add referenceData to props interface
old_iface = """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
}"""
new_iface = """interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Project>) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  referenceData?: any;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("interface: added referenceData")
else:
    changes.append("interface pattern NOT FOUND")

# 2. Destructure referenceData
old_dest = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories
}) => {"""
new_dest = """export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  referenceData
}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured referenceData")
else:
    changes.append("destructure pattern NOT FOUND")

# 3. Funding Source: input -> dropdown
old_fund = """              <input
                type="text"
                value={formData.funding_source}
                onChange={e => setFormData({ ...formData, funding_source: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />"""
new_fund = """              <select
                value={formData.funding_source}
                onChange={e => setFormData({ ...formData, funding_source: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.funding_sources || [formData.funding_source]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>"""
if old_fund in src:
    src = src.replace(old_fund, new_fund)
    changes.append("Funding Source -> dropdown")
else:
    changes.append("Funding Source pattern NOT FOUND")

# 4. Implementing Agency: input -> dropdown — need to find the current block first
# We'll use a looser match — search for value={formData.implementing_agency}
old_agency = """              <input
                type="text"
                value={formData.implementing_agency}
                onChange={e => setFormData({ ...formData, implementing_agency: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300"
              />"""
new_agency = """              <select
                value={formData.implementing_agency}
                onChange={e => setFormData({ ...formData, implementing_agency: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-300 bg-white"
              >
                {(referenceData?.implementing_agencies || [formData.implementing_agency]).map((a: string) => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>"""
if old_agency in src:
    src = src.replace(old_agency, new_agency)
    changes.append("Implementing Agency -> dropdown")
else:
    changes.append("Implementing Agency pattern NOT FOUND (check exact input block)")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)