#!/usr/bin/env python3
"""
Markdown to HTML Documentation Builder

Converts all Markdown files to styled HTML with GitHub-style dark theme and
Barbie Pink accents. Optionally organizes files into docs/ directory.

Features:
- GitHub-style dark theme (#0d1117 background, #c9d1d9 text)
- Barbie Pink (#FF69B4) headings and accents
- Syntax highlighting for code blocks
- Automatic link conversion (.md → .html)
- Navigation with links to key pages
- Source file information and timestamps
- Responsive design for mobile and desktop
- Works with file:// protocol (no server needed)

Usage:
    # Basic conversion
    python3 scripts/build_markdown_docs.py --verbose

    # Build and organize files into docs/
    python3 scripts/build_markdown_docs.py --organize --verbose

    # Clean and rebuild everything
    python3 scripts/build_markdown_docs.py --clean --organize --verbose
"""

import argparse
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


def get_html_template():
    """Return the HTML template with GitHub dark theme and Barbie Pink accents"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* GitHub Dark Theme with Barbie Pink Accents */
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            background: #0d1117;
            color: #c9d1d9;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            line-height: 1.25;
            color: #FF69B4;
        }}
        
        h1 {{ 
            font-size: 2.5em; 
            border-bottom: 2px solid #FF69B4; 
            padding-bottom: 0.3em;
            margin-bottom: 1.5rem;
        }}
        
        h2 {{ 
            font-size: 1.75em; 
            border-bottom: 1px solid #21262d; 
            padding-bottom: 0.3em; 
        }}
        
        h3 {{ font-size: 1.5em; }}
        h4 {{ font-size: 1.25em; }}
        h5 {{ font-size: 1.1em; }}
        h6 {{ font-size: 1em; }}
        
        /* Links */
        a {{ 
            color: #58a6ff; 
            text-decoration: none; 
        }}
        
        a:hover {{ 
            text-decoration: underline; 
        }}
        
        /* Navigation */
        .nav {{
            background: #161b22;
            padding: 1rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            border-left: 4px solid #FF69B4;
        }}
        
        .nav-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .nav-links a {{
            padding: 0.5rem 1rem;
            background: #21262d;
            border-radius: 6px;
            border: 1px solid #30363d;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        
        .nav-links a:hover {{
            background: #30363d;
            border-color: #FF69B4;
            transform: translateY(-2px);
            text-decoration: none;
        }}
        
        /* Code */
        code {{
            background: #161b22;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 85%;
            color: #79c0ff;
        }}
        
        pre {{
            background: #161b22;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 1rem 0;
            border: 1px solid #30363d;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #c9d1d9;
        }}
        
        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            overflow-x: auto;
            display: block;
        }}
        
        thead {{
            background: #161b22;
        }}
        
        th {{
            color: #FF69B4;
            font-weight: 600;
            text-align: left;
            padding: 0.75rem;
            border: 1px solid #30363d;
        }}
        
        td {{
            padding: 0.75rem;
            border: 1px solid #30363d;
        }}
        
        tr:nth-child(even) {{
            background: #0d1117;
        }}
        
        tr:hover {{
            background: #161b22;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        li {{
            margin: 0.5rem 0;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 4px solid #FF69B4;
            padding-left: 1rem;
            margin: 1rem 0;
            color: #8b949e;
            font-style: italic;
        }}
        
        /* Horizontal Rule */
        hr {{
            border: none;
            border-top: 1px solid #21262d;
            margin: 2rem 0;
        }}
        
        /* Paragraphs */
        p {{
            margin: 1rem 0;
        }}
        
        /* Images */
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            margin: 1rem 0;
        }}
        
        /* Source Info */
        .source-info {{
            background: #161b22;
            padding: 1rem;
            border-radius: 6px;
            margin: 1.5rem 0;
            font-size: 0.9em;
            color: #8b949e;
            border-left: 4px solid #30363d;
        }}
        
        .source-info strong {{
            color: #c9d1d9;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #30363d;
            color: #8b949e;
            font-size: 0.9em;
            text-align: center;
        }}
        
        /* Mobile Responsive */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 2em;
            }}
            
            h2 {{
                font-size: 1.5em;
            }}
            
            .nav-links {{
                flex-direction: column;
            }}
            
            .nav-links a {{
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-links">
            <a href="{home_link}">🏠 Home</a>
            <a href="{docs_index_link}">📖 Docs Index</a>
            <a href="{map_link}">🗺️ Map App</a>
            {related_links}
        </div>
    </nav>
    
    <main>
        {content}
    </main>
    
    <div class="source-info">
        <strong>📄 Source:</strong> <code>{source_file}</code><br>
        <strong>⏰ Generated:</strong> {timestamp}
    </div>
    
    <div class="footer">
        <p><strong>KRWL HOF Community Events</strong> - Documentation</p>
        <p>📍 Built with Leaflet.js | 🎨 Icons by Lucide | 💖 Barbie Pink Theme</p>
    </div>
</body>
</html>'''


def convert_md_links_to_html(content):
    """Convert Markdown links (.md) to HTML links (.html)"""
    # Match [text](link.md) or [text](path/to/link.md) and convert to .html
    pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
    
    def replace_link(match):
        text = match.group(1)
        link = match.group(2)
        html_link = link.replace('.md', '.html')
        return f'[{text}]({html_link})'
    
    return re.sub(pattern, replace_link, content)


def get_related_links(md_file, is_in_docs=False):
    """Generate related links based on common documentation files"""
    related = []
    
    # Common documentation files
    common_docs = {
        'README': ('📖', 'README'),
        'CHANGELOG': ('📝', 'Changelog'),
        'QUICK_REFERENCE': ('⚡', 'Quick Ref'),
    }
    
    current_name = Path(md_file).stem
    
    for doc_name, (emoji, label) in common_docs.items():
        if doc_name != current_name:
            if is_in_docs:
                link = f'{doc_name}.html'
            else:
                link = f'docs/{doc_name}.html'
            related.append(f'<a href="{link}">{emoji} {label}</a>')
    
    return '\n            '.join(related) if related else ''


def convert_markdown_to_html(md_file, output_file=None, verbose=False):
    """Convert a Markdown file to HTML"""
    try:
        import markdown
        from pygments.formatters import HtmlFormatter
    except ImportError:
        print("❌ Error: Required packages not installed")
        print("   Run: pip install markdown>=3.5.0 Pygments>=2.17.0")
        return False
    
    if verbose:
        print(f"  Converting: {md_file}")
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert .md links to .html
    md_content = convert_md_links_to_html(md_content)
    
    # Convert to HTML
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'codehilite',
        'tables',
        'toc',
        'nl2br',
    ])
    html_content = md.convert(md_content)
    
    # Determine paths
    md_path = Path(md_file)
    
    if output_file is None:
        output_file = md_path.with_suffix('.html')
    
    output_path = Path(output_file)
    is_in_docs = 'docs' in str(output_path)
    
    # Calculate relative links
    if is_in_docs:
        home_link = '../README.html'
        docs_index_link = 'index.html'
        map_link = '../static/index.html'
    else:
        home_link = 'README.html'
        docs_index_link = 'docs/index.html'
        map_link = 'static/index.html'
    
    # Get title from first h1 or filename
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem.replace('_', ' ').title()
    
    # Generate related links
    related_links = get_related_links(md_file, is_in_docs)
    
    # Build final HTML
    template = get_html_template()
    final_html = template.format(
        title=title,
        content=html_content,
        source_file=str(md_path),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        home_link=home_link,
        docs_index_link=docs_index_link,
        map_link=map_link,
        related_links=related_links
    )
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    if verbose:
        print(f"    → {output_file}")
    
    return True


def generate_docs_index(docs_dir, verbose=False):
    """Generate docs/index.html with categorized navigation"""
    if verbose:
        print("\n📑 Generating docs/index.html...")
    
    docs_path = Path(docs_dir)
    
    # Find all HTML files (except index.html)
    html_files = [f for f in docs_path.glob('*.html') if f.name != 'index.html']
    
    # Categorize files
    categories = {
        'Main Documentation': [],
        'Marker & Icon Design': [],
        'Development': [],
        'Other': []
    }
    
    for html_file in sorted(html_files):
        name = html_file.stem
        link = html_file.name
        
        # Read title from HTML if possible
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                title_match = re.search(r'<h1[^>]*>(.+?)</h1>', content)
                title = re.sub(r'<[^>]+>', '', title_match.group(1)) if title_match else name.replace('_', ' ').title()
        except:
            title = name.replace('_', ' ').title()
        
        # Categorize
        if any(x in name.upper() for x in ['README', 'CHANGELOG', 'QUICK_REFERENCE']):
            emoji = '📖' if 'README' in name else '📝' if 'CHANGELOG' in name else '⚡'
            categories['Main Documentation'].append((emoji, title, link))
        elif any(x in name.upper() for x in ['MARKER', 'ICON', 'LUCIDE', 'UNIFIED', 'DESIGN']):
            emoji = '🎨'
            categories['Marker & Icon Design'].append((emoji, title, link))
        elif any(x in name.upper() for x in ['TEST', 'SCRIPT', 'TEMPLATE']):
            emoji = '🛠️'
            categories['Development'].append((emoji, title, link))
        else:
            emoji = '📄'
            categories['Other'].append((emoji, title, link))
    
    # Build HTML content
    content_parts = ['<h1>📚 Documentation Index</h1>']
    content_parts.append('<p>Browse all documentation files organized by category.</p>')
    
    for category, files in categories.items():
        if not files:
            continue
        
        content_parts.append(f'<h2>{category}</h2>')
        content_parts.append('<ul>')
        
        for emoji, title, link in files:
            content_parts.append(f'  <li><a href="{link}">{emoji} {title}</a></li>')
        
        content_parts.append('</ul>')
    
    html_content = '\n'.join(content_parts)
    
    # Generate full HTML
    template = get_html_template()
    final_html = template.format(
        title='Documentation Index',
        content=html_content,
        source_file='Auto-generated from all documentation files',
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        home_link='../README.html',
        docs_index_link='index.html',
        map_link='../static/index.html',
        related_links=''
    )
    
    # Write index
    index_path = docs_path / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    if verbose:
        print(f"  ✓ Generated: {index_path}")


def find_markdown_files(base_dir):
    """Find all Markdown files in the repository"""
    base_path = Path(base_dir)
    md_files = []
    
    # Find all .md files, excluding .git and node_modules
    for md_file in base_path.rglob('*.md'):
        # Skip hidden directories and special directories
        if any(part.startswith('.') for part in md_file.parts):
            continue
        if 'node_modules' in md_file.parts:
            continue
        
        md_files.append(md_file)
    
    return sorted(md_files)


def organize_files(base_dir, verbose=False):
    """Move documentation files to docs/ directory (except root README)"""
    if verbose:
        print("\n📁 Organizing files into docs/ directory...")
    
    base_path = Path(base_dir)
    docs_path = base_path / 'docs'
    docs_path.mkdir(exist_ok=True)
    
    moved_count = 0
    
    # Find all .md and .html files in root
    for ext in ['*.md', '*.html']:
        for file in base_path.glob(ext):
            # Keep README.md and README.html in root
            if file.name in ['README.md', 'README.html']:
                if verbose:
                    print(f"  ⏭️  Skipping (keep in root): {file.name}")
                continue
            
            # Skip DOCUMENTATION_BUILD.md (new file we'll create)
            if file.name == 'DOCUMENTATION_BUILD.md':
                if verbose:
                    print(f"  ⏭️  Skipping (keep in root): {file.name}")
                continue
            
            # Move to docs/
            dest = docs_path / file.name
            if verbose:
                print(f"  📦 Moving: {file.name} → docs/")
            shutil.move(str(file), str(dest))
            moved_count += 1
    
    if verbose:
        print(f"\n  ✓ Moved {moved_count} files to docs/")


def clean_html_files(base_dir, verbose=False):
    """Remove all generated HTML files"""
    if verbose:
        print("\n🧹 Cleaning old HTML files...")
    
    base_path = Path(base_dir)
    removed_count = 0
    
    # Remove HTML files from root (except README.html)
    for html_file in base_path.glob('*.html'):
        if html_file.name != 'README.html':
            if verbose:
                print(f"  🗑️  Removing: {html_file}")
            html_file.unlink()
            removed_count += 1
    
    # Remove all HTML files from docs/
    docs_path = base_path / 'docs'
    if docs_path.exists():
        for html_file in docs_path.glob('*.html'):
            if verbose:
                print(f"  🗑️  Removing: {html_file}")
            html_file.unlink()
            removed_count += 1
    
    if verbose:
        print(f"  ✓ Removed {removed_count} HTML files")


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to styled HTML documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic conversion
  python3 scripts/build_markdown_docs.py --verbose

  # Build and organize files into docs/
  python3 scripts/build_markdown_docs.py --organize --verbose

  # Clean and rebuild everything
  python3 scripts/build_markdown_docs.py --clean --organize --verbose
        '''
    )
    parser.add_argument(
        '--organize',
        action='store_true',
        help='Move documentation files to docs/ directory (keep README in root)'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove all HTML files before building'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Base output directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Get base directory (repository root)
    script_path = Path(__file__).resolve()
    base_dir = script_path.parent.parent
    
    print("=" * 70)
    print("📄 Markdown to HTML Documentation Builder")
    print("=" * 70)
    print()
    
    # Check dependencies
    try:
        import markdown
        import pygments
    except ImportError:
        print("❌ Error: Required packages not installed")
        print()
        print("Install dependencies with:")
        print("  pip install markdown>=3.5.0 Pygments>=2.17.0")
        print()
        return 1
    
    # Clean if requested
    if args.clean:
        clean_html_files(base_dir, args.verbose)
        print()
    
    # Find all Markdown files
    if args.verbose:
        print("🔍 Scanning for Markdown files...")
    
    md_files = find_markdown_files(base_dir)
    
    if args.verbose:
        print(f"  Found {len(md_files)} Markdown files")
        print()
    
    # Convert files
    print("🔄 Converting Markdown to HTML...")
    success_count = 0
    
    for md_file in md_files:
        # Convert to HTML in place
        if convert_markdown_to_html(md_file, verbose=args.verbose):
            success_count += 1
    
    print(f"\n✓ Converted {success_count} of {len(md_files)} files")
    
    # Organize files if requested
    if args.organize:
        organize_files(base_dir, args.verbose)
    
    # Generate docs index
    docs_dir = base_dir / 'docs'
    if docs_dir.exists():
        generate_docs_index(docs_dir, args.verbose)
    
    print()
    print("=" * 70)
    print("✅ Documentation build complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Open docs/index.html in your browser")
    print("  - Check README.html for the landing page")
    print("  - Verify navigation works between pages")
    print()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
