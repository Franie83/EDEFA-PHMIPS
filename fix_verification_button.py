import pathlib

p = pathlib.Path("src/components/verification/VerificationWorkspace.tsx")
src = p.read_text(encoding="utf-8")
changes = []

# Verification submit button — actual current markup (lines 390-397)
old_btn = """                <button
                  type="submit"
                  disabled={isVerifying}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors"
                >
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  {isVerifying ? 'Saving...' : 'Submit Verification & Proceed to Assessment'}
                </button>"""

new_btn = """                <button
                  type="submit"
                  disabled={isVerifying || stage !== 'VERIFICATION'}
                  className="px-5 py-2 rounded-lg text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white inline-flex items-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title={stage !== 'VERIFICATION' ? 'Already verified — see status banner' : ''}
                >
                  <CheckSquare className="w-4 h-4 mr-1.5" />
                  {isVerifying
                    ? 'Saving...'
                    : stage === 'VERIFICATION'
                      ? 'Submit Verification & Proceed to Assessment'
                      : '✓ Already Verified'}
                </button>"""

if old_btn in src:
    src = src.replace(old_btn, new_btn)
    changes.append("disabled Verification submit when step already done")
else:
    changes.append("Verification button pattern NOT FOUND")

p.write_text(src, encoding="utf-8")
print("Changes:")
for c in changes:
    print(" -", c)