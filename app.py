# app.py - 升级版主程序
import os
from bridge import AirdropBridge
from telegram_sender import send_telegram_message

bridge = AirdropBridge()

def run_full_scan():
    """执行完整扫描并推送结果"""
    try:
        result = bridge.run_cycle()
        send_telegram_message("✅ 空投雷达已完成一轮扫描，发现新机会请查看控制台")
    except Exception as e:
        send_telegram_message(f"❌ 扫描异常: {e}")
        raise

# 启动时运行一次
if __name__ == "__main__":
    run_full_scan()