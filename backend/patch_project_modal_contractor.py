"""
Replace the free-text Contractor Name input with a dropdown that fetches
active contractors from /api/contractors.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "projects" / "ProjectModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "contractorList" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# -------- 1. Add Contractor type + import --------
# Actually we just need the shape; define inline
if "Contractor" not in text.split("interface ProjectModalProps")[0]:
    # Add import
    old_import = "import { api } from '../../services/api.ts';"
    new_import = "import { api } from '../../services/api.ts';\nimport { Contractor } from '../../types/index.ts';"
    if old_import in text:
        text = text.replace(old_import, new_import, 1)

# -------- 2. Add contractorList state + fetch --------
# Insert after approvedInterventions state
anchor = "const [interventionsLoading, setInterventionsLoading] = useState(false);"
new_state = anchor + """

  const [contractorList, setContractorList] = useState<Contractor[]>([]);
  const [contractorsLoading, setContractorsLoading] = useState(false);"""

if anchor in text:
    text = text.replace(anchor, new_state, 1)
    print("  Added contractorList state")

# -------- 3. Add useEffect to fetch contractors --------
anchor2 = """  // Fetch Executive-Approved interventions when the modal opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setInterventionsLoading(true);"""

new_effect = """  // Fetch active contractors when the modal opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setContractorsLoading(true);
    (async () => {
      try {
        const list = await api.getContractors();
        if (!cancelled) setContractorList(list || []);
      } catch (err) {
        console.error('Failed to load contractors:', err);
      } finally {
        if (!cancelled) setContractorsLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [isOpen]);

  // Fetch Executive-Approved interventions when the modal opens
  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setInterventionsLoading(true);"""

if anchor2 in text:
    text = text.replace(anchor2, new_effect, 1)
    print("  Added contractor fetch useEffect")

# -------- 4. Replace the Contractor Name input with a select --------
# Find the input by matching placeholder text
old_input_pattern = r'<input[^>]*placeholder="e\.g\., Julius Berger[^"]*"[^>]*/>'
match = re.search(old_input_pattern, text)

if not match:
    print("  WARNING: contractor input not found — will try alt pattern")
    # Try any input right after "Contractor Name" label
    idx = text.find("Contractor Name")
    if idx == -1:
        raise SystemExit("Could not find contractor field")
    # Find the next <input ... /> after that
    m2 = re.search(r'<input[\s\S]*?/>', text[idx:idx + 500])
    if not m2:
        raise SystemExit("Could not find contractor input by anchor")
    old_input = text[idx + m2.start():idx + m2.end()]
    replacement = """<select
                value={formData.contractor}
                onChange={e => setFormData({ ...formData, contractor: e.target.value })}
                disabled={contractorsLoading}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              >
                <option value="">
                  {contractorsLoading ? 'Loading contractors…' : '— Select a registered contractor —'}
                </option>
                {contractorList.map(c => (
                  <option key={c.id} value={c.name}>
                    {c.name} ({c.registration_no || c.id})
                  </option>
                ))}
              </select>"""
    text = text[:idx + m2.start()] + replacement + text[idx + m2.end():]
    print("  Replaced contractor input with select (via anchor)")
else:
    old_input = match.group(0)
    replacement = """<select
                value={formData.contractor}
                onChange={e => setFormData({ ...formData, contractor: e.target.value })}
                disabled={contractorsLoading}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 outline-none focus:border-emerald-600"
              >
                <option value="">
                  {contractorsLoading ? 'Loading contractors…' : '— Select a registered contractor —'}
                </option>
                {contractorList.map(c => (
                  <option key={c.id} value={c.name}>
                    {c.name} ({c.registration_no || c.id})
                  </option>
                ))}
              </select>"""
    text = text.replace(old_input, replacement, 1)
    print("  Replaced contractor input with select")

TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")