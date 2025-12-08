#!/usr/bin/env python3
"""
KRWL HOF Feature Verification Module

This module verifies that all documented features in features.json are still
present in the codebase. Designed for use in CI/CD and local development.
"""

import json
import os
import re
import sys
from pathlib import Path


class FeatureVerifier:
    """Verifies presence of documented features in codebase"""
    
    def __init__(self, repo_root=None, verbose=False):
        self.verbose = verbose
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.features_file = self.repo_root / "features.json"
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "features": []
        }
    
    def log(self, message, level="INFO"):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def load_features(self):
        """Load feature registry from features.json"""
        if not self.features_file.exists():
            print(f"ERROR: Feature registry not found at {self.features_file}")
            sys.exit(1)
        
        with open(self.features_file, 'r') as f:
            return json.load(f)
    
    def _check_single_file(self, file_path):
        """Check if a single file exists"""
        full_path = self.repo_root / file_path
        return full_path.exists()
    
    def check_files_exist(self, feature):
        """Check if all required files exist"""
        if 'files' not in feature:
            return True, []
        
        missing = [f for f in feature['files'] if not self._check_single_file(f)]
        return len(missing) == 0, missing
    
    def _search_pattern_in_file(self, file_path, pattern_str):
        """Search for a pattern in a file"""
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return False, "file not found"
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = re.compile(pattern_str)
            if pattern.search(content):
                return True, None
            return False, "pattern not found"
        except Exception as e:
            return False, f"error reading file: {e}"
    
    def check_code_patterns(self, feature):
        """Check if code patterns exist in specified files"""
        if 'code_patterns' not in feature:
            return True, []
        
        missing = []
        for pattern_def in feature['code_patterns']:
            file_path = pattern_def['file']
            pattern = pattern_def['pattern']
            desc = pattern_def.get('description', pattern)
            
            found, reason = self._search_pattern_in_file(file_path, pattern)
            if not found:
                missing.append({
                    'file': file_path,
                    'pattern': pattern,
                    'description': desc,
                    'reason': reason
                })
        
        return len(missing) == 0, missing
    
    def _check_config_key_in_file(self, config_file, key):
        """Check if a config key exists in a JSON file"""
        full_path = self.repo_root / config_file
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Support nested keys like "map.center"
            keys = key.split('.')
            value = config
            for k in keys:
                if not isinstance(value, dict) or k not in value:
                    return False
                value = value[k]
            return True
        except Exception:
            return False
    
    def check_config_keys(self, feature):
        """Check if required config keys exist"""
        if 'config_keys' not in feature:
            return True, []
        
        missing = []
        for key_def in feature['config_keys']:
            # Handle both string format and object format
            if isinstance(key_def, str):
                # Simple string format: "config.key"
                key = key_def
                # Try both config files
                found = False
                for config_file in ['config.dev.json', 'config.prod.json']:
                    if self._check_config_key_in_file(config_file, key):
                        found = True
                        break
                if not found:
                    missing.append(key)
            else:
                # Object format: {"file": "config.json", "key": "config.key"}
                file_path = key_def['file']
                key = key_def['key']
                if not self._check_config_key_in_file(file_path, key):
                    missing.append(f"{file_path}:{key}")
        
        return len(missing) == 0, missing
    
    def verify_feature(self, feature):
        """Verify a single feature"""
        feature_id = feature.get('id', 'unknown')
        feature_name = feature.get('name', 'Unknown')
        
        self.log(f"Verifying feature: {feature_name} ({feature_id})")
        
        result = {
            'id': feature_id,
            'name': feature_name,
            'category': feature.get('category', 'unknown'),
            'status': 'passed',
            'checks': []
        }
        
        # Check files
        files_exist, missing_files = self.check_files_exist(feature)
        result['checks'].append({
            'type': 'files',
            'passed': files_exist,
            'missing_files': missing_files
        })
        if not files_exist:
            result['status'] = 'failed'
            self.log(f"  Files check FAILED: {len(missing_files)} missing", "ERROR")
        else:
            self.log("  Files check PASSED")
        
        # Check code patterns
        patterns_found, missing_patterns = self.check_code_patterns(feature)
        result['checks'].append({
            'type': 'code_patterns',
            'passed': patterns_found,
            'missing_patterns': missing_patterns
        })
        if not patterns_found:
            result['status'] = 'failed'
            self.log(f"  Patterns check FAILED: {len(missing_patterns)} missing", "ERROR")
        else:
            self.log("  Patterns check PASSED")
        
        # Check config keys
        config_valid, missing_keys = self.check_config_keys(feature)
        result['checks'].append({
            'type': 'config',
            'passed': config_valid,
            'missing_keys': missing_keys
        })
        if not config_valid:
            result['status'] = 'failed'
            self.log(f"  Config check FAILED: {len(missing_keys)} missing", "ERROR")
        else:
            self.log("  Config check PASSED")
        
        return result
    
    def verify_all(self):
        """Verify all features from the registry"""
        data = self.load_features()
        features = data.get('features', [])
        
        self.results['total'] = len(features)
        
        for feature in features:
            result = self.verify_feature(feature)
            self.results['features'].append(result)
            
            if result['status'] == 'passed':
                self.results['passed'] += 1
            else:
                self.results['failed'] += 1
        
        return self.results
    
    def print_summary(self, results):
        """Print human-readable summary"""
        print("=" * 60)
        print("Feature Verification Summary")
        print("=" * 60)
        
        print(f"\nTotal Features: {results['total']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        
        if results['failed'] > 0:
            print("\nFailed features:")
            for feature in results['features']:
                if feature['status'] != 'failed':
                    continue
                
                print(f"\n  ✗ {feature['name']} ({feature['id']})")
                for check in feature['checks']:
                    if check['passed']:
                        continue
                    
                    print(f"    - {check['type']}: FAILED")
                    
                    if 'missing_files' in check and check['missing_files']:
                        for f in check['missing_files']:
                            print(f"      Missing file: {f}")
                    
                    if 'missing_patterns' in check and check['missing_patterns']:
                        for p in check['missing_patterns']:
                            print(f"      Missing pattern: {p['description']}")
                            print(f"        in {p['file']}: {p['reason']}")
                    
                    if 'missing_keys' in check and check['missing_keys']:
                        for k in check['missing_keys']:
                            print(f"      Missing config key: {k}")
        
        print("=" * 60)
        
        if results['failed'] == 0:
            print("\n✓ All features verified successfully!")
            return 0
        else:
            print(f"\n✗ {results['failed']} feature(s) failed verification")
            return 1


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify KRWL HOF features are present in codebase"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each feature check"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=None,
        help="Repository root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    verifier = FeatureVerifier(
        repo_root=args.repo_root,
        verbose=args.verbose
    )
    results = verifier.verify_all()
    
    if args.json:
        print("\n" + json.dumps(results, indent=2))
        sys.exit(0 if results['failed'] == 0 else 1)
    else:
        exit_code = verifier.print_summary(results)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
