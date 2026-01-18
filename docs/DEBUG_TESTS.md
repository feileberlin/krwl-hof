# Test Debugging Guide

This guide helps you debug test failures in the KRWL HOF project, whether you're working locally or investigating CI failures.

## Table of Contents

- [Quick Start](#quick-start)
- [Common Failure Patterns](#common-failure-patterns)
- [Step-by-Step Debugging](#step-by-step-debugging)
- [CI-Specific Debugging](#ci-specific-debugging)
- [Test Commands Reference](#test-commands-reference)

## Quick Start

### Identify Failing Tests

```bash
# List all available tests
python3 src/event_manager.py test --list

# Run all tests and save output
python3 src/event_manager.py test 2>&1 | tee test_output.txt

# Run specific category with verbose output
python3 src/event_manager.py test core --verbose
```

### Quick Fix Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Check Python version: `python3 --version` (should be 3.x)
- [ ] Verify file paths haven't changed: `find . -name "events.json"`
- [ ] Check environment variables: `echo $CI $GITHUB_ACTIONS`
- [ ] Review recent code changes: `git log --oneline -10`

## Common Failure Patterns

### Pattern 1: Missing Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'feedparser'
NameError: name 'feedparser' is not defined
ModuleNotFoundError: No module named 'pydantic'
```

**Root Cause:** Required Python packages are not installed.

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific packages
pip install feedparser beautifulsoup4 lxml pydantic

# Verify installation
pip list | grep -E "(feedparser|beautifulsoup4|lxml|pydantic)"
```

**Prevention:** Always run `pip install -r requirements.txt` after pulling new code.

---

### Pattern 2: Missing Test Fixture Files

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/test_xyz/assets/json/events.json'
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/test_xyz/assets/json/pending_events.json'
```

**Root Cause:** Test setup doesn't create required fixture files in temporary directory.

**Solution:**

1. Locate the failing test file:
```bash
grep -r "test_xyz" tests/
```

2. Check if `setUp()` method creates required files:
```python
def setUp(self):
    """Set up test fixtures"""
    # Create directory structure
    os.makedirs(os.path.join(self.test_path, 'assets/json'), exist_ok=True)
    
    # Create events.json file
    events_data = {
        'events': [],
        'pending_count': 0,
        'last_updated': datetime.now().isoformat()
    }
    events_path = os.path.join(self.test_path, 'assets/json/events.json')
    with open(events_path, 'w') as f:
        json.dump(events_data, f, indent=2)
```

3. Re-run the test:
```bash
python3 src/event_manager.py test test_scraper --verbose
```

**Prevention:** Always create required files in test `setUp()` methods.

---

### Pattern 3: Incorrect File Paths

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/src/templates/index.html'
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/data/events.demo.json'
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/static/leaflet/leaflet.css'
```

**Root Cause:** Files were moved or project structure changed.

**Solution:**

1. Find the current location of the file:
```bash
# For index.html
find . -name "index.html" -type f

# For events.demo.json
find . -name "events.demo.json" -type f

# For leaflet.css
find . -name "leaflet.css" -type f
```

2. Update the test to use the correct path:
```python
# Old (wrong)
template_path = os.path.join(base_path, 'src/templates/index.html')
demo_events_path = os.path.join(base_path, 'data/events.demo.json')
leaflet_css_path = os.path.join(base_path, 'static/leaflet/leaflet.css')

# New (correct)
template_path = os.path.join(base_path, 'public/index.html')
demo_events_path = os.path.join(base_path, 'assets/json/events.demo.json')
leaflet_css_path = os.path.join(base_path, 'lib/leaflet/leaflet.css')
```

3. Re-run the test:
```bash
python3 src/event_manager.py test test_components --verbose
```

**Prevention:** When moving files, search for references in tests: `grep -r "old/path" tests/`

---

### Pattern 4: Configuration/Schema Changes

**Symptoms:**
```
KeyError: 'lucide'
AttributeError: 'dict' object has no attribute 'marker_size'
AssertionError: Uncovered fields: {'marker_size', 'marker_popup_anchor', 'scraped_at'}
```

**Root Cause:** Configuration or schema was updated, but tests weren't updated.

**Solution:**

1. For missing keys, check the source code:
```bash
# Find where the key is defined
grep -r "DEPENDENCIES" src/modules/site_generator.py

# Check configuration
cat config.json | jq '.design'
```

2. Update test to use current configuration:
```python
# Check if key exists before using it
if 'lucide' in DEPENDENCIES:
    lucide_config = DEPENDENCIES['lucide']
else:
    # Handle missing key or skip test
    print("Lucide dependency not configured")
```

3. For schema changes, update test expectations:
```python
# Update required fields to match current schema
required_fields = ['id', 'title', 'start_time', 'location']

# Update optional fields to match current schema
optional_fields = ['marker_size', 'marker_icon', 'category', 'scraped_at']
```

**Prevention:** Run tests after changing configuration or schemas: `python3 src/event_manager.py test`

---

### Pattern 5: Import Path Issues

**Symptoms:**
```
ModuleNotFoundError: No module named 'modules.cdn_inliner'
ImportError: cannot import name 'SomeClass' from 'src.modules.old_module'
```

**Root Cause:** Module was moved, renamed, or deleted.

**Solution:**

1. Find the module's current location:
```bash
# Search for the class/function
grep -r "class CDNInliner" src/

# List all modules
ls -la src/modules/
```

2. Update import statements:
```python
# Old (wrong)
from modules.cdn_inliner import CDNInliner

# New (correct)
from src.modules.site_generator import SiteGenerator
```

3. Re-run the test:
```bash
python3 src/event_manager.py test test_cdn_fallback --verbose
```

**Prevention:** Use IDE refactoring tools when renaming/moving modules.

---

### Pattern 6: Environment-Specific Failures

**Symptoms:**
- Tests pass locally but fail in CI
- Tests fail locally but pass in CI
- Different behavior in development vs production mode

**Root Cause:** Environment detection or configuration differs between local and CI.

**Solution:**

1. Check environment detection:
```bash
# Local environment
python3 -c "from src.modules.utils import is_ci, is_production, is_development; print(f'CI: {is_ci()}, Prod: {is_production()}, Dev: {is_development()}')"

# Simulate CI environment
export CI=true
export GITHUB_ACTIONS=true
python3 -c "from src.modules.utils import is_ci, is_production, is_development; print(f'CI: {is_ci()}, Prod: {is_production()}, Dev: {is_development()}')"
```

2. Check configuration loading:
```bash
python3 -c "from src.modules.utils import load_config; config = load_config('.'); print(f\"Debug: {config['debug']}, Source: {config['data']['source']}\")"
```

3. Run tests in CI mode:
```bash
export CI=true
export GITHUB_ACTIONS=true
python3 src/event_manager.py test
```

**Prevention:** Test with both local and CI environment variables before committing.

## Step-by-Step Debugging

### Step 1: Reproduce the Failure

```bash
# Run the failing test
python3 src/event_manager.py test test_name --verbose

# Or run directly (legacy method)
python3 tests/test_name.py --verbose

# Capture full output
python3 src/event_manager.py test test_name --verbose 2>&1 | tee debug.log
```

### Step 2: Analyze the Error

Read the error message carefully:
- **Line number**: Where did it fail?
- **Error type**: `FileNotFoundError`, `ModuleNotFoundError`, `KeyError`, `AssertionError`?
- **Stack trace**: What was the call chain?

```bash
# Extract just the errors
cat debug.log | grep -A 5 -E "(Error|FAILED|Traceback)"
```

### Step 3: Identify the Root Cause

Use the [Common Failure Patterns](#common-failure-patterns) section above to identify the issue.

```bash
# Check for missing files
find . -name "missing_file.json"

# Check for missing modules
python3 -c "import module_name"

# Check configuration
cat config.json | jq '.'
```

### Step 4: Apply the Fix

Based on the root cause:
- Install missing dependencies
- Create missing fixture files
- Update file paths
- Fix import statements
- Update configuration

### Step 5: Verify the Fix

```bash
# Re-run the specific test
python3 src/event_manager.py test test_name --verbose

# Run related tests
python3 src/event_manager.py test category --verbose

# Run full test suite
python3 src/event_manager.py test
```

### Step 6: Prevent Future Failures

```bash
# Add test for the issue
# Update documentation
# Add validation/assertions
# Update CI workflow if needed
```

## CI-Specific Debugging

### Understanding CI Test Failures

When a CI job fails:

1. **Check the job logs** in GitHub Actions UI
2. **Identify which step failed** (setup, dependencies, test execution)
3. **Look for warnings** before the failure
4. **Check previous successful runs** to see what changed

### Reproducing CI Failures Locally

```bash
# Set CI environment variables
export CI=true
export GITHUB_ACTIONS=true

# Use the same Python version as CI
python3 --version  # Should match workflow's python-version

# Run the same commands as CI workflow
pip install -r requirements.txt
python3 src/event_manager.py generate
python3 src/event_manager.py test
```

### Common CI Issues

#### Issue 1: Dependencies Not Installed

**Workflow check:**
```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
```

**Fix:** Ensure this step exists and runs before tests.

#### Issue 2: Generated Files Missing

**Workflow check:**
```yaml
- name: Generate HTML files
  run: |
    python3 src/event_manager.py generate
```

**Fix:** Ensure generation runs before tests that depend on generated files.

#### Issue 3: Job Dependencies

**Workflow check:**
```yaml
test-job:
  needs: [build-job]  # This job depends on build-job completing
```

**Fix:** Verify dependencies are correctly specified and previous jobs succeeded.

#### Issue 4: Artifacts Not Available

**Workflow check:**
```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ./public

# Later job
- name: Download artifact
  uses: actions/download-artifact@v3
```

**Fix:** Ensure artifact upload/download steps are present.

### Debugging CI Workflow YAML

```bash
# Validate workflow syntax
cat .github/workflows/auto-generate-html.yml | python3 -c "import sys, yaml; yaml.safe_load(sys.stdin)"

# Check for common issues
grep -n "needs:" .github/workflows/*.yml
grep -n "if:" .github/workflows/*.yml
```

## Test Commands Reference

### Basic Commands

```bash
# List all tests
python3 src/event_manager.py test --list

# Run all tests
python3 src/event_manager.py test

# Run with verbose output
python3 src/event_manager.py test --verbose
```

### Category-Based Testing

```bash
# Core functionality tests
python3 src/event_manager.py test core --verbose

# Feature tests
python3 src/event_manager.py test features --verbose

# Infrastructure tests
python3 src/event_manager.py test infrastructure --verbose
```

### Individual Test Execution

```bash
# Run specific test (with or without 'test_' prefix)
python3 src/event_manager.py test test_scraper --verbose
python3 src/event_manager.py test scraper --verbose

# Run test file directly (legacy)
python3 tests/test_scraper.py --verbose

# Run with PYTHONPATH set
PYTHONPATH=$(pwd) python3 tests/test_scraper.py
```

### Dependency Checking

```bash
# Install all dependencies
pip install -r requirements.txt

# Check installed packages
pip list | grep -E "(feedparser|beautifulsoup4|lxml|pydantic)"

# Check for missing dependencies
python3 -c "import feedparser, bs4, lxml, pydantic; print('All required packages installed')"
```

### Environment Checking

```bash
# Check Python version
python3 --version

# Check environment detection
python3 -c "from src.modules.utils import is_ci, is_production, is_development; print(f'CI: {is_ci()}, Prod: {is_production()}, Dev: {is_development()}')"

# Check configuration loading
python3 -c "from src.modules.utils import load_config; config = load_config('.'); print(f\"Debug: {config['debug']}, Source: {config['data']['source']}\")"

# Simulate CI environment
export CI=true
export GITHUB_ACTIONS=true
python3 src/event_manager.py test
```

### File Path Verification

```bash
# Find events.json files
find . -name "events.json" -type f

# Find demo events
find . -name "events.demo.json" -type f

# Find HTML templates
find . -name "*.html" -path "*/templates/*" -o -name "*.html" -path "*/public/*"

# Find library files
find . -name "leaflet.css" -o -name "leaflet.js"
```

### Debugging Output

```bash
# Save test output to file
python3 src/event_manager.py test 2>&1 | tee test_output.txt

# Extract errors only
python3 src/event_manager.py test 2>&1 | grep -A 5 -E "(Error|FAILED|Traceback)"

# Count failures
python3 src/event_manager.py test 2>&1 | grep -c "FAILED"
```

## Best Practices

### When You Encounter Test Failures

1. ✅ **DO**: Read the full error message and stack trace
2. ✅ **DO**: Check if the issue matches a common pattern
3. ✅ **DO**: Reproduce the failure locally before fixing
4. ✅ **DO**: Fix pre-existing test failures, not just your changes
5. ✅ **DO**: Run the full test suite after fixing
6. ✅ **DO**: Document complex fixes in commit messages

7. ❌ **DON'T**: Skip or ignore failing tests
8. ❌ **DON'T**: Commit code without running tests
9. ❌ **DON'T**: Assume tests will pass in CI if they pass locally
10. ❌ **DON'T**: Modify tests to hide failures instead of fixing the root cause

### Maintaining Test Health

```bash
# Run tests before committing
git add .
python3 src/event_manager.py test
git commit -m "fix: your changes"

# Run tests after pulling changes
git pull origin main
pip install -r requirements.txt
python3 src/event_manager.py test

# Run tests periodically
# Add to your shell alias or git hooks
alias test-krwl="cd /path/to/krwl-hof && python3 src/event_manager.py test"
```

## Getting Help

If you're still stuck after trying this guide:

1. **Check recent changes**: `git log --oneline -20`
2. **Search for similar issues**: `git log --all --grep="test failure"`
3. **Review workflow runs**: Check GitHub Actions for patterns
4. **Check documentation**: 
   - [Copilot Instructions](../.github/copilot-instructions.md)
   - [Test README](../tests/README.md)
   - [Project README](../README.md)

## See Also

- [Test README](../tests/README.md) - Test organization and running tests
- [Copilot Instructions](../.github/copilot-instructions.md) - Development guidelines
- [Test Runner Module](../src/modules/test_runner.py) - Test execution implementation
- [GitHub Actions Workflows](../.github/workflows/) - CI/CD configuration
