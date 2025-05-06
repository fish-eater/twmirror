#!/usr/bin/env python3
import os
import shutil
import urllib.request
import re


def print_tree(base_dir, max_depth=2):
    print(f"Directory tree for {base_dir} (depth {max_depth}):")
    if not os.path.isdir(base_dir):
        print(f"  {base_dir}/ not found")
        return
    for root, dirs, files in os.walk(base_dir):
        rel = os.path.relpath(root, base_dir)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirs[:] = []  # don't recurse deeper
            continue
        indent = "    " * depth
        name = base_dir if rel == "." else os.path.basename(root)
        print(f"{indent}{name}/")


def main():
    # 1) Working directory
    cwd = os.getcwd()
    print(f"Working directory: {cwd}")

    # 2) Print trimmed directory tree
    print_tree("scratch-gui", max_depth=2)

    # 3) Copy custom site icon
    src_icon = os.path.join("custom", "site_icon.png")
    dest_icon = os.path.join("scratch-gui", "src", "lib", "assets", "icon.png")
    try:
        shutil.copyfile(src_icon, dest_icon)
        print(f"Copied {src_icon} -> {dest_icon}")
    except Exception as e:
        print(f"Failed to copy site_icon.png: {e}")

    # 4) Download cursors
    cursors = {
        "https://fisheater.peterdance.com/resources/cursor.png":
            os.path.join("scratch-gui", "src", "lib", "assets", "cursor.png"),
        "https://fisheater.peterdance.com/resources/cursor_select.png":
            os.path.join("scratch-gui", "src", "lib", "assets", "cursor_select.png")
    }
    for url, dest in cursors.items():
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Downloaded {url} -> {dest}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    # 5) Patch CSS variable
    css_pattern = re.compile(r"--looks-secondary\s*:\s*#[0-9A-Fa-f]{3,6}\s*;")
    replacement = "--looks-secondary: #00aa00;"
    css_files = [
        os.path.join("scratch-gui", "src", "css", "light.css"),
        os.path.join("scratch-gui", "src", "css", "dark.css")
    ]
    for css in css_files:
        try:
            with open(css, "r", encoding="utf-8") as f:
                content = f.read()
            new_content, count = css_pattern.subn(replacement, content)
            if count > 0:
                with open(css, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Patched CSS in {css} ({count} replacements)")
            else:
                print(f"No matches found in {css}, no changes made")
        except FileNotFoundError:
            print(f"CSS file not found: {css}")
        except Exception as e:
            print(f"Failed to patch CSS in {css}: {e}")


if __name__ == "__main__":
    main()
