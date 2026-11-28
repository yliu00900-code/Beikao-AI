import tempfile
import unittest
from pathlib import Path
from unittest import mock

from automation.adb import take_screenshot


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake-png-data"


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
            stdout.write(PNG_BYTES)
            return fake

        with mock.patch("automation.adb.connected_devices", return_value=["device-A", "device-B"]), \
             mock.patch("automation.adb.CAPTURE_DIR", self.capture_dir), \
             mock.patch("automation.adb.LATEST_SCREENSHOT", self.path), \
             mock.patch("automation.adb.subprocess.run", side_effect=write_png) as run:
            returned = take_screenshot("device-B")

        self.assertEqual(returned, self.path)
        self.assertEqual(self.path.read_bytes(), PNG_BYTES)
        self.assertEqual(run.call_args.args[0][:3], ["adb", "-s", "device-B"])

    def test_failed_capture_preserves_previous_screenshot(self):
        self.path.write_bytes(b"previous-valid-image")
        fake = mock.Mock(returncode=1, stderr=b"device offline")

        def write_partial(command, stdout, stderr, timeout):
            stdout.write(b"partial-data")
            return fake

        with mock.patch("automation.adb.connected_devices", return_value=["device-A"]), \
             mock.patch("automation.adb.CAPTURE_DIR", self.capture_dir), \
             mock.patch("automation.adb.LATEST_SCREENSHOT", self.path), \
             mock.patch("automation.adb.subprocess.run", side_effect=write_partial):
            with self.assertRaisesRegex(RuntimeError, "device offline"):
                take_screenshot()

        self.assertEqual(self.path.read_bytes(), b"previous-valid-image")
        self.assertEqual(list(self.capture_dir.glob(".latest-*.png")), [])

    def test_invalid_png_preserves_previous_screenshot(self):
        self.path.write_bytes(b"previous-valid-image")

        def write_invalid(command, stdout, stderr, timeout):
            stdout.write(b"not-a-png")
            return mock.Mock(returncode=0, stderr=b"")

        with mock.patch("automation.adb.connected_devices", return_value=["device-A"]), \
             mock.patch("automation.adb.CAPTURE_DIR", self.capture_dir), \
             mock.patch("automation.adb.LATEST_SCREENSHOT", self.path), \
             mock.patch("automation.adb.subprocess.run", side_effect=write_invalid):
            with self.assertRaisesRegex(RuntimeError, "不是有效 PNG"):
                take_screenshot()

        self.assertEqual(self.path.read_bytes(), b"previous-valid-image")
        self.assertEqual(list(self.capture_dir.glob(".latest-*.png")), [])


if __name__ == "__main__":
    unittest.main()
