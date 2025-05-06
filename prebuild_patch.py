#!/usr/bin/env python3
import os
import shutil
import re
from pathlib import Path
from urllib.request import urlretrieve

def print_working_dir():
    print(f"Working directory: {os.getcwd()}")

def print_tree(base_dir, depth=2):
    base = Path(base_dir)
    if not base.exists():
        print(f"  [!] {base_dir} does not exist")
        return
    for p in sorted(base.iterdir()):
        line = f"  {p.relative_to('.')}/"
        print(line)
        if p.is_dir() and depth > 1:
            for sub in sorted(p.iterdir()):
                print(f"    {sub.relative_to('.')}")

def copy_file(src, dst):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    print(f"Copied {src} → {dst}")

def download_file(url, dst):
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} → {dst}")
    urlretrieve(url, dst)
    print(f"Downloaded → {dst}")

def patch_red_js():
    path = Path("scratch-gui/src/lib/themes/accent/red.js")
    if not path.exists():
        print(f"  [!] {path} not found, skipping red.js patch")
        return
    text = path.read_text()
    G      = "#00aa00"
    G_T    = "#00aa0059"
    G_LT   = "#00aa0026"
    G_DARK = "hsla(120, 42%, 51%, 1)"
    text, c1 = re.subn(r"'looks-secondary':\s*'#[0-9A-Fa-f]{6}'",
                       f"'looks-secondary': '{G}'", text)
    text, c2 = re.subn(r"'looks-transparent':\s*'#[0-9A-Fa-f]{8}'",
                       f"'looks-transparent': '{G_T}'", text)
    text, c3 = re.subn(r"'looks-light-transparent':\s*'#[0-9A-Fa-f]{8}'",
                       f"'looks-light-transparent': '{G_LT}'", text)
    text, c4 = re.subn(r"'looks-secondary-dark':\s*'[^']+'",
                       f"'looks-secondary-dark': '{G_DARK}'", text)
    path.write_text(text)
    print(f"Patched red.js (replacements: {c1}, {c2}, {c3}, {c4})")

def patch_ejs_templates():
    templates = [
        "scratch-gui/src/playground/index.ejs",
        "scratch-gui/src/playground/embed.ejs",
        "scratch-gui/src/playground/simple.ejs"
    ]
    injection = (
        '<link rel="icon" href="<%= root %>static/icon.png">\n'
        '    <link rel="stylesheet" href="<%= root %>static/overrides.css">'
    )
    for tpl in templates:
        path = Path(tpl)
        if not path.exists():
            print(f"  [!] {tpl} missing, skipping")
            continue
        text = path.read_text()
        # Insert injection just after the opening <head> tag
        new_text = re.sub(
            r"(<head[^>]*>)",
            r"\1\n    " + injection.replace("\n", "\n    "),
            text, count=1
        )
        path.write_text(new_text)
        print(f"Patched head links into {tpl}")

if __name__ == "__main__":
    print_working_dir()
    print("Directory tree for scratch-gui (depth=2):")
    print_tree("scratch-gui")

    # 1) copy in your overrides.css so webpack will drop it at /static/overrides.css
    copy_file("custom/overrides.css", "scratch-gui/static/overrides.css")

    # 2) copy your site icon into static/
    copy_file("custom/site_icon.png", "scratch-gui/static/icon.png")

    # 3) download custom cursors into static/
    download_file("https://fisheater.peterdance.com/resources/cursor.png",
                  "scratch-gui/static/cursor.png")
    download_file("https://fisheater.peterdance.com/resources/cursor_select.png",
                  "scratch-gui/static/cursor_select.png")

    # 4) copy your new default-project.sb3 into both override- and default-
    copy_file("custom/default-project.sb3",
              "scratch-gui/src/lib/default-project/override-default-project.sb3")
    copy_file("custom/default-project.sb3",
              "scratch-gui/src/lib/default-project/default-project.sb3")

    # 5) tweak the red.js palette to green
    patch_red_js()

    # 6) inject favicon + overrides.css link into every template
    patch_ejs_templates()

    print("✅ prebuild_patch complete")
