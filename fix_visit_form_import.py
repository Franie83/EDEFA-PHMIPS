import pathlib

p = pathlib.Path("src/components/field/FieldVisitForm.tsx")
src = p.read_text(encoding="utf-8")

# Fix 1: Add useEffect to the React import
old_import = "import React, { useState } from 'react';"
new_import = "import React, { useState, useEffect } from 'react';"

if old_import in src:
    src = src.replace(old_import, new_import, 1)
    print("Added useEffect to React import")
else:
    # Maybe the file uses just `import { useState } from 'react';`
    old_import2 = "import { useState } from 'react';"
    new_import2 = "import { useState, useEffect } from 'react';"
    if old_import2 in src:
        src = src.replace(old_import2, new_import2, 1)
        print("Added useEffect (variant import)")
    else:
        print("Import pattern NOT FOUND — file's import looks different")

p.write_text(src, encoding="utf-8")