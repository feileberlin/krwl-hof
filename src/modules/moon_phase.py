"""
Moon Phase Calculation Module

Calculates days until next full moon, with logic to skip to the following
full moon if the next one occurs before next Sunday's primetime.

This matches the frontend filtering logic for consistency.
"""

from datetime import datetime, timedelta
import math


def get_next_sunday_primetime():
    """
    Get next Sunday at primetime (20:15).
    
    Returns:
        datetime: Next Sunday at 20:15
    """
    now = datetime.now()
    current_day = now.weekday()  # Monday = 0, Sunday = 6
    
    # Calculate days until Sunday (weekday 6)
    if current_day == 6:  # Today is Sunday
        # Check if we've passed primetime
        primetime_today = now.replace(hour=20, minute=15, second=0, microsecond=0)
        if now >= primetime_today:
            # Next Sunday is in 7 days
            days_until_sunday = 7
        else:
            # Use today's primetime
            return primetime_today
    else:
        # Calculate days until next Sunday
        days_until_sunday = (6 - current_day) % 7
        if days_until_sunday == 0:
            days_until_sunday = 7
    
    # Calculate next Sunday at 20:15
    next_sunday = now + timedelta(days=days_until_sunday)
    next_sunday = next_sunday.replace(hour=20, minute=15, second=0, microsecond=0)
    
    return next_sunday


def calculate_next_full_moon(after_date=None):
    """
    Calculate next full moon date using lunar cycle approximation.
    
    Args:
        after_date: Optional datetime to find full moon after (defaults to now)
        
    Returns:
        datetime: Next full moon date
    """
    if after_date is None:
        after_date = datetime.now()
    
    # Known full moon: January 6, 2000, 18:14 UTC
    # This matches the JavaScript implementation for consistency
    known_full_moon = datetime(2000, 1, 6, 18, 14, 0)
    
    # Lunar cycle length (synodic month) in days
    lunar_cycle_days = 29.53058770576
    
    # Calculate how many lunar cycles have passed
    time_since_known = (after_date - known_full_moon).total_seconds()
    cycles_since_known = math.floor(time_since_known / (lunar_cycle_days * 86400))
    
    # Calculate the full moon date for that cycle
    full_moon = known_full_moon + timedelta(days=cycles_since_known * lunar_cycle_days)
    
    # Find first full moon after the target date
    while full_moon <= after_date:
        full_moon = full_moon + timedelta(days=lunar_cycle_days)
    
    return full_moon


def get_next_full_moon_for_filter():
    """
    Get the next full moon to use for event filtering.
    
    Logic: If the next full moon occurs before next Sunday's primetime,
    skip to the following full moon. This ensures a reasonable time window
    for filtering events.
    
    Returns:
        tuple: (full_moon_datetime, days_until_full_moon)
    """
    now = datetime.now()
    next_sunday = get_next_sunday_primetime()
    
    # Calculate the immediate next full moon
    next_full_moon = calculate_next_full_moon(now)
    
    # If next full moon is before Sunday, use the one after
    if next_full_moon <= next_sunday:
        next_full_moon = calculate_next_full_moon(next_full_moon)
    
    # Calculate days until this full moon
    days_until = (next_full_moon - now).total_seconds() / 86400
    
    return next_full_moon, days_until


def get_full_moon_morning_for_filter():
    """
    Get the morning (6 AM) after the next full moon for filtering.
    This matches the JavaScript getNextFullMoonMorning() implementation.
    
    Returns:
        tuple: (full_moon_morning_datetime, days_until)
    """
    full_moon, _ = get_next_full_moon_for_filter()
    
    # Set to 6am of day after full moon (matches JS implementation)
    day_after_full_moon = full_moon + timedelta(days=1)
    full_moon_morning = day_after_full_moon.replace(hour=6, minute=0, second=0, microsecond=0)
    
    # Calculate days until
    now = datetime.now()
    days_until = (full_moon_morning - now).total_seconds() / 86400
    
    return full_moon_morning, days_until


def get_days_until_full_moon():
    """
    Get the number of days until the next full moon (rounded).
    
    This is the main function to export for the filter bar display.
    
    Returns:
        int: Days until next full moon (rounded to nearest day)
    """
    _, days_until = get_full_moon_morning_for_filter()
    return round(days_until)


def get_days_until_sunday():
    """
    Get the number of days until next Sunday's primetime (rounded).
    
    This is the main function to export for the filter bar display.
    
    Returns:
        int: Days until next Sunday (rounded to nearest day)
    """
    now = datetime.now()
    next_sunday = get_next_sunday_primetime()
    days_until = (next_sunday - now).total_seconds() / 86400
    return round(days_until)


def get_next_sunday_date():
    """
    Get the date of next Sunday's primetime.
    
    Returns:
        str: Date string in format 'YYYY-MM-DD' (e.g., '2026-01-19')
    """
    next_sunday = get_next_sunday_primetime()
    return next_sunday.strftime('%Y-%m-%d')


def get_next_sunday_formatted():
    """
    Get the formatted date of next Sunday for display.
    
    Returns:
        str: Formatted date (e.g., 'January 19' or 'Jan 19')
    """
    next_sunday = get_next_sunday_primetime()
    return next_sunday.strftime('%B %d')  # Full month name + day


if __name__ == '__main__':
    # Test the module
    print("Moon Phase & Sunday Calculator")
    print("=" * 50)
    
    now = datetime.now()
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M')}")
    
    # Sunday calculations
    print("\n" + "=" * 50)
    print("SUNDAY CALCULATIONS")
    print("=" * 50)
    next_sunday = get_next_sunday_primetime()
    print(f"Next Sunday primetime: {next_sunday.strftime('%Y-%m-%d %H:%M')}")
    
    days_until_sunday = get_days_until_sunday()
    print(f"Days until Sunday: {days_until_sunday} days")
    
    sunday_date = get_next_sunday_date()
    print(f"Sunday date (ISO): {sunday_date}")
    
    sunday_formatted = get_next_sunday_formatted()
    print(f"Sunday date (formatted): {sunday_formatted}")
    print(f"Display text: 'till sunday's primetime ({days_until_sunday} days)'")
    print(f"Or: 'till {sunday_formatted}'")
    
    # Full moon calculations
    print("\n" + "=" * 50)
    print("FULL MOON CALCULATIONS")
    print("=" * 50)
    full_moon, days_until_fm = get_next_full_moon_for_filter()
    print(f"Next full moon: {full_moon.strftime('%Y-%m-%d %H:%M')}")
    print(f"Days until full moon: {days_until_fm:.1f} days")
    
    morning, days_until_morning = get_full_moon_morning_for_filter()
    print(f"Full moon morning (6 AM): {morning.strftime('%Y-%m-%d %H:%M')}")
    print(f"Days until: {days_until_morning:.1f} days")
    
    days_rounded = get_days_until_full_moon()
    print(f"Days until (rounded): {days_rounded} days")
    print(f"Display text: 'till next full moon ({days_rounded} days)'")
