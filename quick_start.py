#!/usr/bin/env python3
"""
Quick Start Script for CraftNudge Git Commit Logger

This script helps you get started with the Git commit logger by:
1. Checking system requirements
2. Setting up the environment
3. Running a test to ensure everything works
"""

import sys
import subprocess
import importlib
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        console.print("[red]❌ Python 3.8 or higher is required[/red]")
        return False
    
    console.print(f"[green]✅ Python {version.major}.{version.minor}.{version.micro} detected[/green]")
    return True


def check_git_installation():
    """Check if Git is installed."""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, check=True)
        console.print(f"[green]✅ Git installed: {result.stdout.strip()}[/green]")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]❌ Git is not installed or not in PATH[/red]")
        return False


def check_git_repository():
    """Check if current directory is a Git repository."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, check=True)
        console.print("[green]✅ Current directory is a Git repository[/green]")
        return True
    except subprocess.CalledProcessError:
        console.print("[red]❌ Current directory is not a Git repository[/red]")
        console.print("[yellow]💡 Run this script from within a Git repository[/yellow]")
        return False


def install_dependencies():
    """Install required dependencies."""
    console.print("\n[blue]📦 Installing dependencies...[/blue]")
    
    # Try basic requirements first (no compilation needed)
    try:
        console.print("[yellow]Trying basic requirements (no compilation needed)...[/yellow]")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-basic.txt'], 
                      check=True, capture_output=True)
        console.print("[green]✅ Basic dependencies installed successfully[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[yellow]Basic installation failed, trying minimal requirements...[/yellow]")
        
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-minimal.txt'], 
                          check=True, capture_output=True)
            console.print("[green]✅ Minimal dependencies installed successfully[/green]")
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Minimal installation failed, trying full requirements...[/yellow]")
            
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              check=True, capture_output=True)
                console.print("[green]✅ Full dependencies installed successfully[/green]")
                return True
            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Failed to install dependencies: {e}[/red]")
                console.print("[yellow]💡 Try installing manually: pip install -r requirements-basic.txt[/yellow]")
                return False


def test_imports():
    """Test if all required modules can be imported."""
    console.print("\n[blue]🧪 Testing imports...[/blue]")
    
    required_modules = [
        'git',
        'click',
        'rich'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            console.print(f"[green]✅ {module}[/green]")
        except ImportError:
            console.print(f"[red]❌ {module}[/red]")
            failed_imports.append(module)
    
    if failed_imports:
        console.print(f"\n[red]❌ Failed to import: {', '.join(failed_imports)}[/red]")
        return False
    
    console.print("[green]✅ All imports successful[/green]")
    return True


def test_basic_functionality():
    """Test basic functionality of the commit logger."""
    console.print("\n[blue]🧪 Testing basic functionality...[/blue]")
    
    try:
        # Test imports
        sys.path.insert(0, str(Path(__file__).parent))
        from services.commit_tracker import CommitTrackerService
        from services.data_storage import DataStorageService
        
        # Test service initialization
        tracker = CommitTrackerService()
        storage = DataStorageService()
        
        console.print("[green]✅ Services initialized successfully[/green]")
        
        # Test repository info
        repo_info = tracker.get_repository_info()
        console.print(f"[green]✅ Repository info retrieved: {repo_info['repository_path']}[/green]")
        
        # Test statistics
        stats = storage.get_statistics()
        console.print(f"[green]✅ Statistics retrieved: {stats['total_commits']} commits logged[/green]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Basic functionality test failed: {e}[/red]")
        return False


def run_demo():
    """Run a quick demo of the system."""
    console.print("\n[blue]🎬 Running demo...[/blue]")
    
    try:
        result = subprocess.run([sys.executable, 'example_usage.py'], 
                              capture_output=True, text=True, check=True)
        console.print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
        console.print(f"Error output: {e.stderr}")
        return False


def main():
    """Main quick start function."""
    console.print(Panel(
        "🚀 CraftNudge Git Commit Logger - Quick Start",
        border_style="blue"
    ))
    
    # Check system requirements
    console.print("\n[bold]1. Checking system requirements...[/bold]")
    
    checks_passed = 0
    total_checks = 4
    
    if check_python_version():
        checks_passed += 1
    
    if check_git_installation():
        checks_passed += 1
    
    if check_git_repository():
        checks_passed += 1
    
    # Install dependencies
    console.print("\n[bold]2. Installing dependencies...[/bold]")
    if install_dependencies():
        checks_passed += 1
    
    # Test imports
    console.print("\n[bold]3. Testing imports...[/bold]")
    if test_imports():
        checks_passed += 1
        total_checks += 1
    
    # Test basic functionality
    console.print("\n[bold]4. Testing basic functionality...[/bold]")
    if test_basic_functionality():
        checks_passed += 1
        total_checks += 1
    
    # Summary
    console.print(f"\n[bold]📊 Summary: {checks_passed}/{total_checks} checks passed[/bold]")
    
    if checks_passed == total_checks:
        console.print(Panel(
            "🎉 Setup completed successfully!\n\n"
            "You can now use the Git commit logger:\n"
            "• python cli/track_commit.py --summary\n"
            "• python cli/view_commits.py --detailed\n"
            "• python example_usage.py",
            title="✅ Success",
            border_style="green"
        ))
        
        # Run demo
        if console.input("\nWould you like to run a demo? (y/n): ").lower().startswith('y'):
            run_demo()
    else:
        console.print(Panel(
            "❌ Setup incomplete. Please fix the issues above and try again.",
            title="Setup Failed",
            border_style="red"
        ))
        sys.exit(1)


if __name__ == '__main__':
    main()
