# -*- coding: utf-8 -*-
"""
Airdrop Radar - 单文件版本
包含模拟数据，根路径直接显示项目列表
"""

import os
import sys
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 环境变量 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("ERROR: Please set BOT_TOKEN and CHAT_ID")
    sys.exit(1)

# ===== 模拟数据（直接硬编码，保证显示） =====
MOCK_PROJECTS = [
    {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "模拟"},
    {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "模拟"},
    {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "模拟"},
    {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "模拟"},
    {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "模拟"},
]

last_projects = MOCK_PROJECTS.copy()  # 初始就有数据

# ===== Telegram 发送 =====
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return resp.status_code == 200
    except:
        return False

# ===== 扫描函数 =====
def run_scan():
    global last_projects
    logger.info("Running scan...")
    # 实际可替换为真实API，这里用模拟
    projects = MOCK_PROJECTS.copy()
    last_projects = projects
    msg = f"✅ 扫描完成，发现 {len(projects)} 个项目"
    send_telegram_message(msg)
    logger.info(msg)
    return projects

# 启动时自动扫描一次
run_scan()

# ===== HTTP 处理器 =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self._show_projects()
        elif self.path == '/scan':
            run_scan()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Scan triggered')
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def _show_projects(self):
        global last_projects
        projects = last_projects
        html = """
        <html>
        <head><title>Airdrop Radar</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f0f4f8; }
            h1 { color: #2c3e50; }
            table { width: 100%%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            th { background: #2c3e50; color: white; padding: 12px; text-align: left; }
            td { padding: 12px; border-bottom: 1px solid #ddd; }
            tr:hover { background: #ecf0f1; }
            .score { font-weight: bold; }
            .high { color: green; }
            .medium { color: orange; }
            .low { color: red; }
            .footer { margin-top: 20px; color: #7f8c8d; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .btn { display: inline-block; padding: 8px 16px; background: #3498db; color: white; border-radius: 4px; }
        </style>
        </head>
        <body>
            <h1>📡 Airdrop Radar</h1>
            <p>共发现 <strong>%d</strong> 个项目</p>
            <table>
                <tr><th>#</th><th>项目名称</th><th>链</th><th>评分</th><th>来源</th><th>链接</th></tr>
        """ % len(projects)
        if not projects:
            html += "<tr><td colspan='6' style='text-align:center;'>暂无数据</td></tr>"
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
                <p><a href="/scan" class="btn">🔄 手动触发扫描</a>  (扫描结果会推送到 Telegram)</p>
                <p>最后更新: %s</p>
            </div>
        </body>
        </html>
        """ % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

# ===== 启动 =====
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info("Service started on port " + str(port))
    HTTPServer(('', port), Handler).serve_forever()