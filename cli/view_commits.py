#!/usr/bin/env python3
"""
CraftNudge Git Commit Logger - View Commits Tool

Usage:
    python view_commits.py                    # View all commits
    python view_commits.py --limit 10         # Limit number of commits
    python view_commits.py --author "John"    # Filter by author
    python view_commits.py --search "fix"     # Search in commit messages
    python view_commits.py --detailed         # Show detailed view
    python view_commits.py --json             # Output as JSON
    python view_commits.py --help             # Show help
"""

import sys
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.pagination import Pagination

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.data_storage import DataStorageService
from utils.error_handler import display_error_message, display_info_message

console = Console()


def print_banner():
    """Print the CraftNudge banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                CraftNudge Commit Viewer                      ║
    ║              View your logged commit history                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, border_style="blue"))


def format_commit_table(commits: List, detailed: bool = False) -> Table:
    """Format commits into a rich table."""
    if detailed:
        table = Table(title="📋 Detailed Commit History", show_header=True, header_style="bold blue")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Hash", style="green", no_wrap=True)
        table.add_column("Author", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Date", style="magenta", no_wrap=True)
        table.add_column("Branch", style="blue", no_wrap=True)
        table.add_column("Files", style="red", no_wrap=True)
        
        for commit in commits:
            # Truncate message for display
            message = commit.message
            if len(message) > 50:
                message = message[:47] + "..."
            
            # Format changed files count
            files_count = len(commit.changed_files)
            files_display = f"{files_count} file{'s' if files_count != 1 else ''}"
            
            table.add_row(
                commit.id[:8],
                commit.commit_hash[:8],
                commit.author,
                message,
                commit.timestamp_commit.strftime("%Y-%m-%d %H:%M"),
                commit.branch,
                files_display
            )
    else:
        table = Table(title="📋 Commit History", show_header=True, header_style="bold blue")
        table.add_column("Hash", style="green", no_wrap=True)
        table.add_column("Author", style="yellow")
        table.add_column("Message", style="white")
        table.add_column("Date", style="magenta", no_wrap=True)
        table.add_column("Files", style="red", no_wrap=True)
        
        for commit in commits:
            # Truncate message for display
            message = commit.message
            if len(message) > 60:
                message = message[:57] + "..."
            
            # Format changed files count
            files_count = len(commit.changed_files)
            files_display = f"{files_count} file{'s' if files_count != 1 else ''}"
            
            table.add_row(
                commit.commit_hash[:8],
                commit.author,
                message,
                commit.timestamp_commit.strftime("%Y-%m-%d %H:%M"),
                files_display
            )
    
    return table


def display_commit_details(commit) -> None:
    """Display detailed information about a specific commit."""
    console.print(Panel(f"Commit Details: {commit.commit_hash[:8]}", border_style="green"))
    
    details_table = Table(show_header=False, box=None)
    details_table.add_column("Field", style="cyan", no_wrap=True)
    details_table.add_column("Value", style="white")
    
    details_table.add_row("ID", commit.id)
    details_table.add_row("Hash", commit.commit_hash)
    details_table.add_row("Author", commit.author)
    details_table.add_row("Message", commit.message)
    details_table.add_row("Commit Date", commit.timestamp_commit.strftime("%Y-%m-%d %H:%M:%S UTC"))
    details_table.add_row("Log Date", commit.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"))
    details_table.add_row("Branch", commit.branch)
    details_table.add_row("Repository", commit.repository_path)
    details_table.add_row("Files Changed", str(len(commit.changed_files)))
    
    console.print(details_table)
    
    if commit.changed_files:
        console.print("\n[yellow]Changed Files:[/yellow]")
        for file in commit.changed_files:
            console.print(f"  • {file}")


def output_json(commits: List) -> None:
    """Output commits as JSON."""
    # Convert commits to dictionaries
    commit_dicts = []
    for commit in commits:
        commit_dict = commit.dict()
        # Convert datetime objects to ISO strings
        commit_dict['timestamp'] = commit_dict['timestamp'].isoformat()
        commit_dict['timestamp_commit'] = commit_dict['timestamp_commit'].isoformat()
        commit_dicts.append(commit_dict)
    
    print(json.dumps(commit_dicts, indent=2))


@click.command()
@click.option('--limit', type=int, help='Limit number of commits to display')
@click.option('--author', type=str, help='Filter by author name')
@click.option('--search', type=str, help='Search in commit messages')
@click.option('--detailed', is_flag=True, help='Show detailed view')
@click.option('--json', 'output_json_flag', is_flag=True, help='Output as JSON')
@click.option('--id', 'commit_id', type=str, help='Show details for specific commit ID')
@click.option('--hash', 'commit_hash', type=str, help='Show details for specific commit hash')
def main(limit: Optional[int], author: Optional[str], search: Optional[str], 
         detailed: bool, output_json_flag: bool, commit_id: Optional[str], 
         commit_hash: Optional[str]):
    """
    CraftNudge Git Commit Logger - View logged commits.
    
    This tool displays your logged commit history with various filtering options.
    """
    
    print_banner()
    
    # Initialize storage service
    try:
        storage = DataStorageService()
    except Exception as e:
        display_error_message(f"Failed to initialize storage service: {str(e)}")
        sys.exit(1)
    
    # Load commits
    try:
        commits = storage.load_commits()
    except Exception as e:
        display_error_message(f"Failed to load commits: {str(e)}")
        sys.exit(1)
    
    if not commits:
        display_info_message("No commits have been logged yet.")
        return
    
    # Filter commits
    if author:
        commits = [c for c in commits if author.lower() in c.author.lower()]
    
    if search:
        commits = [c for c in commits if search.lower() in c.message.lower()]
    
    if limit:
        commits = commits[:limit]
    
    if not commits:
        display_info_message("No commits match the specified criteria.")
        return
    
    # Handle specific commit lookup
    if commit_id:
        matching_commits = [c for c in commits if c.id.startswith(commit_id)]
        if matching_commits:
            display_commit_details(matching_commits[0])
        else:
            display_error_message(f"No commit found with ID starting with: {commit_id}")
        return
    
    if commit_hash:
        matching_commits = [c for c in commits if c.commit_hash.startswith(commit_hash)]
        if matching_commits:
            display_commit_details(matching_commits[0])
        else:
            display_error_message(f"No commit found with hash starting with: {commit_hash}")
        return
    
    # Output format
    if output_json_flag:
        output_json(commits)
        return
    
    # Display table
    table = format_commit_table(commits, detailed=detailed)
    console.print(table)
    
    # Show summary
    console.print(f"\n[green]Showing {len(commits)} commit{'s' if len(commits) != 1 else ''}[/green]")


if __name__ == '__main__':
    main()
