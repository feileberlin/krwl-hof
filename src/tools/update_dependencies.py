#!/usr/bin/env python3
"""
One-Command Dependency Updater - Makes library updates trivial

Usage:
  python3 src/tools/update_dependencies.py --check     # Check for updates
  python3 src/tools/update_dependencies.py --update    # Update all (with tests)
  python3 src/tools/update_dependencies.py --leaflet   # Update only Leaflet
  python3 src/tools/update_dependencies.py --lucide    # Update only Lucide
  python3 src/tools/update_dependencies.py --force     # Skip tests (dangerous)
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from modules.site_generator import SiteGenerator
except ImportError:
    print("⚠️  Warning: Could not import SiteGenerator")
    SiteGenerator = None


class DependencyUpdater:
    """Automated dependency update manager"""
    
    DEPENDENCIES = {
        "leaflet": {
            "current_url": "https://unpkg.com/leaflet@1.9.4/package.json",
            "latest_url": "https://unpkg.com/leaflet@latest/package.json",
            "github": "Leaflet/Leaflet",
            "test_command": ["python3", "tests/test_leaflet_compatibility.py"],
        },
        "lucide": {
            "current_url": "https://unpkg.com/lucide@latest/package.json",
            "latest_url": "https://unpkg.com/lucide@latest/package.json",
            "github": "lucide-icons/lucide",
            "test_command": ["python3", "tests/test_lucide_compatibility.py"],
        }
    }
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.site_gen_path = base_path / 'src' / 'modules' / 'site_generator.py'
        
    def get_current_version(self, library: str) -> Optional[str]:
        """Get current version from site_generator.py"""
        if not self.site_gen_path.exists():
            return None
        
        with open(self.site_gen_path, 'r') as f:
            content = f.read()
        
        pattern = rf'"{library}"[^}}]+?"version":\s*"([^"]+)"'
        match = re.search(pattern, content)
        
        return match.group(1) if match else None
    
    def get_latest_version(self, library: str) -> Optional[str]:
        """Get latest version from npm/unpkg"""
        try:
            url = self.DEPENDENCIES[library]["latest_url"]
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                return data.get("version")
        except Exception as e:
            print(f"⚠️  Could not fetch latest version: {e}")
            return None
    
    def check_for_updates(self) -> Dict[str, Dict]:
        """Check if updates are available"""
        print("🔍 Checking for dependency updates...\n")
        
        updates = {}
        for lib in self.DEPENDENCIES.keys():
            current = self.get_current_version(lib)
            latest = self.get_latest_version(lib)
            
            print(f"📦 {lib.title()}:")
            print(f"   Current: {current or 'unknown'}")
            print(f"   Latest:  {latest or 'unknown'}")
            
            if current and latest and current != latest and latest != "latest":
                print(f"   ⬆️  Update available!")
                updates[lib] = {
                    "current": current,
                    "latest": latest,
                    "needs_update": True
                }
            else:
                print(f"   ✅ Up to date")
            
            print()
        
        return updates
    
    def update_version_in_file(self, library: str, new_version: str) -> bool:
        """Update version number in site_generator.py"""
        if not self.site_gen_path.exists():
            print(f"❌ {self.site_gen_path} not found")
            return False
        
        with open(self.site_gen_path, 'r') as f:
            content = f.read()
        
        # Find and replace version
        pattern = rf'("{library}"[^}}]+?"version":\s*)"([^"]+)"'
        new_content = re.sub(
            pattern,
            rf'\1"{new_version}"',
            content
        )
        
        if content == new_content:
            print(f"⚠️  Could not find version string for {library}")
            return False
        
        with open(self.site_gen_path, 'w') as f:
            f.write(new_content)
        
        return True
    
    def download_dependencies(self) -> bool:
        """Download dependencies using event_manager"""
        print("📥 Downloading dependencies...")
        try:
            result = subprocess.run(
                ["python3", "src/event_manager.py", "libs"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("✅ Dependencies downloaded")
                return True
            else:
                print(f"❌ Download failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def run_tests(self, library: Optional[str] = None) -> bool:
        """Run compatibility tests"""
        print("🧪 Running compatibility tests...")
        
        if library:
            # Test specific library
            libs_to_test = [library]
        else:
            # Test all libraries
            libs_to_test = list(self.DEPENDENCIES.keys())
        
        all_passed = True
        for lib in libs_to_test:
            test_cmd = self.DEPENDENCIES[lib]["test_command"]
            print(f"\n   Testing {lib}...")
            
            try:
                result = subprocess.run(
                    test_cmd,
                    cwd=self.base_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   ✅ {lib} tests passed")
                else:
                    print(f"   ❌ {lib} tests failed:")
                    print(result.stdout)
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {lib} test error: {e}")
                all_passed = False
        
        return all_passed
    
    def rebuild_site(self) -> bool:
        """Rebuild the site"""
        print("🔨 Rebuilding site...")
        try:
            result = subprocess.run(
                ["python3", "src/event_manager.py", "generate"],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Site rebuilt successfully")
                return True
            else:
                print(f"❌ Build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
    
    def update_library(self, library: str, skip_tests: bool = False) -> bool:
        """Update a specific library"""
        print(f"\n{'='*70}")
        print(f"🚀 Updating {library.title()}")
        print(f"{'='*70}\n")
        
        # 1. Get versions
        current = self.get_current_version(library)
        latest = self.get_latest_version(library)
        
        if not latest:
            print(f"❌ Could not determine latest version for {library}")
            return False
        
        print(f"📦 Version: {current} → {latest}")
        
        # 2. Update version in code
        print(f"\n📝 Updating version in site_generator.py...")
        if not self.update_version_in_file(library, latest):
            return False
        print(f"✅ Version updated")
        
        # 3. Download new files
        print()
        if not self.download_dependencies():
            print(f"❌ Failed to download {library}")
            # Rollback version change
            if current:
                self.update_version_in_file(library, current)
            return False
        
        # 4. Run tests (unless skipped)
        if not skip_tests:
            print()
            if not self.run_tests(library):
                print(f"\n❌ Tests failed for {library}")
                print(f"💡 Tip: Review test output and fix issues")
                print(f"💡 Or rollback: git checkout src/modules/site_generator.py static/")
                return False
        else:
            print("\n⚠️  Skipping tests (--force mode)")
        
        # 5. Rebuild site
        print()
        if not self.rebuild_site():
            print(f"❌ Site rebuild failed")
            return False
        
        print(f"\n{'='*70}")
        print(f"✅ Successfully updated {library.title()} to {latest}")
        print(f"{'='*70}\n")
        
        print("📋 Next steps:")
        print(f"1. Test locally: cd public && python3 -m http.server 8000")
        print(f"2. Verify {library} works correctly")
        print(f"3. Commit: git add . && git commit -m 'chore: Update {library} to {latest}'")
        
        return True
    
    def update_all(self, skip_tests: bool = False) -> bool:
        """Update all dependencies"""
        print(f"\n{'='*70}")
        print("🚀 Updating All Dependencies")
        print(f"{'='*70}\n")
        
        updates = self.check_for_updates()
        
        if not updates:
            print("✅ All dependencies are up to date!")
            return True
        
        print(f"Found {len(updates)} update(s) available\n")
        
        # Update each library
        success = True
        for lib in updates.keys():
            if not self.update_library(lib, skip_tests):
                success = False
                print(f"\n⚠️  Stopping at {lib} due to failure")
                break
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description="One-command dependency updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check for available updates
  python3 src/tools/update_dependencies.py --check
  
  # Update all dependencies (safe)
  python3 src/tools/update_dependencies.py --update
  
  # Update only Leaflet
  python3 src/tools/update_dependencies.py --leaflet
  
  # Update only Lucide
  python3 src/tools/update_dependencies.py --lucide
  
  # Force update without tests (dangerous!)
  python3 src/tools/update_dependencies.py --update --force
        """
    )
    
    parser.add_argument("--check", action="store_true",
                       help="Check for available updates")
    parser.add_argument("--update", action="store_true",
                       help="Update all dependencies")
    parser.add_argument("--leaflet", action="store_true",
                       help="Update only Leaflet")
    parser.add_argument("--lucide", action="store_true",
                       help="Update only Lucide")
    parser.add_argument("--force", action="store_true",
                       help="Skip compatibility tests (dangerous)")
    
    args = parser.parse_args()
    
    # Default to --check if no action specified
    if not (args.check or args.update or args.leaflet or args.lucide):
        args.check = True
    
    base_path = Path(__file__).parent.parent.parent
    updater = DependencyUpdater(base_path)
    
    try:
        if args.check:
            updater.check_for_updates()
            sys.exit(0)
        
        if args.leaflet:
            success = updater.update_library("leaflet", args.force)
            sys.exit(0 if success else 1)
        
        if args.lucide:
            success = updater.update_library("lucide", args.force)
            sys.exit(0 if success else 1)
        
        if args.update:
            success = updater.update_all(args.force)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
