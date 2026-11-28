"""只读环境诊断：检查 ADB 设备、屏幕尺寸和 Tesseract 语言包。"""
import shutil
import subprocess


def _run(command, timeout=10):
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        return None, "未安装或找不到命令：" + command[0]
    except subprocess.TimeoutExpired:
        return None, "命令执行超时：" + " ".join(command)
    output = (result.stdout or result.stderr).strip()
    if result.returncode != 0:
        return None, output or "命令执行失败"
    return output, None


def run_diagnostics():
    """返回诊断报告；只读取状态，不执行点击、滑动或答题。"""
    lines = ["Beikao-AI 环境诊断", "=" * 24]

    adb_output, adb_error = _run(["adb", "devices"])
    device_serial = None
    if adb_error:
        lines.append("[失败] ADB：" + adb_error)
    else:
        devices = []
        for line in adb_output.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                devices.append((parts[0], parts[1]))
        ready = [serial for serial, state in devices if state == "device"]
        if len(ready) == 1:
            device_serial = ready[0]
            lines.append("[通过] ADB 已连接：" + device_serial)
        elif len(ready) > 1:
            lines.append("[通过] ADB 已连接：" + ", ".join(ready))
            lines.append(
                "[提示] 检测到多台设备，为避免任意选择，本次跳过屏幕分辨率检查。"
            )
            lines.append("[提示] 截图/OCR 请使用 --device 指定目标设备。")
        elif devices:
            lines.append(
                "[待处理] 检测到设备，但尚未授权或未就绪：" +
                ", ".join(serial + " (" + state + ")" for serial, state in devices)
            )
        else:
            lines.append("[待处理] ADB 已安装，但没有检测到已连接设备。")

    if device_serial:
        size_output, size_error = _run(
            ["adb", "-s", device_serial, "shell", "wm", "size"]
        )
        if size_error:
            lines.append("[失败] 屏幕分辨率：" + size_error)
        else:
            lines.append("[通过] 屏幕分辨率：" + size_output)

    if not shutil.which("tesseract"):
        lines.append("[失败] Tesseract：未安装。可执行 pkg install tesseract")
    else:
        langs_output, langs_error = _run(["tesseract", "--list-langs"], timeout=15)
        if langs_error:
            lines.append("[失败] Tesseract 语言包检查：" + langs_error)
        else:
            languages = [
                item.strip() for item in langs_output.splitlines()[1:]
                if item.strip()
            ]
            if "chi_sim" in languages:
                lines.append("[通过] 中文简体语言包 chi_sim 已安装。")
            else:
                lines.append(
                    "[待处理] 未发现 chi_sim；OCR 命令会提示并临时使用 eng（中文识别可能不准）。"
                )
                lines.append(
                    "[提示] README 已提供从官方 tessdata_fast 下载 chi_sim.traineddata 的步骤。"
                )
            lines.append(
                "[信息] 已安装语言：" +
                (", ".join(languages) if languages else "未列出")
            )

    lines.append("")
    lines.append("说明：本命令只检查环境，不会截图、点击、滑动或选择答案。")
    return "\n".join(lines)
