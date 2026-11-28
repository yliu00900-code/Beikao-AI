"""CLI 错误提示测试：常见环境问题应给出简洁中文提示。"""
import contextlib
import io
import sqlite3
import subprocess
import sys
import unittest
from unittest import mock

import main


class CliErrorHandlingTests(unittest.TestCase):
    def invoke(self, arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(sys, "argv", ["main.py", *arguments]):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = main.main()
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_runtime_error_is_reported_without_traceback(self):
        with mock.patch("main.run_diagnostics", side_effect=RuntimeError("ADB 未连接")):
            exit_code, _, stderr = self.invoke(["doctor"])

        self.assertEqual(exit_code, 1)
        self.assertIn("[错误] ADB 未连接", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_subprocess_timeout_is_reported_without_traceback(self):
        timeout = subprocess.TimeoutExpired(cmd="adb", timeout=15)
        with mock.patch("main.swipe_next", side_effect=timeout):
            exit_code, _, stderr = self.invoke(["swipe-next", "--confirm"])

        self.assertEqual(exit_code, 1)
        self.assertIn("[错误]", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_database_error_is_reported_without_traceback(self):
        with mock.patch(
            "main.add_wrong",
            side_effect=sqlite3.OperationalError("database is locked"),
        ):
            exit_code, _, stderr = self.invoke(["add-wrong", "--question", "测试题"])

        self.assertEqual(exit_code, 1)
        self.assertIn("database is locked", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_successful_read_only_command_returns_zero(self):
        with mock.patch("main.run_diagnostics", return_value="诊断完成"):
            exit_code, stdout, stderr = self.invoke(["doctor"])

        self.assertEqual(exit_code, 0)
        self.assertIn("诊断完成", stdout)
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
