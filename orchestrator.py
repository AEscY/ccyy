# -*- coding: utf-8 -*-
import os
import logging
import time
import random
from datetime import datetime

from ai_agent import run_ai_agent
from hunter import run_hunter
from bots.kite_ai import run_kite_bot
from bots.pharos import run_pharos_bot
from bots.arb_claim import run_arb_claim
from telegram import send_telegram_message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESSES = os.environ.get("WALLET_ADDRESSES", "").split(",")

def main():
    start = datetime.now()
    logger.info("🚀 三位一体空投系统启动")

    # 阶段1: AI 情报
    logger.info("📡 AI 情报扫描...")
    ai_projects = run_ai_agent()
    if not ai_projects:
        send_telegram_message("⚠️ AI 未发现项目")
        return

    # 阶段2: Hunter 验证
    logger.info("🔍 Hunter 验证...")
    hunter_projects = run_hunter(ai_projects)
    all_projects = list(set(hunter_projects + ai_projects))
    logger.info(f"共 {len(all_projects)} 个项目")

    # 阶段3: 专用机器人
    logger.info("🤖 执行专用机器人...")
    bot_results = []
    for wallet in WALLET_ADDRESSES:
        wallet = wallet.strip()
        if not wallet:
            continue
        if any("kite" in p.lower() for p in all_projects):
            bot_results.append(f"Kite AI ({wallet[:8]}): {'✅' if run_kite_bot(wallet) else '❌'}")
        if any("pharos" in p.lower() for p in all_projects):
            bot_results.append(f"Pharos ({wallet[:8]}): {'✅' if run_pharos_bot(wallet) else '❌'}")
        if any("arb" in p.lower() for p in all_projects):
            bot_results.append(f"Arbitrum ({wallet[:8]}): {'✅' if run_arb_claim(wallet) else '❌'}")
        time.sleep(random.randint(1, 3))

    # 报告
    elapsed = (datetime.now() - start).seconds
    report = f"""
✅ 三位一体空投系统执行完毕
- AI 发现: {len(ai_projects)} 个
- Hunter 验证: {len(hunter_projects)} 个
- 项目总数: {len(all_projects)} 个
- 机器人执行:
  {'  '.join(bot_results) if bot_results else '  无匹配生态'}
- 耗时: {elapsed} 秒
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    send_telegram_message(report)
    logger.info(report)

if __name__ == "__main__":
    main()
