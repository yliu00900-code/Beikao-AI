import tempfile
import unittest
from pathlib import Path
from unittest import mock

from automation.adb import take_screenshot


class ScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "latest.png"
        self.capture_dir = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_requires_explicit_device_if_multiple_connected(self):
        with mock.patch("automation.adb.connected_devices", return_value=["device-A", "device-B"]), \
             mock.patch("automation.adb.CAPTURE_DIR", self.capture_dir), \
             mock.patch("automation.adb.LATEST_SCREENSHOT", self.path):
            with self.assertRaisesRegex(RuntimeError, "多台设备"):
                take_screenshot()

    def test_rejects_disconnected_serial(self):
        with mock.patch("automation.adb.connected_devices", return_value=["device-A"]):
            with self.assertRaisesRegex(RuntimeError, "未连接"):
                take_screenshot("device-B")

    def test_explicit_serial_is_used_for_capture(self):
        fake = mock.Mock(returncode=0, stderr=b"")
        def write_png(command, stdout, stderr, timeout):
            stdout.write(b"fake-png")
            return fake
        with mock.patch("automation.adb.connected_devices", return_value=["device-A", "device-B"]), \
             mock.patch("automation.adb.CAPTURE_DIR", self.capture_dir), \
             mock.patch("automation.adb.LATEST_SCREENSHOT", self.path), \
             mock.patch("automation.adb.subprocess.run", side_effect=write_png) as run:
            returned = take_screenshot("device-B")
        self.assertEqual(returned, self.path)
        self.assertEqual(self.path.read_bytes(), b"fake-png")
        self.assertEqual(run.call_args.args[0][:3], ["adb", "-s", "device-B"])


if __name__ == "__main__":
    unittest.main()
