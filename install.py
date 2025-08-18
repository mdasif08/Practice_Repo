#!/usr/bin/env python3
"""
Simple installation script for CraftNudge Git Commit Logger
Handles Python version compatibility and dependency installation
"""

import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check Python version and provide recommendations."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13+ detected - using minimal requirements")
        return "minimal"
    
    print("✅ Python version is compatible")
    return "full"


def install_requirements(requirements_file):
    """Install requirements from specified file."""
    print(f"\n📦 Installing from {requirements_file}...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ], capture_output=True, text=True, check=True)
        print("✅ Installation successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main installation function."""
    print("🚀 CraftNudge Git Commit Logger - Installation")
    print("=" * 50)
    
    # Check Python version
    version_check = check_python_version()
    if not version_check:
        sys.exit(1)
    
    # Determine which requirements file to use
    if version_check == "minimal":
        requirements_file = "requirements-basic.txt"
        print("\n💡 Using basic requirements (no compilation needed) for Python 3.13+")
    else:
        requirements_file = "requirements-minimal.txt"
        print("\n💡 Using minimal requirements (no pandas/numpy)")
    
    # Check if requirements file exists
    if not Path(requirements_file).exists():
        print(f"❌ Requirements file {requirements_file} not found")
        sys.exit(1)
    
    # Install dependencies
    if install_requirements(requirements_file):
        print("\n🎉 Installation completed successfully!")
        print("\nNext steps:")
        print("1. Make sure you're in a Git repository")
        print("2. Run: python cli/track_commit.py --summary")
        print("3. Or run: python quick_start.py for a guided setup")
    else:
        print("\n❌ Installation failed. Try these alternatives:")
        print("1. Update pip: python -m pip install --upgrade pip")
        print("2. Try minimal requirements: pip install -r requirements-minimal.txt")
        print("3. Install dependencies one by one if needed")


if __name__ == '__main__':
    main()
