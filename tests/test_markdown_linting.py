#!/usr/bin/env python3
"""
Tests for markdown linting functionality

Tests both the lint_markdown.py script and CLI integration
"""

import sys
import subprocess
from pathlib import Path
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_lint_markdown_script_exists():
    """Test that lint_markdown.py script exists"""
    base_path = Path(__file__).parent.parent
    script_path = base_path / 'scripts' / 'lint_markdown.py'
    assert script_path.exists(), f"lint_markdown.py not found at {script_path}"
    assert script_path.is_file(), "lint_markdown.py is not a file"
    print("✓ lint_markdown.py script exists")


def test_lint_markdown_is_executable():
    """Test that lint_markdown.py is executable"""
    base_path = Path(__file__).parent.parent
    script_path = base_path / 'scripts' / 'lint_markdown.py'
    assert os.access(script_path, os.X_OK), "lint_markdown.py is not executable"
    print("✓ lint_markdown.py is executable")


def test_lint_markdown_help():
    """Test that lint_markdown.py --help works"""
    base_path = Path(__file__).parent.parent
    result = subprocess.run(
        ['python3', 'scripts/lint_markdown.py', '--help'],
        cwd=base_path,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Help command failed: {result.stderr}"
    assert 'Lint markdown files' in result.stdout, "Help text missing"
    assert '--fix' in result.stdout, "Help missing --fix option"
    assert '--all' in result.stdout, "Help missing --all option"
    print("✓ lint_markdown.py --help works")


def test_lint_valid_markdown():
    """Test linting valid markdown"""
    base_path = Path(__file__).parent.parent
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test Markdown

This is a test markdown file.

## Section 1

Some content here.

```python
print("hello")
```

## Section 2

More content.
""")
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/lint_markdown.py', temp_file],
            cwd=base_path,
            capture_output=True,
            text=True
        )
        # Should pass or have only warnings, not errors
        assert '❌ ERROR' not in result.stdout, f"Unexpected errors in valid markdown: {result.stdout}"
        print("✓ Lints valid markdown without errors")
    finally:
        os.unlink(temp_file)


def test_lint_detects_multiple_h1():
    """Test that linter detects multiple H1 headings"""
    base_path = Path(__file__).parent.parent
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# First H1

Some content.

# Second H1

This should be detected as an error.
""")
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/lint_markdown.py', temp_file],
            cwd=base_path,
            capture_output=True,
            text=True
        )
        assert 'Multiple H1 headings' in result.stdout, "Should detect multiple H1 headings"
        print("✓ Detects multiple H1 headings")
    finally:
        os.unlink(temp_file)


def test_lint_detects_missing_code_language():
    """Test that linter detects code blocks without language tags"""
    base_path = Path(__file__).parent.parent
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test

```
code without language
```
""")
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python3', 'scripts/lint_markdown.py', temp_file],
            cwd=base_path,
            capture_output=True,
            text=True
        )
        assert 'Code block without language tag' in result.stdout, "Should detect missing code language"
        print("✓ Detects code blocks without language tags")
    finally:
        os.unlink(temp_file)


def test_lint_fix_trailing_whitespace():
    """Test that --fix removes trailing whitespace"""
    base_path = Path(__file__).parent.parent
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test

Line with trailing spaces   

Another line.
""")
        temp_file = f.name
    
    try:
        # Run with --fix
        subprocess.run(
            ['python3', 'scripts/lint_markdown.py', temp_file, '--fix'],
            cwd=base_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Read fixed file
        with open(temp_file, 'r') as f:
            fixed_content = f.read()
        
        # Check trailing whitespace is removed
        lines = fixed_content.split('\n')
        for line in lines[:-1]:  # Exclude last line (may be empty)
            if line:  # Skip empty lines
                assert line == line.rstrip(), f"Line still has trailing whitespace: '{line}'"
        
        print("✓ --fix removes trailing whitespace")
    finally:
        os.unlink(temp_file)


def test_cli_docs_lint_markdown():
    """Test CLI integration via event_manager.py docs lint-markdown"""
    base_path = Path(__file__).parent.parent
    
    # Test with README.md
    result = subprocess.run(
        ['python3', 'src/event_manager.py', 'docs', 'lint-markdown', 'README.md'],
        cwd=base_path,
        capture_output=True,
        text=True
    )
    
    # Should run successfully (exit code 0 or 1 depending on issues found)
    assert result.returncode in [0, 1], f"CLI command failed unexpectedly: {result.stderr}"
    assert '📝 README.md' in result.stdout, "Should show linting output for README.md"
    print("✓ CLI integration via event_manager.py works")


def test_cli_docs_list_includes_lint_markdown():
    """Test that 'docs --list' includes lint-markdown task"""
    base_path = Path(__file__).parent.parent
    
    result = subprocess.run(
        ['python3', 'src/event_manager.py', 'docs', '--list'],
        cwd=base_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"docs --list failed: {result.stderr}"
    assert 'lint-markdown' in result.stdout, "'docs --list' should include lint-markdown task"
    assert 'Lint markdown files' in result.stdout, "Task description missing"
    print("✓ 'docs --list' includes lint-markdown task")


def test_cli_help_includes_lint_markdown():
    """Test that --help includes lint-markdown examples"""
    base_path = Path(__file__).parent.parent
    
    result = subprocess.run(
        ['python3', 'src/event_manager.py', '--help'],
        cwd=base_path,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"--help failed: {result.stderr}"
    assert 'lint-markdown' in result.stdout, "Help text should mention lint-markdown"
    print("✓ --help includes lint-markdown")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_lint_markdown_script_exists,
        test_lint_markdown_is_executable,
        test_lint_markdown_help,
        test_lint_valid_markdown,
        test_lint_detects_multiple_h1,
        test_lint_detects_missing_code_language,
        test_lint_fix_trailing_whitespace,
        test_cli_docs_lint_markdown,
        test_cli_docs_list_includes_lint_markdown,
        test_cli_help_includes_lint_markdown,
    ]
    
    print("\n" + "=" * 70)
    print("Running Markdown Linting Tests")
    print("=" * 70 + "\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
