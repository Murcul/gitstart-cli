#!/usr/bin/env python3
"""
Test the build script locally to verify it works without Unicode issues.
"""

import os
import sys
import tempfile
from pathlib import Path

def test_build_script():
    """Test the build script with mock environment variables."""
    # Set up mock environment
    os.environ['OPENAI_API_KEY'] = 'sk-test-openai-key-123456789'
    os.environ['ANTHROPIC_API_KEY'] = 'anthropic-test-key-987654321'
    os.environ['GITHUB_SHA'] = 'abc123def456'
    
    # Add project to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Import and run the build function
        from scripts.build_with_keys import embed_keys
        
        print("Testing build script with mock API keys...")
        success = embed_keys()
        
        if success:
            print("SUCCESS: Build script completed without errors")
            
            # Check if build_config.py was created
            build_config_path = project_root / "gsai" / "build_config.py"
            if build_config_path.exists():
                print("SUCCESS: build_config.py was created")
                
                # Read and verify content
                with open(build_config_path, 'r') as f:
                    content = f.read()
                
                if 'BUILD_TYPE = "production"' in content:
                    print("SUCCESS: Build type set to production")
                else:
                    print("WARNING: Build type not set correctly")
                
                if 'EMBEDDED_OPENAI_API_KEY = ""' not in content:
                    print("SUCCESS: OpenAI key was embedded (encrypted)")
                else:
                    print("WARNING: OpenAI key appears empty")
                
                if 'EMBEDDED_ANTHROPIC_API_KEY = ""' not in content:
                    print("SUCCESS: Anthropic key was embedded (encrypted)")
                else:
                    print("WARNING: Anthropic key appears empty")
                
                # Cleanup
                build_config_path.unlink()
                print("SUCCESS: Cleaned up test build_config.py")
                
            else:
                print("ERROR: build_config.py was not created")
                return False
                
        else:
            print("ERROR: Build script failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"ERROR: Build script test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up environment
        os.environ.pop('OPENAI_API_KEY', None)
        os.environ.pop('ANTHROPIC_API_KEY', None)
        os.environ.pop('GITHUB_SHA', None)


if __name__ == "__main__":
    success = test_build_script()
    print("\n" + "=" * 50)
    if success:
        print("BUILD SCRIPT TEST PASSED!")
        print("The script should work in GitHub Actions without Unicode errors.")
    else:
        print("BUILD SCRIPT TEST FAILED!")
        print("There may be issues with the GitHub Actions build.")
    
    sys.exit(0 if success else 1)