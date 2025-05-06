#!/usr/bin/env python3
import os, glob, shutil, re, sys

BUILD = os.path.join("scratch‑gui","build")
if not os.path.isdir(BUILD):
    print(f"ERROR: build dir not found at {BUILD}", file=sys.stderr)
    sys.exit(1)

# 1) Overwrite favicon.ico
SRC_ICON = os.path.join("custom","site_icon.png")
DST_ICON = os.path.join(BUILD,"favicon.ico")
if os.path.exists(SRC_ICON):
    print(f"→ Copying icon: {SRC_ICON} → {DST_ICON}")
    shutil.copy(SRC_ICON, DST_ICON)
else:
    print(f"WARNING: custom icon not found at {SRC_ICON}")

# 2) CSS injection snippet
INJECT = """
<style>
html, body, * {
  cursor: url("https://fisheater.peterdance.com/resources/cursor.png"), auto !important;
}
*:hover {
  cursor: url("https://fisheater.peterdance.com/resources/cursor_select.png"), auto !important;
}
:root { --looks-secondary: #0f0 !important; }
</style>
"""

# 3) Patch every top‐level HTML
for html in glob.glob(os.path.join(BUILD,"*.html")):
    print(f"→ Patching {html}")
    text = open(html, encoding="utf8").read()
    # only inject once
    if INJECT.strip() not in text:
        text = re.sub(r"(?i)<head>", "<head>" + INJECT, text, count=1)
        open(html, "w", encoding="utf8").write(text)
    else:
        print("   (already patched)")

print("Done.")
