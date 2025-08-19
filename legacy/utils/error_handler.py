"""
Error handling utilities for CraftNudge Git Commit Logger.
Provides graceful error handling with user-friendly feedback.
"""

import sys
from typing import Optional, Callable, Any
from pathlib import Path
import git
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


class CraftNudgeError(Exception):
    """Base exception for CraftNudge application."""
    pass


class GitRepositoryError(CraftNudgeError):
    """Raised when Git repository operations fail."""
    pass


class DataStorageError(CraftNudgeError):
    """Raised when data storage operations fail."""
    pass


class ConfigurationError(CraftNudgeError):
    """Raised when configuration is invalid."""
    pass


def handle_git_errors(func: Callable) -> Callable:
    """Decorator to handle Git-related errors gracefully."""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except git.InvalidGitRepositoryError:
            error_msg = (
                "❌ No Git repository found in the current directory.\n"
                "Please run this command from within a Git repository."
            )
            console.print(Panel(error_msg, title="Git Repository Error", border_style="red"))
            sys.exit(1)
        except git.NoSuchPathError:
            error_msg = (
                "❌ The specified Git repository path does not exist.\n"
                "Please check the path and try again."
            )
            console.print(Panel(error_msg, title="Git Path Error", border_style="red"))
            sys.exit(1)
        except git.GitCommandError as e:
            error_msg = f"❌ Git command failed: {str(e)}"
            console.print(Panel(error_msg, title="Git Command Error", border_style="red"))
            sys.exit(1)
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            console.print(Panel(error_msg, title="Unexpected Error", border_style="red"))
            sys.exit(1)
    return wrapper


def handle_file_errors(func: Callable) -> Callable:
    """Decorator to handle file operation errors gracefully."""
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except PermissionError:
            error_msg = (
                "❌ Permission denied when accessing files.\n"
                "Please check file permissions and try again."
            )
            console.print(Panel(error_msg, title="Permission Error", border_style="red"))
            sys.exit(1)
        except FileNotFoundError:
            error_msg = (
                "❌ Required file not found.\n"
                "Please check if the data directory exists."
            )
            console.print(Panel(error_msg, title="File Not Found", border_style="red"))
            sys.exit(1)
        except Exception as e:
            error_msg = f"❌ File operation failed: {str(e)}"
            console.print(Panel(error_msg, title="File Error", border_style="red"))
            sys.exit(1)
    return wrapper


def validate_git_repository(repo_path: Path) -> bool:
    """Validate that the given path is a Git repository."""
    try:
        git.Repo(repo_path)
        return True
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        return False


def validate_data_directory(data_path: Path) -> bool:
    """Validate that the data directory exists and is writable."""
    try:
        data_path.mkdir(parents=True, exist_ok=True)
        # Test write permission
        test_file = data_path / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
        return True
    except (PermissionError, OSError):
        return False


def display_success_message(message: str) -> None:
    """Display a success message with consistent styling."""
    console.print(Panel(message, title="✅ Success", border_style="green"))


def display_info_message(message: str) -> None:
    """Display an info message with consistent styling."""
    console.print(Panel(message, title="ℹ️ Info", border_style="blue"))


def display_warning_message(message: str) -> None:
    """Display a warning message with consistent styling."""
    console.print(Panel(message, title="⚠️ Warning", border_style="yellow"))


def display_error_message(message: str, title: str = "❌ Error") -> None:
    """Display an error message with consistent styling."""
    console.print(Panel(message, title=title, border_style="red"))


def safe_exit(exit_code: int = 0, message: Optional[str] = None) -> None:
    """Safely exit the application with optional message."""
    if message:
        if exit_code == 0:
            display_success_message(message)
        else:
            display_error_message(message)
    sys.exit(exit_code)
