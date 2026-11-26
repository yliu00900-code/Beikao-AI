"""需要明确确认才执行的单次屏幕滑动。"""
import subprocess

from config import (
    SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y,
    SWIPE_DURATION_MS,
)
from automation.adb import connected_devices


def swipe_next(device_serial=None, confirmed=False):
    """执行一次滑动；必须显式确认，且多设备时必须指定目标序列号。"""
    if not confirmed:
        raise RuntimeError("为避免误触，必须明确确认后才能滑动；请通过命令行添加 --confirm。")

    devices = connected_devices()
    if not devices:
        raise RuntimeError("没有已连接的 ADB 设备")

    if device_serial:
        if device_serial not in devices:
            raise RuntimeError(
                f"指定设备 {device_serial} 未连接。当前设备：{', '.join(devices)}"
            )
    else:
        if len(devices) > 1:
            raise RuntimeError(
                "检测到多台设备，请使用 --device 指定目标设备：" + ", ".join(devices)
            )
        device_serial = devices[0]

    subprocess.run(
        ["adb", "-s", device_serial, "shell", "input", "swipe",
         str(SWIPE_START_X), str(SWIPE_START_Y),
         str(SWIPE_END_X), str(SWIPE_END_Y),
         str(SWIPE_DURATION_MS)],
        check=True, timeout=15
    )
    return device_serial
