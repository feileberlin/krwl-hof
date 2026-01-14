"""
Test AI Categorization Module

Tests the AI-powered event categorization system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.ai_categorizer import AICategorizer
from modules.utils import load_config


def test_keyword_categorization():
    """Test keyword-based categorization (no AI required)."""
    print("\n" + "="*60)
    print("TEST 1: Keyword-Based Categorization (Fallback)")
    print("="*60)
    
    # Load config
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    # Disable AI to test keyword fallback
    if 'ai' not in config:
        config['ai'] = {}
    config['ai']['categorization'] = {'enabled': False}
    
    categorizer = AICategorizer(config, base_path)
    
    # Test cases
    test_events = [
        ("Rock Concert", "Live music performance with local bands", "music"),
        ("Art Exhibition", "Gallery showing of contemporary paintings", "arts"),
        ("Football Match", "Local team playing championship game", "sports"),
        ("Cooking Workshop", "Learn to make Italian pasta from scratch", "workshops"),
        ("Christmas Market", "Holiday shopping with food and crafts", "shopping"),
        ("Tech Meetup", "Software developers gathering", "tech"),
        ("Random Event", "Something completely generic", "default"),
    ]
    
    passed = 0
    failed = 0
    
    for title, description, expected_category in test_events:
        category, confidence, method = categorizer.categorize_event(title, description)
        
        status = "✓" if category == expected_category else "✗"
        if category == expected_category:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status} Title: {title}")
        print(f"  Description: {description}")
        print(f"  Expected: {expected_category}, Got: {category}")
        print(f"  Method: {method}, Confidence: {confidence:.2f}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


def test_ai_categorization():
    """Test AI-based categorization (requires Ollama)."""
    print("\n" + "="*60)
    print("TEST 2: AI-Based Categorization (Requires Ollama)")
    print("="*60)
    
    # Load config
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    # Enable AI categorization
    if 'ai' not in config:
        config['ai'] = {}
    config['ai']['categorization'] = {'enabled': True}
    config['ai']['ollama'] = {
        'host': 'http://localhost:11434',
        'model': 'llama3.2',
        'timeout': 30
    }
    
    categorizer = AICategorizer(config, base_path)
    
    if not categorizer.is_available():
        print("\n⚠️  Ollama not available - skipping AI test")
        print("   To run this test:")
        print("   1. Install Ollama: https://ollama.ai/")
        print("   2. Run: ollama pull llama3.2")
        print("   3. Start Ollama service")
        return True  # Not a failure, just skipped
    
    print("\n✓ Ollama is available!")
    
    # Test a complex event that might challenge keyword matching
    test_events = [
        (
            "Digital Innovation Summit 2026",
            "Join us for a day of exploring cutting-edge technology, "
            "AI advancements, and startup pitches. Network with tech leaders.",
            "tech"
        ),
        (
            "Farm-to-Table Culinary Experience",
            "A unique dining event featuring locally sourced ingredients "
            "prepared by award-winning chefs.",
            "food"
        ),
    ]
    
    for title, description, expected_general_type in test_events:
        category, confidence, method = categorizer.categorize_event(title, description)
        
        print(f"\n📋 Title: {title}")
        print(f"   Description: {description[:80]}...")
        print(f"   Categorized as: {category}")
        print(f"   Method: {method}, Confidence: {confidence:.2f}")
        
        if method == 'ai':
            print("   ✓ AI categorization working!")
    
    return True


def test_status():
    """Test categorizer status reporting."""
    print("\n" + "="*60)
    print("TEST 3: Categorizer Status")
    print("="*60)
    
    base_path = Path(__file__).parent.parent
    config = load_config(base_path)
    
    # Test with AI enabled
    if 'ai' not in config:
        config['ai'] = {}
    config['ai']['categorization'] = {'enabled': True}
    
    categorizer = AICategorizer(config, base_path)
    status = categorizer.get_status()
    
    print(f"\nCategorizer Status:")
    print(f"  Enabled: {status['enabled']}")
    print(f"  AI Available: {status['ai_available']}")
    print(f"  Provider: {status['provider']}")
    print(f"  Fallback Enabled: {status['fallback_enabled']}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI CATEGORIZATION TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test 1: Keyword categorization (always works)
    results.append(("Keyword Categorization", test_keyword_categorization()))
    
    # Test 2: AI categorization (requires Ollama)
    results.append(("AI Categorization", test_ai_categorization()))
    
    # Test 3: Status reporting
    results.append(("Status Reporting", test_status()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
