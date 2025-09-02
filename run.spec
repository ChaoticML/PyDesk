# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['E:\\GitHub\\PyDesk'],  # Correct projectpad
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
        ('app/database.py', 'app'),
        ('site-packages/matplotlib', 'site-packages/matplotlib')
    ],
    hiddenimports=[
        'waitress',
        'markdown',
        'matplotlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['flask_session'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data,
              cipher=block_cipher)

exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,  # Gebruik de datas hier
              [],
              name='PyDesk',
              debug=False,
              bootloader_ignore_signals=False,
              strip=False,
              upx=True,
              upx_exclude=[],
              runtime_tmpdir=None,
              console=False,
              disable_windowed_traceback=False,
              target_arch='none',
              codesign_identity=None,
              entitlements_file=None )