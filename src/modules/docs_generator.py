"""
Documentation Generator Module

Generates styled HTML documentation from Markdown files in docs/ directory.
Uses the application's Barbie Pink color scheme and Lucide icons.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import markdown
from pygments.formatters import HtmlFormatter

# Configure module logger
logger = logging.getLogger(__name__)


class DocsGenerator:
    """Generates styled documentation from Markdown files"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.docs_source_path = self.base_path / 'docs'
        self.docs_output_path = self.base_path / 'public' / 'docs'
        self.assets_path = self.base_path / 'assets'
        self.config_path = self.base_path / 'config.json'
        
        # Ensure output directory exists
        self.docs_output_path.mkdir(parents=True, exist_ok=True)
        
        # Load config for design tokens
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        # Configure Markdown processor
        self.md = markdown.Markdown(extensions=[
            'extra',  # Tables, fenced code blocks, etc.
            'codehilite',  # Syntax highlighting
            'toc',  # Table of contents
            'meta',  # Metadata
            'sane_lists'  # Better list handling
        ])
    
    def get_doc_files(self) -> List[Path]:
        """Get all Markdown files in docs directory"""
        return sorted(self.docs_source_path.glob('*.md'))
    
    def generate_docs_css(self) -> str:
        """Generate CSS for documentation using design tokens"""
        colors = self.config['design']['colors']
        typography = self.config['design']['typography']
        spacing = self.config['design']['spacing']
        borders = self.config['design']['borders']
        shadows = self.config['design']['shadows']
        
        # Generate Pygments CSS for syntax highlighting
        formatter = HtmlFormatter(style='monokai')
        pygments_css = formatter.get_style_defs('.codehilite')
        
        css = f"""
/* Documentation Styles - Generated from config.json design tokens */

:root {{
    /* Colors from design tokens */
    --color-primary: {colors['primary']};
    --color-primary-hover: {colors['primary_hover']};
    --color-bg-primary: {colors['bg_primary']};
    --color-bg-secondary: {colors['bg_secondary']};
    --color-bg-tertiary: {colors['bg_tertiary']};
    --color-text-primary: {colors['text_primary']};
    --color-text-secondary: {colors['text_secondary']};
    --color-text-tertiary: {colors['text_tertiary']};
    --color-border-primary: {colors['border_primary']};
    --color-border-secondary: {colors['border_secondary']};
    --color-accent: {colors['accent']};
    --color-success: {colors['success']};
    --color-warning: {colors['warning']};
    --color-error: {colors['error']};
    
    /* Typography */
    --font-family-base: {typography['font_family_base']};
    --font-family-mono: {typography['font_family_mono']};
    --font-size-base: {typography['font_size_base']};
    --font-size-small: {typography['font_size_small']};
    --font-size-large: {typography['font_size_large']};
    --line-height-base: {typography['line_height_base']};
    
    /* Spacing */
    --spacing-sm: {spacing['sm']};
    --spacing-md: {spacing['md']};
    --spacing-lg: {spacing['lg']};
    --spacing-xl: {spacing['xl']};
    --spacing-xxl: {spacing['xxl']};
    
    /* Borders */
    --border-radius-small: {borders['radius_small']};
    --border-radius-medium: {borders['radius_medium']};
    --border-radius-large: {borders['radius_large']};
    
    /* Shadows */
    --shadow-small: {shadows['small']};
    --shadow-medium: {shadows['medium']};
    --shadow-large: {shadows['large']};
    --shadow-glow-primary: {shadows['glow_primary']};
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-family-base);
    background: var(--color-bg-primary);
    color: var(--color-text-primary);
    line-height: var(--line-height-base);
    font-size: var(--font-size-base);
}}

/* Layout */
.docs-container {{
    display: flex;
    min-height: 100vh;
}}

/* Sidebar Navigation */
.docs-sidebar {{
    width: 280px;
    background: var(--color-bg-secondary);
    border-right: 1px solid var(--color-border-primary);
    padding: var(--spacing-lg);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
}}

.docs-logo {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-primary);
}}

.docs-logo-icon {{
    color: var(--color-primary);
    width: 32px;
    height: 32px;
}}

.docs-logo-text {{
    font-size: var(--font-size-large);
    font-weight: 600;
    color: var(--color-primary);
}}

.docs-nav {{
    list-style: none;
}}

.docs-nav-item {{
    margin-bottom: var(--spacing-sm);
}}

.docs-nav-link {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--color-text-secondary);
    text-decoration: none;
    border-radius: var(--border-radius-small);
    transition: all 0.2s ease;
}}

.docs-nav-link:hover {{
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
}}

.docs-nav-link.active {{
    background: var(--color-bg-tertiary);
    color: var(--color-primary);
    border-left: 2px solid var(--color-primary);
}}

.docs-nav-icon {{
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}}

/* Main Content */
.docs-main {{
    margin-left: 280px;
    flex: 1;
    padding: var(--spacing-xl);
    max-width: 900px;
}}

.docs-content {{
    background: var(--color-bg-secondary);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-xxl);
    box-shadow: var(--shadow-medium);
}}

/* Back to App Link */
.back-to-app {{
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--color-accent);
    text-decoration: none;
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-small);
    transition: color 0.2s ease;
}}

.back-to-app:hover {{
    color: var(--color-primary);
}}

/* Typography */
.docs-content h1 {{
    color: var(--color-primary);
    font-size: 2.5rem;
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 2px solid var(--color-border-primary);
}}

.docs-content h2 {{
    color: var(--color-text-primary);
    font-size: 2rem;
    margin-top: var(--spacing-xl);
    margin-bottom: var(--spacing-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}}

.docs-content h2::before {{
    content: '';
    width: 4px;
    height: 1.5rem;
    background: var(--color-primary);
    border-radius: 2px;
}}

.docs-content h3 {{
    color: var(--color-text-primary);
    font-size: 1.5rem;
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
}}

.docs-content h4 {{
    color: var(--color-text-secondary);
    font-size: 1.25rem;
    margin-top: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
}}

.docs-content p {{
    margin-bottom: var(--spacing-md);
    color: var(--color-text-primary);
}}

.docs-content a {{
    color: var(--color-accent);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s ease;
}}

.docs-content a:hover {{
    border-bottom-color: var(--color-accent);
}}

/* Lists */
.docs-content ul,
.docs-content ol {{
    margin-bottom: var(--spacing-md);
    padding-left: var(--spacing-xl);
}}

.docs-content li {{
    margin-bottom: var(--spacing-sm);
    color: var(--color-text-primary);
}}

/* Code */
.docs-content code {{
    font-family: var(--font-family-mono);
    background: var(--color-bg-tertiary);
    padding: 2px 6px;
    border-radius: var(--border-radius-small);
    font-size: var(--font-size-small);
    color: var(--color-primary);
}}

.docs-content pre {{
    background: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-primary);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    overflow-x: auto;
}}

.docs-content pre code {{
    background: none;
    padding: 0;
    color: var(--color-text-primary);
}}

/* Tables */
.docs-content table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: var(--spacing-md);
    background: var(--color-bg-tertiary);
    border-radius: var(--border-radius-medium);
    overflow: hidden;
}}

.docs-content th {{
    background: var(--color-bg-primary);
    color: var(--color-primary);
    padding: var(--spacing-md);
    text-align: left;
    font-weight: 600;
}}

.docs-content td {{
    padding: var(--spacing-md);
    border-top: 1px solid var(--color-border-primary);
    color: var(--color-text-primary);
}}

.docs-content tr:hover td {{
    background: var(--color-bg-secondary);
}}

/* Blockquotes */
.docs-content blockquote {{
    border-left: 4px solid var(--color-primary);
    padding-left: var(--spacing-md);
    margin: var(--spacing-md) 0;
    color: var(--color-text-secondary);
    font-style: italic;
    background: var(--color-bg-tertiary);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-small);
}}

/* Horizontal Rule */
.docs-content hr {{
    border: none;
    height: 1px;
    background: var(--color-border-primary);
    margin: var(--spacing-lg) 0;
}}

/* Syntax Highlighting */
{pygments_css}

.codehilite {{
    background: var(--color-bg-tertiary) !important;
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}}

/* Mobile Responsiveness */
@media (max-width: 768px) {{
    .docs-sidebar {{
        display: none;
    }}
    
    .docs-main {{
        margin-left: 0;
        padding: var(--spacing-md);
    }}
    
    .docs-content {{
        padding: var(--spacing-md);
    }}
    
    .docs-content h1 {{
        font-size: 2rem;
    }}
    
    .docs-content h2 {{
        font-size: 1.5rem;
    }}
}}

/* Scrollbar Styling */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--color-bg-primary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--color-border-primary);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--color-primary);
}}
"""
        return css
    
    def get_icon_for_file(self, filename: str) -> str:
        """Get appropriate emoji icon for documentation file"""
        icon_map = {
            'CHANGELOG': '📋',
            'COLOR_SCHEME': '🎨',
            'DEPENDENCY': '📦',
            'EASY': '⚡',
            'IMPLEMENTATION': '✅',
            'KISS': '💖',
            'LEAFLET': '🗺️',
            'LUCIDE': '😊',
            'MARKDOWN': '📝',
            'PROOF': '🛡️',
            'PYTHON': '🐍',
            'QUICK_REFERENCE': '🔖',
            'SSG': '📁',
        }
        
        for key, icon in icon_map.items():
            if key in filename.upper():
                return icon
        
        return '📄'  # Default icon
    
    def generate_navigation(self, doc_files: List[Path], current_file: Path = None) -> str:
        """Generate navigation HTML with emoji icons"""
        nav_items = []
        
        for doc_file in doc_files:
            filename = doc_file.stem
            icon = self.get_icon_for_file(filename)
            # Convert filename to title (e.g., CHANGELOG -> Changelog)
            title = filename.replace('_', ' ').title()
            output_filename = f"{filename}.html"
            
            active_class = ' active' if current_file and doc_file == current_file else ''
            
            nav_items.append(f'''
            <li class="docs-nav-item">
                <a href="{output_filename}" class="docs-nav-link{active_class}">
                    <span class="docs-nav-icon">{icon}</span>
                    <span>{title}</span>
                </a>
            </li>
            ''')
        
        return '\n'.join(nav_items)
    
    def generate_html(self, doc_file: Path, content_html: str, navigation: str) -> str:
        """Generate complete HTML document"""
        filename = doc_file.stem
        title = filename.replace('_', ' ').title()
        css = self.generate_docs_css()
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - KRWL HOF Documentation</title>
    <meta name="description" content="KRWL HOF Community Events Documentation">
    <style>
{css}
    </style>
</head>
<body>
    <div class="docs-container">
        <!-- Sidebar Navigation -->
        <nav class="docs-sidebar">
            <div class="docs-logo">
                <span class="docs-logo-icon">📚</span>
                <span class="docs-logo-text">Docs</span>
            </div>
            <ul class="docs-nav">
{navigation}
            </ul>
        </nav>
        
        <!-- Main Content -->
        <main class="docs-main">
            <a href="../index.html" class="back-to-app">
                <span>←</span>
                Back to App
            </a>
            <article class="docs-content">
{content_html}
            </article>
        </main>
    </div>
</body>
</html>"""
        return html
    
    def generate_index(self, doc_files: List[Path]) -> str:
        """Generate index page listing all documentation"""
        navigation = self.generate_navigation(doc_files)
        
        content_items = []
        for doc_file in doc_files:
            filename = doc_file.stem
            icon = self.get_icon_for_file(filename)
            title = filename.replace('_', ' ').title()
            output_filename = f"{filename}.html"
            
            # Read first paragraph from markdown as description
            with open(doc_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                description = ''
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        description = line.strip()[:150] + '...' if len(line.strip()) > 150 else line.strip()
                        break
            
            content_items.append(f'''
            <div style="background: var(--color-bg-tertiary); padding: var(--spacing-lg); border-radius: var(--border-radius-medium); margin-bottom: var(--spacing-md);">
                <h3 style="margin-top: 0; display: flex; align-items: center; gap: var(--spacing-sm);">
                    <span style="font-size: 24px;">{icon}</span>
                    <a href="{output_filename}" style="color: var(--color-text-primary); text-decoration: none;">{title}</a>
                </h3>
                <p style="color: var(--color-text-secondary); margin-bottom: 0;">{description}</p>
            </div>
            ''')
        
        content_html = f"""
        <h1>Documentation</h1>
        <p>Welcome to the KRWL HOF Community Events documentation. Select a topic to learn more:</p>
        {''.join(content_items)}
        """
        
        return self.generate_html(Path('index.md'), content_html, navigation)
    
    def generate_all(self):
        """Generate HTML for all Markdown documentation files"""
        logger.info("Generating documentation HTML from Markdown files...")
        
        doc_files = self.get_doc_files()
        if not doc_files:
            logger.warning("No documentation files found in docs/ directory")
            return
        
        logger.info(f"Found {len(doc_files)} documentation files")
        
        # Generate navigation HTML (same for all pages)
        navigation = self.generate_navigation(doc_files)
        
        # Generate each documentation page
        for doc_file in doc_files:
            logger.info(f"Processing {doc_file.name}...")
            
            # Read and convert Markdown to HTML
            with open(doc_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Reset markdown processor for new document
            self.md.reset()
            content_html = self.md.convert(markdown_content)
            
            # Generate navigation with current file highlighted
            current_nav = self.generate_navigation(doc_files, doc_file)
            
            # Generate complete HTML
            html = self.generate_html(doc_file, content_html, current_nav)
            
            # Write to output
            output_file = self.docs_output_path / f"{doc_file.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Generated {output_file}")
        
        # Generate index page
        logger.info("Generating documentation index...")
        index_html = self.generate_index(doc_files)
        index_file = self.docs_output_path / 'index.html'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        logger.info(f"Generated {index_file}")
        
        logger.info(f"Documentation generation complete! {len(doc_files)} pages created.")


def main():
    """Command-line interface for docs generator"""
    import sys
    import os
    
    # Get base path
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Generate documentation
    generator = DocsGenerator(base_path)
    generator.generate_all()


if __name__ == '__main__':
    main()
