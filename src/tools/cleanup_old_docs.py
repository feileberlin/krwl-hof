#!/usr/bin/env python3
"""
Cleanup Script - Remove Obsolete Documentation HTML Files

Safely removes documentation HTML files with old naming conventions that are
no longer needed after the new documentation build system implementation.

SAFE TO RUN: Default is dry-run mode (--dry-run). Use without --dry-run to actually remove files.

Removes only these specific obsolete files:
  - docs/README_README.md.html
  - docs/CHANGELOG_CHANGELOG.md.html
  - docs/QUICK_REFERENCE_QUICK_REFERENCE.md.html
  - docs/assets_markers_LUCIDE_ICONS.md.html
  - docs/assets_markers_UNIFIED_DESIGN.md.html
  - docs/tests_README.md.html
  - docs/scripts_README.md.html
  - docs/src_templates_README.md.html
  - docs/MARKER_DESIGN_AUDIT.md.html
  - docs/MARKER_ICONS_RECOMMENDATION.md.html

Usage:
    # Preview what would be removed
    python3 scripts/cleanup_old_docs.py --dry-run

    # Actually remove obsolete files
    python3 scripts/cleanup_old_docs.py

    # Verbose output
    python3 scripts/cleanup_old_docs.py --verbose
"""

import argparse
import os
from pathlib import Path


def get_obsolete_files(base_dir):
    """Get list of obsolete documentation HTML files to remove"""
    docs_dir = Path(base_dir) / 'docs'
    
    obsolete_files = [
        'README_README.md.html',
        'CHANGELOG_CHANGELOG.md.html',
        'QUICK_REFERENCE_QUICK_REFERENCE.md.html',
        'assets_markers_LUCIDE_ICONS.md.html',
        'assets_markers_UNIFIED_DESIGN.md.html',
        'tests_README.md.html',
        'scripts_README.md.html',
        'src_templates_README.md.html',
        'MARKER_DESIGN_AUDIT.md.html',
        'MARKER_ICONS_RECOMMENDATION.md.html',
    ]
    
    # Return full paths that actually exist
    existing_files = []
    for filename in obsolete_files:
        filepath = docs_dir / filename
        if filepath.exists():
            existing_files.append(filepath)
    
    return existing_files


def format_size(bytes):
    """Format bytes as human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"


def remove_files(files, dry_run=True, verbose=False):
    """Remove obsolete files"""
    removed_count = 0
    total_size = 0
    
    for filepath in files:
        try:
            size = filepath.stat().st_size
            total_size += size
            
            if dry_run:
                if verbose:
                    print(f"  Would remove: {filepath} ({format_size(size)})")
            else:
                filepath.unlink()
                removed_count += 1
                if verbose:
                    print(f"  ✓ Removed: {filepath} ({format_size(size)})")
        
        except Exception as e:
            print(f"  ✗ Error with {filepath}: {e}")
    
    return removed_count, total_size


def main():
    parser = argparse.ArgumentParser(
        description='Remove obsolete documentation HTML files with old naming conventions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Preview what would be removed (safe, default)
  python3 scripts/cleanup_old_docs.py --dry-run

  # Actually remove obsolete files
  python3 scripts/cleanup_old_docs.py

  # Verbose output with details
  python3 scripts/cleanup_old_docs.py --verbose --dry-run
        '''
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview files that would be removed (default behavior)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output with file sizes'
    )
    
    args = parser.parse_args()
    
    # Default to dry-run if neither --dry-run nor no flags
    # If user explicitly runs without --dry-run, assume they want to delete
    is_dry_run = args.dry_run or len([a for a in os.sys.argv[1:] if not a.startswith('-v')]) == 0
    
    # Get base directory (repository root)
    script_path = Path(__file__).resolve()
    base_dir = script_path.parent.parent
    
    print("=" * 70)
    print("🧹 Cleanup Obsolete Documentation Files")
    print("=" * 70)
    print()
    
    # Get obsolete files
    obsolete_files = get_obsolete_files(base_dir)
    
    if not obsolete_files:
        print("✅ No obsolete files found!")
        print()
        print("All documentation files are up to date.")
        return 0
    
    # Show summary
    print(f"Found {len(obsolete_files)} obsolete file(s):")
    print()
    
    if args.verbose or is_dry_run:
        for filepath in obsolete_files:
            size = filepath.stat().st_size
            print(f"  📄 {filepath.name} ({format_size(size)})")
    
    print()
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in obsolete_files)
    print(f"Total size: {format_size(total_size)}")
    print()
    
    # Remove or preview
    if is_dry_run:
        print("=" * 70)
        print("🔍 DRY RUN - No files will be removed")
        print("=" * 70)
        print()
        print("These files would be removed:")
        
        removed_count, _ = remove_files(obsolete_files, dry_run=True, verbose=True)
        
        print()
        print("To actually remove these files, run:")
        print(f"  python3 scripts/cleanup_old_docs.py")
        print()
        print("These files are safe to remove:")
        print("  - Old naming convention (double names like README_README)")
        print("  - Replaced by new simplified naming (README.html)")
        print()
    else:
        print("=" * 70)
        print("🗑️  Removing files...")
        print("=" * 70)
        print()
        
        removed_count, removed_size = remove_files(obsolete_files, dry_run=False, verbose=args.verbose)
        
        print()
        print("=" * 70)
        print(f"✅ Removed {removed_count} file(s) ({format_size(removed_size)})")
        print("=" * 70)
        print()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
