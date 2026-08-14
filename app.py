# -*- coding: utf-8 -*-
"""
app.py - 主入口 (升级版 v2.0)
"""

import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

from bridge import AirdropBridge
from telegram_sender import send_telegram_message

# ===== 日志配置 =====
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 环境变量检查 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("ERROR: Please set BOT_TOKEN and CHAT_ID environment variables")
    sys.exit(1)

# ===== 初始化 Bridge =====
bridge = AirdropBridge()

def run_full_scan():
    """执行完整扫描并推送结果"""
    try:
        result = bridge.run_cycle()
        send_telegram_message("Scan result: " + result)
        logger.info("Message sent successfully")
    except Exception as e:
        error_msg = "Scan exception: " + str(e)
        send_telegram_message(error_msg)
        logger.error(error_msg)

# ===== HTTP 服务器 =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Airdrop Radar v2.0 - CryptoRank + OnChain')
        elif self.path == '/scan':
            run_full_scan()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Scan triggered, check Telegram')
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # 屏蔽 HTTP 默认日志

# ===== 启动 =====
if __name__ == "__main__":
    # 启动时执行一次
    run_full_scan()
    # 启动 Web 服务
    port = int(os.environ.get('PORT', 10000))
    logger.info("Service started, listening on port " + str(port))
    HTTPServer(('', port), Handler).serve_forever()