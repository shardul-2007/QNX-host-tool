"""
Unit tests for Project Analyzer.
"""

import unittest
from pathlib import Path
from qnx_sentinel.analyzer.project_analyzer import ProjectAnalyzer
from qnx_sentinel.core.exceptions import InvalidProjectError


class TestProjectAnalyzer(unittest.TestCase):

    def setUp(self):
        self.samples_dir = Path(__file__).resolve().parent.parent / "samples"
        self.clean_proj = self.samples_dir / "qnx8_sensor_service"
        self.legacy_proj = self.samples_dir / "legacy_linux_telematics"

    def test_clean_project_structure(self):
        analyzer = ProjectAnalyzer(self.clean_proj)
        struct = analyzer.analyze()
        self.assertEqual(struct.project_name, "qnx8_sensor_service")
        self.assertIn("CMake", struct.build_systems)
        self.assertIn("QNX_Recursive_Make", struct.build_systems)
        self.assertGreater(struct.metrics.c_files, 0)
        self.assertEqual(len(struct.missing_configs), 0)

    def test_legacy_project_structure(self):
        analyzer = ProjectAnalyzer(self.legacy_proj)
        struct = analyzer.analyze()
        self.assertEqual(struct.project_name, "legacy_linux_telematics")
        self.assertIn("CMake", struct.build_systems)
        self.assertGreater(len(struct.missing_configs), 0)
        self.assertGreater(len(struct.incompatible_dependencies), 0)

    def test_invalid_directory(self):
        with self.assertRaises(InvalidProjectError):
            ProjectAnalyzer(Path("non_existent_directory_12345"))


if __name__ == "__main__":
    unittest.main()
