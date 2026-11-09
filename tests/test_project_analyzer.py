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

    def test_empty_project(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            analyzer = ProjectAnalyzer(tmp_path)
            struct = analyzer.analyze()
            self.assertEqual(struct.metrics.total_files, 0)
            self.assertEqual(struct.metrics.lines_of_code, 0)
            self.assertIn("Custom/Generic", struct.build_systems)

    def test_invalid_include_paths(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            src_file = tmp_path / "main.c"
            src_file.write_text(
                '#include "non_existent_header_xyz.h"\nint main() { return 0; }\n',
                encoding="utf-8"
            )
            analyzer = ProjectAnalyzer(tmp_path)
            struct = analyzer.analyze()
            self.assertEqual(len(struct.unresolved_includes), 1)
            self.assertIn("non_existent_header_xyz.h", struct.unresolved_includes[0])

    def test_malformed_configuration_files(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            cmake_file = tmp_path / "CMakeLists.txt"
            # Incomplete / corrupted CMakeLists
            cmake_file.write_text(
                'cmake_minimum_required(VERSION 3.20\nproject(broken_syntax\n',
                encoding="utf-8"
            )
            analyzer = ProjectAnalyzer(tmp_path)
            struct = analyzer.analyze()
            # Does not crash, detects CMake build system and flags missing configs
            self.assertIn("CMake", struct.build_systems)
            self.assertGreater(len(struct.missing_configs), 0)


if __name__ == "__main__":
    unittest.main()
