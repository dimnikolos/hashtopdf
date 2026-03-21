# hashtopdf.spec
# Build with:  pyinstaller hashtopdf.spec

import os
from PyInstaller.utils.hooks import collect_data_files

# --- tkinterdnd2: bundle the entire package folder (contains .dll + .tcl) ---
tkdnd_pkg = r'C:\Python\Python313\Lib\site-packages\tkinterdnd2'
tkdnd_datas = []
for root_dir, dirs, files in os.walk(tkdnd_pkg):
    for f in files:
        full = os.path.join(root_dir, f)
        rel  = os.path.relpath(os.path.dirname(full), os.path.dirname(tkdnd_pkg))
        tkdnd_datas.append((full, rel))

block_cipher = None

a = Analysis(
    ['hashtopdf.py'],
    pathex=[],
    binaries=[],
    datas=tkdnd_datas,
    hiddenimports=['tkinterdnd2'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HashToPDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # ← no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',        # ← our custom icon
    version=None,
    onefile=True,           # ← single .exe
)
