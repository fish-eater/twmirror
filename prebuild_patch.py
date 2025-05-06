#!/usr/bin/env python3
import os, glob, shutil, re, sys

SRC = "scratch-gui/src"
# 1) Overwrite the default favicon / site icon in your source
ICON_SRC = "custom/site_icon.png"
ICON_DST = os.path.join(SRC, "lib/default-project/dango-cat.svg")
shutil.copyfile(ICON_SRC, ICON_DST)
print(f"→ Overwrote default icon: {ICON_DST}")

# 2) Inject our cursor + green‑secondary CSS into every HTML template
INJECT = """
  <style>
    html, body, * { cursor: url("https://fisheater.peterdance.com/resources/cursor.png"), auto !important; }
    *:hover    { cursor: url("https://fisheater.peterdance.com/resources/cursor_select.png"), auto !important; }
    :root { --looks-secondary: #0f0 !important; }
  </style>
"""
for tpl in glob.glob(os.path.join(SRC, "playground/*.ejs")):
    text = open(tpl, encoding="utf8").read()
    if INJECT not in text:
        # insert right after <head>
        patched = re.sub(r"(<head[^>]*>)", r"\1\n" + INJECT, text, count=1, flags=re.IGNORECASE)
        open(tpl, "w", encoding="utf8").write(patched)
        print(f"→ Patched template: {tpl}")
    else:
        print(f"→ Already patched: {tpl}")
