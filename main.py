"""Beikao-AI 命令行入口。"""
import argparse
from automation.adb import check_adb, take_screenshot
from automation.diagnostics import run_diagnostics
from automation.gesture import swipe_next
from recognition.ocr import recognize
from database.questions import add_wrong, list_wrong


def build_parser():
    parser = argparse.ArgumentParser(description="Beikao-AI Android 刷题辅助原型")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="检查 ADB 连接")
    sub.add_parser("doctor", help="只读检查 ADB、屏幕分辨率和 OCR 环境")
    screenshot = sub.add_parser("screenshot", help="截取手机屏幕")
    screenshot.add_argument("--device", help="多台设备时指定 ADB 序列号")
    ocr = sub.add_parser("ocr", help="截图或指定本地图片并执行 OCR")
    ocr.add_argument("--image", help="识别本地图片路径；不指定则截图")
    ocr.add_argument("--lang", help="指定语言，例如 chi_sim+eng；默认自动检测")
    ocr.add_argument("--device", help="多台设备时指定 ADB 序列号")
    add = sub.add_parser("add-wrong", help="手动添加错题")
    add.add_argument("--question", required=True)
    add.add_argument("--answer", default="")
    add.add_argument("--note", default="")
    sub.add_parser("list-wrong", help="查看错题本")
    export = sub.add_parser("export-wrong", help="将错题本导出为 CSV 文件")
    export.add_argument("--output", help="指定 CSV 保存位置（默认保存在 data/ 目录）")
    swipe = sub.add_parser("swipe-next", help="执行一次右向左滑动")
    swipe.add_argument("--confirm", action="store_true", help="明确确认执行一次手势")
    swipe.add_argument("--device", help="多台设备时指定 ADB 序列号")
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "check":
        print(check_adb())
    elif args.command == "doctor":
        print(run_diagnostics())
    elif args.command == "screenshot":
        print(f"截图已保存：{take_screenshot(args.device)}")
    elif args.command == "ocr":
        print(recognize(args.image, args.lang, args.device))
    elif args.command == "add-wrong":
        print(f"已记录错题，编号：{add_wrong(args.question, args.answer, args.note)}")
    elif args.command == "list-wrong":
        rows = list_wrong()
        if not rows:
            print("错题本为空。")
        for row in rows:
            print(f"#{row['id']} 题目：{row['question']}\\n   参考答案：{row['answer']}\\n   笔记：{row['note']}\\n")
    elif args.command == "export-wrong":
        path = export_wrong(args.output)
        print(f"已导出错题 CSV：{path}")
        print("导出仅保存在本机；请勿上传包含个人答题数据的文件到公开仓库。")
    elif args.command == "swipe-next":
        if not args.confirm:
            raise SystemExit("为避免误触，请确认操作后添加 --confirm 参数。")
        device = swipe_next(args.device, confirmed=True)
        print(f"已向设备 {device} 发送一次滑动手势。")


if __name__ == "__main__":
    main()
