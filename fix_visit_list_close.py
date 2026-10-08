import pathlib

p = pathlib.Path("src/components/field/FieldVisitList.tsx")
src = p.read_text(encoding="utf-8")

# The exact broken region:
#       </div>
#     </div>                 ← STRAY (closes outer wrapper early)
#                              ← blank line
#       {/* Lightbox for evidence preview */}
#       ...
#       )}
#     </div>                 ← correct outer wrapper close
#   );
# };

# Remove the FIRST "</div>" of the duplicated pair that appears right before the lightbox comment
old = """          </div>
        ))}
      </div>
    </div>

      {/* Lightbox for evidence preview */}"""
new = """          </div>
        ))}
      </div>

      {/* Lightbox for evidence preview */}"""

if old in src:
    src = src.replace(old, new, 1)
    p.write_text(src, encoding="utf-8")
    print("Removed the stray closing </div> before the lightbox")
else:
    print("Pattern not found. Trying looser match...")
    # Loose match: two </div> lines with blank line before the lightbox comment
    import re
    pattern = re.compile(
        r"(</div>\n\s*</div>\n)\s*\n(\s*\{/\* Lightbox for evidence preview \*/)",
        re.MULTILINE
    )
    new_src, n = pattern.subn(r"\1\n\2", src)
    if n:
        p.write_text(new_src, encoding="utf-8")
        print(f"Loose fix applied ({n} match)")
    else:
        print("Still no match — paste the last 30 lines of the file:")
        print("\n".join(src.splitlines()[-30:]))