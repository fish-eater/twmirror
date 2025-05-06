#!/usr/bin/env python3
import os
import shutil
import re
import argparse
from pathlib import Path
from urllib.request import urlretrieve

def print_working_dir():
    print("Working directory:", os.getcwd())

def print_tree(base_dir, depth=1):
    base = Path(base_dir)
    if not base.exists():
        print(f"  [!] {base_dir} not found")
        return
    for p in sorted(base.iterdir()):
        print(f"  {p.relative_to('.')}/")
        if p.is_dir() and depth > 1:
            for sub in sorted(p.iterdir()):
                print(f"    {sub.relative_to('.')}")

def copy_file(src, dst):
    dstp = Path(dst)
    dstp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dstp)
    print(f"Copied {src} → {dstp}")

def download_file(url, dst):
    dstp = Path(dst)
    dstp.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} → {dstp}")
    urlretrieve(url, dstp)
    print(f"Downloaded → {dstp}")

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
    print(f"Patched red.js (replaced {c1},{c2},{c3},{c4} occurrences)")

def inject_overrides_css():
    """After build: inject an external overrides.css link into every HTML file
    under scratch-gui/build."""
    #points to github raw file
    OVERRIDE_CSS_URL = (
        "https://corsproxy.io/?url="
        "https://raw.githubusercontent.com/fish-eater/twmirror/"
        "main/custom/overrides.css"
    )

    build_dir = Path("scratch-gui/build")
    for html_file in build_dir.glob("*.html"):
        content = html_file.read_text(encoding="utf-8")
        # skip if already injected
        if OVERRIDE_CSS_URL in content:
            continue
        # insert just before </head>
        updated = content.replace(
            "</head>",
            f'  <link rel="stylesheet" href="{OVERRIDE_CSS_URL}">\n</head>'
        )
        html_file.write_text(updated, encoding="utf-8")
        print(f"Injected overrides.css link into {html_file.relative_to(build_dir)}")

def main(inject_only=False):
    if not inject_only:
        print_working_dir()
        print("Directory tree for scratch-gui (depth=1):")
        print_tree("scratch-gui", depth=1)

        # 1) site icon
        copy_file("custom/site_icon.png",
                  "scratch-gui/src/lib/gui/assets/icon.png")

        # 2) cursors
        download_file("https://fisheater.peterdance.com/resources/cursor.png",
                      "scratch-gui/src/lib/gui/assets/cursor.png")
        download_file("https://fisheater.peterdance.com/resources/cursor_select.png",
                      "scratch-gui/src/lib/gui/assets/cursor_select.png")

        # 3) default‑project .sb3 overrides
        copy_file("custom/default-project.sb3",
                  "scratch-gui/src/lib/default-project/default-project.sb3")
        copy_file("custom/default-project.sb3",
                  "scratch-gui/src/lib/default-project/override-default-project.sb3")

        # 4) greenify red.js
        patch_red_js()

        print("\n✅ Pre‑build patch completed — now run your build step\n")

    # after build, inject into each HTML
    inject_overrides_css()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inject", action="store_true",
                        help="Only do the post‑build HTML injection")
    args = parser.parse_args()
    main(inject_only=args.inject)
