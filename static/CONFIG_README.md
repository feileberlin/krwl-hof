# Configuration Files

## static/config.json

This file is used for **local development only**. It's tracked in git to provide a working default configuration.

**During deployment:**
- Production (`main` branch): Gets replaced by `config.prod.json`
- Preview (`preview` branch): Gets replaced by `config.preview.json`
- The deployment workflow also injects `build_info` with commit SHA and PR number

## Source Config Files

The source configuration files are in the repository root:

- **config.prod.json** - Production configuration (real events, watermark disabled)
- **config.preview.json** - Preview configuration (real events, watermark enabled with "PREVIEW")
- **config.dev.json** - Development/Testing configuration (real + demo events, watermark enabled with "TESTING")

## Modifying Configuration

1. Edit the appropriate source config file in the root directory
2. For production: Edit `config.prod.json`
3. For preview: Edit `config.preview.json`
4. For local development: Edit `config.dev.json` and copy to `static/config.json`

The deployment workflows automatically handle copying the correct config during deployment.
