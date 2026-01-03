#!/usr/bin/env python3
"""
Generate CHANGELOG.md from Git history of merged PRs.

This script extracts PR information from Git merge commits and creates
a comprehensive CHANGELOG.md file documenting all changes to the project.
"""

import subprocess
import re
from datetime import datetime
from collections import defaultdict
import sys
import json
from pathlib import Path

# Determine repository root dynamically
REPO_ROOT = Path(__file__).parent.parent

def run_git_command(cmd_list):
    """Run a git command and return the output."""
    result = subprocess.run(
        cmd_list,
        shell=False,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd_list)}", file=sys.stderr)
        print(f"Error: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout.strip()

def get_repo_info():
    """Extract repository owner and name from git remote URL."""
    remote_url = run_git_command(['git', 'config', '--get', 'remote.origin.url'])
    
    # Parse GitHub URL (handles both HTTPS and SSH formats)
    match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote_url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return owner, repo
    
    # Fallback to config.json if available
    config_path = REPO_ROOT / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Try to extract from config if it has repository info
                return 'feileberlin', 'krwl-hof'  # Safe fallback
        except Exception:
            pass
    
    return 'feileberlin', 'krwl-hof'  # Default fallback

def extract_pr_number(subject):
    """Extract PR number from merge commit subject."""
    match = re.search(r'#(\d+)', subject)
    return int(match.group(1)) if match else None

def get_all_prs():
    """Get all merged PRs from git history."""
    # Get repository info
    repo_owner, repo_name = get_repo_info()
    
    # Get all commits (not just merges, since grafted repos may not have proper merge commits)
    cmd = ['git', 'log', '--format=%H|%s|%aI']
    output = run_git_command(cmd)
    
    prs = []
    for line in output.split('\n'):
        if not line:
            continue
        
        parts = line.split('|')
        if len(parts) < 3:
            continue
            
        commit_hash, subject, date_str = parts[0], parts[1], parts[2]
        
        # Only process lines that are PR merges
        if 'Merge pull request' not in subject:
            continue
            
        pr_number = extract_pr_number(subject)
        
        if pr_number:
            # Get full commit message (PR description)
            desc_cmd = ['git', 'log', '--format=%B', '-n', '1', commit_hash]
            full_message = run_git_command(desc_cmd)
            
            # Extract description (everything after first 2 lines)
            lines = full_message.split('\n')
            description = '\n'.join(lines[2:]).strip()
            
            # Extract branch name from subject (owner-agnostic)
            branch_match = re.search(r'from [^/]+/([\w/-]+)', subject)
            branch = branch_match.group(1) if branch_match else ""
            
            # Parse date
            try:
                merge_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError as exc:
                print(f"Warning: failed to parse merge date '{date_str}': {exc}", file=sys.stderr)
                merge_date = datetime.now()
            
            prs.append({
                'number': pr_number,
                'branch': branch,
                'description': description,
                'date': merge_date,
                'commit': commit_hash[:7]
            })
    
    # Sort by PR number (ascending)
    prs.sort(key=lambda x: x['number'])
    return prs

def categorize_pr(branch, description):
    """Categorize PR based on branch name and description."""
    branch_lower = branch.lower()
    desc_lower = description.lower()
    
    # Check for keywords
    if any(word in branch_lower or word in desc_lower for word in ['fix', 'bug', 'error', 'issue']):
        return 'Fixed'
    elif any(word in branch_lower or word in desc_lower for word in ['add', 'implement', 'create', 'new']):
        return 'Added'
    elif any(word in branch_lower or word in desc_lower for word in ['update', 'change', 'refactor', 'improve', 'enhance']):
        return 'Changed'
    elif any(word in branch_lower or word in desc_lower for word in ['remove', 'delete', 'clean']):
        return 'Removed'
    elif any(word in branch_lower or word in desc_lower for word in ['security', 'vulnerability']):
        return 'Security'
    else:
        return 'Changed'

def group_prs_by_date(prs):
    """Group PRs by year-month for changelog sections."""
    grouped = defaultdict(list)
    for pr in prs:
        key = pr['date'].strftime('%Y-%m')
        grouped[key].append(pr)
    return grouped

def generate_changelog():
    """Generate the complete CHANGELOG.md content."""
    print("Fetching PR history from git...")
    prs = get_all_prs()
    print(f"Found {len(prs)} merged PRs")
    
    # Get repository info for links
    repo_owner, repo_name = get_repo_info()
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"
    
    # Group by date
    grouped_prs = group_prs_by_date(prs)
    
    # Build changelog content
    changelog = []
    changelog.append("# Changelog")
    changelog.append("")
    changelog.append("All notable changes to the KRWL HOF Community Events project are documented in this file.")
    changelog.append("")
    changelog.append("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),")
    changelog.append("and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).")
    changelog.append("")
    changelog.append("---")
    changelog.append("")
    
    # Sort date groups (newest first)
    sorted_groups = sorted(grouped_prs.keys(), reverse=True)
    
    for date_key in sorted_groups:
        prs_in_month = grouped_prs[date_key]
        
        # Create section header
        year, month = date_key.split('-')
        month_name = datetime.strptime(month, '%m').strftime('%B')
        changelog.append(f"## {month_name} {year}")
        changelog.append("")
        
        # Group by category
        categorized = defaultdict(list)
        for pr in prs_in_month:
            category = categorize_pr(pr['branch'], pr['description'])
            categorized[category].append(pr)
        
        # Output by category
        category_order = ['Added', 'Changed', 'Fixed', 'Removed', 'Security']
        for category in category_order:
            if category in categorized:
                changelog.append(f"### {category}")
                changelog.append("")
                for pr in categorized[category]:
                    # Format PR entry
                    title = pr['description'].split('\n')[0] if pr['description'] else pr['branch']
                    if not title or title.strip() == '':
                        title = pr['branch'].replace('copilot/', '').replace('-', ' ').title()
                    
                    changelog.append(f"- **PR #{pr['number']}** ({pr['date'].strftime('%Y-%m-%d')}): {title}")
                    
                    # Add additional description lines if available
                    desc_lines = pr['description'].split('\n')[1:]
                    for line in desc_lines:
                        line = line.strip()
                        if line and not line.startswith('<!--'):
                            changelog.append(f"  {line}")
                
                changelog.append("")
        
        changelog.append("---")
        changelog.append("")
    
    # Add footer
    changelog.append("## Project Information")
    changelog.append("")
    changelog.append("### Repository")
    changelog.append(f"- **URL**: {repo_url}")
    changelog.append(f"- **Issues**: {repo_url}/issues")
    changelog.append(f"- **Discussions**: {repo_url}/discussions")
    changelog.append("")
    changelog.append("### Contributing")
    changelog.append("For information on how to contribute, see the [README.md](README.md) file.")
    changelog.append("")
    changelog.append("---")
    changelog.append("")
    changelog.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d')}*")
    changelog.append(f"*This file is auto-generated from Git history. Do not edit manually.*")
    changelog.append("")
    
    return '\n'.join(changelog)

def main():
    """Main function."""
    try:
        print("Generating CHANGELOG.md...")
        content = generate_changelog()
        
        # Write to file using dynamic path
        output_path = REPO_ROOT / 'docs' / 'CHANGELOG.md'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ CHANGELOG.md generated successfully at {output_path}")
        print(f"   Total lines: {len(content.split(chr(10)))}")
        
    except Exception as e:
        print(f"❌ Error generating CHANGELOG: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
