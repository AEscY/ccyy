import os
import requests
from telegram import Bot
from telegram.ext import Application

# 从 Render 设置的环境变量中读取
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def check_airdrops():
    # 这里是一个示例：调用免费空投数据源
    # 你可以后续替换成更复杂的链上监控逻辑[reference:7]
    try:
        response = requests.get('https://api.airdrops.io/active/')
        if response.status_code == 200:
            data = response.json()
            # 简单处理，只取前3个
            msg = "🚀 最新空投机会:\n"
            for item in data.get('data', [])[:3]:
                msg += f"\n• {item.get('name')}: {item.get('url')}"
            return msg
    except Exception as e:
        return f"❌ 扫描出错: {e}"
    return "⚠️ 暂时没有发现新空投"

def main():
    bot = Bot(token=BOT_TOKEN)
    msg = check_airdrops()
    bot.send_message(chat_id=CHAT_ID, text=msg)
    print("✅ 消息已发送")

if __name__ == "__main__":
    main()