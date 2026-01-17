#!/usr/bin/env python3
"""
CSS Linter - Simple but effective CSS validation and style checking.

Checks for:
- Syntax errors (unmatched braces, missing semicolons)
- Code quality (duplicate selectors, empty rules)
- Best practices (vendor prefixes, important overuse)
- Consistency (property order, spacing)
- KISS violations (file size, selector complexity)
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class CSSLinter:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def lint_file(self, file_path: Path) -> Dict:
        """Lint a single CSS file."""
        content = file_path.read_text()
        filename = file_path.name
        
        # Run all checks
        self.check_syntax(content, filename)
        self.check_duplicates(content, filename)
        self.check_best_practices(content, filename)
        self.check_consistency(content, filename)
        self.check_kiss(content, filename, file_path)
        
        return {
            'file': filename,
            'errors': len([e for e in self.errors if e['file'] == filename]),
            'warnings': len([w for w in self.warnings if w['file'] == filename]),
            'info': len([i for i in self.info if i['file'] == filename])
        }
    
    def check_syntax(self, content: str, filename: str):
        """Check for basic syntax errors."""
        # Remove comments first
        content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Check for unmatched braces
        open_braces = content_no_comments.count('{')
        close_braces = content_no_comments.count('}')
        if open_braces != close_braces:
            self.errors.append({
                'file': filename,
                'type': 'UNMATCHED_BRACES',
                'message': f'Unmatched braces: {open_braces} opening, {close_braces} closing'
            })
        
        # Check for properties without semicolons (simple check)
        lines = content_no_comments.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            # If line has : but no ; and not ending with { or }
            if ':' in line and not line.endswith((';', '{', '}', ',')):
                # Skip @rules and selectors
                if not line.startswith('@') and '{' not in line:
                    self.warnings.append({
                        'file': filename,
                        'line': i,
                        'type': 'MISSING_SEMICOLON',
                        'message': f'Possible missing semicolon: {line[:50]}'
                    })
    
    def check_duplicates(self, content: str, filename: str):
        """Check for duplicate selectors and properties."""
        # Remove comments
        content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Find all selector blocks
        blocks = re.findall(r'([^{}]+)\{([^{}]*)\}', content_no_comments)
        
        selector_counts = defaultdict(int)
        for selector, _ in blocks:
            selector = selector.strip()
            if selector and not selector.startswith('@'):
                selector_counts[selector] += 1
        
        # Report duplicates
        for selector, count in selector_counts.items():
            if count > 1:
                self.warnings.append({
                    'file': filename,
                    'type': 'DUPLICATE_SELECTOR',
                    'message': f'Selector "{selector[:50]}" defined {count} times'
                })
    
    def check_best_practices(self, content: str, filename: str):
        """Check for best practice violations."""
        # Remove comments
        content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Check for !important overuse
        important_count = content_no_comments.count('!important')
        if important_count > 5:
            self.warnings.append({
                'file': filename,
                'type': 'IMPORTANT_OVERUSE',
                'message': f'Too many !important declarations ({important_count})'
            })
        
        # Check for vendor prefixes (should use autoprefixer)
        vendor_prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
        for prefix in vendor_prefixes:
            count = content_no_comments.count(prefix)
            if count > 3:
                self.info.append({
                    'file': filename,
                    'type': 'VENDOR_PREFIX',
                    'message': f'Consider using autoprefixer instead of manual {prefix} ({count} uses)'
                })
        
        # Check for inline hardcoded colors (should use CSS variables)
        hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', content_no_comments)
        rgb_colors = re.findall(r'rgba?\([^)]+\)', content_no_comments)
        
        # Filter out those in comments about the palette
        if len(hex_colors) > 5:
            self.warnings.append({
                'file': filename,
                'type': 'HARDCODED_COLORS',
                'message': f'Found {len(hex_colors)} hex colors - should use CSS variables'
            })
        
        if len(rgb_colors) > 5:
            self.warnings.append({
                'file': filename,
                'type': 'HARDCODED_COLORS',
                'message': f'Found {len(rgb_colors)} rgb/rgba colors - should use CSS variables'
            })
    
    def check_consistency(self, content: str, filename: str):
        """Check for consistency issues."""
        lines = content.split('\n')
        
        # Check for mixed indentation
        tabs = sum(1 for line in lines if line.startswith('\t'))
        spaces = sum(1 for line in lines if line.startswith('    '))
        
        if tabs > 5 and spaces > 5:
            self.warnings.append({
                'file': filename,
                'type': 'MIXED_INDENTATION',
                'message': f'Mixed indentation: {tabs} tabs, {spaces} spaces'
            })
        
        # Check for trailing whitespace
        trailing_ws = sum(1 for line in lines if line.rstrip() != line and line.strip())
        if trailing_ws > 10:
            self.info.append({
                'file': filename,
                'type': 'TRAILING_WHITESPACE',
                'message': f'{trailing_ws} lines with trailing whitespace'
            })
    
    def check_kiss(self, content: str, filename: str, file_path: Path):
        """Check KISS principles."""
        # Remove comments for accurate line count
        content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        code_lines = len([l for l in content_no_comments.split('\n') if l.strip()])
        
        # Count selectors
        selectors = re.findall(r'^[^{}]+\{', content_no_comments, flags=re.MULTILINE)
        selector_count = len(selectors)
        
        # File size check
        file_size_kb = file_path.stat().st_size / 1024
        
        if code_lines > 300:
            self.errors.append({
                'file': filename,
                'type': 'FILE_TOO_LARGE',
                'message': f'File has {code_lines} code lines (max 300)'
            })
        elif code_lines > 200:
            self.warnings.append({
                'file': filename,
                'type': 'FILE_LARGE',
                'message': f'File has {code_lines} code lines (consider splitting)'
            })
        
        if selector_count > 50:
            self.errors.append({
                'file': filename,
                'type': 'TOO_MANY_SELECTORS',
                'message': f'File has {selector_count} selectors (max 50)'
            })
        elif selector_count > 30:
            self.warnings.append({
                'file': filename,
                'type': 'MANY_SELECTORS',
                'message': f'File has {selector_count} selectors (consider splitting)'
            })
        
        if file_size_kb > 50:
            self.warnings.append({
                'file': filename,
                'type': 'FILE_SIZE',
                'message': f'File size is {file_size_kb:.1f} KB (consider optimization)'
            })
    
    def print_report(self):
        """Print linting report."""
        print("=" * 60)
        print("CSS Linting Report")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                file = error['file']
                line = error.get('line', '')
                line_str = f":{line}" if line else ""
                print(f"   {file}{line_str} - {error['type']}")
                print(f"      {error['message']}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                file = warning['file']
                line = warning.get('line', '')
                line_str = f":{line}" if line else ""
                print(f"   {file}{line_str} - {warning['type']}")
                print(f"      {warning['message']}")
        
        if self.info:
            print(f"\n💡 INFO ({len(self.info)}):")
            for info in self.info[:10]:  # Limit to 10
                file = info['file']
                print(f"   {file} - {info['type']}")
                print(f"      {info['message']}")
            if len(self.info) > 10:
                print(f"   ... and {len(self.info) - 10} more")
        
        if not self.errors and not self.warnings and not self.info:
            print("\n✅ No issues found!")
        
        print("\n" + "=" * 60)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings, {len(self.info)} info")
        print("=" * 60)
        
        return len(self.errors) == 0


def main():
    """Main entry point."""
    css_dir = Path('assets/css')
    
    if not css_dir.exists():
        print(f"❌ CSS directory not found: {css_dir}")
        return 1
    
    linter = CSSLinter()
    
    css_files = sorted(css_dir.glob('*.css'))
    # Skip auto-generated files
    css_files = [f for f in css_files if f.name != 'design-tokens.css']
    
    print(f"Linting {len(css_files)} CSS files...\n")
    
    for css_file in css_files:
        result = linter.lint_file(css_file)
        status = "✓" if result['errors'] == 0 else "✗"
        print(f"{status} {css_file.name}: {result['errors']} errors, {result['warnings']} warnings")
    
    print()
    success = linter.print_report()
    
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
