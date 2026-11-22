"""需要明确确认才执行的屏幕滑动。"""
import subprocess
from config import SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y, SWIPE_DURATION_MS
from automation.adb import connected_devices


def swipe_next():
    if not connected_devices():
        raise RuntimeError("没有已连接的 ADB 设备")
    subprocess.run(
        ["adb", "shell", "input", "swipe",
         str(SWIPE_START_X), str(SWIPE_START_Y),
         str(SWIPE_END_X), str(SWIPE_END_Y),
         str(SWIPE_DURATION_MS)],
        check=True, timeout=15
    )
