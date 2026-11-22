# Beikao-AI

面向 Android「备考通」刷题场景的个人学习辅助原型。第一版实现 ADB 连接检查、屏幕截图、OCR 文字识别、本地错题本，以及需要人工确认才执行的滑动手势。

> 安全原则：当前版本不会自动选择答案，也不会自动连续答题。AI 答案建议尚未接入，程序不会编造答案。请先核对识别结果和解析，再自行操作 App。

## 目录

- `main.py`：命令行入口
- `config.py`：本机路径与手势坐标
- `automation/adb.py`：ADB 连接检查和截图
- `automation/gesture.py`：显式确认后执行滑动
- `recognition/ocr.py`：Tesseract OCR
- `answer/solver.py`：后续 AI 分析接口
- `database/questions.py`：SQLite 错题本

## Android / Termux 环境

在 Android 手机上安装 Termux，然后执行：

```bash
pkg update && pkg upgrade
pkg install python android-tools tesseract
```

在系统设置中开启开发者选项和无线调试。根据无线调试页面显示的地址、端口，在 Termux 中配对并连接：

```bash
adb pair 手机显示的IP:配对端口
adb connect 手机显示的IP:连接端口
adb devices
```

配对码只在 Termux 提示时输入，不要分享配对码、密码或 API Key。

## 获取项目与运行

在 Termux 中进入你想存放项目的目录，执行：

```bash
git clone https://github.com/yliu00900-code/Beikao-AI.git
cd Beikao-AI
python main.py check
```

常用命令：

```bash
python main.py screenshot
python main.py ocr
python main.py add-wrong --question "示例题目" --answer "C" --note "复习知识点"
python main.py list-wrong
python main.py swipe-next --confirm
```

截图保存到本地 `captures/latest.png`；错题数据库保存在本地 `data/questions.db`。OCR 需要安装 Tesseract 中文语言数据。滑动坐标可在 `config.py` 修改。首次使用前请先校准坐标，避免误触。

## 已知限制与下一步

- ADB 无线调试需要手机系统支持，且每次连接状态可能变化。
- 默认滑动坐标只是占位值，必须按实际屏幕分辨率校准。
- OCR 识别结果需要人工检查；复杂题目、图片和公式可能识别不准。
- 下一步再接入可审阅的 AI 解析，并加入题目去重、错题复习和导出功能。

## 隐私

不要把截图、个人答题数据、账号信息、配对码或密钥提交到公开仓库。公开仓库只保存程序代码。
