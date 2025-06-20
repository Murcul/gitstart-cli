"""
Key resolver that consolidates all API key sources.
This module provides the final API keys to use, considering all sources.
"""

import os


def get_final_api_keys():
    """Get the final API keys to use, considering all sources in priority order."""
    
    # Priority order:
    # 1. Environment variables (highest priority)
    # 2. User configured keys (from global config)
    # 3. Embedded keys (from build)
    # 4. Empty strings (fallback)
    
    final_openai = ''
    final_anthropic = ''
    sources = {'openai': 'none', 'anthropic': 'none'}
    
    # Step 1: Check environment variables
    env_openai = os.getenv('OPENAI_API_KEY', '').strip()
    env_anthropic = os.getenv('ANTHROPIC_API_KEY', '').strip()
    
    if env_openai:
        final_openai = env_openai
        sources['openai'] = 'environment'
    
    if env_anthropic:
        final_anthropic = env_anthropic
        sources['anthropic'] = 'environment'
    
    # Step 2: Check embedded keys (only if not already set)
    if not final_openai or not final_anthropic:
        try:
            from gsai.embedded_keys import get_api_keys, has_embedded_keys
            if has_embedded_keys():
                keys = get_api_keys()
                embedded_openai = keys.get('openai', '').strip()
                embedded_anthropic = keys.get('anthropic', '').strip()
                
                if not final_openai and embedded_openai:
                    final_openai = embedded_openai
                    sources['openai'] = 'embedded'
                
                if not final_anthropic and embedded_anthropic:
                    final_anthropic = embedded_anthropic
                    sources['anthropic'] = 'embedded'
        except Exception:
            pass
    
    # Step 3: Check user configured keys (only if not already set)
    if not final_openai or not final_anthropic:
        try:
            import pathlib
            global_config_file = pathlib.Path.home() / ".ai" / "gsai" / ".env"
            
            if global_config_file.exists():
                with open(global_config_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            value = value.strip()
                            
                            if key == "OPENAI_API_KEY" and not final_openai and value:
                                final_openai = value
                                sources['openai'] = 'user_config'
                            
                            elif key == "ANTHROPIC_API_KEY" and not final_anthropic and value:
                                final_anthropic = value
                                sources['anthropic'] = 'user_config'
        except Exception:
            pass
    
    return {
        'openai_key': final_openai,
        'anthropic_key': final_anthropic,
        'openai_source': sources['openai'],
        'anthropic_source': sources['anthropic'],
        'has_any': bool(final_openai or final_anthropic)
    }


def patch_cli_settings():
    """Patch the CLI settings object to use resolved keys."""
    try:
        from gsai.config import cli_settings
        
        keys = get_final_api_keys()
        
        # Force override the keys if we have better ones from our resolver
        if keys['openai_key']:
            cli_settings.OPENAI_API_KEY = keys['openai_key']
        
        if keys['anthropic_key']:
            cli_settings.ANTHROPIC_API_KEY = keys['anthropic_key']
        
        return True
    except Exception:
        return False


def get_key_status():
    """Get a status summary of all key sources."""
    keys = get_final_api_keys()
    
    status = {
        'has_keys': keys['has_any'],
        'openai': {
            'available': bool(keys['openai_key']),
            'source': keys['openai_source']
        },
        'anthropic': {
            'available': bool(keys['anthropic_key']),
            'source': keys['anthropic_source']
        }
    }
    
    # Add embedded key info
    try:
        from gsai.embedded_keys import has_embedded_keys, is_production_build
        status['build'] = {
            'has_embedded': has_embedded_keys(),
            'is_production': is_production_build()
        }
    except Exception:
        status['build'] = {
            'has_embedded': False,
            'is_production': False
        }
    
    return status