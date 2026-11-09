"""
Unit tests for SDK Auditor.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from qnx_sentinel.audit.sdk_auditor import SDKAuditor


class TestSDKAuditor(unittest.TestCase):

    def test_missing_environment(self):
        # Empty env
        auditor = SDKAuditor(override_env={})
        sdk = auditor.audit()
        self.assertFalse(sdk.is_qnx_sdp_detected)
        self.assertIsNone(sdk.qnx_host)
        self.assertIsNone(sdk.qnx_target)
        self.assertIsNotNone(sdk.env_script_suggested)
        self.assertTrue(any("QNX_HOST environment variable is not defined" in n for n in sdk.diagnostic_notes))

    def test_valid_environment_mock(self):
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            host_dir = tmp_path / "host"
            target_dir = tmp_path / "target"
            host_dir.mkdir()
            target_dir.mkdir()
            (target_dir / "aarch64le").mkdir()

            mock_env = {
                "QNX_HOST": str(host_dir),
                "QNX_TARGET": str(target_dir),
            }
            auditor = SDKAuditor(override_env=mock_env)
            sdk = auditor.audit()
            self.assertTrue(sdk.is_qnx_sdp_detected)
            self.assertEqual(sdk.qnx_host, str(host_dir))
            self.assertEqual(sdk.qnx_target, str(target_dir))
            self.assertIn("aarch64le", sdk.supported_targets)


if __name__ == "__main__":
    unittest.main()
