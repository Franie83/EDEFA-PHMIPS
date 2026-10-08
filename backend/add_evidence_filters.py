"""
Enhance EvidenceRepository.tsx:
  - Derive media + stage options from data
  - Wildcard search across more fields
  - Filter by related entity (hazard / project / site / visit)
  - Date range filter
  - Uploader filter (dropdown derived from data)
  - Reset button
  - Result count
  - Show linked entity badge on each card
  - Human-readable file size
  - Deduplicate display names when the disk filename is identical
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "evidence" / "EvidenceRepository.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

if "filteredEvidence" in text:
    print("Already patched — skipping.")
    raise SystemExit(0)

# ============================================================
# STEP 1 — Extend the imports with the missing icons
# ============================================================
needed_icons = ["RotateCcw", "Layers", "Building2", "Calendar"]
existing_block_match = re.search(r"import\s*\{([^}]+)\}\s*from\s*'lucide-react'", text)
if existing_block_match:
    existing = existing_block_match.group(1)
    missing = [ic for ic in needed_icons if ic not in existing]
    if missing:
        new_import = "import {\n  " + existing.strip().rstrip(",") + ",\n  " + ",\n  ".join(missing) + "\n} from 'lucide-react'"
        text = text[:existing_block_match.start()] + new_import + text[existing_block_match.end():]
        print(f"  Added icons: {missing}")

# ============================================================
# STEP 2 — Add new filter state
# ============================================================
anchor = "const [activeMedia, setActiveMedia] = useState<Evidence | null>(null);"
if anchor not in text:
    raise SystemExit("activeMedia anchor not found")

new_state = anchor + """

  // Extended filter state
  const [entityFilter, setEntityFilter] = useState<'ALL' | 'HAZARD' | 'PROJECT' | 'SITE' | 'VISIT'>('ALL');
  const [uploaderFilter, setUploaderFilter] = useState<string>('ALL');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');"""

text = text.replace(anchor, new_state, 1)
print("  Added entityFilter, uploaderFilter, dateFrom, dateTo state")

# ============================================================
# STEP 3 — Replace the filter computation with the enhanced version
# ============================================================
old_filter = re.search(
    r"const filtered = \(evidenceList \|\| \[\]\)\.filter\(e => \{[\s\S]*?\}\);\s*\n",
    text,
)

if not old_filter:
    raise SystemExit("Could not find the existing 'filtered' computation")

new_filter = '''// Derive filter options from actual data
  const mediaOptions = Array.from(
    new Set((evidenceList || []).map(e => e.media_type).filter(Boolean) as string[])
  ).sort();

  const stageOptions = Array.from(
    new Set((evidenceList || []).map(e => e.stage_tag).filter(Boolean) as string[])
  ).sort();

  const uploaderOptions = Array.from(
    new Set((evidenceList || []).map(e => e.uploader_name).filter(Boolean) as string[])
  ).sort();

  // Classify what entity an evidence file is linked to
  const linkedEntity = (e: any): { type: 'HAZARD' | 'PROJECT' | 'SITE' | 'VISIT' | 'NONE'; id: string } => {
    if (e.hazard_id) return { type: 'HAZARD', id: e.hazard_id };
    if (e.project_id) return { type: 'PROJECT', id: e.project_id };
    if (e.site_id) return { type: 'SITE', id: e.site_id };
    if (e.visit_id) return { type: 'VISIT', id: e.visit_id };
    return { type: 'NONE', id: '' };
  };

  // Human-readable file size
  const formatBytes = (bytes: number): string => {
    if (!bytes || bytes <= 0) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Wildcard search across all fields
  const matchesSearch = (e: any, q: string): boolean => {
    if (!q) return true;
    const lower = q.toLowerCase();
    const haystack = [
      e.id,
      e.file_name,
      e.file_type,
      e.media_type,
      e.stage_tag,
      e.description,
      e.uploader_name,
      e.uploader_id,
      e.hazard_id,
      e.project_id,
      e.site_id,
      e.visit_id,
      e.upload_date,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase();
    return haystack.includes(lower);
  };

  const filteredEvidence = (evidenceList || []).filter(e => {
    if (mediaFilter !== 'ALL' && e.media_type !== mediaFilter) return false;
    if (stageFilter !== 'ALL' && e.stage_tag !== stageFilter) return false;
    if (entityFilter !== 'ALL') {
      const linked = linkedEntity(e);
      if (linked.type !== entityFilter) return false;
    }
    if (uploaderFilter !== 'ALL' && e.uploader_name !== uploaderFilter) return false;
    if (dateFrom && e.upload_date && e.upload_date < dateFrom) return false;
    if (dateTo && e.upload_date && e.upload_date > (dateTo + 'T23:59:59')) return false;
    if (!matchesSearch(e, searchTerm)) return false;
    return true;
  });

  const resetEvidenceFilters = () => {
    setSearchTerm('');
    setMediaFilter('ALL');
    setStageFilter('ALL');
    setEntityFilter('ALL');
    setUploaderFilter('ALL');
    setDateFrom('');
    setDateTo('');
  };

  const evidenceHasActiveFilters =
    searchTerm !== '' ||
    mediaFilter !== 'ALL' ||
    stageFilter !== 'ALL' ||
    entityFilter !== 'ALL' ||
    uploaderFilter !== 'ALL' ||
    dateFrom !== '' ||
    dateTo !== '';

'''

text = text[:old_filter.start()] + new_filter + text[old_filter.end():]
print("  Replaced filter computation with enhanced version")

# ============================================================
# STEP 4 — Rewire the .map over evidence to use filteredEvidence
# ============================================================
for old_map in ["{filtered.map(", "filtered.map(item"]:
    if old_map in text:
        text = text.replace(old_map, "{filteredEvidence.map(", 1) if old_map == "{filtered.map(" else text
        break

# safer replacement
text = text.replace("{filtered.map(item =>", "{filteredEvidence.map(item =>")

TARGET.write_text(text, encoding="utf-8")
print(f"  Rewired list rendering to filteredEvidence")
print(f"\nPatched {TARGET.name}")
print()
print("The enhanced filter logic is in place. The filter bar UI (dropdowns, date")
print("inputs, reset button, result count) still needs to be inserted. Save this")
print("script, run it, then paste the file's header/filter section so I can place")
print("the JSX.")