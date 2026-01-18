# Test Debugging Quick Reference

**Quick access to test debugging resources when tests fail.**

## 🚨 Tests Failing? Start Here!

### 1️⃣ Quick Diagnosis (30 seconds)

```bash
# What's failing?
python3 src/event_manager.py test 2>&1 | tee test_output.txt

# Check for missing dependencies
pip list | grep -E "(feedparser|beautifulsoup4|lxml|pydantic)"
```

### 2️⃣ Common Quick Fixes (1 minute)

```bash
# Fix 90% of issues:
pip install -r requirements.txt

# Re-run tests:
python3 src/event_manager.py test
```

## 📚 Full Documentation

- **[Complete Debugging Guide](DEBUG_TESTS.md)** - Detailed walkthrough with examples
- **[Test README](../tests/README.md)** - Test organization and commands
- **[Copilot Instructions](../.github/copilot-instructions.md)** - Development guidelines

## 🎯 Common Issues at a Glance

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |
| `FileNotFoundError: .../events.json` | Test fixture missing | Check test `setUp()` method |
| `FileNotFoundError: .../templates/index.html` | Wrong path | Update to `public/index.html` |
| `KeyError: 'lucide'` | Config changed | Check source code for current keys |
| Passes locally, fails in CI | Environment difference | Set `CI=true` and test locally |
| Fails locally, passes in CI | Environment difference | Check local config and dependencies |

## 🔧 Essential Commands

```bash
# List tests
python3 src/event_manager.py test --list

# Run all tests
python3 src/event_manager.py test

# Run with verbose output
python3 src/event_manager.py test test_name --verbose

# Simulate CI environment
export CI=true GITHUB_ACTIONS=true
python3 src/event_manager.py test
```

## 🆘 Still Stuck?

1. Check [DEBUG_TESTS.md](DEBUG_TESTS.md) for detailed guidance
2. Search recent changes: `git log --oneline -20`
3. Check CI workflow logs in GitHub Actions UI
4. Review error patterns in [Common Failure Patterns](DEBUG_TESTS.md#common-failure-patterns)

---

**Remember:** Always fix pre-existing test failures, even if unrelated to your changes. This keeps the codebase healthy! 🏥
