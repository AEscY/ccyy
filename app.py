# -*- coding: utf-8 -*-
"""
Airdrop Radar - 极致稳定版
保证根路径始终显示项目列表，错误不会导致空白
"""

import os
import sys
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# 基础日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 环境变量检查（只检查必需的） =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("BOT_TOKEN or CHAT_ID not set, but service will still run")
    # 不退出，继续运行，但Telegram功能会失效

# ===== 固定模拟数据（保证始终有内容） =====
PROJECTS = [
    {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "本地"},
    {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "本地"},
    {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "本地"},
    {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "本地"},
    {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "本地"},
    {"name": "Base Network", "chain": "Base", "score": 71, "url": "https://base.org", "source": "本地"},
    {"name": "Avalanche", "chain": "Avalanche", "score": 68, "url": "https://avax.network", "source": "本地"},
]

last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
current_projects = PROJECTS.copy()

# ===== 尝试获取真实数据（如果API_KEY存在） =====
def try_fetch_real_data():
    """尝试从CryptoRank获取数据，失败则静默保留模拟数据"""
    api_key = os.environ.get("API_KEY") or os.environ.get("CRYPTORANK_API_KEY")
    if not api_key:
        logger.info("No API_KEY provided, using local data")
        return

    try:
        import requests
        url = "https://api.cryptorank.io/v1/airdrops"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"limit": 10, "status": "active"}
        resp = requests.get(url, headers=headers, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", [])
            if items:
                new_projects = []
                for item in items[:10]:
                    chain = item.get("chain", "多链")
                    if isinstance(chain, list):
                        chain = chain[0] if chain else "多链"
                    new_projects.append({
                        "name": item.get("name", "未知"),
                        "chain": chain,
                        "score": min(item.get("popularity", 50) + 10, 100),
                        "url": item.get("website", "") or item.get("url", ""),
                        "source": "CryptoRank"
                    })
                global current_projects, last_scan_time
                current_projects = new_projects
                last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Fetched {len(new_projects)} real projects from CryptoRank")
    except Exception as e:
        logger.warning(f"Real data fetch failed: {e}")

# 启动时尝试获取真实数据
try_fetch_real_data()

# ===== Telegram发送（可选） =====
def send_telegram_message(text):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            return False
        import requests
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return resp.status_code == 200
    except:
        return False

def run_scan():
    """手动扫描：尝试获取真实数据，然后更新页面"""
    global current_projects, last_scan_time
    api_key = os.environ.get("API_KEY") or os.environ.get("CRYPTORANK_API_KEY")
    if api_key:
        try:
            import requests
            url = "https://api.cryptorank.io/v1/airdrops"
            headers = {"Authorization": f"Bearer {api_key}"}
            params = {"limit": 10, "status": "active"}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                if items:
                    new_projects = []
                    for item in items[:10]:
                        chain = item.get("chain", "多链")
                        if isinstance(chain, list):
                            chain = chain[0] if chain else "多链"
                        new_projects.append({
                            "name": item.get("name", "未知"),
                            "chain": chain,
                            "score": min(item.get("popularity", 50) + 10, 100),
                            "url": item.get("website", "") or item.get("url", ""),
                            "source": "CryptoRank"
                        })
                    current_projects = new_projects
                    last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    send_telegram_message(f"✅ 扫描完成，发现 {len(current_projects)} 个真实项目")
                    return
        except Exception as e:
            logger.warning(f"Scan failed: {e}")
    # 如果没有API或失败，保留现有数据，并发送提示
    send_telegram_message("⚠️ 扫描完成，但未能获取新数据（使用本地缓存）")

# ===== HTTP处理器 =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self._serve_html()
            elif self.path == '/scan':
                run_scan()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Scan triggered, check Telegram')
            elif self.path == '/health':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            elif self.path == '/api/projects':
                self._serve_json()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            # 如果处理过程中出错，返回错误信息而不是空白
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: {e}".encode())

    def _serve_json(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(current_projects, ensure_ascii=False).encode('utf-8'))

    def _serve_html(self):
        projects = current_projects
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Airdrop Radar</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #0a0e17; color: #e0e0e0; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; padding: 20px; background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; }
                .header h1 { font-size: 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .stats { font-size: 14px; color: #8899bb; }
                .stats span { color: #00d4ff; font-weight: bold; }
                .btn { display: inline-block; padding: 10px 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; border: none; cursor: pointer; transition: opacity 0.2s; }
                .btn:hover { opacity: 0.85; }
                .btn-secondary { background: #1a2744; color: #8899bb; }
                .btn-secondary:hover { background: #243b5e; }
                .table-wrapper { background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; overflow: hidden; }
                table { width: 100%; border-collapse: collapse; }
                th { background: #1a2744; color: #8899bb; font-weight: 600; font-size: 13px; text-transform: uppercase; padding: 14px 16px; text-align: left; }
                td { padding: 14px 16px; border-bottom: 1px solid #1a2744; font-size: 14px; }
                tr:hover td { background: #1a2744; }
                .score { font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 13px; display: inline-block; }
                .score-high { background: rgba(0, 212, 255, 0.15); color: #00d4ff; }
                .score-medium { background: rgba(255, 193, 7, 0.15); color: #ffc107; }
                .score-low { background: rgba(255, 82, 82, 0.15); color: #ff5252; }
                .chain-tag { display: inline-block; padding: 2px 12px; background: #1a2744; border-radius: 12px; font-size: 12px; color: #8899bb; }
                .source-tag { display: inline-block; padding: 2px 10px; background: #0a0e17; border-radius: 10px; font-size: 11px; color: #556688; border: 1px solid #1a2744; }
                .link { color: #00d4ff; text-decoration: none; }
                .link:hover { text-decoration: underline; }
                .footer { margin-top: 20px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; color: #556688; font-size: 13px; }
                @media (max-width: 768px) {
                    body { padding: 10px; }
                    .header { flex-direction: column; align-items: stretch; text-align: center; }
                    .header h1 { font-size: 20px; }
                    th, td { padding: 10px 8px; font-size: 12px; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1>📡 Airdrop Radar</h1>
                        <div class="stats">共发现 <span>%d</span> 个项目</div>
                    </div>
                    <div style="display:flex;gap:10px;flex-wrap:wrap;">
                        <a href="/scan" class="btn">🔄 立即扫描</a>
                        <a href="/api/projects" class="btn btn-secondary">📊 API</a>
                    </div>
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead><tr><th>#</th><th>项目名称</th><th>链</th><th>评分</th><th>来源</th><th>链接</th></tr></thead>
                        <tbody>
        """ % len(projects)

        if not projects:
            html += "<tr><td colspan='6' style='text-align:center;padding:40px;'>暂无数据</td></tr>"
        else:
            for idx, p in enumerate(projects, 1):
                name = p.get('name', '未知')
                chain = p.get('chain', '-')
                score = p.get('score', 0)
                source = p.get('source', '-')
                url = p.get('url', '')
                score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"
                link = f"<a href='{url}' target='_blank' class='link'>访问</a>" if url else '-'
                html += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><strong>{name}</strong></td>
                            <td><span class="chain-tag">{chain}</span></td>
                            <td><span class="score {score_class}">{score}</span></td>
                            <td><span class="source-tag">{source}</span></td>
                            <td>{link}</td>
                        </tr>
                """

        html += f"""
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <span>🕒 最后更新: {last_scan_time}</span>
                    <span>⚡ 数据自动推送到 Telegram</span>
                </div>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def log_message(self, format, *args):
        pass

# ===== 启动 =====
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Airdrop Radar started on port {port}")
    HTTPServer(('', port), Handler).serve_forever()