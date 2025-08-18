#!/usr/bin/env python3
"""
Script to fetch real commits from GitHub repositories and store them in PostgreSQL database.
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent))

from services.database_service import DatabaseService

def fetch_github_commits(repo_owner, repo_name, token, max_commits=10):
    """Fetch real commits from a GitHub repository."""
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers, params={'per_page': max_commits})
        response.raise_for_status()
        
        commits_data = response.json()
        print(f"✅ Successfully fetched {len(commits_data)} commits from {repo_owner}/{repo_name}")
        
        return commits_data
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching commits: {str(e)}")
        return []

def process_github_commits(commits_data, repo_name):
    """Process GitHub commits and convert to our database format."""
    
    processed_commits = []
    
    for commit_data in commits_data:
        try:
            # Extract commit information
            commit_hash = commit_data['sha']
            author_info = commit_data['commit']['author']
            commit_info = commit_data['commit']
            
            # Get author name (prefer GitHub username if available)
            author_name = commit_data['author']['login'] if commit_data.get('author') else author_info['name']
            
            # Get commit message
            message = commit_info['message']
            
            # Get commit date
            commit_date = datetime.fromisoformat(author_info['date'].replace('Z', '+00:00'))
            
            # Get branch (default to main)
            branch = "main"  # GitHub API doesn't provide branch info in commits endpoint
            
            # Get files changed (if available)
            files_changed = []
            if commit_data.get('files'):
                files_changed = [file['filename'] for file in commit_data['files']]
            
            # Create commit object
            commit_obj = {
                'commit_hash': commit_hash,
                'author': author_name,
                'author_email': author_info['email'],
                'message': message,
                'timestamp_commit': commit_date,
                'branch': branch,
                'repository_name': repo_name,
                'files_changed': files_changed,
                'lines_added': 0,  # GitHub API doesn't provide this in basic commits endpoint
                'lines_deleted': 0
            }
            
            processed_commits.append(commit_obj)
            
        except Exception as e:
            print(f"⚠️ Error processing commit {commit_data.get('sha', 'unknown')}: {str(e)}")
            continue
    
    return processed_commits

def save_commits_to_database(commits, db_service):
    """Save processed commits to PostgreSQL database."""
    
    saved_count = 0
    
    for commit in commits:
        try:
            # Check if commit already exists
            existing_commit = db_service.get_commit_by_hash(commit['commit_hash'])
            
            if existing_commit:
                print(f"⏭️ Commit {commit['commit_hash'][:8]} already exists, skipping...")
                continue
            
            # Save new commit
            commit_id = db_service.save_commit(commit)
            saved_count += 1
            print(f"✅ Saved commit {commit['commit_hash'][:8]}: {commit['message'][:50]}...")
            
        except Exception as e:
            print(f"❌ Error saving commit {commit['commit_hash'][:8]}: {str(e)}")
            continue
    
    return saved_count

def main():
    """Main function to fetch and store real GitHub commits."""
    
    # GitHub configuration
    GITHUB_TOKEN = "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"
    
    # List of repositories to fetch commits from
    repositories = [
        {"owner": "mdasif08", "name": "Practice_Repo"},
        {"owner": "mdasif08", "name": "Arour"},
        # Add more repositories here
    ]
    
    print("🚀 Starting to fetch real GitHub commits...")
    print(f"📋 Will fetch from {len(repositories)} repositories")
    
    try:
        # Initialize database service
        db_service = DatabaseService()
        print("✅ Connected to PostgreSQL database")
        
        total_saved = 0
        
        for repo in repositories:
            print(f"\n📁 Fetching commits from {repo['owner']}/{repo['name']}...")
            
            # Fetch commits from GitHub
            commits_data = fetch_github_commits(
                repo['owner'], 
                repo['name'], 
                GITHUB_TOKEN, 
                max_commits=5  # Limit to 5 commits per repo
            )
            
            if commits_data:
                # Process commits
                processed_commits = process_github_commits(commits_data, repo['name'])
                
                if processed_commits:
                    # Save to database
                    saved_count = save_commits_to_database(processed_commits, db_service)
                    total_saved += saved_count
                    print(f"💾 Saved {saved_count} new commits from {repo['name']}")
                else:
                    print(f"⚠️ No commits to save from {repo['name']}")
            else:
                print(f"❌ No commits fetched from {repo['name']}")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Get final statistics
        stats = db_service.get_statistics()
        print(f"\n🎉 Summary:")
        print(f"   Total commits in database: {stats['total_commits']}")
        print(f"   Unique authors: {stats['unique_authors']}")
        print(f"   New commits added: {total_saved}")
        
        print("\n✅ Real GitHub commits have been fetched and stored in PostgreSQL!")
        print("🖱️ Now click 'Track Now' in your frontend to see the real commits!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        if 'db_service' in locals():
            db_service.close()

if __name__ == '__main__':
    main()
