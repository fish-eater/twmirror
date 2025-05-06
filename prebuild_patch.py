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
        print(f"  {p.relative_to('.')}/")
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
    # green palette
    G      = "#00aa00"
    G_T    = "#00aa0059"
    G_LT   = "#00aa0026"
    G_DARK = "hsla(120, 42%, 51%, 1)"
    text, c1 = re.subn(
        r"'looks-secondary':\s*'#[0-9A-Fa-f]{6}'",
        f"'looks-secondary': '{G}'", text
    )
    text, c2 = re.subn(
        r"'looks-transparent':\s*'#[0-9A-Fa-f]{8}'",
        f"'looks-transparent': '{G_T}'", text
    )
    text, c3 = re.subn(
        r"'looks-light-transparent':\s*'#[0-9A-Fa-f]{8}'",
        f"'looks-light-transparent': '{G_LT}'", text
    )
    text, c4 = re.subn(
        r"'looks-secondary-dark':\s*'[^']+'",
        f"'looks-secondary-dark': '{G_DARK}'", text
    )
    path.write_text(text)
    print(f"Patched red.js (replacements: {c1}, {c2}, {c3}, {c4})")

def patch_global_styles():
    path = Path("scratch-gui/src/lib/themes/global-styles.css")
    if not path.exists():
        print(f"  [!] {path} not found, skipping global-styles.css patch")
        return
    override = "\n/* fish‑eater overrides */\n:root {\n  --looks-secondary: #00aa00;\n}\n"
    with path.open("a") as f:
        f.write(override)
    print(f"Appended overrides to {path}")

def patch_entry_imports():
    """
    Prepend an import of global-styles.css into each playground entrypoint
    so that Webpack’s style-loader will inject your cursor + var-override CSS.
    """
    entries = {
        "scratch-gui/src/playground/editor.jsx":       "../lib/themes/global-styles.css",
        "scratch-gui/src/playground/player.jsx":       "../lib/themes/global-styles.css",
        "scratch-gui/src/playground/fullscreen.jsx":   "../lib/themes/global-styles.css",
        "scratch-gui/src/playground/embed.jsx":        "../lib/themes/global-styles.css",
        "scratch-gui/src/playground/addon-settings.jsx":"../../lib/themes/global-styles.css",
        "scratch-gui/src/playground/credits/credits.jsx":"../../lib/themes/global-styles.css"
    }
    for file, rel_css in entries.items():
        path = Path(file)
        if not path.exists():
            print(f"  [!] {path} not found, skipping CSS import")
            continue
        text = path.read_text()
        import_line = f"import '{rel_css}';"
        if import_line in text:
            print(f"  [*] CSS import already in {path.name}")
            continue
        # insert after any `'use strict';` or at top
        lines = text.splitlines()
        idx = 0
        if lines and re.match(r"^['\"]use strict['\"];", lines[0]):
            idx = 1
        lines.insert(idx, import_line)
        path.write_text("\n".join(lines) + "\n")
        print(f"Inserted CSS import into {path}")

def patch_webpack_favicon():
    """
    Add `favicon` option to every HtmlWebpackPlugin instance in webpack.config.js
    so that <link rel="icon"> points to our custom icon.png.
    """
    cfg = Path("scratch-gui/webpack.config.js")
    if not cfg.exists():
        print(f"  [!] {cfg} not found, skipping webpack.config.js patch")
        return
    text = cfg.read_text()
    # Look for each new HtmlWebpackPlugin({ and inject a favicon line
    pattern = r"(new HtmlWebpackPlugin\(\s*{)"
    repl = r"\1\n                favicon: path.resolve(__dirname, 'src/lib/gui/assets/icon.png'),"
    new_text, count = re.subn(pattern, repl, text)
    if count:
        # ensure we have the `path` module imported
        if "require('path')" not in new_text:
            new_text = "const path = require('path');\n" + new_text
        cfg.write_text(new_text)
        print(f"Injected favicon into {count} HtmlWebpackPlugin() calls in webpack.config.js")
    else:
        print("  [!] No HtmlWebpackPlugin() calls found to patch in webpack.config.js")

if __name__ == "__main__":
    print_working_dir()
    print("Directory tree for scratch-gui (depth=2):")
    print_tree("scratch-gui")

    # 1) site icon
    copy_file("custom/site_icon.png",
              "scratch-gui/src/lib/gui/assets/icon.png")

    # 2) cursors
    download_file("https://fisheater.peterdance.com/resources/cursor.png",
                  "scratch-gui/src/lib/gui/assets/cursor.png")
    download_file("https://fisheater.peterdance.com/resources/cursor_select.png",
                  "scratch-gui/src/lib/gui/assets/cursor_select.png")

    # 3) dango‑cat override
    copy_file("custom/dango-cat.svg",
              "scratch-gui/src/lib/default-project/dango-cat.svg")

    # 4) greenify red.js
    patch_red_js()

    # 5) append your global CSS overrides
    patch_global_styles()

    # 6) inject that CSS into every JS entry
    patch_entry_imports()

    # 7) configure webpack to use your favicon
    patch_webpack_favicon()

    print("\n✅ prebuild_patch.py complete — now run `npm run build` as usual.")
