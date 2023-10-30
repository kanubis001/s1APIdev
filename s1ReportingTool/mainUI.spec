# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['mainUI.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\fireb\\OneDrive\\Develop_private\\Python_git\\s1APIdev\\s1ReportingTool\\reportwidget.ui','.'),
('C:\\Users\\fireb\\OneDrive\\Develop_private\\Python_git\\s1APIdev\\s1ReportingTool\\index.ui','.')],
    hiddenimports=[],
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
    name='mainUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\fireb\\OneDrive\\Develop_private\\Python_git\\s1APIdev\\s1ReportingTool\\icon\\comsys_S1.ico'],
)
