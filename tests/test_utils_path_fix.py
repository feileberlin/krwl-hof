#!/usr/bin/env python3
"""
Test to verify utils.py functions use the correct 'public/' directory path
instead of the deprecated 'target/' directory.
"""

import sys
import unittest
import json
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.utils import update_events_in_html, archive_old_events


class TestUtilsPathFix(unittest.TestCase):
    """Test that utils.py functions reference the correct directory paths"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create required directory structure
        assets_dir = self.base_path / 'assets' / 'json'
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        public_dir = self.base_path / 'public'
        public_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test events.json
        test_events = {
            "events": [
                {
                    "id": "test_event_1",
                    "title": "Test Event 1",
                    "start": "2026-03-15T10:00:00Z",
                    "category": "test"
                }
            ],
            "last_updated": "2026-01-17T16:00:00Z"
        }
        
        with open(assets_dir / 'events.json', 'w', encoding='utf-8') as f:
            json.dump(test_events, f, indent=2)
        
        # Create test index.html with EVENTS placeholder
        test_html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<script>
const EVENTS = [];
</script>
</body>
</html>"""
        
        with open(public_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(test_html)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_update_events_in_html_uses_public_directory(self):
        """Verify update_events_in_html looks for index.html in public/ directory"""
        # This function should find public/index.html, not target/index.html
        result = update_events_in_html(self.base_path)
        
        # Should succeed because public/index.html exists
        self.assertTrue(result, "update_events_in_html should succeed when public/index.html exists")
        
        # Verify the HTML was actually updated
        index_path = self.base_path / 'public' / 'index.html'
        with open(index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # The EVENTS array should now contain the test event
        self.assertIn('test_event_1', html_content, "HTML should contain the test event ID")
        self.assertIn('Test Event 1', html_content, "HTML should contain the test event title")
    
    def test_update_events_in_html_fails_without_public_directory(self):
        """Verify update_events_in_html fails gracefully if public/index.html doesn't exist"""
        # Remove public/index.html
        index_path = self.base_path / 'public' / 'index.html'
        index_path.unlink()
        
        # Should fail because public/index.html is missing
        result = update_events_in_html(self.base_path)
        self.assertFalse(result, "update_events_in_html should fail when public/index.html is missing")
    
    def test_archive_old_events_uses_public_directory(self):
        """Verify archive_old_events saves archived_events.json to public/ directory"""
        # Add an old event to trigger archiving
        assets_dir = self.base_path / 'assets' / 'json'
        events_file = assets_dir / 'events.json'
        
        with open(events_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        # Add an event that has already passed (2020)
        events_data['events'].append({
            "id": "old_event",
            "title": "Old Event",
            "start_time": "2020-01-01T10:00:00Z",
            "end_time": "2020-01-01T12:00:00Z",
            "category": "test"
        })
        
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events_data, f, indent=2)
        
        # Run archiving
        archived_count = archive_old_events(self.base_path)
        
        # Should have archived 1 event
        self.assertEqual(archived_count, 1, "Should archive 1 old event")
        
        # Verify archived_events.json was created in public/ directory
        archive_path = self.base_path / 'public' / 'archived_events.json'
        self.assertTrue(archive_path.exists(), "archived_events.json should exist in public/ directory")
        
        # Verify the archived event is in the file
        with open(archive_path, 'r', encoding='utf-8') as f:
            archive_data = json.load(f)
        
        self.assertEqual(len(archive_data['archived_events']), 1, "Should have 1 archived event")
        self.assertEqual(archive_data['archived_events'][0]['id'], 'old_event', "Should archive the old event")
    
    def test_no_target_directory_references(self):
        """Verify that functions don't try to access the old 'target/' directory"""
        # The functions should work even if target/ directory doesn't exist
        # (because they should be using public/ instead)
        
        # Explicitly verify target/ doesn't exist
        target_dir = self.base_path / 'target'
        self.assertFalse(target_dir.exists(), "target/ directory should not exist in test setup")
        
        # Both functions should work without target/
        result = update_events_in_html(self.base_path)
        self.assertTrue(result, "update_events_in_html should work without target/ directory")


if __name__ == '__main__':
    print("Running Utils Path Fix Tests...")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestUtilsPathFix)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("Utils Path Fix Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All utils path fix tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some utils path fix tests failed!")
        sys.exit(1)
