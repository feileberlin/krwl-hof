#!/usr/bin/env python3
"""
Update GitHub Repository Details

This script updates the repository About section using GitHub API.
Requires a GitHub Personal Access Token with 'repo' scope.

Usage:
    python3 scripts/update_github_about.py

Environment Variables:
    GITHUB_TOKEN - GitHub Personal Access Token (required)
                   Get one at: https://github.com/settings/tokens
"""

import json
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error


def load_settings():
    """Load repository settings from JSON file."""
    settings_file = Path('.github/repository-settings.json')
    
    if not settings_file.exists():
        print(f"❌ Error: Settings file not found: {settings_file}")
        sys.exit(1)
    
    with open(settings_file, 'r') as f:
        return json.load(f)


def update_repository_details(token, owner, repo, settings):
    """Update repository description and homepage using GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    
    data = {
        'description': settings['description'],
        'homepage': settings['homepage'],
        'has_issues': settings.get('has_issues', True),
        'has_projects': settings.get('has_projects', True),
        'has_wiki': settings.get('has_wiki', False),
    }
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
    }
    
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='PATCH'
    )
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                print("✅ Repository description and homepage updated")
                return True
            else:
                print(f"❌ Failed to update repository: HTTP {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8')}")
        return False


def update_repository_topics(token, owner, repo, topics):
    """Update repository topics using GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    
    data = {
        'names': topics
    }
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.mercy-preview+json',
        'Content-Type': 'application/json',
    }
    
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='PUT'
    )
    
    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                print("✅ Repository topics updated")
                return True
            else:
                print(f"❌ Failed to update topics: HTTP {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(f"   Response: {e.read().decode('utf-8')}")
        return False


def main():
    """Main entry point."""
    # Check for GitHub token
    token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("")
        print("To set up a Personal Access Token:")
        print("  1. Go to: https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Give it a name (e.g., 'Update Repository Details')")
        print("  4. Select scope: 'repo' (Full control of private repositories)")
        print("  5. Click 'Generate token'")
        print("  6. Copy the token and run:")
        print("     export GITHUB_TOKEN='your_token_here'")
        print("")
        print("Alternatively, update manually at:")
        print("  https://github.com/feileberlin/krwl-hof/settings")
        sys.exit(1)
    
    # Repository details
    owner = 'feileberlin'
    repo = 'krwl-hof'
    
    print(f"🔧 Updating GitHub repository details for {owner}/{repo}...")
    print("")
    
    # Load settings
    settings = load_settings()
    
    print("📝 Repository Details:")
    print(f"   Description: {settings['description']}")
    print(f"   Homepage: {settings['homepage']}")
    print(f"   Topics: {', '.join(settings['topics'])}")
    print("")
    
    # Update repository details
    print("🔄 Updating repository description and homepage...")
    success1 = update_repository_details(token, owner, repo, settings)
    
    print("")
    print("🔄 Updating repository topics...")
    success2 = update_repository_topics(token, owner, repo, settings['topics'])
    
    print("")
    if success1 and success2:
        print("🎉 GitHub repository details updated successfully!")
        print("")
        print(f"🌐 View at: https://github.com/{owner}/{repo}")
        return 0
    else:
        print("⚠️  Some updates failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
