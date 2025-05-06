import os, glob, shutil

# 1) HTML patches
ICON = '<link rel="icon" href="custom/site_icon.png">'
CSS_CURSOR = """
<style>
  /* default cursor */
  html, body, * {
    cursor: url("https://fisheater.peterdance.com/resources/cursor.png"), auto !important;
  }
  /* pointer/hover cursor */
  a:hover, button:hover, [role="button"]:hover, [style*="cursor:pointer"] {
    cursor: url("https://fisheater.peterdance.com/resources/cursor_select.png"), auto !important;
  }
  /* change secondary look color */
  :root { --looks-secondary: green !important; }
</style>
"""

for path in glob.glob('scratch-gui/build/*.html'):
  print(f'Patching HTML {path}')
  with open(path, 'r') as f:
    contents = f.read()
    # inject favicon + cursor+color CSS just before </head>
    contents = contents.replace(
      '</head>',
      ICON + CSS_CURSOR + '</head>'
    )
    # your existing removals
    contents = contents.replace(
      '<link rel="manifest" href="manifest.webmanifest">',
      ''
    )
  with open(path, 'w') as f:
    f.write(contents)

# 2) JS patches (unchanged)
for path in glob.glob('scratch-gui/build/**/*.js', recursive=True):
  print(f'Patching JS {path}')
  with open(path, 'r') as f:
    contents = f.read().replace(
      'https://trampoline.turbowarp.org',
      'https://trampoline.turbowarp.xyz'
    )
  with open(path, 'w') as f:
    f.write(contents)

# 3) cleanup + index.html swap (unchanged)
os.remove('scratch-gui/build/sw.js')
os.remove('scratch-gui/build/manifest.webmanifest')
os.remove('scratch-gui/build/fullscreen.html')
os.remove('scratch-gui/build/index.html')
shutil.copy('scratch-gui/build/editor.html', 'scratch-gui/build/index.html')
shutil.copy('robots.txt',      'scratch-gui/build/robots.txt')
