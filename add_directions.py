"""
add_directions.py — adds a "Get Directions" link across the app.

1. Creates src/components/common/DirectionsLink.tsx (new reusable component).
2. Injects the DirectionsLink into:
   - SiteList.tsx (site cards)
   - HazardDetailModal.tsx (Geographic Placement block)
   - ProjectDetailModal.tsx (Location & Coordinates block)
   - FieldVisitForm.tsx (next to Acquire GPS button)

Each file is backed up to *.bak_<timestamp> before being modified.
Run from the eco/ folder:  python add_directions.py
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(r".\src\components")
COMMON = ROOT / "common"
COMMON.mkdir(parents=True, exist_ok=True)

ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")

def backup(p: Path) -> Path:
    b = p.with_suffix(p.suffix + f".bak_{ts}")
    shutil.copy2(p, b)
    print(f"  backup -> {b.name}")
    return b

def write_if_new(p: Path, content: str):
    if p.exists():
        print(f"  {p.name} already exists — leaving as-is")
        return
    p.write_text(content, encoding="utf-8")
    print(f"  created {p}")

# ============================================================
# 1. Create DirectionsLink.tsx
# ============================================================
DIRECTIONS_COMPONENT = '''import React from 'react';
import { Navigation } from 'lucide-react';

interface DirectionsLinkProps {
  lat: number | null | undefined;
  lng: number | null | undefined;
  label?: string;
  className?: string;
  /** If provided, appended to the label after a " — " separator */
  destination?: string;
}

/**
 * Renders a link that opens Google Maps turn-by-turn directions
 * to the given coordinates. Works on desktop (browser) and on mobile
 * (opens the Google Maps app or offers the choice of maps apps).
 * Returns null when coordinates are missing or invalid.
 */
export const DirectionsLink: React.FC<DirectionsLinkProps> = ({
  lat,
  lng,
  label = 'Directions',
  className = 'text-blue-700 hover:text-blue-950 font-semibold inline-flex items-center text-xs',
  destination,
}) => {
  const latN = Number(lat);
  const lngN = Number(lng);
  if (!isFinite(latN) || !isFinite(lngN)) return null;
  if (latN < -90 || latN > 90) return null;
  if (lngN < -180 || lngN > 180) return null;

  const url = `https://www.google.com/maps/dir/?api=1&destination=${latN},${lngN}`;
  const text = destination ? `${label} — ${destination}` : label;

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={className}
      title="Open turn-by-turn directions in your maps app"
    >
      <Navigation className="w-3.5 h-3.5 mr-1" />
      {text}
    </a>
  );
};
'''

print("Step 1 — create DirectionsLink.tsx")
write_if_new(COMMON / "DirectionsLink.tsx", DIRECTIONS_COMPONENT)

# ============================================================
# 2. Patch SiteList.tsx — add Directions link next to "View On Map"
# ============================================================
print("\nStep 2 — patch SiteList.tsx")
site_list = ROOT / "sites" / "SiteList.tsx"
if site_list.exists():
    backup(site_list)
    src = site_list.read_text(encoding="utf-8")

    # Add import
    if "DirectionsLink" not in src:
        src = re.sub(
            r"(import\s+\{[^}]*\}\s+from\s+['\"]lucide-react['\"];)",
            r"\1\nimport { DirectionsLink } from '../common/DirectionsLink.tsx';",
            src,
            count=1,
        )

    # Replace the footer block that contains "View On Map"
    old_footer = re.compile(
        r"""<button\s+onClick=\{\(\)\s*=>\s*onNavigateToMap\(site\.latitude,\s*site\.longitude\)\}.*?</button>""",
        re.DOTALL,
    )
    m = old_footer.search(src)
    if m:
        old_btn = m.group(0)
        new_btn = (
            '<div className="flex items-center gap-2">\n'
            '                ' + old_btn + '\n'
            '                <DirectionsLink\n'
            '                  lat={site.latitude}\n'
            '                  lng={site.longitude}\n'
            '                  label="Directions"\n'
            '                />\n'
            '              </div>'
        )
        src = src[:m.start()] + new_btn + src[m.end():]
        print("  added DirectionsLink next to View On Map")
    else:
        print("  could not find View On Map button — skipped")

    site_list.write_text(src, encoding="utf-8")
else:
    print("  SiteList.tsx not found — skipped")

# ============================================================
# 3. Patch HazardDetailModal.tsx — add Directions in Geographic Placement
# ============================================================
print("\nStep 3 — patch HazardDetailModal.tsx")
haz_modal = ROOT / "hazards" / "HazardDetailModal.tsx"
if haz_modal.exists():
    backup(haz_modal)
    src = haz_modal.read_text(encoding="utf-8")

    if "DirectionsLink" not in src:
        src = re.sub(
            r"(import\s+\{[^}]*\}\s+from\s+['\"]lucide-react['\"];)",
            r"\1\nimport { DirectionsLink } from '../common/DirectionsLink.tsx';",
            src,
            count=1,
        )

    # After the "Locate on GIS Map" button, insert DirectionsLink
    anchor = re.compile(
        r'(<button[\s\S]*?Locate on GIS Map[\s\S]*?</button>)',
        re.DOTALL,
    )
    m = anchor.search(src)
    if m:
        insert_after = m.group(1)
        insertion = (
            insert_after
            + '\n              <div className="mt-2 flex justify-center">\n'
            + '                <DirectionsLink\n'
            + '                  lat={h.latitude}\n'
            + '                  lng={h.longitude}\n'
            + '                  label="Get Directions"\n'
            + '                />\n'
            + '              </div>'
        )
        src = src[:m.start()] + insertion + src[m.end():]
        print("  added DirectionsLink below Locate on GIS Map")
    else:
        print("  could not find Locate on GIS Map button — skipped")

    haz_modal.write_text(src, encoding="utf-8")
else:
    print("  HazardDetailModal.tsx not found — skipped")

# ============================================================
# 4. Patch ProjectDetailModal.tsx — add Directions in Location & Coordinates
# ============================================================
print("\nStep 4 — patch ProjectDetailModal.tsx")
proj_modal = ROOT / "projects" / "ProjectDetailModal.tsx"
if proj_modal.exists():
    backup(proj_modal)
    src = proj_modal.read_text(encoding="utf-8")

    if "DirectionsLink" not in src:
        src = re.sub(
            r"(import\s+\{[^}]*\}\s+from\s+['\"]lucide-react['\"];)",
            r"\1\nimport { DirectionsLink } from '../common/DirectionsLink.tsx';",
            src,
            count=1,
        )

    # After "View Project on GIS Map"
    anchor = re.compile(
        r'(<button[\s\S]*?View Project on GIS Map[\s\S]*?</button>)',
        re.DOTALL,
    )
    m = anchor.search(src)
    if m:
        insertion = (
            m.group(1)
            + '\n              <div className="mt-2 flex justify-center">\n'
            + '                <DirectionsLink\n'
            + '                  lat={project.latitude}\n'
            + '                  lng={project.longitude}\n'
            + '                  label="Get Directions"\n'
            + '                />\n'
            + '              </div>'
        )
        src = src[:m.start()] + insertion + src[m.end():]
        print("  added DirectionsLink below View Project on GIS Map")
    else:
        print("  could not find View Project on GIS Map button — skipped")

    proj_modal.write_text(src, encoding="utf-8")
else:
    print("  ProjectDetailModal.tsx not found — skipped")

# ============================================================
# 5. Patch FieldVisitForm.tsx — add Directions next to Acquire GPS
# ============================================================
print("\nStep 5 — patch FieldVisitForm.tsx")
visit_form = ROOT / "field" / "FieldVisitForm.tsx"
if visit_form.exists():
    backup(visit_form)
    src = visit_form.read_text(encoding="utf-8")

    if "DirectionsLink" not in src:
        src = re.sub(
            r"(import\s+\{[^}]*\}\s+from\s+['\"]lucide-react['\"];)",
            r"\1\nimport { DirectionsLink } from '../common/DirectionsLink.tsx';",
            src,
            count=1,
        )

    # After "Acquire GPS" button, insert a DirectionsLink for the current coords
    anchor = re.compile(
        r'(<button[\s\S]*?Acquire GPS[\s\S]*?</button>)',
        re.DOTALL,
    )
    m = anchor.search(src)
    if m:
        insertion = (
            m.group(1)
            + '\n              <DirectionsLink\n'
            + '                lat={gpsLatitude}\n'
            + '                lng={gpsLongitude}\n'
            + '                label="Directions to these coordinates"\n'
            + '                className="mt-2 text-blue-700 hover:text-blue-950 text-[11px] font-semibold inline-flex items-center"\n'
            + '              />'
        )
        src = src[:m.start()] + insertion + src[m.end():]
        print("  added DirectionsLink below Acquire GPS button")
    else:
        print("  could not find Acquire GPS button — skipped")

    visit_form.write_text(src, encoding="utf-8")
else:
    print("  FieldVisitForm.tsx not found — skipped")

print()
print("Done. Next steps:")
print("  1. Save all modified files (they're already written).")
print("  2. Hard-refresh the browser: Ctrl+Shift+R twice.")
print("  3. Test the new Directions links.")