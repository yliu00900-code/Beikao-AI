"""Tesseract OCR：支持检测语言包、中文缺失时降级提示，以及本地图片识别。"""
import shutil
import subprocess
import sys
from pathlib import Path
from automation.adb import take_screenshot


def available_languages():
    if not shutil.which("tesseract"):
        raise RuntimeError("找不到 tesseract。请在 Termux 执行：pkg install tesseract")
    result = subprocess.run(
        ["tesseract", "--list-langs"], capture_output=True, text=True, timeout=15
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "无法读取 Tesseract 语言包列表")
    lines = (result.stdout or result.stderr).splitlines()
    # Tesseract 的首行是说明，后续每行是语言代码。
    return [line.strip() for line in lines[1:] if line.strip()]


def select_language(requested, languages):
    """返回 OCR 语言参数及可选提示；显式请求缺失语言时拒绝静默降级。"""
    installed = set(languages)
    if requested:
        wanted = [part.strip() for part in requested.split("+") if part.strip()]
        missing = [lang for lang in wanted if lang not in installed]
        if missing:
            raise RuntimeError(
                "缺少指定语言包：" + ", ".join(missing) +
                "。已安装语言：" + (", ".join(languages) or "无")
            )
        return "+".join(wanted), None
    if "chi_sim" in installed and "eng" in installed:
        return "chi_sim+eng", None
    if "chi_sim" in installed:
        return "chi_sim", None
    if "eng" in installed:
        return "eng", "尚未安装 chi_sim 中文语言包，本次仅使用 eng；中文识别准确度可能很低。"
    if languages:
        return languages[0], "没有发现 chi_sim 或 eng，本次使用已安装的语言：" + languages[0]
    raise RuntimeError("Tesseract 没有可用语言包。请先安装至少一个 traineddata 语言文件。")


def recognize(image_path=None, language=None, device_serial=None):
    """识别指定图片，或先截取 ADB 设备屏幕再识别；所有数据只在本机处理。"""
    langs = available_languages()
    selected, warning = select_language(language, langs)
    if warning:
        print("[OCR 提示] " + warning, file=sys.stderr)

    if image_path is None:
        source = take_screenshot(device_serial)
    else:
        source = Path(image_path).expanduser()
        if not source.is_file():
            raise RuntimeError(f"图片文件不存在：{source}")

    result = subprocess.run(
        ["tesseract", str(source), "stdout", "-l", selected],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "OCR 识别失败")
    return result.stdout.strip() or "没有识别到文字，请检查图片清晰度和语言数据。"
