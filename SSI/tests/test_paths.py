"""
SSI Paths Tests - Verification of path configuration correctness

Version: 1.0
Date: 2026-07-31
"""

import os
import sys
from pathlib import Path
import unittest
import tempfile
import shutil

# Add parent directory to sys.path for imports to work
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from SSI.config.paths import SSIPaths
from SSI.config.validator import SSIConfigValidator, validate_paths, ConfigValidationError


class TestSSIPaths(unittest.TestCase):
    """Tests for SSIPaths class."""
    
    def setUp(self):
        """Setup before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
    
    def tearDown(self):
        """Cleanup after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_no_double_ssi_prefix(self):
        """Test that paths do not contain double SSI/SSI prefix."""
        paths = SSIPaths()
        
        # Check all module paths
        module_paths = [
            paths.v2_path, paths.v3_path, paths.v4_path,
            paths.strategy_path, paths.laboratories_path,
            paths.feedback_path, paths.decision_path, paths.evolution_path
        ]
        
        for path in module_paths:
            self.assertNotIn("SSI/SSI", path, f"Path {path} contains double SSI/SSI prefix")
            self.assertNotIn("SSI\\SSI", path, f"Path {path} contains double SSI\\SSI prefix")
        
        # Check all data paths
        data_paths = [
            paths.data_root, paths.raw_data_path, paths.processed_data_path,
            paths.worlds_data_path, paths.results_data_path
        ]
        
        for path in data_paths:
            self.assertNotIn("SSI/SSI", path, f"Path {path} contains double SSI/SSI prefix")
            self.assertNotIn("SSI\\SSI", path, f"Path {path} contains double SSI\\SSI prefix")
        
        # Check configuration paths
        config_paths = [paths.config_path, paths.utils_path, paths.tests_path]
        
        for path in config_paths:
            self.assertNotIn("SSI/SSI", path, f"Path {path} contains double SSI/SSI prefix")
            self.assertNotIn("SSI\\SSI", path, f"Path {path} contains double SSI\\SSI prefix")
    
    def test_get_absolute_path_returns_path_object(self):
        """Test that get_absolute_path returns a Path object."""
        paths = SSIPaths()
        result = paths.get_absolute_path("v2")
        self.assertIsInstance(result, Path)
    
    def test_get_absolute_path_no_ssi_ssi(self):
        """Test that get_absolute_path does not return paths with SSI/SSI."""
        paths = SSIPaths()
        
        # Test all standard paths
        test_paths = [
            paths.v2_path, paths.v3_path, paths.v4_path,
            paths.data_root, paths.raw_data_path, paths.config_path
        ]
        
        for relative_path in test_paths:
            absolute_path = paths.get_absolute_path(relative_path)
            path_str = str(absolute_path)
            self.assertNotIn("SSI/SSI", path_str, 
                           f"Absolute path {path_str} contains SSI/SSI")
            self.assertNotIn("SSI\\SSI", path_str,
                           f"Absolute path {path_str} contains SSI\\SSI")
    
    def test_root_path_resolves_correctly(self):
        """Test that root_path is correctly set."""
        paths = SSIPaths()
        # root_path should be SSI directory
        self.assertTrue(paths.root_path.exists() or paths.root_path.name == "SSI")
    
    def test_paths_are_relative(self):
        """Test that module paths are relative (do not start with SSI/)."""
        paths = SSIPaths()
        
        # Module paths should not start with "SSI/"
        module_paths = [
            paths.v2_path, paths.v3_path, paths.v4_path,
            paths.strategy_path, paths.laboratories_path,
            paths.feedback_path, paths.decision_path, paths.evolution_path
        ]
        
        for path in module_paths:
            self.assertFalse(path.startswith("SSI/"), 
                           f"Path {path} starts with SSI/")
            self.assertFalse(path.startswith("SSI" + chr(92)),
                           f"Path {path} starts with SSI backslash")
    
    def test_pathlib_usage(self):
        """Test that root_path uses pathlib.Path."""
        paths = SSIPaths()
        self.assertIsInstance(paths.root_path, Path)


class TestPathValidator(unittest.TestCase):
    """Tests for path validator."""
    
    def test_validate_paths_no_double_prefix(self):
        """Test that validate_paths does not report errors for correct paths."""
        try:
            result = validate_paths()
            self.assertTrue(result)
        except ConfigValidationError:
            self.fail("validate_paths() reported errors for correct paths")
    
    def test_validator_path_no_ssi_ssi(self):
        """Test validate_path_no_ssi_ssi method."""
        validator = SSIConfigValidator()
        
        # Correct paths
        self.assertTrue(validator.validate_path_no_ssi_ssi("v2/test"))
        self.assertTrue(validator.validate_path_no_ssi_ssi("data/raw"))
        self.assertTrue(validator.validate_path_no_ssi_ssi("SSI/v2"))
        
        # Incorrect paths
        self.assertFalse(validator.validate_path_no_ssi_ssi("SSI/SSI/v2"))
        self.assertFalse(validator.validate_path_no_ssi_ssi("SSI\\SSI\\v2"))


class TestImportPortability(unittest.TestCase):
    """Test import portability."""
    
    def test_warstwa5_generator_import_no_io(self):
        """Test that import of warstwa5_generator does not create files."""
        # Change working directory to temporary
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        original_path = sys.path.copy()
        
        try:
            os.chdir(temp_dir)
            
            # Add temporary directory to sys.path
            sys.path.insert(0, temp_dir)
            
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
                    self.assertEqual(len(new_files), 0, 
                                   f"Import created files: {new_files}")
                except FileNotFoundError:
                    # This is expected - paths are relative
                    # but should not create files
                    pass
                except Exception:
                    # Other errors are acceptable, important that no files are created
                    files_after = set(os.listdir(temp_dir))
                    new_files = files_after - files_before
                    self.assertEqual(len(new_files), 0,
                                   f"Import created files before error: {new_files}")
                    
        finally:
            os.chdir(original_cwd)
            sys.path = original_path
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestWorkingDirectoryIndependence(unittest.TestCase):
    """Test independence from working directory."""
    
    def test_paths_independent_of_cwd(self):
        """Test that paths are independent of current working directory."""
        original_cwd = os.getcwd()
        paths1 = None
        paths2 = None
        
        try:
            # Get paths in current directory
            from SSI.config.paths import SSIPaths
            paths1 = SSIPaths()
            
            # Change working directory
            temp_dir = tempfile.mkdtemp()
            os.chdir(temp_dir)
            
            # Get paths in new directory
            paths2 = SSIPaths()
            
            # root_path should be the same
            self.assertEqual(paths1.root_path, paths2.root_path)
            
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
