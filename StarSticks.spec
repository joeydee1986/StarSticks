# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for StarSticks
Creates a single portable .exe with all dependencies bundled
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Assets folder will be added later when we have joystick images
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pygame',
        'pygame.joystick',
        'xml.etree.ElementTree',
    ],
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
    name='StarSticks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress the executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console enabled for debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file later
    version_file=None,  # TODO: Add version info later
)
