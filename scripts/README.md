# Scripts Directory

This directory contains utility scripts and thin wrapper scripts for the KRWL HOF project.

## Contents

### Wrapper Scripts (Delegate to `src/modules/`)
- **check_kiss.py** - KISS compliance checker (delegates to `src/modules/kiss_checker.py`)
- **verify_features.py** - Feature registry verification (delegates to `src/modules/feature_verifier.py`)
- **test_filters.py** - Filter testing (delegates to `src/modules/filter_tester.py`)
- **config_editor.py** - Configuration editor (delegates to `src/modules/config_editor.py`)

### Utility Scripts
- **manage_libs.py** - CDN library manager (download, verify, update third-party libraries)
- **generate_demo_events.py** - Generate demo events with dynamic timestamps
- **cleanup_obsolete.py** - Remove obsolete files from the project

### Documentation Scripts
- **build_markdown_docs.py** - 📄 Markdown to HTML documentation builder with GitHub dark theme
- **cleanup_old_docs.py** - 🧹 Remove obsolete documentation HTML files with old naming conventions

## Usage

All scripts can be run from the project root directory:

```bash
# Wrapper scripts
python3 scripts/check_kiss.py --verbose
python3 scripts/verify_features.py --verbose
python3 scripts/test_filters.py --verbose
python3 scripts/config_editor.py

# Utility scripts
python3 scripts/manage_libs.py download
python3 scripts/generate_demo_events.py > events.demo.json
python3 scripts/cleanup_obsolete.py

# Documentation scripts
python3 scripts/build_markdown_docs.py --organize --verbose
python3 scripts/cleanup_old_docs.py --dry-run
```

## Documentation Build System

The documentation build system converts all Markdown files to styled HTML with a consistent GitHub-style dark theme and Barbie Pink accents.

### Quick Start

```bash
# Install dependencies
pip install markdown>=3.5.0 Pygments>=2.17.0

# Build all documentation
python3 scripts/build_markdown_docs.py --organize --verbose

# Clean and rebuild everything
python3 scripts/build_markdown_docs.py --clean --organize --verbose

# View documentation
open docs/index.html  # macOS
xdg-open docs/index.html  # Linux
start docs/index.html  # Windows
```

### Build Script Options

**build_markdown_docs.py** - Convert Markdown files to HTML

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Show detailed output with file-by-file conversion |
| `--organize` | Move documentation files to docs/ (keep README in root) |
| `--clean` | Remove all HTML files before building |
| `--output-dir DIR` | Change base output directory |

**Examples:**

```bash
# Basic conversion (in place)
python3 scripts/build_markdown_docs.py --verbose

# Build and organize into docs/ directory
python3 scripts/build_markdown_docs.py --organize --verbose

# Full clean rebuild
python3 scripts/build_markdown_docs.py --clean --organize --verbose
```

### Cleanup Script Options

**cleanup_old_docs.py** - Remove obsolete documentation HTML files

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview what would be removed (safe, default) |
| `--verbose`, `-v` | Show detailed output with file sizes |

**Examples:**

```bash
# Preview what would be removed (safe)
python3 scripts/cleanup_old_docs.py --dry-run --verbose

# Actually remove obsolete files
python3 scripts/cleanup_old_docs.py
```

### File Organization

After running `--organize`, documentation is structured as:

```
krwl-hof/
├── README.md / README.html        # Stay in root (GitHub + landing page)
├── DOCUMENTATION_BUILD.md         # Build system guide (stays in root)
└── docs/
    ├── index.html                 # Auto-generated navigation index
    ├── CHANGELOG.md / .html       # All other docs in docs/
    ├── QUICK_REFERENCE.md / .html
    └── ...
```

### Features

- ✅ **GitHub Dark Theme**: `#0d1117` background, `#c9d1d9` text
- ✅ **Barbie Pink Accents**: `#FF69B4` headings and highlights
- ✅ **Syntax Highlighting**: Code blocks with Pygments
- ✅ **Automatic Links**: Converts `.md` links to `.html` links
- ✅ **Navigation**: Every page links to Home, Docs Index, Map App
- ✅ **Responsive Design**: Mobile-first, works on all devices
- ✅ **Works Offline**: Pure HTML/CSS, no server needed (file:// protocol)
- ✅ **Auto Index**: Generates `docs/index.html` with categorized navigation

### Workflow

```bash
# 1. Edit Markdown files
vim docs/CHANGELOG.md

# 2. Build HTML
python3 scripts/build_markdown_docs.py --organize --verbose

# 3. View in browser
open docs/index.html

# 4. Commit both .md and .html
git add docs/
git commit -m "📄 Update documentation"
```

### Documentation

See [DOCUMENTATION_BUILD.md](../DOCUMENTATION_BUILD.md) for complete documentation including:
- Full feature list and benefits
- CI/CD integration examples
- Troubleshooting guide
- Technical details
- KISS principle compliance

## See Also
- Test scripts: [`../tests/`](../tests/)
- Main application: [`../src/event_manager.py`](../src/event_manager.py)
