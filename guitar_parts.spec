# -*- mode: python ; coding: utf-8 -*-
import sys

# Platform-specific settings
if sys.platform.startswith('win'):
    # Windows-specific settings
    block_cipher = None
elif sys.platform.startswith('linux'):
    # Linux-specific settings
    block_cipher = None
else:
    raise Exception("Unsupported platform")

a = Analysis(['guitar_parts.py'],
             pathex=[],
             binaries=[],
             datas=[('db/schema.sql', 'db')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GuitarParts',
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
    icon='resources/guitar-logo.ico',
)