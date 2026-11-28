"""ADB 连接检查与屏幕截图。"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from config import CAPTURE_DIR, LATEST_SCREENSHOT


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


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


def take_screenshot(device_serial=None):
    """保存当前连接设备截图；多设备时要求指定序列号，并保护上一张有效截图。"""
    devices = connected_devices()
    if not devices:
        raise RuntimeError("没有已连接的 ADB 设备，请先运行 python main.py check")
    if device_serial and device_serial not in devices:
        raise RuntimeError(f"指定设备 {device_serial} 未连接。当前设备：{', '.join(devices)}")
    if not device_serial:
        if len(devices) > 1:
            raise RuntimeError("检测到多台设备，请使用 --device 指定其中一台：" + ", ".join(devices))
        device_serial = devices[0]

    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        # 先写入同目录临时文件；只有收到有效 PNG 后才替换 latest.png。
        with tempfile.NamedTemporaryFile(
            prefix=".latest-", suffix=".png", dir=CAPTURE_DIR, delete=False
        ) as output:
            temporary_path = Path(output.name)
            result = subprocess.run(
                ["adb", "-s", device_serial, "exec-out", "screencap", "-p"],
                stdout=output, stderr=subprocess.PIPE, timeout=30
            )

        if result.returncode:
            message = result.stderr.decode("utf-8", "ignore").strip()
            raise RuntimeError(message or "ADB 截图失败，上一张有效截图已保留。")

        with temporary_path.open("rb") as image_file:
            signature = image_file.read(len(_PNG_SIGNATURE))
        if signature != _PNG_SIGNATURE:
            raise RuntimeError("ADB 返回内容不是有效 PNG，已保留上一张有效截图。")

        os.replace(temporary_path, LATEST_SCREENSHOT)
        temporary_path = None
        return LATEST_SCREENSHOT
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("ADB 截图超时，请检查无线调试连接后重试。") from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
