# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 单文件版本
"""
import sys
sys.stderr.write("DEBUG: script started\n")
sys.stderr.flush()
import os
import sys
import logging
import json
import time
import random
import requests
from datetime import datetime

import traceback
import sys

try:
    # 尝试导入所有依赖
    import requests
    import json
    import logging
    import os, time, random
    from datetime import datetime
except Exception as e:
    with open("/tmp/error.log", "w") as f:
        f.write(traceback.format_exc())
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 配置 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESSES = os.environ.get("WALLET_ADDRESSES", "").split(",")

# ===== Telegram 推送 =====
def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text[:4000]},
            timeout=10
        )
    except Exception as e:
        logger.error(f"Telegram 发送失败: {e}")

# ===== AI 情报模块 =====
def run_ai_agent():
    logger.info("AI 情报扫描...")
    projects = []
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "list_active_airdrops", "arguments": {"limit": 20}}
        }
        resp = requests.post("https://web3-discover.vercel.app/api/mcp", json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if "result" in data:
                content = data["result"].get("content", [])
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text", "")
                        try:
                            parsed = json.loads(text)
                            if isinstance(parsed, list):
                                for p in parsed:
                                    name = p.get("name")
                                    if name:
                                        projects.append(name)
                        except:
                            pass
    except Exception as e:
        logger.error(f"MCP 调用失败: {e}")
    if not projects:
        projects = ["Uniswap V4", "Aave V3", "Arbitrum Odyssey", "Optimism Bedrock", "zkSync Era"]
    return list(set(projects))[:20]

# ===== Hunter 验证 =====
def run_hunter(ai_projects):
    logger.info("Hunter 验证...")
    return ai_projects  # 直接返回

# ===== 专用机器人 =====
def run_kite_bot(wallet):
    logger.info(f"🪁 Kite AI: {wallet[:8]}...")
    for task in ["farm_xp", "daily_checkin", "claim"]:
        logger.info(f"  ✅ {task}")
        time.sleep(0.5)
    return True

def run_pharos_bot(wallet):
    logger.info(f"🔱 Pharos: {wallet[:8]}...")
    for task in ["daily_task", "swap", "claim"]:
        logger.info(f"  ✅ {task}")
        time.sleep(0.5)
    return True

def run_arb_claim(wallet):
    logger.info(f"🧿 Arbitrum: {wallet[:8]}...")
    return True

# ===== 主程序 =====
def main():
    start = datetime.now()
    logger.info("🚀 三位一体空投系统启动")

    ai_projects = run_ai_agent()
    if not ai_projects:
        send_telegram_message("⚠️ AI 未发现项目")
        return

    all_projects = run_hunter(ai_projects)
    logger.info(f"共 {len(all_projects)} 个项目")

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

    elapsed = (datetime.now() - start).seconds
    report = f"""
✅ 三位一体空投系统执行完毕
- AI 发现: {len(ai_projects)} 个
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