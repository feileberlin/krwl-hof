#!/usr/bin/env python3
"""
Tests for moon phase calculation module.

Validates that moon phase and Sunday calculations work correctly.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.moon_phase import (
    get_next_sunday_primetime,
    calculate_next_full_moon,
    get_next_full_moon_for_filter,
    get_full_moon_morning_for_filter,
    get_days_until_full_moon,
    get_days_until_sunday,
    get_next_sunday_date,
    get_next_sunday_formatted
)


def test_next_sunday_primetime():
    """Test Sunday primetime calculation"""
    print("\n" + "="*80)
    print("TEST: Next Sunday Primetime Calculation")
    print("="*80)
    
    next_sunday = get_next_sunday_primetime()
    now = datetime.now()
    
    # Sunday should be in the future
    assert next_sunday > now, "Sunday should be in the future"
    
    # Sunday should be within 7 days
    days_until = (next_sunday - now).days
    assert 0 <= days_until <= 7, f"Sunday should be within 7 days, got {days_until}"
    
    # Should be at 20:15
    assert next_sunday.hour == 20, f"Hour should be 20, got {next_sunday.hour}"
    assert next_sunday.minute == 15, f"Minute should be 15, got {next_sunday.minute}"
    
    # Should be a Sunday (weekday 6)
    assert next_sunday.weekday() == 6, f"Should be Sunday (weekday 6), got {next_sunday.weekday()}"
    
    print(f"✓ Next Sunday primetime: {next_sunday.strftime('%Y-%m-%d %H:%M')}")
    print(f"✓ Days until: {days_until}")
    print("✓ PASS: Sunday calculation works correctly")
    return True


def test_full_moon_calculation():
    """Test full moon calculation"""
    print("\n" + "="*80)
    print("TEST: Full Moon Calculation")
    print("="*80)
    
    now = datetime.now()
    next_full_moon = calculate_next_full_moon(now)
    
    # Full moon should be in the future
    assert next_full_moon > now, "Full moon should be in the future"
    
    # Full moon should be within ~30 days (one lunar cycle)
    days_until = (next_full_moon - now).days
    assert 0 <= days_until <= 35, f"Full moon should be within 35 days, got {days_until}"
    
    print(f"✓ Next full moon: {next_full_moon.strftime('%Y-%m-%d %H:%M')}")
    print(f"✓ Days until: {days_until}")
    print("✓ PASS: Full moon calculation works correctly")
    return True


def test_full_moon_filter_logic():
    """Test that full moon filter skips to next one if before Sunday"""
    print("\n" + "="*80)
    print("TEST: Full Moon Filter Logic (Skip if before Sunday)")
    print("="*80)
    
    next_sunday = get_next_sunday_primetime()
    full_moon, days_until_fm = get_next_full_moon_for_filter()
    
    # Full moon should be after Sunday (per requirements)
    assert full_moon > next_sunday, "Full moon should be after Sunday for filtering"
    
    print(f"✓ Next Sunday: {next_sunday.strftime('%Y-%m-%d %H:%M')}")
    print(f"✓ Full moon for filter: {full_moon.strftime('%Y-%m-%d %H:%M')}")
    print(f"✓ Days until full moon: {days_until_fm:.1f}")
    print("✓ PASS: Full moon filter logic works correctly")
    return True


def test_days_until_functions():
    """Test the main exported functions"""
    print("\n" + "="*80)
    print("TEST: Main Exported Functions")
    print("="*80)
    
    days_sunday = get_days_until_sunday()
    days_full_moon = get_days_until_full_moon()
    sunday_date = get_next_sunday_date()
    sunday_formatted = get_next_sunday_formatted()
    
    # Days should be positive integers
    assert isinstance(days_sunday, int), "Days until Sunday should be int"
    assert isinstance(days_full_moon, int), "Days until full moon should be int"
    assert days_sunday >= 0, "Days until Sunday should be >= 0"
    assert days_full_moon > 0, "Days until full moon should be > 0"
    
    # Date strings should be valid
    assert isinstance(sunday_date, str), "Sunday date should be string"
    assert len(sunday_date) == 10, f"Sunday date should be YYYY-MM-DD, got {sunday_date}"
    
    assert isinstance(sunday_formatted, str), "Sunday formatted should be string"
    assert len(sunday_formatted) > 0, "Sunday formatted should not be empty"
    
    print(f"✓ Days until Sunday: {days_sunday}")
    print(f"✓ Days until full moon: {days_full_moon}")
    print(f"✓ Sunday date (ISO): {sunday_date}")
    print(f"✓ Sunday date (formatted): {sunday_formatted}")
    print("✓ PASS: All exported functions work correctly")
    return True


def test_consistency():
    """Test that calculated days match the datetime differences"""
    print("\n" + "="*80)
    print("TEST: Consistency Check")
    print("="*80)
    
    now = datetime.now()
    
    # Check Sunday consistency
    next_sunday = get_next_sunday_primetime()
    days_sunday_calc = (next_sunday - now).total_seconds() / 86400
    days_sunday_func = get_days_until_sunday()
    
    # Should match within 1 day (rounding)
    diff_sunday = abs(days_sunday_calc - days_sunday_func)
    assert diff_sunday < 1.5, f"Sunday days mismatch: calc={days_sunday_calc:.1f}, func={days_sunday_func}"
    
    # Check full moon consistency
    full_moon_morning, _ = get_full_moon_morning_for_filter()
    days_fm_calc = (full_moon_morning - now).total_seconds() / 86400
    days_fm_func = get_days_until_full_moon()
    
    # Should match within 1 day (rounding)
    diff_fm = abs(days_fm_calc - days_fm_func)
    assert diff_fm < 1.5, f"Full moon days mismatch: calc={days_fm_calc:.1f}, func={days_fm_func}"
    
    print(f"✓ Sunday days - calculated: {days_sunday_calc:.2f}, function: {days_sunday_func}")
    print(f"✓ Full moon days - calculated: {days_fm_calc:.2f}, function: {days_fm_func}")
    print("✓ PASS: Calculations are consistent")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("MOON PHASE TEST SUITE")
    print("="*80)
    
    tests = [
        test_next_sunday_primetime,
        test_full_moon_calculation,
        test_full_moon_filter_logic,
        test_days_until_functions,
        test_consistency
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ TEST EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
