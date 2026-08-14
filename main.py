import os
import requests
import sys

# 读取环境变量
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    print("❌ 错误：未设置 BOT_TOKEN 环境变量")
    sys.exit(1)
if not CHAT_ID:
    print("❌ 错误：未设置 CHAT_ID 环境变量")
    sys.exit(1)

def check_airdrops():
    """获取最新空投列表（示例用 airdrops.io 公开 API）"""
    try:
        response = requests.get('https://api.airdrops.io/active/')
        if response.status_code == 200:
            data = response.json()
            msg = "🚀 最新空投机会:\n"
            items = data.get('data', [])[:3]   # 取前3个
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

def send_telegram_message(text):
    """通过 Telegram Bot API 发送消息（同步请求）"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            return True
        else:
            print(f"发送失败: {resp.text}")
            return False
    except Exception as e:
        print(f"发送异常: {e}")
        return False

def main():
    msg = check_airdrops()
    if send_telegram_message(msg):
        print("✅ 消息发送成功")
    else:
        print("❌ 消息发送失败")
        sys.exit(1)

if __name__ == "__main__":
    main()