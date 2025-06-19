# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path('.').resolve()
sys.path.insert(0, str(project_root))

a = Analysis(
    ['gsai/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gsai',
        'gsai.main',
        'gsai.config',
        'gsai.chat',
        'gsai.build_config',
        'pydantic_ai',
        'pydantic_ai_slim',
        'pydantic_ai.agent',
        'pydantic_ai.messages',
        'pydantic_ai.models',
        'pydantic_ai.tools',
        'openai',
        'anthropic',
        'typer',
        'rich',
        'pydantic',
        'pydantic_settings',
        'loguru',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='gsai',
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
)