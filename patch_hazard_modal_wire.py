import pathlib

p = pathlib.Path("src/components/hazards/HazardReportModal.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# ---------- 1. Add referenceData prop to interface ----------
old_iface = """interface HazardReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: any) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  editHazard?: Hazard | null;
}"""

new_iface = """interface HazardReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (formData: any) => Promise<void>;
  statesAndLgas: Record<string, string[]>;
  categories: string[];
  editHazard?: Hazard | null;
  referenceData?: any;
}"""

if old_iface in src:
    src = src.replace(old_iface, new_iface)
    changes.append("interface: added referenceData prop")

# ---------- 2. Destructure referenceData ----------
old_dest = """export const HazardReportModal: React.FC<HazardReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  editHazard
}) => {"""

new_dest = """export const HazardReportModal: React.FC<HazardReportModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  statesAndLgas,
  categories,
  editHazard,
  referenceData
}) => {"""

if old_dest in src:
    src = src.replace(old_dest, new_dest)
    changes.append("destructured referenceData")

# ---------- 3. Replace Severity options ----------
old_sev = """                  <option value="CRITICAL">CRITICAL (Catastrophic risk)</option>
                  <option value="HIGH">HIGH (Severe destruction)</option>
                  <option value="MEDIUM">MEDIUM (Manageable)</option>
                  <option value="LOW">LOW (Early onset)</option>"""

new_sev = """                  {(referenceData?.severities || ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']).map((s: string) => (
                    <option key={s} value={s}>{s}</option>
                  ))}"""

if old_sev in src:
    src = src.replace(old_sev, new_sev)
    changes.append("replaced Severity options with dynamic list")
else:
    changes.append("Severity option pattern NOT FOUND")

# ---------- 4. Replace Urgency options ----------
old_urg = """                  <option value="IMMEDIATE">IMMEDIATE (Within 7 days)</option>
                  <option value="HIGH">HIGH (Within 30 days)</option>
                  <option value="NORMAL">NORMAL (Budget pipeline)</option>
                  <option value="ROUTINE">ROUTINE (Monitoring)</option>"""

new_urg = """                  {(referenceData?.urgencies || ['IMMEDIATE', 'HIGH', 'NORMAL', 'ROUTINE']).map((u: string) => (
                    <option key={u} value={u}>{u}</option>
                  ))}"""

if old_urg in src:
    src = src.replace(old_urg, new_urg)
    changes.append("replaced Urgency options with dynamic list")
else:
    changes.append("Urgency option pattern NOT FOUND")

# ---------- 5. Replace Reporter Category options ----------
old_rep = """                  <option value="FIELD_OFFICER">EPO Field Inspector</option>
                  <option value="LGA_OFFICIAL">LGA Environmental Desk</option>
                  <option value="COMMUNITY_LEADER">Community Leader / Traditional Head</option>
                  <option value="PUBLIC">General Citizen / Public</option>"""

new_rep = """                  {(referenceData?.reporter_types || ['FIELD_OFFICER', 'LGA_OFFICIAL', 'COMMUNITY_LEADER', 'PUBLIC']).map((r: string) => (
                    <option key={r} value={r}>{r.replace(/_/g, ' ')}</option>
                  ))}"""

if old_rep in src:
    src = src.replace(old_rep, new_rep)
    changes.append("replaced Reporter Category options with dynamic list")
else:
    changes.append("Reporter option pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)