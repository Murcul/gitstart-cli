#!/usr/bin/env python3
"""
Build script for creating a shareable executable of GitStart CoPilot CLI
with embedded API keys using uv and PyInstaller.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> bool:
    """Run a command and return True if successful."""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_dependencies() -> bool:
    """Check if required build dependencies are available."""
    # Check for uv
    if not shutil.which("uv"):
        print("Missing dependency: uv")
        return False
    
    # Check for python (try python3 first, then python)
    python_cmd = None
    for cmd in ["python3", "python"]:
        if shutil.which(cmd):
            python_cmd = cmd
            break
    
    if not python_cmd:
        print("Missing dependency: python (tried python3 and python)")
        return False
    
    return True


def create_build_config(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    output_dir: Path = Path("dist")
) -> Path:
    """Create a temporary build configuration with embedded API keys."""
    build_config = f'''"""
Build-time configuration with embedded API keys.
This file is generated during build and should not be committed.
"""

EMBEDDED_OPENAI_API_KEY = "{openai_key or ''}"
EMBEDDED_ANTHROPIC_API_KEY = "{anthropic_key or ''}"
'''
    
    # Create a temporary build config file
    config_file = Path("gsai/build_config.py")
    with open(config_file, "w") as f:
        f.write(build_config)
    
    return config_file


def modify_config_for_build(openai_key: Optional[str], anthropic_key: Optional[str]) -> None:
    """Modify config.py to use embedded API keys when available."""
    config_path = Path("gsai/config.py")
    
    # Read the current config
    with open(config_path, "r") as f:
        content = f.read()
    
    # Add import for build config at the top
    import_line = "try:\n    from gsai.build_config import EMBEDDED_OPENAI_API_KEY, EMBEDDED_ANTHROPIC_API_KEY\nexcept ImportError:\n    EMBEDDED_OPENAI_API_KEY = ''\n    EMBEDDED_ANTHROPIC_API_KEY = ''"
    
    # Find the Settings class and modify the API key fields
    modified_content = content.replace(
        'OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")',
        f'OPENAI_API_KEY: str = Field(default=EMBEDDED_OPENAI_API_KEY or "", description="OpenAI API Key")'
    ).replace(
        'ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API Key")',
        f'ANTHROPIC_API_KEY: str = Field(default=EMBEDDED_ANTHROPIC_API_KEY or "", description="Anthropic API Key")'
    )
    
    # Add the import at the beginning (after the docstring)
    lines = modified_content.split('\n')
    import_added = False
    for i, line in enumerate(lines):
        if line.startswith('"""') and '"""' in line[3:]:
            # Single line docstring
            lines.insert(i + 1, "")
            lines.insert(i + 2, import_line)
            import_added = True
            break
        elif line.startswith('"""'):
            # Multi-line docstring, find the end
            for j in range(i + 1, len(lines)):
                if '"""' in lines[j]:
                    lines.insert(j + 1, "")
                    lines.insert(j + 2, import_line)
                    import_added = True
                    break
            break
    
    if not import_added:
        lines.insert(0, import_line)
        lines.insert(1, "")
    
    modified_content = '\n'.join(lines)
    
    # Write the modified config
    with open(config_path, "w") as f:
        f.write(modified_content)


def build_executable(
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    output_dir: Path = Path("dist"),
    app_name: str = "gsai"
) -> bool:
    """Build the executable using uv and PyInstaller."""
    
    print("Starting build process...")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Create build config with embedded keys
    build_config_file = create_build_config(openai_api_key, anthropic_api_key, output_dir)
    
    try:
        # Modify config.py to use embedded keys
        modify_config_for_build(openai_api_key, anthropic_api_key)
        
        # Install PyInstaller in the uv environment
        if not run_command(["uv", "add", "--dev", "pyinstaller"]):
            return False
        
        # Create PyInstaller spec file
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['gsai/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gsai/agents/prompts/templates', 'gsai/agents/prompts/templates'),
    ],
    hiddenimports=[
        'gsai.agents',
        'gsai.agents.tools',
        'gsai.agents.tools_agentic',
        'gsai.agents.prompts',
        'tree_sitter',
        'tree_sitter_language_pack',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
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
    icon=None,
)
'''
        
        spec_file = Path(f"{app_name}.spec")
        with open(spec_file, "w") as f:
            f.write(spec_content)
        
        # Build with PyInstaller
        if not run_command(["uv", "run", "pyinstaller", str(spec_file), "--distpath", str(output_dir)]):
            return False
        
        print(f"Build completed successfully! Executable is at: {output_dir}/{app_name}")
        return True
        
    finally:
        # Clean up temporary files
        if build_config_file.exists():
            build_config_file.unlink()
        
        # Restore original config.py
        if run_command(["git", "checkout", "gsai/config.py"]):
            print("Restored original config.py")
        
        # Clean up spec file
        if spec_file.exists():
            spec_file.unlink()


def main():
    parser = argparse.ArgumentParser(description="Build GitStart CoPilot CLI executable")
    parser.add_argument(
        "--openai-key",
        help="OpenAI API key to embed in the executable"
    )
    parser.add_argument(
        "--anthropic-key", 
        help="Anthropic API key to embed in the executable"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="Output directory for the executable (default: dist)"
    )
    parser.add_argument(
        "--app-name",
        default="gsai",
        help="Name of the executable (default: gsai)"
    )
    
    args = parser.parse_args()
    
    # Check if at least one API key is provided
    if not args.openai_key and not args.anthropic_key:
        print("Warning: No API keys provided. The executable will require manual configuration.")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Build the executable
    if build_executable(
        openai_api_key=args.openai_key,
        anthropic_api_key=args.anthropic_key,
        output_dir=args.output_dir,
        app_name=args.app_name
    ):
        print("Build successful!")
        print(f"Your executable is ready at: {args.output_dir}/{args.app_name}")
        print("\nTo use the executable:")
        print(f"  ./{args.output_dir}/{args.app_name} --help")
    else:
        print("Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()