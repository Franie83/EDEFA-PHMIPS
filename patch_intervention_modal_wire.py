import pathlib

p = pathlib.Path("src/components/interventions/InterventionModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# 1. Add referenceData to props interface
old_iface = """interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  hazard?: Hazard | null;
  onSuccess?: () => void;
  currentUser?: { role?: string; name?: string } | null;
}"""
new_iface = """interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  hazard?: Hazard | null;
  onSuccess?: () => void;
  currentUser?: { role?: string; name?: string } | null;
  referenceData?: any;
}"""
if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("interface: added referenceData")
else:
    changes.append("interface pattern NOT FOUND")

# 2. Destructure
old_dest = """export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  hazard,
  onSuccess,
  currentUser
}) => {"""
new_dest = """export const InterventionModal: React.FC<InterventionModalProps> = ({
  isOpen,
  onClose,
  hazard,
  onSuccess,
  currentUser,
  referenceData
}) => {"""
if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured referenceData")
else:
    changes.append("destructure pattern NOT FOUND")

# 3. Priority options
old_pri = """                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>"""
new_pri = """                {(referenceData?.priorities || ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']).map((pr: string) => (
                  <option key={pr} value={pr}>{pr}</option>
                ))}"""
if old_pri in src:
    src = src.replace(old_pri, new_pri)
    changes.append("replaced Priority options")
else:
    changes.append("Priority options NOT FOUND")

# 4. Proposed Funding input -> dropdown
old_fund = """              <input
                value={form.proposed_funding}
                onChange={set('proposed_funding')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />"""
new_fund = """              <select
                value={form.proposed_funding}
                onChange={set('proposed_funding')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-white"
              >
                {(referenceData?.funding_sources || [form.proposed_funding]).map((fs: string) => (
                  <option key={fs} value={fs}>{fs}</option>
                ))}
              </select>"""
if old_fund in src:
    src = src.replace(old_fund, new_fund)
    changes.append("Proposed Funding -> dropdown")
else:
    changes.append("Proposed Funding pattern NOT FOUND")

# 5. Responsible Department input -> dropdown
old_dept = """              <input
                value={form.responsible_department}
                onChange={set('responsible_department')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              />"""
new_dept = """              <select
                value={form.responsible_department}
                onChange={set('responsible_department')}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600 bg-white"
              >
                {(referenceData?.departments || [form.responsible_department]).map((d: string) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>"""
if old_dept in src:
    src = src.replace(old_dept, new_dept)
    changes.append("Responsible Department -> dropdown")
else:
    changes.append("Responsible Department pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)