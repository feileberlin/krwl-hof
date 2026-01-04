#!/usr/bin/env python3
"""
Tests for the event archiving module

This test suite validates the configurable monthly event archiving system,
including configuration loading, event archiving logic, and archive organization.
"""

import sys
import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.archive_events import EventArchiver, print_config_info


class TestEventArchiver(unittest.TestCase):
    """Test the EventArchiver class and its functionality"""
    
    def setUp(self):
        """
        Set up test fixtures.
        
        Creates temporary directories and config files for testing
        without affecting actual event data.
        """
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create required directory structure
        events_dir = self.base_path / 'assets' / 'json'
        events_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration
        self.test_config = {
            "app": {"name": "Test App"},
            "archiving": {
                "enabled": True,
                "schedule": {
                    "day_of_month": 1,
                    "time": "02:00",
                    "timezone": "UTC"
                },
                "retention": {
                    "active_window_days": 60
                },
                "organization": {
                    "group_by": "month",
                    "format": "YYYYMM",
                    "path": "assets/json/events/archived"
                }
            }
        }
        
        # Create test events
        self.test_events = {
            "events": [
                {
                    "id": "old_event_1",
                    "title": "Old Event 1",
                    "start": (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
                    "category": "test"
                },
                {
                    "id": "old_event_2",
                    "title": "Old Event 2",
                    "start": (datetime.now() - timedelta(days=75)).strftime('%Y-%m-%d'),
                    "category": "test"
                },
                {
                    "id": "recent_event_1",
                    "title": "Recent Event 1",
                    "start": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    "category": "test"
                },
                {
                    "id": "recent_event_2",
                    "title": "Recent Event 2",
                    "start": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
                    "category": "test"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        # Save test events to file
        events_file = events_dir / 'events.json'
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_events, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures by removing temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_archiver_initialization(self):
        """Test EventArchiver initialization with valid config"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        self.assertTrue(archiver.enabled)
        self.assertEqual(archiver.retention_days, 60)
        self.assertEqual(archiver.format, 'YYYYMM')
        self.assertTrue(archiver.archive_path.exists())
    
    def test_archiver_initialization_with_defaults(self):
        """Test EventArchiver initialization uses defaults for missing config"""
        minimal_config = {"app": {"name": "Test"}}
        archiver = EventArchiver(minimal_config, self.base_path)
        
        # Should use defaults
        self.assertTrue(archiver.enabled)
        self.assertEqual(archiver.retention_days, 60)
    
    def test_get_config_info(self):
        """Test getting archiving configuration information"""
        archiver = EventArchiver(self.test_config, self.base_path)
        info = archiver.get_config_info()
        
        self.assertIn('enabled', info)
        self.assertIn('retention_days', info)
        self.assertIn('schedule', info)
        self.assertIn('archive_path', info)
        self.assertEqual(info['enabled'], True)
        self.assertEqual(info['retention_days'], 60)
    
    def test_get_archive_filename(self):
        """Test archive filename generation"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        test_date = datetime(2026, 1, 15)
        filename = archiver._get_archive_filename(test_date)
        
        self.assertEqual(filename, '202601.json')
    
    def test_get_archive_filename_with_dash_format(self):
        """Test archive filename with YYYY-MM format"""
        config = self.test_config.copy()
        config['archiving']['organization']['format'] = 'YYYY-MM'
        archiver = EventArchiver(config, self.base_path)
        
        test_date = datetime(2026, 1, 15)
        filename = archiver._get_archive_filename(test_date)
        
        self.assertEqual(filename, '2026-01.json')
    
    def test_parse_event_date_iso_format(self):
        """Test parsing ISO format event dates"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        # Test ISO format with timezone
        date_str = "2026-01-15T10:30:00Z"
        parsed = archiver._parse_event_date(date_str)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 1)
        self.assertEqual(parsed.day, 15)
    
    def test_parse_event_date_simple_format(self):
        """Test parsing simple date format"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        date_str = "2026-01-15"
        parsed = archiver._parse_event_date(date_str)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 1)
    
    def test_parse_event_date_invalid(self):
        """Test parsing invalid event dates returns None"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        self.assertIsNone(archiver._parse_event_date(None))
        self.assertIsNone(archiver._parse_event_date("invalid-date"))
        self.assertIsNone(archiver._parse_event_date(""))
    
    def test_archive_events_dry_run(self):
        """Test archiving in dry-run mode (no file changes)"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        results = archiver.archive_events(dry_run=True)
        
        self.assertTrue(results['enabled'])
        self.assertTrue(results['dry_run'])
        self.assertEqual(results['total_events'], 4)
        self.assertEqual(results['archived_count'], 2)  # 2 events older than 60 days
        self.assertEqual(results['active_count'], 2)    # 2 events within 60 days
        
        # Verify no files were created (dry run)
        archive_files = list(archiver.archive_path.glob('*.json'))
        self.assertEqual(len(archive_files), 0)
    
    def test_archive_events_actual_run(self):
        """Test actual archiving operation (creates files)"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        results = archiver.archive_events(dry_run=False)
        
        self.assertTrue(results['enabled'])
        self.assertFalse(results['dry_run'])
        self.assertEqual(results['archived_count'], 2)
        self.assertEqual(results['active_count'], 2)
        
        # Verify archive files were created
        archive_files = list(archiver.archive_path.glob('*.json'))
        self.assertGreater(len(archive_files), 0)
        
        # Verify events.json was updated
        events_file = self.base_path / 'assets' / 'json' / 'events.json'
        with open(events_file, 'r', encoding='utf-8') as f:
            updated_events = json.load(f)
        
        self.assertEqual(len(updated_events['events']), 2)
        
        # Verify only recent events remain
        event_ids = [e['id'] for e in updated_events['events']]
        self.assertIn('recent_event_1', event_ids)
        self.assertIn('recent_event_2', event_ids)
        self.assertNotIn('old_event_1', event_ids)
        self.assertNotIn('old_event_2', event_ids)
    
    def test_archive_disabled(self):
        """Test archiving when disabled in config"""
        config = self.test_config.copy()
        config['archiving']['enabled'] = False
        archiver = EventArchiver(config, self.base_path)
        
        results = archiver.archive_events(dry_run=False)
        
        self.assertFalse(results['enabled'])
        self.assertIn('message', results)
    
    def test_list_archives_empty(self):
        """Test listing archives when none exist"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        archives = archiver.list_archives()
        
        self.assertEqual(len(archives), 0)
    
    def test_list_archives_with_files(self):
        """Test listing archives after archiving"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        # Create archives
        archiver.archive_events(dry_run=False)
        
        # List them
        archives = archiver.list_archives()
        
        self.assertGreater(len(archives), 0)
        
        # Verify archive structure
        for archive in archives:
            self.assertIn('filename', archive)
            self.assertIn('period', archive)
            self.assertIn('event_count', archive)
            self.assertIn('last_updated', archive)
    
    def test_load_and_save_archive_file(self):
        """Test loading and saving archive files"""
        archiver = EventArchiver(self.test_config, self.base_path)
        
        filename = '202601.json'
        test_data = {
            'archived_events': [
                {'id': 'test1', 'title': 'Test Event 1'},
                {'id': 'test2', 'title': 'Test Event 2'}
            ]
        }
        
        # Save archive
        archiver._save_archive_file(filename, test_data)
        
        # Load it back
        loaded_data = archiver._load_archive_file(filename)
        
        self.assertEqual(len(loaded_data['archived_events']), 2)
        self.assertEqual(loaded_data['archived_events'][0]['id'], 'test1')
        self.assertIn('last_updated', loaded_data)
    
    def test_archive_events_without_start_date(self):
        """Test handling events without start date (should be kept active)"""
        # Add event without start date
        self.test_events['events'].append({
            'id': 'no_date_event',
            'title': 'Event Without Date',
            'category': 'test'
        })
        
        events_file = self.base_path / 'assets' / 'json' / 'events.json'
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_events, f)
        
        archiver = EventArchiver(self.test_config, self.base_path)
        archiver.archive_events(dry_run=False)
        
        # Event without date should remain active
        events_file = self.base_path / 'assets' / 'json' / 'events.json'
        with open(events_file, 'r', encoding='utf-8') as f:
            updated_events = json.load(f)
        
        event_ids = [e['id'] for e in updated_events['events']]
        self.assertIn('no_date_event', event_ids)


class TestPrintConfigInfo(unittest.TestCase):
    """Test the print_config_info helper function"""
    
    def test_print_config_info(self):
        """Test that print_config_info runs without errors"""
        temp_dir = tempfile.mkdtemp()
        base_path = Path(temp_dir)
        
        config = {
            "app": {"name": "Test"},
            "archiving": {
                "enabled": True,
                "schedule": {
                    "day_of_month": 1,
                    "time": "02:00",
                    "timezone": "UTC"
                },
                "retention": {
                    "active_window_days": 60
                },
                "organization": {
                    "path": "assets/json/events/archived"
                }
            }
        }
        
        try:
            archiver = EventArchiver(config, base_path)
            # Should not raise any exceptions
            print_config_info(archiver)
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    # Run tests with verbose output
    print("Running Event Archiving Tests...")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEventArchiver))
    suite.addTests(loader.loadTestsFromTestCase(TestPrintConfigInfo))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Event Archiving Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All event archiving tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some event archiving tests failed!")
        sys.exit(1)
