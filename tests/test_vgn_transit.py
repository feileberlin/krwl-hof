#!/usr/bin/env python3
"""
Tests for VGN Transit Integration Module

Tests reachability analysis, source suggestion, and transit data features.
"""

import json
import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.vgn_transit import VGNTransit, ReachableStation, RegionalSource
from modules.utils import load_config


class TestVGNTransit(unittest.TestCase):
    """Test VGN Transit Integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_path = Path(__file__).parent.parent
        self.config = load_config(self.base_path)
        
        # Create test config with VGN enabled
        self.test_config = self.config.copy()
        self.test_config['vgn'] = {
            'enabled': True,
            'reference_location': {
                'name': 'Hof Hauptbahnhof',
                'lat': 50.308053,
                'lon': 11.9233
            },
            'reachability': {
                'max_travel_time_minutes': 30,
                'max_transfers': 2
            },
            'analysis': {
                'cache_hours': 24,
                'output_path': 'assets/json/vgn_analysis.json'
            },
            'source_discovery': {
                'enabled': True,
                'categories': ['community', 'culture', 'news']
            }
        }
        
        self.vgn = VGNTransit(self.test_config, self.base_path)
    
    def test_vgn_initialization(self):
        """Test VGN Transit initialization"""
        self.assertIsNotNone(self.vgn)
        self.assertEqual(self.vgn.reference_lat, 50.308053)
        self.assertEqual(self.vgn.reference_lon, 11.9233)
        self.assertEqual(self.vgn.enabled, True)
    
    def test_is_available(self):
        """Test VGN availability check"""
        # Note: This will fail if VGN library is not installed, which is expected
        result = self.vgn.is_available()
        self.assertIsInstance(result, bool)
        
        if not result:
            print("⚠️  VGN library not installed - skipping integration tests")
            print("   Install with: pip install vgn")
    
    def test_get_reachable_stations_mock(self):
        """Test getting reachable stations (mock data)"""
        # This test uses mock data, so it should work even without VGN library
        stations = self.vgn._get_mock_reachable_stations(30)
        
        self.assertIsInstance(stations, list)
        self.assertGreater(len(stations), 0, "Should return at least one station")
        
        # Check first station is Hof Hauptbahnhof (0 minutes away)
        hof_hbf = stations[0]
        self.assertEqual(hof_hbf.name, "Hof Hauptbahnhof")
        self.assertEqual(hof_hbf.travel_time_minutes, 0)
        self.assertEqual(hof_hbf.municipality, "Hof")
        
        # All stations should be within 30 minutes
        for station in stations:
            self.assertLessEqual(station.travel_time_minutes, 30)
    
    def test_get_reachable_municipalities(self):
        """Test getting reachable municipalities"""
        municipalities = self.vgn.get_reachable_municipalities(30)
        
        self.assertIsInstance(municipalities, list)
        
        if len(municipalities) > 0:
            # Check structure of first municipality
            muni = municipalities[0]
            self.assertIn('name', muni)
            self.assertIn('stations', muni)
            self.assertIn('station_count', muni)
            self.assertIn('min_travel_time', muni)
            
            # Hof should be in the list with 0 min travel time
            hof_muni = next((m for m in municipalities if m['name'] == 'Hof'), None)
            if hof_muni:
                self.assertEqual(hof_muni['min_travel_time'], 0)
    
    def test_suggest_event_sources(self):
        """Test event source suggestion"""
        sources = self.vgn.suggest_event_sources(30)
        
        self.assertIsInstance(sources, list)
        
        if len(sources) > 0:
            # Check structure of first source
            source = sources[0]
            self.assertIsInstance(source, RegionalSource)
            self.assertIsNotNone(source.name)
            self.assertIsNotNone(source.url)
            self.assertIsNotNone(source.type)
            self.assertIsNotNone(source.municipality)
    
    def test_load_regional_source_database(self):
        """Test loading regional source database"""
        db = self.vgn._load_regional_source_database()
        
        self.assertIsInstance(db, dict)
        
        # Should have default sources for Hof
        self.assertIn('Hof', db)
        hof_sources = db['Hof']
        self.assertIsInstance(hof_sources, list)
        self.assertGreater(len(hof_sources), 0)
        
        # Check structure of first source
        if len(hof_sources) > 0:
            source = hof_sources[0]
            self.assertIn('name', source)
            self.assertIn('type', source)
            self.assertIn('url', source)
            self.assertIn('category', source)
    
    def test_export_analysis_report(self):
        """Test exporting analysis report"""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            report = self.vgn.export_analysis_report(30, output_path)
            
            # Check report structure
            self.assertIn('generated_at', report)
            self.assertIn('reference_location', report)
            self.assertIn('max_travel_time_minutes', report)
            self.assertIn('reachable_stations', report)
            self.assertIn('reachable_municipalities', report)
            self.assertIn('suggested_sources', report)
            
            # Check file was created
            self.assertTrue(output_path.exists())
            
            # Verify file is valid JSON
            with open(output_path, 'r') as f:
                saved_report = json.load(f)
                self.assertEqual(saved_report['max_travel_time_minutes'], 30)
        
        finally:
            # Cleanup
            if output_path.exists():
                output_path.unlink()
    
    def test_reachable_station_dataclass(self):
        """Test ReachableStation dataclass"""
        station = ReachableStation(
            name="Test Station",
            id="test_station",
            municipality="Test City",
            latitude=50.0,
            longitude=11.0,
            travel_time_minutes=15,
            transfers=1,
            line="S1"
        )
        
        self.assertEqual(station.name, "Test Station")
        self.assertEqual(station.travel_time_minutes, 15)
        self.assertEqual(station.line, "S1")
    
    def test_regional_source_dataclass(self):
        """Test RegionalSource dataclass"""
        source = RegionalSource(
            name="Test Source",
            type="html",
            url="https://example.com",
            municipality="Test City",
            category="community",
            description="Test source description",
            distance_km=10.0,
            travel_time_minutes=20
        )
        
        self.assertEqual(source.name, "Test Source")
        self.assertEqual(source.type, "html")
        self.assertEqual(source.travel_time_minutes, 20)
    
    def test_cultural_venue_dataclass(self):
        """Test CulturalVenue dataclass"""
        from modules.vgn_transit import CulturalVenue
        
        venue = CulturalVenue(
            name="Test Museum",
            venue_type="museum",
            latitude=50.3,
            longitude=11.9,
            address="Test Street 1",
            website="https://test-museum.de",
            nearest_station="Hof Hbf",
            distance_to_station_km=0.5,
            travel_time_minutes=0,
            osm_id="node/12345"
        )
        
        self.assertEqual(venue.name, "Test Museum")
        self.assertEqual(venue.venue_type, "museum")
        self.assertEqual(venue.nearest_station, "Hof Hbf")
    
    def test_calculate_distance(self):
        """Test distance calculation (Haversine formula)"""
        # Distance between Hof and Rehau (approx 10.4 km)
        distance = self.vgn._calculate_distance(
            50.308053, 11.9233,  # Hof
            50.2489, 12.0364     # Rehau
        )
        
        # Check distance is reasonable (between 10 and 11 km)
        self.assertGreater(distance, 10.0)
        self.assertLess(distance, 11.0)
    
    def test_discover_venues_disabled(self):
        """Test venue discovery when VGN is disabled"""
        disabled_config = self.test_config.copy()
        disabled_config['vgn']['enabled'] = False
        
        vgn_disabled = VGNTransit(disabled_config, self.base_path)
        
        # Should return empty list gracefully
        venues = vgn_disabled.discover_cultural_venues(
            radius_km=5.0,
            max_travel_time_minutes=30
        )
        
        self.assertEqual(venues, [])
    
    def test_config_disabled_vgn(self):
        """Test behavior when VGN is disabled in config"""
        disabled_config = self.test_config.copy()
        disabled_config['vgn']['enabled'] = False
        
        vgn_disabled = VGNTransit(disabled_config, self.base_path)
        
        self.assertEqual(vgn_disabled.enabled, False)
        self.assertEqual(vgn_disabled.is_available(), False)
        
        # Operations should return empty/None gracefully
        stations = vgn_disabled.get_reachable_stations(30)
        self.assertEqual(stations, [])


def run_tests(verbose=False):
    """Run all VGN transit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVGNTransit)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()


if __name__ == '__main__':
    # Parse command line args
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    # Run tests
    success = run_tests(verbose=verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
