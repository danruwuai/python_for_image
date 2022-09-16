# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['C:\\Users\\danru\\work\\project\\workspace\\image\\python_for_image\\packed\\aao'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['altgraph', 'ca-certificates', 'certifi', 'future', 'openssl', 'pefile', 'pip', 'pyinstaller-hooks-contrib', 'tzdata', 'wheel', 'wincertstore', 'pyinstaller', 'python', 'pywin32-ctypes', 'setuptools', 'sqlite', 'vc', 'vs2015_runtime'],
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
    name='Analysis_aao',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='color.ico',
)
