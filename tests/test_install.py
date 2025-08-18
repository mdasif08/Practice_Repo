"""
Unit tests for the install.py script.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from install import (
    check_python_version,
    install_requirements,
    main
)


class TestPythonVersionCheck:
    """Test Python version checking functionality."""
    
    def test_check_python_version_current(self):
        """Test Python version check with current version."""
        result = check_python_version()
        assert result in ["minimal", "full"]
    
    @patch('sys.version_info')
    def test_check_python_version_313_plus(self, mock_version_info):
        """Test Python version check with Python 3.13+."""
        mock_version_info.major = 3
        mock_version_info.minor = 13
        
        result = check_python_version()
        assert result == "minimal"
    
    @patch('sys.version_info')
    def test_check_python_version_312(self, mock_version_info):
        """Test Python version check with Python 3.12."""
        mock_version_info.major = 3
        mock_version_info.minor = 12
        
        result = check_python_version()
        assert result == "full"
    
    @patch('sys.version_info')
    def test_check_python_version_38(self, mock_version_info):
        """Test Python version check with Python 3.8."""
        mock_version_info.major = 3
        mock_version_info.minor = 8
        
        result = check_python_version()
        assert result == "full"
    
    @patch('sys.version_info')
    def test_check_python_version_37(self, mock_version_info):
        """Test Python version check with Python 3.7 (too old)."""
        mock_version_info.major = 3
        mock_version_info.minor = 7
        
        result = check_python_version()
        assert result is False
    
    @patch('sys.version_info')
    def test_check_python_version_2(self, mock_version_info):
        """Test Python version check with Python 2."""
        mock_version_info.major = 2
        mock_version_info.minor = 7
        
        result = check_python_version()
        assert result is False


class TestRequirementsInstallation:
    """Test requirements installation functionality."""
    
    @patch('subprocess.run')
    def test_install_requirements_success(self, mock_run):
        """Test successful requirements installation."""
        mock_run.return_value.returncode = 0
        
        result = install_requirements('requirements-basic.txt')
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_requirements_failure(self, mock_run):
        """Test failed requirements installation."""
        mock_run.return_value.returncode = 1
        
        result = install_requirements('requirements-basic.txt')
        assert result is False
    
    @patch('subprocess.run')
    def test_install_requirements_file_not_found(self, mock_run):
        """Test requirements installation with file not found."""
        mock_run.side_effect = FileNotFoundError()
        
        result = install_requirements('nonexistent.txt')
        assert result is False
    
    @patch('subprocess.run')
    def test_install_requirements_permission_error(self, mock_run):
        """Test requirements installation with permission error."""
        mock_run.side_effect = PermissionError()
        
        result = install_requirements('requirements-basic.txt')
        assert result is False


class TestMainFunction:
    """Test main function functionality."""
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_main_success_minimal(self, mock_path, mock_install, mock_version):
        """Test main function with minimal requirements success."""
        mock_version.return_value = "minimal"
        mock_path.return_value = True
        mock_install.return_value = True
        
        # Should return normally when successful
        result = main()
        assert result is None
        mock_install.assert_called_with('requirements-basic.txt')
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_main_success_full(self, mock_path, mock_install, mock_version):
        """Test main function with full requirements success."""
        mock_version.return_value = "full"
        mock_path.return_value = True
        mock_install.return_value = True
        
        # Should return normally when successful
        result = main()
        assert result is None
        mock_install.assert_called_with('requirements-minimal.txt')
    
    @patch('install.check_python_version')
    def test_main_python_version_failure(self, mock_version):
        """Test main function with Python version failure."""
        mock_version.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('install.check_python_version')
    @patch('pathlib.Path.exists')
    def test_main_requirements_file_not_found(self, mock_path, mock_version):
        """Test main function with requirements file not found."""
        mock_version.return_value = "minimal"
        mock_path.return_value = False
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_main_installation_failure(self, mock_path, mock_install, mock_version):
        """Test main function with installation failure."""
        mock_version.return_value = "minimal"
        mock_path.return_value = True
        mock_install.return_value = False
        
        # Should return normally even on installation failure
        result = main()
        assert result is None


class TestInstallationWorkflow:
    """Test complete installation workflows."""
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_complete_successful_workflow_minimal(self, mock_path, mock_install, mock_version):
        """Test complete successful workflow with minimal requirements."""
        mock_version.return_value = "minimal"
        mock_path.return_value = True
        mock_install.return_value = True
        
        # Should return normally when successful
        result = main()
        assert result is None
        mock_install.assert_called_once_with('requirements-basic.txt')
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_complete_successful_workflow_full(self, mock_path, mock_install, mock_version):
        """Test complete successful workflow with full requirements."""
        mock_version.return_value = "full"
        mock_path.return_value = True
        mock_install.return_value = True
        
        # Should return normally when successful
        result = main()
        assert result is None
        mock_install.assert_called_once_with('requirements-minimal.txt')
    
    @patch('install.check_python_version')
    @patch('install.install_requirements')
    @patch('pathlib.Path.exists')
    def test_complete_failed_workflow(self, mock_path, mock_install, mock_version):
        """Test complete failed installation workflow."""
        mock_version.return_value = "minimal"
        mock_path.return_value = True
        mock_install.return_value = False  # All installations fail
        
        # Should return normally even on failure
        result = main()
        assert result is None


class TestPythonVersionLogic:
    """Test Python version logic comprehensively."""
    
    def test_python_version_logic(self):
        """Test Python version logic with various versions."""
        from install import check_python_version
        
        # Test Python 3.8+
        with patch('sys.version_info') as mock_version:
            mock_version.major = 3
            mock_version.minor = 8
            assert check_python_version() == "full"
        
        # Test Python 3.7 (too old)
        with patch('sys.version_info') as mock_version:
            mock_version.major = 3
            mock_version.minor = 7
            assert check_python_version() is False
        
        # Test Python 2
        with patch('sys.version_info') as mock_version:
            mock_version.major = 2
            mock_version.minor = 7
            assert check_python_version() is False


class TestErrorHandling:
    """Test error handling in installation process."""
    
    @patch('subprocess.run')
    def test_install_requirements_various_errors(self, mock_run):
        """Test install_requirements with various error conditions."""
        # Test CalledProcessError
        mock_run.side_effect = Exception("Installation failed")
        
        result = install_requirements('requirements-basic.txt')
        assert result is False
    
    @patch('install.check_python_version')
    def test_main_with_version_detection_error(self, mock_version):
        """Test main function with version detection error."""
        mock_version.side_effect = Exception("Version detection failed")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
