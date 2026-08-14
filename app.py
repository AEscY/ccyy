# -*- coding: utf-8 -*-
"""
Airdrop Radar - 多链真实数据版本
支持 CryptoRank API + 多链配置
"""

import os
import sys
import logging
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import List, Dict, Optional

import requests
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 环境变量 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.error("ERROR: Please set BOT_TOKEN and CHAT_ID environment variables")
    sys.exit(1)

# ===== 配置加载 =====
def load_config():
    """加载 config.yaml 配置文件"""
    default_config = {
        "rpc": {
            "ethereum": "https://eth.llamarpc.com",
            "polygon": "https://polygon.llamarpc.com",
            "arbitrum": "https://arb1.arbitrum.io/rpc",
            "optimism": "https://mainnet.optimism.io",
            "base": "https://base.llamarpc.com",
            "bsc": "https://bsc.llamarpc.com",
            "avalanche": "https://api.avax.network/ext/bc/C/rpc"
        },
        "cryptorank": {
            "api_key": "",
            "base_url": "https://api.cryptorank.io/v1"
        },
        "scanner": {
            "min_score": 60,
            "max_items": 20,
            "timeout": 15
        }
    }
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
            if config:
                # 环境变量优先：API_KEY 或 CRYPTORANK_API_KEY
                api_key = os.environ.get("API_KEY") or os.environ.get("CRYPTORANK_API_KEY")
                if api_key:
                    config["cryptorank"]["api_key"] = api_key
                return config
    except Exception as e:
        logger.warning(f"Config load failed: {e}, using defaults")
    
    # 如果配置文件加载失败，从环境变量读取
    api_key = os.environ.get("API_KEY") or os.environ.get("CRYPTORANK_API_KEY")
    if api_key:
        default_config["cryptorank"]["api_key"] = api_key
    return default_config

CONFIG = load_config()
logger.info(f"API Key configured: {'Yes' if CONFIG.get('cryptorank', {}).get('api_key') else 'No'}")

# ===== 模拟数据（兜底用） =====
MOCK_PROJECTS = [
    {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "模拟"},
    {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "模拟"},
    {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "模拟"},
    {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "模拟"},
    {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "模拟"},
    {"name": "Base Network", "chain": "Base", "score": 71, "url": "https://base.org", "source": "模拟"},
    {"name": "Avalanche", "chain": "Avalanche", "score": 68, "url": "https://avax.network", "source": "模拟"},
]

last_projects = MOCK_PROJECTS.copy()
last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ===== CryptoRank 数据获取 =====
def fetch_cryptorank_airdrops() -> Optional[List[Dict]]:
    """从 CryptoRank 获取真实空投数据"""
    api_key = CONFIG.get("cryptorank", {}).get("api_key", "")
    base_url = CONFIG.get("cryptorank", {}).get("base_url", "https://api.cryptorank.io/v1")

    if not api_key:
        logger.warning("CryptoRank API key not configured, using mock data")
        return None

    try:
        url = f"{base_url}/airdrops"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"limit": 20, "status": "active"}
        resp = requests.get(url, headers=headers, params=params, timeout=CONFIG.get("scanner", {}).get("timeout", 15))

        if resp.status_code == 200:
            data = resp.json()
            projects = []
            for item in data.get("data", [])[:20]:
                chain = item.get("chain", "多链")
                if isinstance(chain, list):
                    chain = chain[0] if chain else "多链"
                projects.append({
                    "name": item.get("name", "未知"),
                    "chain": chain,
                    "score": min(item.get("popularity", 50) + 10, 100),
                    "url": item.get("website", "") or item.get("url", ""),
                    "source": "CryptoRank"
                })
            return projects
        else:
            logger.error(f"CryptoRank API error: {resp.status_code}")
            return None
    except Exception as e:
        logger.error(f"CryptoRank fetch error: {e}")
        return None

# ===== Telegram 发送 =====
def send_telegram_message(text: str) -> bool:
    """发送消息到 Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return False

# ===== 扫描函数 =====
def run_scan():
    """执行扫描，优先使用真实数据，失败时回退到模拟数据"""
    global last_projects, last_scan_time
    logger.info("Starting scan...")

    projects = fetch_cryptorank_airdrops()

    if projects:
        logger.info(f"Got {len(projects)} projects from CryptoRank")
    else:
        logger.warning("Using mock data as fallback")
        projects = MOCK_PROJECTS.copy()

    projects.sort(key=lambda x: x.get("score", 0), reverse=True)
    max_items = CONFIG.get("scanner", {}).get("max_items", 20)
    last_projects = projects[:max_items]
    last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    msg = f"✅ 扫描完成，发现 {len(last_projects)} 个项目"
    send_telegram_message(msg)
    logger.info(msg)

    return last_projects

# ===== 启动时自动扫描 =====
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
            self.wfile.write(b'Scan triggered, check Telegram')
        elif self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/api/projects':
            self._api_projects()
        else:
            self.send_response(404)
            self.end_headers()

    def _api_projects(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(last_projects, ensure_ascii=False).encode('utf-8'))

    def _show_projects(self):
        projects = last_projects
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Airdrop Radar</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #0a0e17; color: #e0e0e0; min-height: 100vh; padding: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; padding: 20px; background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; }
                .header h1 { font-size: 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                .header .stats { font-size: 14px; color: #8899bb; }
                .header .stats span { color: #00d4ff; font-weight: bold; }
                .btn { display: inline-block; padding: 10px 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; border: none; cursor: pointer; transition: opacity 0.2s; }
                .btn:hover { opacity: 0.85; }
                .btn-secondary { background: #1a2744; color: #8899bb; }
                .btn-secondary:hover { background: #243b5e; }
                .table-wrapper { background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; overflow: hidden; }
                table { width: 100%; border-collapse: collapse; }
                th { background: #1a2744; color: #8899bb; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; padding: 14px 16px; text-align: left; }
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
                .footer { margin-top: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; color: #556688; font-size: 13px; }
                .empty { text-align: center; padding: 60px 20px; color: #556688; }
                .empty .icon { font-size: 48px; margin-bottom: 16px; }
                @media (max-width: 768px) {
                    body { padding: 10px; }
                    .header { flex-direction: column; align-items: stretch; text-align: center; }
                    .header h1 { font-size: 20px; }
                    table { font-size: 12px; }
                    th, td { padding: 10px 8px; }
                    .score { font-size: 11px; padding: 2px 8px; }
                    .chain-tag { font-size: 10px; padding: 1px 8px; }
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
                        <a href="/api/projects" class="btn btn-secondary">📊 JSON API</a>
                    </div>
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>项目名称</th>
                                <th>链</th>
                                <th>评分</th>
                                <th>来源</th>
                                <th>链接</th>
                            </tr>
                        </thead>
                        <tbody>
        """ % len(projects)

        if not projects:
            html += """
                            <tr>
                                <td colspan="6" class="empty">
                                    <div class="icon">🔭</div>
                                    <div>暂无数据，请点击「立即扫描」</div>
                                </td>
                            </tr>
            """
        else:
            for idx, p in enumerate(projects, 1):
                name = p.get('name', '未知')
                chain = p.get('chain', '-')
                score = p.get('score', 0)
                source = p.get('source', '-')
                url = p.get('url', '')

                if score >= 80:
                    score_class = "score-high"
                elif score >= 60:
                    score_class = "score-medium"
                else:
                    score_class = "score-low"

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

        html += """
                        </tbody>
                    </table>
                </div>
                <div class="footer">
                    <span>🕒 最后更新: %s</span>
                    <span>⚡ 数据自动推送到 Telegram</span>
                </div>
            </div>
        </body>
        </html>
        """ % last_scan_time

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