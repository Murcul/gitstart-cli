# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path('.').resolve()
sys.path.insert(0, str(project_root))

# Get all template files
template_files = []
templates_dir = project_root / 'gsai' / 'agents' / 'prompts' / 'templates'
if templates_dir.exists():
    for template_file in templates_dir.rglob('*'):
        if template_file.is_file():
            rel_path = template_file.relative_to(project_root)
            template_files.append((str(template_file), str(rel_path.parent)))

a = Analysis(
    ['gsai/main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=template_files,
    hiddenimports=[
        # Core gsai modules
        'gsai',
        'gsai.main',
        'gsai.config',
        'gsai.chat',
        'gsai.security',
        'gsai.utils',
        'gsai.special',
        'gsai.linter',
        'gsai.display_helpers',
        'gsai.repo_map',
        
        # Agents
        'gsai.agents',
        'gsai.agents.master',
        'gsai.agents.code_writing',
        'gsai.agents.question_answering',
        'gsai.agents.git_operations',
        'gsai.agents.implementation_planning',
        'gsai.agents.research',
        'gsai.agents.ticket_writing',
        'gsai.agents.models',
        
        # Tools
        'gsai.agents.tools',
        'gsai.agents.tools.view_file',
        'gsai.agents.tools.str_replace',
        'gsai.agents.tools.sequential_thinking',
        'gsai.agents.tools.search_for_files',
        'gsai.agents.tools.search_for_code',
        'gsai.agents.tools.save_to_memory',
        'gsai.agents.tools.run_command',
        'gsai.agents.tools.quick_view_file',
        'gsai.agents.tools.overwrite_file',
        'gsai.agents.tools.move_file',
        'gsai.agents.tools.list_files',
        'gsai.agents.tools.lint_source_code',
        'gsai.agents.tools.git_tools',
        'gsai.agents.tools.deps',
        'gsai.agents.tools.delete_file',
        
        # Agentic tools
        'gsai.agents.tools_agentic',
        'gsai.agents.tools_agentic.extract_relevant_context_from_url',
        'gsai.agents.tools_agentic.expert',
        'gsai.agents.tools_agentic.web_search',
        'gsai.agents.tools_agentic.web_navigation',
        
        # Prompts
        'gsai.agents.prompts',
        'gsai.agents.prompts.helpers',
        'gsai.agents.prompts.templates',
        
        # Build config (if it exists)
        'gsai.build_config',
        
        # Core dependencies
        'pydantic_ai',
        'pydantic_ai.agent',
        'pydantic_ai.messages',
        'pydantic_ai.models',
        'pydantic_ai.tools',
        'pydantic_ai.exceptions',
        'pydantic_ai.settings',
        'pydantic_ai._utils',
        
        # AI providers
        'openai',
        'openai.types',
        'openai._client',
        'anthropic',
        'anthropic._client',
        'anthropic.types',
        
        # CLI and UI
        'typer',
        'typer.main',
        'typer.core',
        'rich',
        'rich.console',
        'rich.table',
        'rich.panel',
        'rich.text',
        'rich.markdown',
        'rich.syntax',
        'rich.progress',
        'rich.live',
        'rich.layout',
        'rich.prompt',
        
        # Settings and validation
        'pydantic',
        'pydantic.main',
        'pydantic.fields',
        'pydantic.types',
        'pydantic_settings',
        'pydantic_settings.main',
        
        # Logging
        'loguru',
        'loguru._logger',
        
        # Git operations
        'git',
        'GitPython',
        
        # Code analysis
        'tree_sitter',
        'tree_sitter_language_pack',
        'grep_ast',
        
        # Web and search
        'beautifulsoup4',
        'bs4',
        'duckduckgo_search',
        'requests',
        'httpx',
        
        # Templates and text processing
        'jinja2',
        'jinja2.environment',
        'jinja2.loaders',
        
        # Token counting
        'tiktoken',
        'tiktoken.core',
        
        # Syntax highlighting
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        
        # File matching
        'pathspec',
        
        # Graph operations
        'networkx',
        'networkx.algorithms',
        
        # Async utilities
        'asyncer',
        
        # Caching
        'diskcache',
        
        # Package resolution fixes
        'importlib_metadata',
        'importlib_metadata._meta',
        
        # Git modules
        'git',
        'gitdb',
        'gitdb.db',
        'smmap',
        
        # Beautiful Soup
        'bs4',
        'bs4.builder',
        'bs4.element',
        
        # Standard library modules that might be missing
        'json',
        'csv',
        'sqlite3',
        'zlib',
        'gzip',
        'base64',
        'uuid',
        'hashlib',
        'hmac',
        'secrets',
        'datetime',
        'time',
        'os',
        'sys',
        'pathlib',
        'subprocess',
        'tempfile',
        'shutil',
        'glob',
        'fnmatch',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'html',
        'html.parser',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
        'email',
        'email.mime',
        'asyncio',
        'concurrent',
        'concurrent.futures',
        'threading',
        'multiprocessing',
        'queue',
        'collections',
        'collections.abc',
        'itertools',
        'functools',
        'operator',
        'contextlib',
        'weakref',
        'copy',
        'pickle',
        'struct',
        'socket',
        'ssl',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy packages we don't need
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'jupyter',
        'IPython',
        'notebook',
        'django',
        'flask',
        'tornado',
        'twisted',
        'docutils',
        'sphinx',
        'pytest',
        'pip',
        'wheel',
    ],
    noarchive=False,
    optimize=0,
)

# Filter out any None values from datas
a.datas = [item for item in a.datas if item is not None]

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