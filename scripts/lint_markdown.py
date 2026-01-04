#!/usr/bin/env python3
"""
Markdown Linting Tool

Lints markdown files for common issues:
- Heading structure (no skipped levels, single H1)
- Line length (max 120 characters for prose)
- Code blocks (must have language tags)
- Trailing whitespace
- Multiple blank lines
- File ending with newline

Usage:
    python3 scripts/lint_markdown.py [--fix] [FILE_OR_DIR]
    python3 scripts/lint_markdown.py --all
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


class MarkdownLinter:
    """Lints markdown files for common issues"""
    
    # Rules configuration
    MAX_LINE_LENGTH = 120  # For prose, not code blocks
    
    def __init__(self, fix: bool = False, verbose: bool = False):
        self.fix = fix
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.fixed = []
        
    def lint_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Lint a single markdown file
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Tuple of (success, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        self.fixed = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
        except Exception as e:
            self.errors.append(f"Cannot read file: {e}")
            return False, self.errors, self.warnings
        
        lines = content.split('\n')
        
        # Run linting rules
        self._check_headings(lines)
        self._check_line_length(lines)
        self._check_code_blocks(lines)
        self._check_trailing_whitespace(lines)
        self._check_multiple_blank_lines(lines)
        self._check_file_ending(content)
        
        # Apply fixes if requested
        if self.fix and self.fixed:
            fixed_content = self._apply_fixes(lines)
            if fixed_content != original_content:
                file_path.write_text(fixed_content, encoding='utf-8')
                print(f"✓ Fixed {len(self.fixed)} issue(s) in {file_path}")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_headings(self, lines: List[str]):
        """Check heading structure"""
        h1_count = 0
        last_level = 0
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            # Track fenced code blocks (```), which we always skip for heading checks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip lines inside fenced code blocks
            if in_code_block:
                continue
            
            # Skip indented code blocks (4+ leading spaces)
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces >= 4:
                continue
            
            # Check for ATX-style headings
            if line.startswith('#'):
                match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if not match:
                    self.errors.append(f"Line {i}: Malformed heading (needs space after #)")
                    continue
                
                level = len(match.group(1))
                
                # Check for single H1
                if level == 1:
                    h1_count += 1
                    if h1_count > 1:
                        self.errors.append(f"Line {i}: Multiple H1 headings found (only one allowed)")
                
                # Check for skipped levels
                if last_level > 0 and level > last_level + 1:
                    self.warnings.append(f"Line {i}: Heading level skipped (jumped from H{last_level} to H{level})")
                
                last_level = level
        
        if h1_count == 0:
            self.warnings.append("No H1 heading found")
    
    def _check_line_length(self, lines: List[str]):
        """Check line length for prose (excluding code blocks and tables)"""
        in_code_block = False
        in_table = False
        
        for i, line in enumerate(lines, 1):
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            # Skip code blocks and indented code
            if in_code_block or line.startswith('    '):
                continue
            
            # Track tables - a line is part of a table if it contains pipes
            # Reset table mode if current line doesn't contain a pipe (unless it's blank)
            if '|' in line:
                in_table = True
            elif line.strip():  # Non-empty line without pipe
                in_table = False
            # Empty lines don't change table state
            
            # Skip tables, URLs, and headings
            if in_table or line.startswith('#') or 'http' in line:
                continue
            
            # Check length for prose
            if len(line) > self.MAX_LINE_LENGTH:
                # Allow long lines with links or code
                if not ('[' in line and '](' in line) and not '`' in line:
                    self.warnings.append(
                        f"Line {i}: Line too long ({len(line)} > {self.MAX_LINE_LENGTH} characters)"
                    )
    
    def _check_code_blocks(self, lines: List[str]):
        """Check that fenced code blocks have language tags"""
        in_code_block = False
        opening_backticks = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('```'):
                # Count backticks at the start
                backtick_count = len(stripped) - len(stripped.lstrip('`'))
                
                if not in_code_block:
                    # Opening fence - check for language tag
                    if stripped == '`' * backtick_count:
                        self.warnings.append(
                            f"Line {i}: Code block without language tag (e.g., ```python)"
                        )
                    in_code_block = True
                    opening_backticks = backtick_count
                elif backtick_count >= opening_backticks:
                    # Closing fence - must have same or more backticks
                    in_code_block = False
                    opening_backticks = 0
    
    def _check_trailing_whitespace(self, lines: List[str]):
        """Check for trailing whitespace"""
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                self.warnings.append(f"Line {i}: Trailing whitespace")
                if self.fix:
                    self.fixed.append(('trailing_whitespace', i))
    
    def _check_multiple_blank_lines(self, lines: List[str]):
        """Check for multiple consecutive blank lines"""
        blank_count = 0
        
        for i, line in enumerate(lines, 1):
            if not line.strip():
                blank_count += 1
                if blank_count > 2:
                    self.warnings.append(f"Line {i}: Multiple consecutive blank lines")
                    if self.fix:
                        self.fixed.append(('multiple_blanks', i))
            else:
                blank_count = 0
    
    def _check_file_ending(self, content: str):
        """Check that file ends with newline"""
        if content and not content.endswith('\n'):
            self.warnings.append("File should end with newline")
            if self.fix:
                self.fixed.append(('missing_newline', 'EOF'))
    
    def _apply_fixes(self, lines: List[str]) -> str:
        """Apply automatic fixes
        
        Args:
            lines: File lines
            
        Returns:
            Fixed content as string
        """
        # Remove trailing whitespace
        lines = [line.rstrip() for line in lines]
        
        # Remove multiple consecutive blank lines (keep max 2)
        fixed_lines = []
        blank_count = 0
        
        for line in lines:
            if not line.strip():
                blank_count += 1
                if blank_count <= 2:
                    fixed_lines.append(line)
            else:
                blank_count = 0
                fixed_lines.append(line)
        
        # Ensure file ends with newline
        content = '\n'.join(fixed_lines)
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content
    
    def lint_directory(self, dir_path: Path) -> Tuple[int, int]:
        """Lint all markdown files in directory
        
        Args:
            dir_path: Directory path
            
        Returns:
            Tuple of (files_with_errors, total_files)
        """
        md_files = sorted(dir_path.rglob('*.md'))
        
        # Exclude certain directories
        exclude_patterns = ['.git', 'node_modules', 'venv', '.venv', '__pycache__']
        md_files = [
            f for f in md_files 
            if not any(pattern in str(f) for pattern in exclude_patterns)
        ]
        
        if not md_files:
            print(f"No markdown files found in {dir_path}")
            return 0, 0
        
        print(f"\n{'=' * 70}")
        print(f"Linting {len(md_files)} markdown file(s)")
        print(f"{'=' * 70}\n")
        
        files_with_issues = 0
        total_errors = 0
        total_warnings = 0
        
        for md_file in md_files:
            relative_path = md_file.relative_to(dir_path)
            
            success, errors, warnings = self.lint_file(md_file)
            
            if errors or warnings:
                files_with_issues += 1
                total_errors += len(errors)
                total_warnings += len(warnings)
                
                print(f"\n📝 {relative_path}")
                print("-" * 70)
                
                for error in errors:
                    print(f"  ❌ ERROR: {error}")
                
                for warning in warnings:
                    print(f"  ⚠️  WARNING: {warning}")
            elif self.verbose:
                print(f"✓ {relative_path}")
        
        # Summary
        print(f"\n{'=' * 70}")
        if files_with_issues == 0:
            print("✅ All markdown files passed linting")
        else:
            print(f"Found issues in {files_with_issues}/{len(md_files)} file(s)")
            print(f"  Errors: {total_errors}")
            print(f"  Warnings: {total_warnings}")
            
            if not self.fix:
                print(f"\nRun with --fix to automatically fix some issues")
        print(f"{'=' * 70}\n")
        
        return files_with_issues, len(md_files)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Lint markdown files for common issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/lint_markdown.py README.md
  python3 scripts/lint_markdown.py --all
  python3 scripts/lint_markdown.py --fix --all
  python3 scripts/lint_markdown.py .github/
        """
    )
    parser.add_argument('path', nargs='?', default=None,
                       help='File or directory to lint')
    parser.add_argument('--all', action='store_true',
                       help='Lint all markdown files in repository')
    parser.add_argument('--fix', action='store_true',
                       help='Automatically fix some issues')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output (show all files)')
    
    args = parser.parse_args()
    
    # Get repository root
    base_path = Path(__file__).parent.parent
    
    # Determine what to lint
    if args.all:
        target_path = base_path
    elif args.path:
        target_path = Path(args.path)
        if not target_path.is_absolute():
            target_path = base_path / target_path
    else:
        parser.print_help()
        return 1
    
    # Validate path
    if not target_path.exists():
        print(f"Error: Path not found: {target_path}")
        return 1
    
    # Run linter
    linter = MarkdownLinter(fix=args.fix, verbose=args.verbose)
    
    if target_path.is_file():
        success, errors, warnings = linter.lint_file(target_path)
        
        print(f"\n📝 {target_path.name}")
        print("-" * 70)
        
        for error in errors:
            print(f"  ❌ ERROR: {error}")
        
        for warning in warnings:
            print(f"  ⚠️  WARNING: {warning}")
        
        if not errors and not warnings:
            print("  ✅ No issues found")
        
        return 0 if success else 1
    else:
        files_with_issues, total_files = linter.lint_directory(target_path)
        return 0 if files_with_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
