# -*- mode: python ; coding: utf-8 -*-
# General Development System (GDS) — PyInstaller spec
# Run from PROJECT ROOT: pyinstaller desktop/GDS.spec
import os

from PyInstaller.utils.hooks import collect_all

datas = [('config', 'config'), ('apps', 'apps')]
binaries = []
hiddenimports = ['django', 'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.admin.templatetags', 'config', 'config.settings', 'config.settings.desktop', 'config.urls', 'config.wsgi', 'apps', 'apps.core', 'apps.accounts', 'apps.warehouse', 'apps.purchasing', 'apps.inventory', 'tkinter', 'waitress', 'waitress.server', 'waitress.adjustments', 'openpyxl', 'psycopg2', 'psycopg2.extensions', 'psycopg2.extras', 'pystray', 'PIL']
tmp_ret = collect_all('django')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['desktop/desktop_launcher.py'],
    pathex=[os.path.abspath('.')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GDS Management',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GDS Management',
)
