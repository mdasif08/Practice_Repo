#!/usr/bin/env python3
"""
CraftNudge Git Commit Logger - Main CLI Tool

Usage:
    python track_commit.py                    # Track latest commit
    python track_commit.py --all              # Track all commits
    python track_commit.py --latest           # Track latest commit (default)
    python track_commit.py --range START END  # Track commit range
    python track_commit.py --summary          # Show tracking summary
    python track_commit.py --stats            # Show statistics
    python track_commit.py --help             # Show help
"""

import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.commit_tracker import CommitTrackerService
from services.data_storage import DataStorageService
from utils.error_handler import (
    display_success_message,
    display_info_message,
    display_error_message,
    safe_exit
)

console = Console()


def print_banner():
    """Print the CraftNudge banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CraftNudge Git Logger                     ║
    ║              Track your coding patterns over time            ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, border_style="blue"))


def display_summary(tracker: CommitTrackerService):
    """Display tracking summary."""
    summary = tracker.get_tracking_summary()
    
    # Repository info
    repo_info = summary['repository']
    tracking_status = summary['tracking_status']
    
    table = Table(title="📊 Tracking Summary", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Repository Path", repo_info['repository_path'])
    table.add_row("Active Branch", repo_info['active_branch'])
    table.add_row("Total Repository Commits", str(repo_info['total_commits']))
    table.add_row("Total Logged Commits", str(tracking_status['total_logged_commits']))
    table.add_row("Coverage Percentage", f"{tracking_status['coverage_percentage']}%")
    table.add_row("Repository Status", "🟢 Clean" if not repo_info['is_dirty'] else "🟡 Dirty")
    
    console.print(table)
    
    if repo_info['untracked_files']:
        console.print("\n[yellow]⚠️  Untracked files:[/yellow]")
        for file in repo_info['untracked_files'][:5]:  # Show first 5
            console.print(f"  • {file}")
        if len(repo_info['untracked_files']) > 5:
            console.print(f"  ... and {len(repo_info['untracked_files']) - 5} more")


def display_statistics(storage: DataStorageService):
    """Display commit statistics."""
    stats = storage.get_statistics()
    
    if stats['total_commits'] == 0:
        display_info_message("No commits have been logged yet.")
        return
    
    table = Table(title="📈 Commit Statistics", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    table.add_row("Total Commits", str(stats['total_commits']))
    table.add_row("Unique Authors", str(stats['unique_authors']))
    table.add_row("Average Files per Commit", str(stats['average_files_per_commit']))
    
    if stats['most_active_author']:
        table.add_row(
            "Most Active Author", 
            f"{stats['most_active_author']['name']} ({stats['most_active_author']['commits']} commits)"
        )
    
    if stats['date_range']:
        date_range = stats['date_range']
        table.add_row("Date Range", f"{date_range['earliest'].strftime('%Y-%m-%d')} to {date_range['latest'].strftime('%Y-%m-%d')}")
    
    console.print(table)


@click.command()
@click.option('--all', 'track_all', is_flag=True, help='Track all commits in the repository')
@click.option('--latest', 'track_latest', is_flag=True, help='Track the latest commit (default)')
@click.option('--range', 'commit_range', nargs=2, type=str, help='Track commits in range (START END)')
@click.option('--limit', type=int, help='Limit number of commits to track (when using --all)')
@click.option('--summary', is_flag=True, help='Show tracking summary')
@click.option('--stats', is_flag=True, help='Show commit statistics')
@click.option('--repo-path', type=click.Path(exists=True, file_okay=False, dir_okay=True), 
              help='Path to Git repository (default: current directory)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(track_all: bool, track_latest: bool, commit_range: Optional[tuple], 
         limit: Optional[int], summary: bool, stats: bool, repo_path: Optional[str], 
         verbose: bool):
    """
    CraftNudge Git Commit Logger - Track your coding patterns over time.
    
    This tool logs Git commits with metadata to help you reflect on your coding patterns.
    Data is stored locally in data/behaviors/commits.jsonl.
    """
    
    print_banner()
    
    # Initialize services
    try:
        repo_path_obj = Path(repo_path) if repo_path else None
        tracker = CommitTrackerService(repo_path=repo_path_obj)
        storage = DataStorageService()
    except Exception as e:
        display_error_message(f"Failed to initialize services: {str(e)}")
        sys.exit(1)
    
    # Handle different commands
    if summary:
        display_summary(tracker)
        return
    
    if stats:
        display_statistics(storage)
        return
    
    if commit_range:
        start_commit, end_commit = commit_range
        try:
            entry_ids = tracker.track_commit_range(start_commit, end_commit)
            if entry_ids:
                display_success_message(f"Tracked {len(entry_ids)} commits in range {start_commit}..{end_commit}")
            else:
                display_info_message("No new commits found in the specified range.")
        except Exception as e:
            display_error_message(f"Failed to track commit range: {str(e)}")
            sys.exit(1)
        return
    
    if track_all:
        try:
            entry_ids = tracker.track_all_commits(limit=limit)
            if entry_ids:
                display_success_message(f"Successfully tracked {len(entry_ids)} commits")
            else:
                display_info_message("No new commits to track.")
        except Exception as e:
            display_error_message(f"Failed to track all commits: {str(e)}")
            sys.exit(1)
        return
    
    # Default: track latest commit
    try:
        entry_id = tracker.track_latest_commit()
        if entry_id:
            display_success_message("Latest commit tracked successfully!")
        else:
            display_info_message("No new commits to track.")
    except Exception as e:
        display_error_message(f"Failed to track latest commit: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
