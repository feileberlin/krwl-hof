#!/usr/bin/env python3
"""Test dependency URL construction

This test verifies that dependency URLs are correctly constructed
with proper path separators between base_url and file paths.

Background:
- The site_generator constructs URLs by concatenating base_url + src path
- All src paths must start with '/' to avoid malformed URLs
- Example: base_url='https://unpkg.com/leaflet@1.9.4/dist' + src='/leaflet.css'
  -> 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' ✓

Regression check for GitHub issue where missing '/' caused:
- https://unpkg.com/leaflet@1.9.4/distleaflet.css ✗ (404 error)
"""

import sys
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from modules.site_generator import DEPENDENCIES


class TestDependencyURLConstruction(unittest.TestCase):
    """Test that dependency URLs are properly constructed"""
    
    def test_leaflet_urls_have_proper_separators(self):
        """Test: Leaflet src paths start with '/' for proper URL construction"""
        leaflet_config = DEPENDENCIES['leaflet']
        base_url = leaflet_config['base_url'].format(version=leaflet_config['version'])
        
        # Verify base_url doesn't end with '/'
        self.assertFalse(base_url.endswith('/'), 
                        "base_url should not end with '/' for this test to be valid")
        
        # Test each file
        for file_info in leaflet_config['files']:
            src = file_info['src']
            dest = file_info['dest']
            
            # Src path must start with '/' (unless it's empty string for special cases)
            if src:  # Non-empty src
                self.assertTrue(src.startswith('/'), 
                              f"File '{dest}' has src='{src}' which must start with '/'")
                
                # Construct URL as done in site_generator.py line 180
                url = f"{base_url}{src}"
                
                # Verify no double slashes (except in protocol)
                url_without_protocol = url.replace('https://', '').replace('http://', '')
                self.assertNotIn('//', url_without_protocol,
                                f"URL '{url}' contains double slashes")
                
                # Verify the path segment separator exists
                # The URL should have '/dist/filename' not '/distfilename'
                self.assertIn('/dist/', url, 
                            f"URL '{url}' should contain '/dist/' separator")
    
    def test_leaflet_css_url_correct(self):
        """Test: Leaflet CSS URL is correctly formed"""
        leaflet_config = DEPENDENCIES['leaflet']
        base_url = leaflet_config['base_url'].format(version=leaflet_config['version'])
        
        # Find CSS file
        css_file = next(f for f in leaflet_config['files'] if f['dest'].endswith('leaflet.css'))
        url = f"{base_url}{css_file['src']}"
        
        expected = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
        self.assertEqual(url, expected, 
                        f"CSS URL should be '{expected}' not '{url}'")
    
    def test_leaflet_js_url_correct(self):
        """Test: Leaflet JS URL is correctly formed"""
        leaflet_config = DEPENDENCIES['leaflet']
        base_url = leaflet_config['base_url'].format(version=leaflet_config['version'])
        
        # Find JS file
        js_file = next(f for f in leaflet_config['files'] if f['dest'].endswith('leaflet.js'))
        url = f"{base_url}{js_file['src']}"
        
        expected = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
        self.assertEqual(url, expected, 
                        f"JS URL should be '{expected}' not '{url}'")
    
    def test_leaflet_image_urls_correct(self):
        """Test: Leaflet image URLs are correctly formed"""
        leaflet_config = DEPENDENCIES['leaflet']
        base_url = leaflet_config['base_url'].format(version=leaflet_config['version'])
        
        # Test all image files
        expected_urls = {
            'marker-icon.png': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
            'marker-icon-2x.png': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
            'marker-shadow.png': 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png'
        }
        
        for filename, expected_url in expected_urls.items():
            image_file = next(f for f in leaflet_config['files'] 
                            if filename in f['dest'])
            url = f"{base_url}{image_file['src']}"
            
            self.assertEqual(url, expected_url, 
                           f"Image URL for {filename} should be '{expected_url}' not '{url}'")
    
    def test_lucide_urls_have_proper_separators(self):
        """Test: Lucide src paths are properly formatted"""
        lucide_config = DEPENDENCIES['lucide']
        base_url = lucide_config['base_url'].format(version=lucide_config['version'])
        
        for file_info in lucide_config['files']:
            src = file_info['src']
            dest = file_info['dest']
            
            # Non-empty src must start with '/'
            if src:
                self.assertTrue(src.startswith('/'),
                              f"Lucide file '{dest}' has src='{src}' which must start with '/'")
                
                # Construct URL
                url = f"{base_url}{src}"
                
                # Verify no double slashes (except in protocol)
                url_without_protocol = url.replace('https://', '').replace('http://', '')
                self.assertNotIn('//', url_without_protocol,
                                f"URL '{url}' contains double slashes")
    
    def test_no_malformed_urls(self):
        """Test: No URLs have missing path separators (regression test)"""
        # This is the actual bug we're fixing
        # Bad: https://unpkg.com/leaflet@1.9.4/distleaflet.css
        # Good: https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
        
        for pkg_name, pkg_config in DEPENDENCIES.items():
            base_url = pkg_config['base_url'].format(version=pkg_config['version'])
            
            for file_info in pkg_config['files']:
                if file_info['src']:  # Non-empty src
                    url = f"{base_url}{file_info['src']}"
                    
                    # Check for common malformed patterns
                    malformed_patterns = [
                        '/distleaflet',      # Missing / between dist and leaflet
                        '/distimages',       # Missing / between dist and images  
                        '/distlucide',       # Missing / between dist and lucide
                    ]
                    
                    for pattern in malformed_patterns:
                        self.assertNotIn(pattern, url,
                                       f"URL '{url}' contains malformed pattern '{pattern}'")


def run_tests():
    """Run all URL construction tests"""
    print("\n" + "=" * 70)
    print("Testing Dependency URL Construction")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDependencyURLConstruction)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✓ All URL construction tests passed!")
    else:
        print("✗ Some tests failed")
        if result.failures:
            print(f"  Failures: {len(result.failures)}")
            for test, traceback in result.failures:
                print(f"    - {test}")
        if result.errors:
            print(f"  Errors: {len(result.errors)}")
            for test, traceback in result.errors:
                print(f"    - {test}")
    print("=" * 70 + "\n")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
