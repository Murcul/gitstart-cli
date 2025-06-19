# Encrypted API Key Embedding System

This document explains the secure API key embedding system that allows distributing the GitStart AI CLI with pre-configured API keys from GitHub Secrets.

## Overview

The system encrypts API keys during the GitHub Actions build process and embeds them securely into the application. Users can run `gsai chat` immediately without manual API key configuration.

## How It Works

### 1. Build-Time Encryption
- GitHub Actions reads API keys from repository secrets
- Keys are encrypted using AES-256 with PBKDF2 key derivation
- Encrypted keys are embedded into `gsai/build_config.py`
- The application is built with these encrypted keys included

### 2. Runtime Decryption
- When the application starts, it automatically decrypts embedded keys
- Decryption uses deterministic key derivation for consistent results
- Decrypted keys are used seamlessly by the application
- If decryption fails, the application gracefully falls back to user configuration

### 3. Security Features
- **AES-256 Encryption**: Industry-standard encryption for API keys
- **PBKDF2 Key Derivation**: 100,000 iterations for key strengthening
- **Deterministic Salt**: Enables consistent decryption across runs
- **Graceful Degradation**: Falls back to user keys if embedded keys fail
- **No Plain Text**: API keys never appear in plain text in the binary

## Files Involved

### Core Components
- `gsai/crypto_utils.py` - Encryption/decryption utilities
- `gsai/build_config.py` - Contains embedded encrypted keys (generated)
- `scripts/build_with_keys.py` - Build script that embeds keys
- `gsai/config.py` - Configuration system with decryption

### Updated Components
- `gsai/chat.py` - Handles encrypted key detection
- `gsai/main.py` - Status command shows encryption info
- `.github/workflows/build-release.yml` - Build process
- `pyproject.toml` - Added cryptography dependency

## GitHub Actions Integration

The build workflow now:
1. Reads `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` from repository secrets
2. Runs `scripts/build_with_keys.py` to encrypt and embed keys
3. Builds the application with PyInstaller
4. Creates releases with embedded encrypted keys

## User Experience

### With Embedded Keys (Production Build)
```bash
# No setup required - works immediately
gsai chat
# ✅ API keys configured: OpenAI, Anthropic (Embedded - Encrypted)
```

### Without Embedded Keys (Development)
```bash
gsai chat
# Shows setup dialog with options to configure keys
```

### Status Check
```bash
gsai status
# Shows build type, encryption status, and key sources
```

## Security Considerations

### What's Protected
- ✅ API keys are never stored in plain text
- ✅ Encryption key is derived deterministically (no storage needed)
- ✅ Failed decryption doesn't crash the application
- ✅ Users can still configure their own keys if needed

### What's Not Protected
- ⚠️ The application binary contains encrypted keys
- ⚠️ With enough effort, keys could potentially be extracted
- ⚠️ This is meant for convenience, not high-security environments

### Threat Model
This system protects against:
- ✅ Casual inspection of binary files
- ✅ Accidental exposure in logs or error messages  
- ✅ Simple string searches in the executable

This system does NOT protect against:
- ❌ Determined reverse engineering efforts
- ❌ Memory dumping of running processes
- ❌ Sophisticated binary analysis

## Development Workflow

### Testing Encryption Locally
```bash
# Test the encryption system
python3 test_crypto_only.py

# Test with dependencies (requires virtual environment)
python3 test_encryption.py
```

### Building with Keys
```bash
# Set environment variables
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run build script
python scripts/build_with_keys.py

# Build application
pyinstaller gsai.spec
```

### GitHub Secrets Setup
1. Go to repository Settings → Secrets and variables → Actions
2. Add secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
3. These will be automatically embedded in releases

## Configuration Priority

The system uses this priority order for API keys:
1. **Environment variables** (highest priority)
2. **User-configured keys** (via `gsai configure`)
3. **Embedded encrypted keys** (from build)
4. **Default empty** (triggers setup prompt)

## Troubleshooting

### "Build configuration issue" Error
- This appears when a production build has encrypted keys but decryption failed
- Usually indicates a problem with the encryption/decryption process
- Try rebuilding or contact support

### Keys Not Working After Build
- Check `gsai status` to verify build type and encryption status
- Ensure GitHub Secrets are properly configured
- Verify the build script ran successfully

### Development vs Production Detection
- **Development**: `BUILD_TYPE = "development"`, no embedded keys
- **Production**: `BUILD_TYPE = "production"`, has embedded keys
- The application automatically detects the build type

## Implementation Details

### Encryption Process
```python
# 1. Generate deterministic salt from system data
salt = hashlib.sha256("gsai-secure-keys-v1.0-<app-path>").digest()[:16]

# 2. Derive encryption key using PBKDF2
kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt, iterations=100000)
key = base64.urlsafe_b64encode(kdf.derive(b"gsai-embedded-key-protection-2024"))

# 3. Encrypt API key with Fernet (AES-256)
fernet = Fernet(key)
encrypted = fernet.encrypt(api_key.encode())
embedded_key = base64.urlsafe_b64encode(encrypted).decode()
```

### Detection Logic
```python
# Encrypted keys are much longer than typical API keys and base64-encoded
def is_encrypted_key(key_value: str) -> bool:
    try:
        base64.urlsafe_b64decode(key_value.encode())
        return len(key_value) > 100  # Encrypted keys are longer
    except:
        return False
```

## Future Improvements

Potential enhancements for the encryption system:
- Hardware-based key derivation (TPM/Secure Enclave)
- Per-user key derivation with user identification
- Time-based key rotation with versioning
- Remote key validation and revocation
- Obfuscation of the encryption logic itself

---

This system provides a good balance between security and convenience for distributing pre-configured API keys while maintaining the ability for users to configure their own keys when needed.