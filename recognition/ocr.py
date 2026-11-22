"""使用本机 Tesseract 对手机截图进行 OCR。"""
import shutil
import subprocess
from automation.adb import take_screenshot


def recognize():
    if not shutil.which("tesseract"):
        raise RuntimeError("找不到 tesseract。请在 Termux 执行：pkg install tesseract")
    image_path = take_screenshot()
    result = subprocess.run(
        ["tesseract", str(image_path), "stdout", "-l", "chi_sim+eng"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "OCR 识别失败")
    return result.stdout.strip() or "没有识别到文字，请检查截图清晰度和中文语言数据。"
