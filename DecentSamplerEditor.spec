# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    [os.path.join('src', 'main.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join('src', 'styles', 'main_theme.qss'), os.path.join('styles')),
        ('Examples', 'Examples'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DecentSamplerEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=sys.platform == 'linux',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DecentSamplerEditor',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='DecentSamplerEditor.app',
        icon=None,
        bundle_identifier='com.decentsampler.editor',
    )
