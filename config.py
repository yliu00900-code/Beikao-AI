"""本地设备配置。按手机屏幕实际分辨率校准手势坐标。"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CAPTURE_DIR = BASE_DIR / "captures"
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "questions.db"
LATEST_SCREENSHOT = CAPTURE_DIR / "latest.png"

# 占位坐标：屏幕中部由右向左滑动。首次使用前必须自行校准。
SWIPE_START_X = 900
SWIPE_START_Y = 900
SWIPE_END_X = 180
SWIPE_END_Y = 900
SWIPE_DURATION_MS = 350
