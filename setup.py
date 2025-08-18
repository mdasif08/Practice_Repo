"""
Setup script for CraftNudge Git Commit Logger
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [line.strip() for line in requirements_path.read_text().splitlines() 
                   if line.strip() and not line.startswith("#")]

setup(
    name="craftnudge-git-logger",
    version="1.0.0",
    author="CraftNudge Team",
    author_email="team@craftnudge.com",
    description="A microservice-based Git commit logger for tracking coding patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/craftnudge/git-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "track-commit=cli.track_commit:main",
            "view-commits=cli.view_commits:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="git, commit, logger, tracking, development, productivity",
    project_urls={
        "Bug Reports": "https://github.com/craftnudge/git-logger/issues",
        "Source": "https://github.com/craftnudge/git-logger",
        "Documentation": "https://github.com/craftnudge/git-logger/blob/main/README.md",
    },
)
