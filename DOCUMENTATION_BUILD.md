# Documentation Build System

## Overview

The KRWL HOF project uses an automated Markdown-to-HTML build system that converts all documentation files to styled HTML with a consistent GitHub-style dark theme and Barbie Pink accents. This ensures documentation is browsable on any platform, including static hosting, GitHub Pages, and local file systems (file:// protocol).

## Why This System Exists

### The Problem
- **Limited Markdown rendering**: Many hosting platforms (static servers, file:// protocol) don't render Markdown
- **Inconsistent styling**: Raw Markdown varies between viewers
- **Navigation difficulties**: No easy way to browse between documents
- **Accessibility**: Command-line tools can't read Markdown files easily

### The Solution
- **Universal HTML**: Works everywhere - browsers, file systems, any hosting platform
- **Consistent styling**: GitHub-style dark theme with Barbie Pink (#FF69B4) accents
- **Easy navigation**: Every page has links to key documents and the documentation index
- **Professional appearance**: Syntax highlighting, responsive design, mobile-friendly
- **No server required**: Pure HTML/CSS, works with file:// protocol

## Directory Structure

After building documentation, the structure looks like this:

```
krwl-hof/
├── README.md                      # Stays in root (for GitHub)
├── README.html                    # Stays in root (web landing page)
├── DOCUMENTATION_BUILD.md         # This guide (stays in root)
│
├── docs/                          # All other documentation
│   ├── index.html                 # Auto-generated navigation index
│   ├── CHANGELOG.md               # Documentation markdown files
│   ├── CHANGELOG.html             # Generated HTML files
│   ├── QUICK_REFERENCE.md
│   ├── QUICK_REFERENCE.html
│   ├── MARKER_DESIGN_AUDIT.md
│   ├── MARKER_DESIGN_AUDIT.html
│   └── ...                        # Other documentation
│
├── scripts/
│   ├── build_markdown_docs.py     # Main build script
│   └── cleanup_old_docs.py        # Remove obsolete files
│
└── requirements.txt               # Includes markdown>=3.5.0, Pygments>=2.17.0
```

### File Organization Rules

**Stays in Root:**
- `README.md` / `README.html` - GitHub compatibility and web landing page
- `DOCUMENTATION_BUILD.md` - This build guide

**Goes to docs/:**
- All other `.md` and `.html` documentation files
- `CHANGELOG.md`, `QUICK_REFERENCE.md`, design documents, etc.
- Subdirectory documentation (tests/README.md, scripts/README.md, etc.)

## Quick Start

### 1. Install Dependencies

```bash
pip install markdown>=3.5.0 Pygments>=2.17.0
```

Dependencies are listed in `requirements.txt`.

### 2. Build Documentation

```bash
# Basic build - convert all .md files to .html in place
python3 scripts/build_markdown_docs.py --verbose

# Build and organize - move docs to docs/ directory (recommended)
python3 scripts/build_markdown_docs.py --organize --verbose

# Clean rebuild - remove old HTML and rebuild everything
python3 scripts/build_markdown_docs.py --clean --organize --verbose
```

### 3. View Documentation

Open in your browser:
```bash
# macOS
open docs/index.html

# Linux
xdg-open docs/index.html

# Windows
start docs/index.html
```

Or simply double-click `docs/index.html` in your file manager.

## Build Workflow

### Typical Development Workflow

```
┌─────────────────┐
│  Edit README.md │  1. Edit Markdown files
│  Edit DOCS/*.md │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build HTML     │  2. Run build script
│  python3 build  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  View in        │  3. Review in browser
│  Browser        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Commit Both    │  4. Commit .md and .html
│  .md and .html  │
└─────────────────┘
```

### Commands Summary

```bash
# Full rebuild with organization
python3 scripts/build_markdown_docs.py --clean --organize --verbose

# Quick rebuild (no reorganization)
python3 scripts/build_markdown_docs.py --verbose

# Just organize existing files
python3 scripts/build_markdown_docs.py --organize

# Clean old HTML files
python3 scripts/build_markdown_docs.py --clean
```

## Build Options

### Main Script: `build_markdown_docs.py`

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Show detailed output with file-by-file conversion |
| `--organize` | Move documentation files to docs/ (keep README in root) |
| `--clean` | Remove all HTML files before building |
| `--output-dir DIR` | Change base output directory (default: repository root) |

### Cleanup Script: `cleanup_old_docs.py`

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview what would be removed (safe, default) |
| `--verbose`, `-v` | Show detailed output with file sizes |

Removes obsolete HTML files with old naming conventions:
- `docs/README_README.md.html` → now just `README.html`
- `docs/CHANGELOG_CHANGELOG.md.html` → now just `CHANGELOG.html`
- etc.

## Features

### HTML Styling

Every generated HTML page includes:

- **GitHub Dark Theme**: `#0d1117` background, `#c9d1d9` text
- **Barbie Pink Accents**: `#FF69B4` for headings, borders, highlights
- **Responsive Design**: Mobile-first, adapts to all screen sizes
- **Syntax Highlighting**: Code blocks with Pygments (Python, JS, Shell, etc.)
- **Navigation Bar**: Links to Home, Docs Index, Map App, Related Docs
- **Source Information**: Shows source .md file and generation timestamp
- **Professional Layout**: Consistent spacing, typography, and structure

### Automatic Link Conversion

The build system automatically converts Markdown links to HTML:
- `[Text](file.md)` → `[Text](file.html)`
- `[Text](../path/file.md)` → `[Text](../path/file.html)`

### Documentation Index

The `docs/index.html` file is auto-generated with:
- **Categorized navigation**: Main docs, design docs, development docs
- **Emoji icons**: Visual distinction between document types
- **Alphabetical sorting**: Easy to find specific documents
- **Smart categorization**: Based on filename patterns

Categories:
- 📖 **Main Documentation**: README, CHANGELOG, QUICK_REFERENCE
- 🎨 **Marker & Icon Design**: Design system, icon docs
- 🛠️ **Development**: Tests, scripts, templates
- 📄 **Other**: Everything else

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Documentation

on:
  push:
    branches: [main]
    paths:
      - '**.md'
      - 'scripts/build_markdown_docs.py'

jobs:
  build-docs:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Install dependencies
        run: |
          pip install markdown>=3.5.0 Pygments>=2.17.0
      
      - name: Build documentation
        run: |
          python3 scripts/build_markdown_docs.py --organize --verbose
      
      - name: Commit changes
        run: |
          git config --local user.name "GitHub Actions"
          git config --local user.email "actions@github.com"
          git add docs/ README.html
          git diff --quiet && git diff --staged --quiet || git commit -m "📄 Update documentation HTML"
          git push
```

### Manual Build Before Push

```bash
# Before committing Markdown changes
python3 scripts/build_markdown_docs.py --organize --verbose

# Stage both .md and .html files
git add docs/*.md docs/*.html README.html

# Commit
git commit -m "📄 Update documentation"
git push
```

## Troubleshooting

### Issue: Missing Dependencies

**Error:**
```
❌ Error: Required packages not installed
```

**Solution:**
```bash
pip install markdown>=3.5.0 Pygments>=2.17.0
```

### Issue: Files Not Moving to docs/

**Problem:** Files stay in root after `--organize`

**Solution:** 
- README.md and README.html intentionally stay in root
- DOCUMENTATION_BUILD.md stays in root
- All other files should move
- Check output with `--verbose` flag

### Issue: Links Broken After Organization

**Problem:** Links between documents don't work

**Solution:**
- Use relative paths in Markdown: `[link](file.md)` not `/file.md`
- The build script automatically converts `.md` → `.html`
- Navigation links are automatically adjusted based on file location

### Issue: Syntax Highlighting Not Working

**Problem:** Code blocks appear as plain text

**Solution:**
```bash
# Ensure Pygments is installed
pip install Pygments>=2.17.0

# Rebuild
python3 scripts/build_markdown_docs.py --clean --verbose
```

### Issue: Old HTML Files Remain

**Problem:** Obsolete HTML files with old naming

**Solution:**
```bash
# Preview what would be removed
python3 scripts/cleanup_old_docs.py --dry-run --verbose

# Remove obsolete files
python3 scripts/cleanup_old_docs.py
```

## Benefits

### ✅ Universal Compatibility
- Works on any platform (macOS, Linux, Windows)
- No server required (file:// protocol works)
- Compatible with all hosting (GitHub Pages, Netlify, Vercel, etc.)

### ✅ Professional Appearance
- Consistent GitHub-style dark theme
- Beautiful syntax highlighting
- Responsive mobile design
- Professional typography

### ✅ Easy Navigation
- Every page links to key documents
- Auto-generated documentation index
- Breadcrumb navigation
- Related document suggestions

### ✅ Low Maintenance
- Single command to rebuild all docs
- Automatic link conversion
- Auto-generated index
- No manual HTML editing needed

### ✅ Developer Friendly
- Edit Markdown as usual
- Build with one command
- Preview instantly in browser
- Works with all editors

### ✅ Future Proof
- Pure HTML/CSS (no JavaScript required)
- No external dependencies at runtime
- Works offline
- Archive-friendly

## Technical Details

### Dependencies

**Build Time:**
- `markdown>=3.5.0` - Markdown to HTML conversion
- `Pygments>=2.17.0` - Syntax highlighting for code blocks

**Runtime:**
- None! Pure HTML/CSS

### File Processing

1. **Scan**: Find all `.md` files (excluding `.git`, `node_modules`, hidden directories)
2. **Convert**: Transform Markdown to HTML with extensions:
   - `fenced_code` - Code blocks with syntax highlighting
   - `codehilite` - Pygments integration
   - `tables` - GitHub-style tables
   - `toc` - Table of contents generation
   - `nl2br` - Newline to `<br>` conversion
3. **Template**: Wrap in full HTML template with navigation
4. **Links**: Convert all `.md` links to `.html` links
5. **Organize**: Optionally move to `docs/` directory
6. **Index**: Generate `docs/index.html` with categories

### HTML Template

Each page includes:
- Full HTML5 doctype
- Responsive viewport meta tag
- Embedded CSS (no external stylesheets)
- Navigation with relative links
- Main content area
- Source file information
- Generation timestamp
- Footer with project info

## KISS Principle Compliance

This build system follows the **Keep It Simple, Stupid** principle:

✅ **Simple**: Two Python scripts, clear purpose
✅ **Minimal Dependencies**: Only markdown + Pygments
✅ **No Complex Build Tools**: No webpack, no npm, no frameworks
✅ **Pure HTML/CSS**: No JavaScript at runtime
✅ **Standard Library First**: Uses pathlib, argparse, re
✅ **Clear Error Messages**: Helpful feedback on issues
✅ **Single Responsibility**: Each script does one thing well

## See Also

- [Scripts Documentation](scripts/README.md) - All utility scripts
- [Quick Reference](docs/QUICK_REFERENCE.md) - Common commands
- [README](README.md) - Main project documentation
- [Changelog](docs/CHANGELOG.md) - Version history

## Questions?

- Check the troubleshooting section above
- Run with `--help` flag for usage information
- Review the source code (it's well commented!)
- Check `scripts/README.md` for all available scripts
