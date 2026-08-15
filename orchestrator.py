# -*- coding: utf-8 -*-
import os
import sys
import logging
import traceback
import time
import random
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入模块
try:
    from ai_agent import run_ai_agent
    from hunter import run_hunter
    from bots.kite_ai import run_kite_bot
    from bots.pharos import run_pharos_bot
    from bots.arb_claim import run_arb_claim
    from telegram import send_telegram_message
except Exception as e:
    logger.error(f"导入模块失败: {e}")
    traceback.print_exc()
    sys.exit(1)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESSES = os.environ.get("WALLET_ADDRESSES", "").split(",")

def main():
    try:
        start = datetime.now()
        logger.info("🚀 三位一体空投系统启动")

        # 阶段1
        logger.info("📡 AI 情报扫描...")
        ai_projects = run_ai_agent()
        if not ai_projects:
            logger.warning("AI 未发现项目，发送通知后退出")
            send_telegram_message("⚠️ AI 未发现新项目")
            return

        logger.info(f"AI 发现 {len(ai_projects)} 个项目: {ai_projects[:5]}...")

        # 阶段2
        logger.info("🔍 Hunter 验证...")
        hunter_projects = run_hunter(ai_projects)
        all_projects = list(set(hunter_projects + ai_projects))
        logger.info(f"共 {len(all_projects)} 个项目")

        # 阶段3
        logger.info("🤖 执行专用机器人...")
        bot_results = []
        for wallet in WALLET_ADDRESSES:
            wallet = wallet.strip()
            if not wallet:
                continue
            if any("kite" in p.lower() for p in all_projects):
                try:
                    result = run_kite_bot(wallet)
                    bot_results.append(f"Kite AI ({wallet[:8]}): {'✅' if result else '❌'}")
                except Exception as e:
                    bot_results.append(f"Kite AI ({wallet[:8]}): ❌ 异常 {e}")
            if any("pharos" in p.lower() for p in all_projects):
                try:
                    result = run_pharos_bot(wallet)
                    bot_results.append(f"Pharos ({wallet[:8]}): {'✅' if result else '❌'}")
                except Exception as e:
                    bot_results.append(f"Pharos ({wallet[:8]}): ❌ 异常 {e}")
            if any("arb" in p.lower() for p in all_projects):
                try:
                    result = run_arb_claim(wallet)
                    bot_results.append(f"Arbitrum ({wallet[:8]}): {'✅' if result else '❌'}")
                except Exception as e:
                    bot_results.append(f"Arbitrum ({wallet[:8]}): ❌ 异常 {e}")
            time.sleep(random.randint(1, 3))

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

    except Exception as e:
        logger.error(f"主程序异常: {e}")
        traceback.print_exc()
        send_telegram_message(f"❌ 系统运行失败: {e}")
        raise

if __name__ == "__main__":
    main()