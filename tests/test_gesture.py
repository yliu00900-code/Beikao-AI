import unittest
from unittest import mock

from automation.gesture import swipe_next


class SwipeSafetyTests(unittest.TestCase):
    def test_confirmation_is_required_before_device_lookup(self):
        with mock.patch("automation.gesture.connected_devices") as devices, \
             mock.patch("automation.gesture.subprocess.run") as run:
            with self.assertRaisesRegex(RuntimeError, "明确确认"):
                swipe_next()
        devices.assert_not_called()
        run.assert_not_called()

    def test_no_connected_device_fails_without_touch(self):
        with mock.patch("automation.gesture.connected_devices", return_value=[]), \
             mock.patch("automation.gesture.subprocess.run") as run:
            with self.assertRaisesRegex(RuntimeError, "没有已连接"):
                swipe_next(confirmed=True)
        run.assert_not_called()

    def test_multiple_devices_require_explicit_serial(self):
        with mock.patch(
            "automation.gesture.connected_devices",
            return_value=["192.0.2.1:40001", "192.0.2.2:40002"],
        ), mock.patch("automation.gesture.subprocess.run") as run:
            with self.assertRaisesRegex(RuntimeError, "--device"):
                swipe_next(confirmed=True)
        run.assert_not_called()

    def test_unknown_serial_is_rejected(self):
        with mock.patch("automation.gesture.connected_devices", return_value=["device-A"]), \
             mock.patch("automation.gesture.subprocess.run") as run:
            with self.assertRaisesRegex(RuntimeError, "未连接"):
                swipe_next("device-B", confirmed=True)
        run.assert_not_called()

    def test_explicit_serial_is_the_only_target(self):
        fake_result = mock.Mock(returncode=0)
        with mock.patch(
            "automation.gesture.connected_devices",
            return_value=["device-A", "device-B"],
        ), mock.patch("automation.gesture.subprocess.run", return_value=fake_result) as run:
            selected = swipe_next("device-B", confirmed=True)

        self.assertEqual(selected, "device-B")
        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["adb", "-s", "device-B"])
        self.assertEqual(command[3:6], ["shell", "input", "swipe"])
        run.assert_called_once()

    def test_single_device_can_be_selected_unambiguously(self):
        with mock.patch("automation.gesture.connected_devices", return_value=["device-A"]), \
             mock.patch("automation.gesture.subprocess.run") as run:
            selected = swipe_next(confirmed=True)
        self.assertEqual(selected, "device-A")
        self.assertEqual(run.call_args.args[0][:3], ["adb", "-s", "device-A"])


if __name__ == "__main__":
    unittest.main()
