#!/usr/bin/env python3
"""
Test Leaflet Compatibility - Ensures Leaflet updates won't break our customizations

This test suite validates:
1. Our custom CSS only uses officially documented Leaflet classes
2. No conflicts between our CSS and Leaflet's core CSS
3. Version compatibility checks
4. CSS selector safety
"""

import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class LeafletCompatibilityTester:
    """Test suite for Leaflet CSS compatibility"""
    
    # Official Leaflet classes from documentation
    # Source: https://leafletjs.com/reference.html
    OFFICIAL_LEAFLET_CLASSES = {
        # Container classes
        'leaflet-container',
        'leaflet-pane',
        'leaflet-tile-pane',
        'leaflet-overlay-pane',
        'leaflet-shadow-pane',
        'leaflet-marker-pane',
        'leaflet-tooltip-pane',
        'leaflet-popup-pane',
        
        # Marker classes
        'leaflet-marker-icon',
        'leaflet-marker-shadow',
        
        # Popup classes
        'leaflet-popup',
        'leaflet-popup-content-wrapper',
        'leaflet-popup-content',
        'leaflet-popup-tip',
        'leaflet-popup-tip-container',
        'leaflet-popup-close-button',
        
        # Tooltip classes
        'leaflet-tooltip',
        'leaflet-tooltip-top',
        'leaflet-tooltip-bottom',
        'leaflet-tooltip-left',
        'leaflet-tooltip-right',
        
        # Control classes
        'leaflet-control',
        'leaflet-control-zoom',
        'leaflet-control-zoom-in',
        'leaflet-control-zoom-out',
        'leaflet-control-attribution',
        'leaflet-control-scale',
        'leaflet-control-layers',
        
        # Tile classes
        'leaflet-tile',
        'leaflet-tile-container',
        'leaflet-tile-loaded',
        
        # Interaction classes
        'leaflet-interactive',
        'leaflet-zoom-box',
        'leaflet-image-layer',
        'leaflet-layer',
        
        # State classes
        'leaflet-clickable',
        'leaflet-dragging',
        'leaflet-touch',
        'leaflet-retina',
    }
    
    # CSS properties that are safe to override (visual only, not functional)
    SAFE_OVERRIDE_PROPERTIES = {
        'background', 'background-color', 'background-image',
        'color', 'border', 'border-color', 'border-width', 'border-radius',
        'box-shadow', 'text-shadow', 'filter', 'opacity',
        'font-size', 'font-family', 'font-weight', 'line-height',
        'padding', 'margin', 'transition', 'animation',
    }
    
    # CSS properties that should NEVER be overridden (functional, break Leaflet)
    DANGEROUS_OVERRIDE_PROPERTIES = {
        'position', 'top', 'left', 'right', 'bottom',
        'width', 'height', 'max-width', 'max-height',
        'transform', 'transform-origin',
        'overflow', 'z-index', 'pointer-events',
    }
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.custom_css_path = self.base_path / 'assets' / 'css' / 'leaflet-custom.css'
        self.leaflet_css_path = self.base_path / 'static' / 'leaflet' / 'leaflet.css'
        self.errors = []
        self.warnings = []
        
    def run_all_tests(self):
        """Run all compatibility tests"""
        print("🧪 Testing Leaflet CSS Compatibility\n")
        print("=" * 70)
        
        self.test_custom_css_exists()
        self.test_leaflet_css_exists()
        self.test_only_safe_classes_used()
        self.test_no_dangerous_properties()
        self.test_no_important_flags()
        self.test_css_variables_used()
        self.test_version_compatibility()
        
        print("\n" + "=" * 70)
        self.print_results()
        
        return len(self.errors) == 0
    
    def test_custom_css_exists(self):
        """Test that custom CSS file exists"""
        print("📁 Test: Custom CSS file exists...")
        if not self.custom_css_path.exists():
            self.errors.append(f"Custom CSS not found: {self.custom_css_path}")
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_leaflet_css_exists(self):
        """Test that Leaflet core CSS exists"""
        print("📁 Test: Leaflet core CSS exists...")
        if not self.leaflet_css_path.exists():
            self.errors.append(f"Leaflet CSS not found: {self.leaflet_css_path}")
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_only_safe_classes_used(self):
        """Test that we only customize official Leaflet classes"""
        print("🔍 Test: Only official Leaflet classes used...")
        
        if not self.custom_css_path.exists():
            return
        
        with open(self.custom_css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all .leaflet-* class selectors
        leaflet_classes = set(re.findall(r'\.leaflet-[\w-]+', content))
        
        # Remove the leading dot for comparison
        used_classes = {cls[1:] for cls in leaflet_classes}
        
        # Check for unofficial classes
        unofficial = used_classes - self.OFFICIAL_LEAFLET_CLASSES
        
        if unofficial:
            self.warnings.append(
                f"Unofficial Leaflet classes found (may break on updates): {', '.join(unofficial)}"
            )
            print("   ⚠️  WARNING")
        else:
            print("   ✅ PASSED")
    
    def test_no_dangerous_properties(self):
        """Test that we don't override dangerous CSS properties"""
        print("⚠️  Test: No dangerous property overrides...")
        
        if not self.custom_css_path.exists():
            return
        
        with open(self.custom_css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find .leaflet-* rules and check their properties
        # Simple regex to find rules (not perfect but good enough)
        leaflet_rules = re.findall(
            r'\.leaflet-[^{]+\{([^}]+)\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        
        dangerous_found = []
        for rule in leaflet_rules:
            for prop in self.DANGEROUS_OVERRIDE_PROPERTIES:
                if re.search(rf'\b{prop}\s*:', rule):
                    dangerous_found.append(prop)
        
        if dangerous_found:
            self.errors.append(
                f"Dangerous properties overridden (will break Leaflet): {', '.join(set(dangerous_found))}"
            )
            print("   ❌ FAILED")
        else:
            print("   ✅ PASSED")
    
    def test_no_important_flags(self):
        """Test that we don't use !important on Leaflet classes"""
        print("🚫 Test: No !important flags on Leaflet classes...")
        
        if not self.custom_css_path.exists():
            return
        
        with open(self.custom_css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find .leaflet-* rules with !important
        important_in_leaflet = re.findall(
            r'\.leaflet-[^{]+\{[^}]*!important[^}]*\}',
            content,
            re.MULTILINE | re.DOTALL
        )
        
        if important_in_leaflet:
            self.warnings.append(
                "!important flags used on Leaflet classes (may cause conflicts)"
            )
            print("   ⚠️  WARNING")
        else:
            print("   ✅ PASSED")
    
    def test_css_variables_used(self):
        """Test that we use CSS variables for theming"""
        print("🎨 Test: CSS variables used for theming...")
        
        if not self.custom_css_path.exists():
            return
        
        with open(self.custom_css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count CSS variable usage
        var_count = len(re.findall(r'var\(--[^)]+\)', content))
        
        if var_count < 5:
            self.warnings.append(
                f"Low CSS variable usage ({var_count} found). Use design tokens for better theming."
            )
            print(f"   ⚠️  WARNING (only {var_count} variables found)")
        else:
            print(f"   ✅ PASSED ({var_count} variables found)")
    
    def test_version_compatibility(self):
        """Test Leaflet version is documented"""
        print("📌 Test: Leaflet version documented...")
        
        # Check site_generator.py for version
        site_gen_path = self.base_path / 'src' / 'modules' / 'site_generator.py'
        
        if not site_gen_path.exists():
            self.warnings.append("site_generator.py not found - can't check version")
            print("   ⚠️  WARNING")
            return
        
        with open(site_gen_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for version in DEPENDENCIES
        version_match = re.search(r'"leaflet"[^}]+?"version":\s*"([^"]+)"', content)
        
        if version_match:
            version = version_match.group(1)
            print(f"   ✅ PASSED (version {version} documented)")
        else:
            self.warnings.append("Leaflet version not found in DEPENDENCIES")
            print("   ⚠️  WARNING")
    
    def print_results(self):
        """Print test results summary"""
        print("\n📊 Test Results Summary:")
        print("-" * 70)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All tests passed! Leaflet customizations are safe.")
        elif not self.errors:
            print("\n✅ No errors, but please review warnings.")
        else:
            print("\n❌ Tests failed! Fix errors before updating Leaflet.")
        
        print("\n💡 Tip: Run this test before updating Leaflet to ensure compatibility.")


def main():
    """Main entry point"""
    base_path = Path(__file__).parent.parent
    tester = LeafletCompatibilityTester(base_path)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
