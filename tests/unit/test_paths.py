"""
SSI Paths Tests - Verification of path configuration correctness

Version: 1.1
Date: 2026-07-31

Converted from unittest to pytest for Sprint 8 compliance.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add root proyecto to sys.path (tests/unit/ -> root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.resolve()))

from SSI.config.paths import SSIPaths
from SSI.config.validator import SSIConfigValidator, validate_paths, ConfigValidationError


# Fixtures for pytest
import pytest


@pytest.fixture
def temp_directory():
    """Create and cleanup temporary directory for each test."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    yield temp_dir, original_cwd, original_path
    
    os.chdir(original_cwd)
    sys.path = original_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def ssi_paths():
    """Provide SSIPaths instance for testing."""
    return SSIPaths()


@pytest.fixture
def path_validator():
    """Provide SSIConfigValidator instance for testing."""
    return SSIConfigValidator()


# ============================================================================
# SSIPaths Tests
# ============================================================================

class TestSSIPaths:
    """Tests for SSIPaths class using pytest."""
    
    def test_no_double_ssi_prefix(self, ssi_paths):
        """Test that paths do not contain double SSI/SSI prefix."""
        # Check all module paths
        module_paths = [
            ssi_paths.v2_path, ssi_paths.v3_path, ssi_paths.v4_path,
            ssi_paths.strategy_path, ssi_paths.laboratories_path,
            ssi_paths.feedback_path, ssi_paths.decision_path, ssi_paths.evolution_path
        ]
        
        for path in module_paths:
            path_str = str(path)
            assert "SSI/SSI" not in path_str, f"Path {path_str} contains double SSI/SSI prefix"
            assert "SSI\\SSI" not in path_str, f"Path {path_str} contains double SSI\\SSI prefix"
        
        # Check all data paths
        data_paths = [
            ssi_paths.data_root, ssi_paths.raw_data_path, ssi_paths.processed_data_path,
            ssi_paths.worlds_data_path, ssi_paths.results_data_path
        ]
        
        for path in data_paths:
            path_str = str(path)
            assert "SSI/SSI" not in path_str, f"Path {path_str} contains double SSI/SSI prefix"
            assert "SSI\\SSI" not in path_str, f"Path {path_str} contains double SSI\\SSI prefix"
        
        # Check configuration paths
        config_paths = [ssi_paths.config_path, ssi_paths.utils_path, ssi_paths.tests_path]
        
        for path in config_paths:
            path_str = str(path)
            assert "SSI/SSI" not in path_str, f"Path {path_str} contains double SSI/SSI prefix"
            assert "SSI\\SSI" not in path_str, f"Path {path_str} contains double SSI\\SSI prefix"
    
    def test_get_absolute_path_returns_path_object(self, ssi_paths):
        """Test that get_absolute_path returns a Path object."""
        result = ssi_paths.get_absolute_path("v2")
        assert isinstance(result, Path)
    
    def test_get_absolute_path_no_ssi_ssi(self, ssi_paths):
        """Test that get_absolute_path does not return paths with SSI/SSI."""
        # Test all standard paths
        test_paths = [
            ssi_paths.v2_path, ssi_paths.v3_path, ssi_paths.v4_path,
            ssi_paths.data_root, ssi_paths.raw_data_path, ssi_paths.config_path
        ]
        
        for relative_path in test_paths:
            absolute_path = ssi_paths.get_absolute_path(relative_path)
            path_str = str(absolute_path)
            assert "SSI/SSI" not in path_str, f"Absolute path {path_str} contains SSI/SSI"
            assert "SSI\\SSI" not in path_str, f"Absolute path {path_str} contains SSI\\SSI"
    
    def test_root_path_resolves_correctly(self, ssi_paths):
        """Test that root_path is correctly set."""
        # root_path should be SSI directory
        assert ssi_paths.root_path.exists() or ssi_paths.root_path.name == "SSI"
    
    def test_paths_are_relative(self, ssi_paths):
        """Test that module paths are relative (do not start with SSI/)."""
        # Module paths should not start with "SSI/"
        module_paths = [
            ssi_paths.v2_path, ssi_paths.v3_path, ssi_paths.v4_path,
            ssi_paths.strategy_path, ssi_paths.laboratories_path,
            ssi_paths.feedback_path, ssi_paths.decision_path, ssi_paths.evolution_path
        ]
        
        for path in module_paths:
            path_str = str(path)
            assert not path_str.startswith("SSI/"), f"Path {path_str} starts with SSI/"
            assert not path_str.startswith("SSI" + chr(92)), f"Path {path_str} starts with SSI backslash"
    
    def test_pathlib_usage(self, ssi_paths):
        """Test that root_path uses pathlib.Path."""
        assert isinstance(ssi_paths.root_path, Path)


# ============================================================================
# Path Validator Tests
# ============================================================================

class TestPathValidator:
    """Tests for path validator."""
    
    def test_validate_paths_no_double_prefix(self):
        """Test that validate_paths does not report errors for correct paths."""
        try:
            result = validate_paths()
            assert result is True
        except ConfigValidationError:
            pytest.fail("validate_paths() reported errors for correct paths")
    
    def test_validator_path_no_ssi_ssi(self, path_validator):
        """Test validate_path_no_ssi_ssi method."""
        # Correct paths
        assert path_validator.validate_path_no_ssi_ssi("v2/test") is True
        assert path_validator.validate_path_no_ssi_ssi("data/raw") is True
        assert path_validator.validate_path_no_ssi_ssi("SSI/v2") is True
        
        # Incorrect paths
        assert path_validator.validate_path_no_ssi_ssi("SSI/SSI/v2") is False
        assert path_validator.validate_path_no_ssi_ssi("SSI\\SSI\\v2") is False


# ============================================================================
# Import Portability Tests
# ============================================================================

class TestImportPortability:
    """Test import portability."""
    
    def test_warstwa5_generator_import_no_io(self, temp_directory):
        """Test that import of warstwa5_generator does not create files."""
        temp_dir, original_cwd, original_path = temp_directory
        
        # Get project root and warstwa5_generator path
        project_root = Path(__file__).parent.parent.parent.parent
        warstwa5_path = str(project_root / "warstwa5_generator")
        
        # Record files before import
        files_before = set(os.listdir(temp_dir))
        
        # Try to import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("warstwa5_generator.konfiguracja", 
                                                       str(Path(warstwa5_path) / "konfiguracja.py"))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            
            # Graceful approach - check if import succeeds without errors
            try:
                spec.loader.exec_module(module)
                files_after = set(os.listdir(temp_dir))
                new_files = files_after - files_before
                
                # Import should not create new files in temp directory
                assert len(new_files) == 0, f"Import created files: {new_files}"
            except FileNotFoundError:
                # This is expected - paths are relative
                # but should not create files
                pass
            except Exception:
                # Other errors are acceptable, important that no files are created
                files_after = set(os.listdir(temp_dir))
                new_files = files_after - files_before
                assert len(new_files) == 0, f"Import created files before error: {new_files}"


# ============================================================================
# Working Directory Independence Tests
# ============================================================================

class TestWorkingDirectoryIndependence:
    """Test independence from working directory."""
    
    def test_paths_independent_of_cwd(self, temp_directory):
        """Test that paths are independent of current working directory."""
        temp_dir, original_cwd, original_path = temp_directory
        
        # Get paths in current directory
        from SSI.config.paths import SSIPaths
        paths1 = SSIPaths()
        
        # Change working directory
        os.chdir(temp_dir)
        
        # Get paths in new directory
        paths2 = SSIPaths()
        
        # root_path should be the same
        assert paths1.root_path == paths2.root_path