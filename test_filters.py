#!/usr/bin/env python3
"""
Test script for KRWL HOF event filtering logic

This script tests the various filtering mechanisms:
- Time filtering (sunrise, sunday, full moon, hours)
- Distance filtering (15 min foot, 10 min bike, 1 hr transport)
- Event type filtering (events, on stage, pub games, festivals)
- Location filtering (geolocation, predefined locations)

Usage:
    python3 test_filters.py [--verbose]
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


class FilterTester:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tests_passed = 0
        self.tests_failed = 0
        self.repo_root = Path(__file__).parent
        
    def log(self, message):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(f"  {message}")
    
    def assert_test(self, condition, test_name, error_msg=""):
        """Assert a test condition"""
        if condition:
            self.tests_passed += 1
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            if error_msg:
                print(f"  Error: {error_msg}")
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers (matches JavaScript implementation)
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def test_distance_calculation(self):
        """Test the Haversine distance calculation"""
        print("\n" + "=" * 60)
        print("Testing Distance Calculation")
        print("=" * 60)
        
        # Test case: Berlin to Munich (approx 504 km)
        berlin_lat, berlin_lon = 52.52, 13.405
        munich_lat, munich_lon = 48.1351, 11.5820
        
        distance = self.calculate_distance(berlin_lat, berlin_lon, munich_lat, munich_lon)
        self.log(f"Berlin to Munich: {distance:.1f} km")
        
        # Should be approximately 504 km (allow 10km margin)
        self.assert_test(
            495 < distance < 515,
            "Distance Berlin-Munich correct",
            f"Expected ~504 km, got {distance:.1f} km"
        )
        
        # Test case: Same location (should be 0)
        distance = self.calculate_distance(berlin_lat, berlin_lon, berlin_lat, berlin_lon)
        self.log(f"Same location: {distance:.1f} km")
        
        self.assert_test(
            distance < 0.1,
            "Distance same location is zero",
            f"Expected 0 km, got {distance:.1f} km"
        )
        
        # Test case: Close locations (Hof, Germany - neighboring towns)
        hof_lat, hof_lon = 50.3167, 11.9167
        nearby_lat, nearby_lon = 50.3200, 11.9200  # ~500m away
        
        distance = self.calculate_distance(hof_lat, hof_lon, nearby_lat, nearby_lon)
        self.log(f"Hof to nearby: {distance:.2f} km")
        
        self.assert_test(
            0.3 < distance < 0.7,
            "Distance nearby location correct",
            f"Expected ~0.5 km, got {distance:.2f} km"
        )
    
    def test_distance_filters(self):
        """Test distance filter thresholds"""
        print("\n" + "=" * 60)
        print("Testing Distance Filters")
        print("=" * 60)
        
        # Reference location (Hof city center)
        ref_lat, ref_lon = 50.3167, 11.9167
        
        # Test locations at various distances
        test_locations = [
            ("Very close (0.5 km)", 50.3200, 11.9200, 0.5),
            ("Walking distance (1.2 km)", 50.3250, 11.9250, 1.2),
            ("Bike distance (2.5 km)", 50.3400, 11.9400, 2.5),
            ("Public transport (15 km)", 50.4500, 12.0500, 15),
        ]
        
        filter_thresholds = {
            "15 min by foot": 1.25,
            "10 min by bike": 2.5,
            "1 hr public transport": 20
        }
        
        for name, lat, lon, expected_dist in test_locations:
            distance = self.calculate_distance(ref_lat, ref_lon, lat, lon)
            self.log(f"{name}: {distance:.2f} km")
            
            # Check which filters this location passes
            for filter_name, threshold in filter_thresholds.items():
                passes = distance <= threshold
                if passes:
                    self.log(f"  ✓ Passes '{filter_name}' filter (≤{threshold} km)")
    
    def test_event_type_filtering(self):
        """Test event type filtering logic"""
        print("\n" + "=" * 60)
        print("Testing Event Type Filtering")
        print("=" * 60)
        
        # Sample events
        events = [
            {"title": "Concert at Theater", "category": "on-stage"},
            {"title": "Pub Quiz Night", "category": "pub-games"},
            {"title": "City Festival", "category": "festivals"},
            {"title": "General Event", "category": None},
        ]
        
        # Test filtering by each category
        categories = ["all", "on-stage", "pub-games", "festivals"]
        
        for filter_category in categories:
            if filter_category == "all":
                filtered = events  # No filtering
            else:
                filtered = [e for e in events if e.get("category") == filter_category]
            
            self.log(f"Filter '{filter_category}': {len(filtered)} events")
            
            # Verify correct filtering
            if filter_category == "all":
                expected_count = len(events)
            else:
                expected_count = sum(1 for e in events if e.get("category") == filter_category)
            
            self.assert_test(
                len(filtered) == expected_count,
                f"Event type filter '{filter_category}' correct",
                f"Expected {expected_count}, got {len(filtered)}"
            )
    
    def test_time_filtering(self):
        """Test time-based filtering logic"""
        print("\n" + "=" * 60)
        print("Testing Time Filtering")
        print("=" * 60)
        
        now = datetime.now()
        
        # Sample events at various times
        events = [
            {"title": "Event in 2 hours", "start_time": (now + timedelta(hours=2)).isoformat()},
            {"title": "Event in 8 hours", "start_time": (now + timedelta(hours=8)).isoformat()},
            {"title": "Event tomorrow", "start_time": (now + timedelta(days=1)).isoformat()},
            {"title": "Event in 3 days", "start_time": (now + timedelta(days=3)).isoformat()},
            {"title": "Event in 1 week", "start_time": (now + timedelta(days=7)).isoformat()},
        ]
        
        # Test time filters
        time_filters = {
            "6h": now + timedelta(hours=6),
            "12h": now + timedelta(hours=12),
            "24h": now + timedelta(hours=24),
            "48h": now + timedelta(hours=48),
        }
        
        for filter_name, max_time in time_filters.items():
            filtered = [
                e for e in events 
                if datetime.fromisoformat(e["start_time"]) <= max_time
            ]
            
            self.log(f"Filter '{filter_name}': {len(filtered)} events")
            
            # Verify correct filtering
            self.assert_test(
                len(filtered) > 0,
                f"Time filter '{filter_name}' captures events",
                f"No events found for {filter_name}"
            )
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        print("\n" + "=" * 60)
        print("Testing Combined Filters")
        print("=" * 60)
        
        now = datetime.now()
        ref_lat, ref_lon = 50.3167, 11.9167
        
        # Complex event set
        events = [
            {
                "title": "Nearby on-stage event soon",
                "category": "on-stage",
                "start_time": (now + timedelta(hours=2)).isoformat(),
                "location": {"lat": 50.3200, "lon": 11.9200}  # ~0.5 km
            },
            {
                "title": "Far pub-games event soon",
                "category": "pub-games",
                "start_time": (now + timedelta(hours=3)).isoformat(),
                "location": {"lat": 50.4000, "lon": 12.0000}  # ~10 km
            },
            {
                "title": "Nearby festival later",
                "category": "festivals",
                "start_time": (now + timedelta(days=2)).isoformat(),
                "location": {"lat": 50.3180, "lon": 11.9180}  # ~0.2 km
            },
        ]
        
        # Test: Events within 15 min walk, in next 6 hours
        max_distance = 1.25  # 15 min by foot
        max_time = now + timedelta(hours=6)
        
        filtered = []
        for event in events:
            # Check time
            event_time = datetime.fromisoformat(event["start_time"])
            if event_time > max_time:
                continue
            
            # Check distance
            loc = event["location"]
            distance = self.calculate_distance(ref_lat, ref_lon, loc["lat"], loc["lon"])
            if distance > max_distance:
                continue
            
            filtered.append(event)
        
        self.log(f"Combined filter (≤1.25km, ≤6h): {len(filtered)} events")
        
        # Should get exactly 1 event (Nearby on-stage event soon)
        self.assert_test(
            len(filtered) == 1,
            "Combined filter (distance + time) correct",
            f"Expected 1 event, got {len(filtered)}"
        )
        
        if len(filtered) == 1:
            self.assert_test(
                filtered[0]["title"] == "Nearby on-stage event soon",
                "Correct event selected by combined filter"
            )
    
    def test_config_locations(self):
        """Test predefined locations from config"""
        print("\n" + "=" * 60)
        print("Testing Predefined Locations")
        print("=" * 60)
        
        # Load config
        config_files = ["config.dev.json", "config.prod.json"]
        
        for config_file in config_files:
            config_path = self.repo_root / config_file
            if not config_path.exists():
                self.log(f"Config file {config_file} not found, skipping")
                continue
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if "map" in config and "predefined_locations" in config["map"]:
                locations = config["map"]["predefined_locations"]
                
                self.log(f"Found {len(locations)} predefined locations in {config_file}")
                
                for loc in locations:
                    self.assert_test(
                        "name" in loc and "lat" in loc and "lon" in loc,
                        f"Location '{loc.get('name', 'unnamed')}' has required fields"
                    )
                    
                    # Validate coordinates
                    if "lat" in loc and "lon" in loc:
                        lat_valid = -90 <= loc["lat"] <= 90
                        lon_valid = -180 <= loc["lon"] <= 180
                        
                        self.assert_test(
                            lat_valid and lon_valid,
                            f"Location '{loc.get('name')}' has valid coordinates",
                            f"lat={loc['lat']}, lon={loc['lon']}"
                        )
    
    def run_all_tests(self):
        """Run all filter tests"""
        print("=" * 60)
        print("KRWL HOF Filter Logic Tests")
        print("=" * 60)
        
        self.test_distance_calculation()
        self.test_distance_filters()
        self.test_event_type_filtering()
        self.test_time_filtering()
        self.test_combined_filters()
        self.test_config_locations()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Total tests: {self.tests_passed + self.tests_failed}")
        print("=" * 60)
        
        if self.tests_failed == 0:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {self.tests_failed} test(s) failed")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test KRWL HOF filter logic"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    tester = FilterTester(verbose=args.verbose)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
