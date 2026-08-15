# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 仅使用 MCP + 本地备用
"""

import os
import logging
from datetime import datetime
import requests
import json

from mcp_client import list_active_airdrops, check_wallet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS", "")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=10)
    except Exception as e:
        logger.error(f"Telegram 发送失败: {e}")

def main():
    logger.info("🚀 开始执行空投雷达（MCP 模式）")
    
    # 1. 通过 MCP 获取空投
    projects = []
    try:
        result = list_active_airdrops(limit=20)
        if result and "result" in result:
            content = result["result"].get("content", [])
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
    except Exception as e:
        logger.error(f"MCP 获取失败: {e}")

    if not projects:
        # 无数据时使用本地备份
        projects = ["Uniswap V4", "Aave V3", "Arbitrum Odyssey", "Optimism Bedrock", "zkSync Era"]
        logger.info("使用本地备份数据")

    projects = list(set(projects))
    logger.info(f"共 {len(projects)} 个项目")

    # 2. 简单分析（不依赖 AI 模块）
    strategy = []
    for p in projects:
        strategy.append({"project": p, "actions": ["research", "claim"]})

    # 3. 钱包检查（可选）
    wallet_info = ""
    if WALLET_ADDRESS:
        try:
            result = check_wallet(WALLET_ADDRESS)
            if result and "result" in result:
                wallet_info = f"\n📊 钱包资格: {result['result'].get('content', [])}"
        except Exception as e:
            logger.error(f"钱包检查失败: {e}")

    # 4. 报告
    report = f"""
✅ 空投雷达执行完毕
- 发现项目: {len(projects)} 个
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{wallet_info}
"""
    send_telegram(report)
    logger.info(report)

if __name__ == "__main__":
    main()