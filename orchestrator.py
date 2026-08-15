# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 统一调度器（MCP 优先）
"""

import os
import sys
import logging
from datetime import datetime
import requests
import yaml
import json

# 导入 MCP 客户端
from mcp_client import list_active_airdrops, get_airdrop, check_wallet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 配置 =====
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS", "")
API_KEY = os.environ.get("API_KEY", "")  # CryptoRank 可选

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=10)
    except Exception as e:
        logger.error(f"Telegram 发送失败: {e}")

# ===== MCP 发现 =====
def discover_with_mcp():
    logger.info("🟢 步骤1: MCP 发现空投...")
    try:
        result = list_active_airdrops(limit=20, sort_by="added")
        if result and "result" in result:
            content = result["result"].get("content", [])
            projects = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text", "")
                    try:
                        data = json.loads(text)
                        if isinstance(data, list):
                            for p in data:
                                projects.append(p.get("name", "未知"))
                    except:
                        pass
            if projects:
                logger.info(f"MCP 发现 {len(projects)} 个项目")
                return projects
        return []
    except Exception as e:
        logger.error(f"MCP 失败: {e}")
        return []

# ===== 备用：CryptoRank（如果有 API Key） =====
def scan_cryptorank():
    if not API_KEY:
        return []
    logger.info("🟡 步骤2: CryptoRank 扫描...")
    try:
        from scanner.cryptorank_radar import CryptoRankRadar
        radar = CryptoRankRadar(api_key=API_KEY)
        projects = radar.get_airdrops(limit=20)
        if projects:
            names = [p.get("name", "未知") for p in projects]
            logger.info(f"CryptoRank 发现 {len(names)} 个项目")
            return names
        return []
    except Exception as e:
        logger.error(f"CryptoRank 失败: {e}")
        return []

# ===== 钱包检查 =====
def check_wallet_eligibility():
    if not WALLET_ADDRESS:
        return None
    logger.info(f"🔵 钱包检查: {WALLET_ADDRESS}")
    try:
        result = check_wallet(WALLET_ADDRESS)
        if result and "result" in result:
            return result["result"].get("content", [])
        return None
    except Exception as e:
        logger.error(f"钱包检查失败: {e}")
        return None

# ===== 主流程 =====
def main():
    start = datetime.now()
    logger.info("🚀 执行三位一体空投系统 (MCP 优先)")

    # 1. MCP
    projects = discover_with_mcp()
    if not projects and API_KEY:
        projects = scan_cryptorank()

    if not projects:
        send_telegram("⚠️ 未发现新空投项目（所有数据源均不可用）")
        return

    projects = list(set(projects))
    logger.info(f"去重后共 {len(projects)} 个项目")

    # 2. AI 分析
    from commander.hunter import analyze_projects
    strategy = analyze_projects(projects)
    logger.info(f"生成 {len(strategy)} 条策略")

    # 3. 执行
    from executor.farmer import execute_strategy
    result = execute_strategy(strategy)

    # 4. 钱包检查
    wallet_result = check_wallet_eligibility()

    elapsed = (datetime.now() - start).seconds
    report = f"""
✅ *三位一体空投系统执行完毕*
- 发现项目: {len(projects)} 个
- 生成策略: {len(strategy)} 条
- 执行结果: 成功 {result['executed']} 个，失败 {result['failed']} 个
- 耗时: {elapsed} 秒
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    if wallet_result:
        report += f"\n📊 *钱包资格*\n{json.dumps(wallet_result, ensure_ascii=False)[:500]}"

    send_telegram(report)
    logger.info(report)

if __name__ == "__main__":
    main()