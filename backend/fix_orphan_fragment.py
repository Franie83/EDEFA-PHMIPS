"""
Remove the orphaned fragment left behind by the earlier migration.

The three lines:
            <X className="w-5 h-5" />
          </button>
        </div>

...appear right after the closing </div></div> of the header, but they belong
to a deleted media modal. They have no opening tags, so they break JSX parsing.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "src" / "components" / "hazards" / "HazardDetailModal.tsx"

if not TARGET.exists():
    raise SystemExit(f"Not found: {TARGET}")

text = TARGET.read_text(encoding="utf-8")

# The orphaned fragment (with its exact surrounding context)
BROKEN = """          </div>
        </div>
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}"""

FIXED = """          </div>
        </div>

        {/* Content Body */}"""

if FIXED in text:
    print("Already fixed — skipping.")
    raise SystemExit(0)

if BROKEN not in text:
    raise SystemExit(
        "Orphan fragment not found in expected form. "
        "Paste the lines around line 105-116 to adapt the fix."
    )

text = text.replace(BROKEN, FIXED, 1)
TARGET.write_text(text, encoding="utf-8")
print(f"Patched {TARGET.name}")
print("  - Removed orphaned <X /> + </button> + </div> fragment")
print("  - Header now closes cleanly into the Content Body")