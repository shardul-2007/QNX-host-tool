"""
Unit tests for Build Configuration Assistant.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from qnx_sentinel.analyzer.project_analyzer import ProjectAnalyzer
from qnx_sentinel.builder.config_assistant import ConfigAssistant


class TestConfigAssistant(unittest.TestCase):

    def test_plan_and_dry_run_safety(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            # Create a simple CMakeLists.txt
            cmake_file = tmp_path / "CMakeLists.txt"
            cmake_file.write_text(
                "cmake_minimum_required(VERSION 3.20)\n"
                "project(test_app)\n"
                "set(CMAKE_CXX_FLAGS \"-lang-c++\")\n"
                "add_executable(test_app main.cpp)\n"
                "target_link_libraries(test_app PRIVATE pthread)\n",
                encoding="utf-8"
            )

            p_analyzer = ProjectAnalyzer(tmp_path)
            struct = p_analyzer.analyze()

            assistant = ConfigAssistant(tmp_path)
            plans = assistant.plan_changes(struct)

            # Proposes qnx.toolchain.cmake, CMakePresets.json, and CMakeLists.txt modifications
            self.assertIn("qnx.toolchain.cmake", plans)
            self.assertIn("CMakePresets.json", plans)
            self.assertIn("CMakeLists.txt", plans)

            # Ensure dry run: files not yet created on disk
            self.assertFalse((tmp_path / "qnx.toolchain.cmake").exists())
            self.assertFalse((tmp_path / "CMakePresets.json").exists())

            # Refuse application without confirmation
            with self.assertRaises(PermissionError):
                assistant.apply_plan(plans, confirmed=False)

            # Apply with confirmation
            applied = assistant.apply_plan(plans, confirmed=True)
            self.assertEqual(len(applied), 3)
            self.assertTrue((tmp_path / "qnx.toolchain.cmake").exists())
            self.assertTrue((tmp_path / "CMakePresets.json").exists())

            # Check that CMakeLists.txt was patched
            patched_content = cmake_file.read_text(encoding="utf-8")
            self.assertNotIn("-lang-c++", patched_content)
            self.assertIn("if(NOT CMAKE_SYSTEM_NAME STREQUAL \"QNX\")", patched_content)


if __name__ == "__main__":
    unittest.main()
