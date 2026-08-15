# -*- coding: utf-8 -*-
"""
Airdrop Radar - 使用 three.ws 免费 API
数据源：https://three.ws (Airdrop Eligibility)
"""

import os
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
    logger.error("ERROR: Please set BOT_TOKEN and CHAT_ID environment variables")
    # 不退出，让网页能显示，但 Telegram 功能会失效

# ===== 本地兜底数据 =====
PROJECTS = [
    {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "本地"},
    {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "本地"},
    {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "本地"},
    {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "本地"},
    {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "本地"},
    {"name": "Base Network", "chain": "Base", "score": 71, "url": "https://base.org", "source": "本地"},
    {"name": "Avalanche", "chain": "Avalanche", "score": 68, "url": "https://avax.network", "source": "本地"},
]

current_projects = PROJECTS.copy()
last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ============================================================
# 数据源: three.ws Airdrop Eligibility API (完全免费，无需 Key)
# 文档: https://three.ws
# ============================================================
def fetch_three_ws_airdrops() -> list:
    """
    从 three.ws 获取空投资格数据
    注意：此 API 需要传入钱包地址来查询资格
    这里我们使用一个示例地址来获取通用空投列表
    """
    try:
        # 使用一个公开的示例钱包地址来获取空投信息
        # 你可以替换成自己的钱包地址
        example_wallet = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        url = f"https://three.ws/api/crypto/airdrop/{example_wallet}"
        
        logger.info("正在从 three.ws 获取空投数据...")
        resp = requests.get(url, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"three.ws 响应: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            # 根据 three.ws 的实际响应结构解析
            # 如果响应是列表，直接处理
            if isinstance(data, list):
                projects = []
                for item in data[:20]:
                    if isinstance(item, dict):
                        projects.append({
                            "name": item.get("name") or item.get("project") or "未知空投",
                            "chain": item.get("chain") or item.get("network") or "多链",
                            "score": int(item.get("score") or item.get("popularity") or 70),
                            "url": item.get("url") or item.get("website") or "",
                            "source": "three.ws"
                        })
                if projects:
                    logger.info(f"three.ws 获取到 {len(projects)} 个项目")
                    return projects
            
            # 如果响应是字典，尝试提取 data 字段
            if isinstance(data, dict):
                items = data.get("data") or data.get("airdrops") or data.get("results")
                if isinstance(items, list):
                    projects = []
                    for item in items[:20]:
                        if isinstance(item, dict):
                            projects.append({
                                "name": item.get("name") or item.get("project") or "未知空投",
                                "chain": item.get("chain") or item.get("network") or "多链",
                                "score": int(item.get("score") or item.get("popularity") or 70),
                                "url": item.get("url") or item.get("website") or "",
                                "source": "three.ws"
                            })
                    if projects:
                        logger.info(f"three.ws 获取到 {len(projects)} 个项目")
                        return projects
            
            logger.warning("three.ws 返回数据格式未知，尝试备用方案")
            return None
            
        else:
            logger.error(f"three.ws API 错误: {resp.status_code} - {resp.text[:100]}")
            return None
            
    except Exception as e:
        logger.error(f"three.ws 请求异常: {e}")
        return None

# ============================================================
# 备用数据源: Airdrop Tracker (无需注册)
# ============================================================
def fetch_airdrop_tracker() -> list:
    """从 Airdrop Tracker 获取数据"""
    try:
        url = "https://airdrop-tracker-omega.vercel.app/api/airdrops"
        logger.info("正在从 Airdrop Tracker 获取数据...")
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                projects = []
                for item in data[:20]:
                    projects.append({
                        "name": item.get("name") or item.get("project") or "未知",
                        "chain": item.get("chain") or "多链",
                        "score": int(item.get("score") or 60),
                        "url": item.get("url") or item.get("website") or "",
                        "source": "Airdrop Tracker"
                    })
                logger.info(f"Airdrop Tracker 获取到 {len(projects)} 个项目")
                return projects
        return None
    except Exception as e:
        logger.error(f"Airdrop Tracker 请求异常: {e}")
        return None

# ============================================================
# 统一获取函数（按优先级尝试）
# ============================================================
def fetch_airdrops() -> list:
    """按优先级依次尝试各个数据源"""
    # 1. 尝试 three.ws
    projects = fetch_three_ws_airdrops()
    if projects:
        return projects
    
    # 2. 尝试 Airdrop Tracker
    projects = fetch_airdrop_tracker()
    if projects:
        return projects
    
    # 3. 所有数据源都失败，返回 None
    return None

# ============================================================
# Telegram 发送
# ============================================================
def send_telegram_message(text: str) -> bool:
    try:
        if not BOT_TOKEN or not CHAT_ID:
            return False
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Telegram 发送失败: {e}")
        return False

# ============================================================
# 扫描函数
# ============================================================
def run_scan():
    global current_projects, last_scan_time
    logger.info("开始扫描空投...")

    projects = fetch_airdrops()

    if projects:
        current_projects = projects
        source = projects[0].get("source", "未知") if projects else "未知"
        msg = f"✅ 扫描完成，发现 {len(projects)} 个项目 (来源: {source})"
        logger.info(msg)
    else:
        current_projects = PROJECTS.copy()
        msg = "⚠️ 扫描完成（使用本地数据，所有 API 均不可用）"
        logger.warning(msg)

    last_scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send_telegram_message(msg)

# ===== 启动时自动扫描 =====
run_scan()

# ============================================================
# HTTP 服务器（保持不变）
# ============================================================
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
            logger.error(f"请求错误: {e}")
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
        project_count = len(projects)

        rows = ""
        if not projects:
            rows = "<tr><td colspan='6' style='text-align:center;padding:40px;'>暂无数据</td></tr>"
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
                rows += f"""
                        <tr>
                            <td>{idx}</td>
                            <td><strong>{name}</strong></td>
                            <td><span class="chain-tag">{chain}</span></td>
                            <td><span class="score {score_class}">{score}</span></td>
                            <td><span class="source-tag">{source}</span></td>
                            <td>{link}</td>
                        </tr>
                """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airdrop Radar</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #0a0e17; color: #e0e0e0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px; margin-bottom: 25px; padding: 20px; background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; }}
        .header h1 {{ font-size: 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .stats {{ font-size: 14px; color: #8899bb; }}
        .stats span {{ color: #00d4ff; font-weight: bold; }}
        .btn {{ display: inline-block; padding: 10px 24px; background: linear-gradient(135deg, #00d4ff, #7b2ffc); color: white; text-decoration: none; border-radius: 8px; font-size: 14px; font-weight: 600; border: none; cursor: pointer; transition: opacity 0.2s; }}
        .btn:hover {{ opacity: 0.85; }}
        .btn-secondary {{ background: #1a2744; color: #8899bb; }}
        .btn-secondary:hover {{ background: #243b5e; }}
        .table-wrapper {{ background: #141b2d; border-radius: 12px; border: 1px solid #1e2d45; overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #1a2744; color: #8899bb; font-weight: 600; font-size: 13px; text-transform: uppercase; padding: 14px 16px; text-align: left; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #1a2744; font-size: 14px; }}
        tr:hover td {{ background: #1a2744; }}
        .score {{ font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 13px; display: inline-block; }}
        .score-high {{ background: rgba(0, 212, 255, 0.15); color: #00d4ff; }}
        .score-medium {{ background: rgba(255, 193, 7, 0.15); color: #ffc107; }}
        .score-low {{ background: rgba(255, 82, 82, 0.15); color: #ff5252; }}
        .chain-tag {{ display: inline-block; padding: 2px 12px; background: #1a2744; border-radius: 12px; font-size: 12px; color: #8899bb; }}
        .source-tag {{ display: inline-block; padding: 2px 10px; background: #0a0e17; border-radius: 10px; font-size: 11px; color: #556688; border: 1px solid #1a2744; }}
        .link {{ color: #00d4ff; text-decoration: none; }}
        .link:hover {{ text-decoration: underline; }}
        .footer {{ margin-top: 20px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; color: #556688; font-size: 13px; }}
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ flex-direction: column; align-items: stretch; text-align: center; }}
            .header h1 {{ font-size: 20px; }}
            th, td {{ padding: 10px 8px; font-size: 12px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📡 Airdrop Radar</h1>
                <div class="stats">共发现 <span>{project_count}</span> 个项目</div>
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
                    {rows}
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
    logger.info(f"🚀 Airdrop Radar 启动，监听端口 {port}")
    logger.info("📡 数据源: three.ws -> Airdrop Tracker -> 本地数据")
    HTTPServer(('', port), Handler).serve_forever()