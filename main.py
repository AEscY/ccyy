import os
import requests
from telegram import Bot
import sys

# 读取环境变量，如果缺失则报错并退出
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    print("❌ 错误：未设置 BOT_TOKEN 环境变量")
    sys.exit(1)
if not CHAT_ID:
    print("❌ 错误：未设置 CHAT_ID 环境变量")
    sys.exit(1)

def check_airdrops():
    try:
        response = requests.get('https://api.airdrops.io/active/')
        if response.status_code == 200:
            data = response.json()
            msg = "🚀 最新空投机会:\n"
            # 取前3个
            items = data.get('data', [])[:3]
            if not items:
                return "⚠️ 暂时没有发现新空投"
            for item in items:
                name = item.get('name', '未知项目')
                url = item.get('url', '#')
                msg += f"\n• {name}: {url}"
            return msg
        else:
            return f"❌ API 返回状态码 {response.status_code}"
    except Exception as e:
        return f"❌ 扫描出错: {e}"

def main():
    try:
        bot = Bot(token=BOT_TOKEN)
        msg = check_airdrops()
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("✅ 消息发送成功")
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")

if __name__ == "__main__":
    main()