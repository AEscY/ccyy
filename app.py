import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from bridge import AirdropBridge
from telegram_sender import send_telegram_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("❌ 请设置 BOT_TOKEN 和 CHAT_ID 环境变量")
    sys.exit(1)

bridge = AirdropBridge()

def run_full_scan():
    try:
        result = bridge.run_cycle()
        send_telegram_message("✅ 空投雷达已完成一轮扫描")
        logger.info(result)
    except Exception as e:
        error_msg = f"❌ 扫描异常: {e}"
        send_telegram_message(error_msg)
        logger.error(error_msg)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Airdrop Radar Running')
        elif self.path == '/scan':
            run_full_scan()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Scan triggered')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    run_full_scan()
    port = int(os.environ.get('PORT', 10000))
    HTTPServer(('', port), Handler).serve_forever()