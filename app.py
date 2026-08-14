# -*- coding: utf-8 -*-
"""
app.py - Main entry with web interface
"""

import os
import sys
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

from bridge import AirdropBridge
from telegram_sender import send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("ERROR: Please set BOT_TOKEN and CHAT_ID environment variables")
    sys.exit(1)

bridge = AirdropBridge()

def run_full_scan():
    try:
        result = bridge.run_cycle()
        send_telegram_message("Scan result: " + result)
        logger.info("Message sent successfully")
    except Exception as e:
        error_msg = "Scan exception: " + str(e)
        send_telegram_message(error_msg)
        logger.error(error_msg)

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
        elif self.path == '/projects':
            self._show_projects()
        else:
            self.send_response(404)
            self.end_headers()

    def _show_projects(self):
        projects = bridge.get_last_projects()
        html = """
        <html>
        <head><title>Airdrop Radar - Projects</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; }
            table { width: 100%%; border-collapse: collapse; background: white; }
            th { background: #4CAF50; color: white; padding: 10px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
            tr:hover { background: #f1f1f1; }
            .score { font-weight: bold; }
            .high { color: green; }
            .medium { color: orange; }
            .low { color: red; }
            .footer { margin-top: 20px; color: #666; }
        </style>
        </head>
        <body>
            <h1>📡 最新空投雷达扫描结果</h1>
            <p>共发现 <strong>%d</strong> 个项目</p>
            <table>
                <tr>
                    <th>#</th>
                    <th>项目名称</th>
                    <th>链</th>
                    <th>评分</th>
                    <th>来源</th>
                    <th>链接</th>
                </tr>
        """
        if not projects:
            html += "<tr><td colspan='6' style='text-align:center;'>暂无数据，请先执行扫描</td></tr>"
        else:
            for idx, p in enumerate(projects, 1):
                name = p.get('name', '未知')
                chain = p.get('chain', '-')
                score = p.get('score', 0)
                source = p.get('source', '-')
                url = p.get('url', '')
                score_class = 'high' if score >= 80 else 'medium' if score >= 60 else 'low'
                link = f"<a href='{url}' target='_blank'>访问</a>" if url else '-'
                html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{name}</td>
                    <td>{chain}</td>
                    <td class="score {score_class}">{score}</td>
                    <td>{source}</td>
                    <td>{link}</td>
                </tr>
                """
        html += """
            </table>
            <div class="footer">
                <p>🔄 自动更新，访问 <a href="/scan">/scan</a> 手动触发扫描</p>
                <p>📱 扫描结果会推送到您的 Telegram</p>
            </div>
        </body>
        </html>
        """ % (len(projects) if projects else 0)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    run_full_scan()
    port = int(os.environ.get('PORT', 10000))
    logger.info("Service started, listening on port " + str(port))
    HTTPServer(('', port), Handler).serve_forever()