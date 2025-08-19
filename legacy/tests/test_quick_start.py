"""
Unit tests for the quick_start.py script.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from quick_start import (
    check_python_version,
    check_git_installation,
    check_git_repository,
    install_dependencies,
    test_imports,
    test_basic_functionality,
    run_demo,
    main
)


class TestSystemChecks:
    """Test system requirement checks."""
    
    def test_check_python_version_valid(self):
        """Test Python version check with valid version."""
        result = check_python_version()
        assert result is True
    
    def test_check_python_version_invalid_major(self):
        """Test Python version check with invalid major version."""
        with patch('sys.version_info') as mock_version:
            mock_version.major = 2
            mock_version.minor = 7
            result = check_python_version()
            assert result is False
    
    def test_check_python_version_invalid_minor(self):
        """Test Python version check with invalid minor version."""
        with patch('sys.version_info') as mock_version:
            mock_version.major = 3
            mock_version.minor = 6
            result = check_python_version()
            assert result is False
    
    @patch('subprocess.run')
    def test_check_git_installation_success(self, mock_run):
        """Test Git installation check with success."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b'git version 2.30.0'
        
        result = check_git_installation()
        assert result is True
        mock_run.assert_called_once_with(['git', '--version'], capture_output=True, text=True, check=True)
    
    @patch('subprocess.run')
    def test_check_git_installation_not_found(self, mock_run):
        """Test Git installation check with Git not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = check_git_installation()
        assert result is False
    
    @patch('subprocess.run')
    def test_check_git_installation_command_error(self, mock_run):
        """Test Git installation check with command error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git --version")
        
        result = check_git_installation()
        assert result is False
    
    @patch('subprocess.run')
    def test_check_git_repository_success(self, mock_run):
        """Test Git repository check with success."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b'.git'
        
        result = check_git_repository()
        assert result is True
        mock_run.assert_called_once_with(['git', 'rev-parse', '--git-dir'], capture_output=True, text=True, check=True)
    
    @patch('subprocess.run')
    def test_check_git_repository_not_found(self, mock_run):
        """Test Git repository check with no repository."""
        mock_run.side_effect = subprocess.CalledProcessError(128, "git rev-parse --git-dir")
        
        result = check_git_repository()
        assert result is False


class TestDependencyInstallation:
    """Test dependency installation functionality."""
    
    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run):
        """Test successful dependency installation."""
        mock_run.return_value = Mock()
        
        result = install_dependencies()
        assert result is True
        mock_run.assert_called()
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run):
        """Test failed dependency installation."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip install")
        
        result = install_dependencies()
        assert result is False
    
    @patch('subprocess.run')
    def test_install_dependencies_file_not_found(self, mock_run):
        """Test dependency installation with file not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = install_dependencies()
        assert result is False


class TestImportTesting:
    """Test import functionality."""
    
    def test_test_imports_success(self):
        """Test successful import testing."""
        result = test_imports()
        assert result is True
    
    @patch('quick_start.importlib.import_module')
    def test_test_imports_failure(self, mock_import):
        """Test failed import testing."""
        mock_import.side_effect = ImportError("Module not found")
        
        result = test_imports()
        assert result is False


class TestBasicFunctionality:
    """Test basic functionality testing."""
    
    @patch('quick_start.CommitTrackerService')
    @patch('quick_start.DataStorageService')
    def test_test_basic_functionality_success(self, mock_storage_class, mock_tracker_class):
        """Test successful basic functionality test."""
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {'repository_path': '/test/repo'}
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage = Mock()
        mock_storage.get_statistics.return_value = {'total_commits': 0}
        mock_storage_class.return_value = mock_storage
        
        result = test_basic_functionality()
        assert result is True
    
    @patch('quick_start.CommitTrackerService')
    def test_test_basic_functionality_tracker_error(self, mock_tracker_class):
        """Test basic functionality test with tracker error."""
        mock_tracker_class.side_effect = Exception("Tracker error")
        
        result = test_basic_functionality()
        assert result is False
    
    @patch('quick_start.CommitTrackerService')
    @patch('quick_start.DataStorageService')
    def test_test_basic_functionality_storage_error(self, mock_storage_class, mock_tracker_class):
        """Test basic functionality test with storage error."""
        mock_tracker = Mock()
        mock_tracker.get_repository_info.return_value = {'repository_path': '/test/repo'}
        mock_tracker_class.return_value = mock_tracker
        
        mock_storage_class.side_effect = Exception("Storage error")
        
        result = test_basic_functionality()
        assert result is False


class TestDemoFunction:
    """Test demo functionality."""
    
    @patch('quick_start.subprocess.run')
    def test_run_demo_success(self, mock_run):
        """Test successful demo run."""
        mock_run.return_value = Mock()
        
        # Should not raise any exceptions
        run_demo()


class TestMainFunction:
    """Test main function functionality."""
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    @patch('quick_start.console.input')
    def test_main_all_success(self, mock_input, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with all checks passing."""
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = True
        mock_install.return_value = True
        mock_imports.return_value = True
        mock_basic.return_value = True
        mock_input.return_value = 'n'  # Don't run demo
        
        # Should return normally when all checks pass
        result = main()
        assert result is None
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    def test_main_python_version_failure(self, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with Python version check failure."""
        mock_python.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    def test_main_git_installation_failure(self, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with Git installation check failure."""
        mock_python.return_value = True
        mock_git_install.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    def test_main_git_repository_failure(self, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with Git repository check failure."""
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    def test_main_installation_failure(self, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with dependency installation failure."""
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = True
        mock_install.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    @patch('quick_start.console.input')
    def test_main_imports_failure(self, mock_input, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with import testing failure."""
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = True
        mock_install.return_value = True
        mock_imports.return_value = False
        mock_input.return_value = 'n'  # Don't run demo
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    @patch('quick_start.console.input')
    def test_main_basic_functionality_failure(self, mock_input, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test main function with basic functionality testing failure."""
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = True
        mock_install.return_value = True
        mock_imports.return_value = True
        mock_basic.return_value = False
        mock_input.return_value = 'n'  # Don't run demo
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


class TestQuickStartIntegration:
    """Integration tests for quick start functionality."""
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    @patch('quick_start.console.input')
    @patch('quick_start.run_demo')
    def test_complete_successful_workflow(self, mock_demo, mock_input, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test complete successful workflow."""
        # All checks pass
        mock_python.return_value = True
        mock_git_install.return_value = True
        mock_git_repo.return_value = True
        mock_install.return_value = True
        mock_imports.return_value = True
        mock_basic.return_value = True
        mock_input.return_value = 'y'  # Run demo
        mock_demo.return_value = None
        
        # Should return normally when all checks pass
        result = main()
        assert result is None
        mock_demo.assert_called_once()
    
    @patch('quick_start.check_python_version')
    @patch('quick_start.check_git_installation')
    @patch('quick_start.check_git_repository')
    @patch('quick_start.install_dependencies')
    @patch('quick_start.test_imports')
    @patch('quick_start.test_basic_functionality')
    def test_early_exit_on_failure(self, mock_basic, mock_imports, mock_install, mock_git_repo, mock_git_install, mock_python):
        """Test that main exits early on first failure."""
        # First check fails
        mock_python.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
