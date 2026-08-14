import os
import sys
import json
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

# ---------- 日志设置 ----------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------- 环境变量检查 ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    logger.error("❌ 未设置 BOT_TOKEN 环境变量")
    sys.exit(1)
if not CHAT_ID:
    logger.error("❌ 未设置 CHAT_ID 环境变量")
    sys.exit(1)

# ---------- 全局扫描结果缓存（用于 Web 展示） ----------
last_scan_result = "暂无扫描结果"

# ---------- 多数据源尝试（按顺序，第一个成功即停止） ----------
AIRDROP_SOURCES = [
    # 源1：Vercel 部署的免费 API（稳定，无 Key）
    "https://airdrop-tracker-omega.vercel.app/api/airdrops",
    # 源2：备用 API（如果上面失效，可自行替换）
    # "https://api.airdropalert.com/api/airdrops",   # 可能需要 Key
    # 源3：可添加更多……
]

def fetch_airdrops():
    """
    依次尝试每个数据源，返回 (成功标志, 数据或错误信息)
    """
    for idx, url in enumerate(AIRDROP_SOURCES, 1):
        try:
            logger.info(f"📡 尝试数据源 #{idx}: {url}")
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # 简单校验数据结构
                if isinstance(data, list) and len(data) > 0:
                    return True, data
                elif isinstance(data, dict) and data.get('data'):
                    return True, data['data']
                else:
                    logger.warning(f"⚠️ 数据格式异常: {data}")
                    continue
            else:
                logger.warning(f"⚠️ 状态码 {resp.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ 请求失败: {e}")
            continue
    return False, "所有数据源均不可用，请稍后重试"

def format_airdrop_message(raw_data):
    """
    将原始数据格式化为 Telegram 消息
    """
    if not raw_data:
        return "⚠️ 未获取到有效空投数据"
    
    # 根据数据结构灵活提取
    msg = "🚀 **最新空投机会**\n"
    count = 0
    for item in raw_data[:5]:  # 最多取5条
        name = item.get('name') or item.get('project') or item.get('title') or '未知项目'
        url = item.get('url') or item.get('link') or item.get('website') or '#'
        msg += f"\n• [{name}]({url})"
        count += 1
    
    if count == 0:
        msg += "\n（暂无有效数据）"
    else:
        msg += f"\n\n🕒 更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    return msg

def send_telegram_message(text):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return True
        else:
            logger.error(f"Telegram 发送失败: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram 请求异常: {e}")
        return False

def run_scan_and_notify():
    """
    执行一次扫描并推送结果
    """
    global last_scan_result
    logger.info("🔄 开始扫描空投...")
    success, data = fetch_airdrops()
    if success:
        msg = format_airdrop_message(data)
        last_scan_result = msg
    else:
        msg = f"❌ 扫描失败: {data}"
        last_scan_result = msg
    
    # 发送到 Telegram
    if send_telegram_message(msg):
        logger.info("✅ 消息发送成功")
    else:
        logger.error("❌ 消息发送失败")

    return msg

# ---------- HTTP 服务器（处理 Render 端口要求 + 手动触发） ----------
class AirdropHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            # 根路径：显示最新扫描结果（HTML 文本）
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""
            <html><head><title>空投雷达</title></head>
            <body><pre>{last_scan_result}</pre>
            <p><a href="/scan">手动触发扫描</a></p>
            </body></html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif parsed.path == '/scan':
            # 手动触发扫描
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            msg = run_scan_and_notify()
            self.wfile.write(f"扫描完成，结果已发送至 Telegram\n{msg}".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # 屏蔽 HTTP 服务器的默认日志（太吵）
        pass

def run_http_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('', port), AirdropHandler)
    logger.info(f"🌐 HTTP 服务已启动，监听端口 {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        logger.info("服务已停止")

# ---------- 主入口 ----------
if __name__ == "__main__":
    # 启动时先执行一次扫描
    run_scan_and_notify()
    # 再启动 Web 服务器，保持程序运行
    run_http_server()