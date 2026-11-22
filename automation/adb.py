"""ADB 连接检查与屏幕截图。"""
import shutil
import subprocess
from config import CAPTURE_DIR, LATEST_SCREENSHOT


def _run_adb(*args, timeout=20):
    if not shutil.which("adb"):
        raise RuntimeError("找不到 adb。请在 Termux 执行：pkg install android-tools")
    result = subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "ADB 命令失败")
    return result.stdout.strip()


def connected_devices():
    output = _run_adb("devices")
    return [line.split("\t")[0] for line in output.splitlines()[1:] if line.strip().endswith("\tdevice")]


def check_adb():
    output = _run_adb("devices")
    devices = [line for line in output.splitlines()[1:] if line.strip().endswith("\tdevice")]
    return "ADB 已连接：\n" + "\n".join(devices) if devices else (
        "未发现已授权设备。请开启无线调试并执行 adb pair / adb connect。\n" + output
    )


def take_screenshot():
    if not connected_devices():
        raise RuntimeError("没有已连接的 ADB 设备，请先运行 python main.py check")
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    with LATEST_SCREENSHOT.open("wb") as output:
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            stdout=output, stderr=subprocess.PIPE, timeout=30
        )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "ignore") or "截图失败")
    return LATEST_SCREENSHOT
