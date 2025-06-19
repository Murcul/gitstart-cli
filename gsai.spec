# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for gsai CLI application.
This creates a standalone executable with all dependencies bundled.
"""

import sys
from pathlib import Path

# Get the current directory
current_dir = Path('.').absolute()

# Define the main script
main_script = str(current_dir / 'gsai' / 'main.py')

# Data files to include (templates, etc.)
datas = []

# Add Jinja2 templates
templates_dir = current_dir / 'gsai' / 'agents' / 'prompts' / 'templates'
if templates_dir.exists():
    datas.append((str(templates_dir), 'gsai/agents/prompts/templates'))

# Add package metadata for pydantic-ai packages to fix PyInstaller issue
import importlib.metadata
try:
    # Collect metadata for pydantic-ai packages
    for pkg_name in ['pydantic-ai', 'pydantic-ai-slim', 'pydantic-evals', 'pydantic-graph']:
        try:
            dist = importlib.metadata.distribution(pkg_name)
            metadata_path = str(dist._path)
            datas.append((metadata_path, f'pydantic_ai_slim-{dist.version}.dist-info'))
        except importlib.metadata.PackageNotFoundError:
            pass
except Exception:
    pass

# Hidden imports - libraries that PyInstaller might miss
hiddenimports = [
    # Core CLI dependencies
    'typer',
    'typer.main',
    'typer.core',
    'click',
    'click.core',
    'rich',
    'rich.console',
    'rich.table',
    'rich.panel',
    'rich.progress',
    'rich.syntax',
    'rich.markdown',
    'rich.traceback',
    
    # Pydantic and settings
    'pydantic_ai',
    'pydantic_ai.agent',
    'pydantic_ai.models',
    'pydantic_ai.models.openai',
    'pydantic_ai.models.anthropic',
    'pydantic_ai._utils',
    'pydantic_ai_slim',
    'pydantic_evals',
    'pydantic_graph',
    'pydantic',
    'pydantic.main',
    'pydantic.fields',
    'pydantic.types',
    'pydantic_settings',
    'pydantic_settings.main',
    
    # Logging
    'loguru',
    'loguru._logger',
    
    # AI APIs
    'openai',
    'openai.api',
    'openai.models',
    'anthropic',
    'anthropic.client',
    'anthropic.models',
    
    # Git operations
    'git',
    'git.repo',
    'git.cmd',
    'GitPython',
    
    # Tree-sitter
    'tree_sitter',
    'tree_sitter_language_pack',
    'tree_sitter_python',
    'tree_sitter_javascript',
    'tree_sitter_typescript',
    'tree_sitter_java',
    'tree_sitter_cpp',
    'tree_sitter_c',
    'tree_sitter_go',
    'tree_sitter_rust',
    
    # Code analysis
    'grep_ast',
    'grep_ast.ast_grep',
    
    # Web scraping
    'bs4',
    'beautifulsoup4',
    'duckduckgo_search',
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.sessions',
    'urllib3',
    
    # Templates
    'jinja2',
    'jinja2.loaders',
    'jinja2.environment',
    
    # Tokenization
    'tiktoken',
    'tiktoken.core',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    
    # Syntax highlighting
    'pygments',
    'pygments.lexers',
    'pygments.formatters',
    
    # File operations
    'pathspec',
    'pathspec.patterns',
    
    # Graph operations
    'networkx',
    'networkx.classes',
    'networkx.algorithms',
    
    # Async
    'asyncer',
    'asyncio',
    
    # Cache
    'diskcache',
    'diskcache.core',
    
    # Additional imports that might be missed
    'email.mime',  # For some HTTP libraries
    'email.mime.multipart',
    'email.mime.text',
    'json',
    'csv',
    'sqlite3',
    'http.client',
    'ssl',
    'certifi',  # SSL certificates
]

# Binaries to exclude (reduce size)
excludes = [
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas',
    'PIL',
    'tornado',
    'jupyter',
    'notebook',
    'IPython',
]

a = Analysis(
    [main_script],
    pathex=[str(current_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
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
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available
)