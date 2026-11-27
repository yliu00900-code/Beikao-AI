"""只读环境诊断测试：多设备时不得任意挑选一台查询。"""
import unittest
from unittest import mock

from automation.diagnostics import run_diagnostics


class DiagnosticsDeviceSelectionTests(unittest.TestCase):
    def test_single_device_checks_that_devices_resolution(self):
        with mock.patch(
            "automation.diagnostics._run",
            side_effect=[
                ("List of devices attached\ndevice-A\tdevice", None),
                ("Physical size: 1080x2400", None),
            ],
        ) as run, mock.patch("automation.diagnostics.shutil.which", return_value=None):
            report = run_diagnostics()

        self.assertIn("ADB 已连接：device-A", report)
        self.assertIn("屏幕分辨率：Physical size: 1080x2400", report)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[1].args[0][:3], ["adb", "-s", "device-A"])

    def test_multiple_devices_skip_arbitrary_resolution_query(self):
        with mock.patch(
            "automation.diagnostics._run",
            return_value=("List of devices attached\ndevice-A\tdevice\ndevice-B\tdevice", None),
        ) as run, mock.patch("automation.diagnostics.shutil.which", return_value=None):
            report = run_diagnostics()

        self.assertIn("ADB 已连接：device-A, device-B", report)
        self.assertIn("为避免任意选择，本次跳过屏幕分辨率检查", report)
        self.assertIn("截图/OCR 请使用 --device 指定目标设备", report)
        self.assertNotIn("屏幕分辨率：", report)
        run.assert_called_once()

    def test_no_device_does_not_run_resolution_command(self):
        with mock.patch(
            "automation.diagnostics._run",
            return_value=("List of devices attached", None),
        ) as run, mock.patch("automation.diagnostics.shutil.which", return_value=None):
            report = run_diagnostics()

        self.assertIn("没有检测到已连接设备", report)
        run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
