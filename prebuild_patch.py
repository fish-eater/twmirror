#!/usr/bin/env python3
import os
import shutil
import urllib.request

def print_tree(path):
    print(f"Directory tree for {path}:")
    for root, dirs, files in os.walk(path):
        depth = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * depth
        print(f"{indent}{os.path.basename(root)}/")


def safe_copy(src, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print(f"Copied {src} -> {dst}")
    except Exception as e:
        print(f"Failed to copy {src} -> {dst}: {e}")


def safe_download(url, dst):
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        print(f"Downloading {url} -> {dst}")
        urllib.request.urlretrieve(url, dst)
        print(f"Downloaded {url} -> {dst}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")


def patch_css(var_name, old_val, new_val, file_path):
    try:
        with open(file_path, 'r') as f:
            text = f.read()
        if old_val in text:
            text = text.replace(old_val, new_val)
            with open(file_path, 'w') as f:
                f.write(text)
            print(f"Patched {var_name} in {file_path}")
        else:
            print(f"Did not find '{old_val}' in {file_path}")
    except Exception as e:
        print(f"Failed to patch CSS in {file_path}: {e}")


def main():
    # 1) Print working directory
    print("Working directory:", os.getcwd())

    # 2) Ensure scratch-gui is present
    gui_dir = 'scratch-gui'
    if not os.path.isdir(gui_dir):
        print(f"Error: '{gui_dir}' not found. Please checkout TurboWarp/scratch-gui into '{gui_dir}'")
        return

    # 3) Print the directory tree for inspection
    print_tree(gui_dir)

    # 4) Copy custom site icon
    safe_copy(
        os.path.join('custom', 'site_icon.png'),
        os.path.join(gui_dir, 'src', 'lib', 'gui', 'assets', 'icon.png')
    )

    # 5) Download cursors
    safe_download(
        'https://fisheater.peterdance.com/resources/cursor.png',
        os.path.join(gui_dir, 'src', 'lib', 'gui', 'assets', 'cursor.png')
    )
    safe_download(
        'https://fisheater.peterdance.com/resources/cursor_select.png',
        os.path.join(gui_dir, 'src', 'lib', 'gui', 'assets', 'cursor_select.png')
    )

    # 6) Patch CSS var in light theme
    patch_css(
        'looks-secondary',
        '--looks-secondary: #888888;',
        '--looks-secondary: #00aa00;',
        os.path.join(gui_dir, 'src', 'lib', 'themes', 'gui', 'light.css')
    )

if __name__ == '__main__':
    main()
