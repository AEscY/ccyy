# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 统一调度器
依次执行：Airdrop Hunter Pro → AI 情报分析 → 专用机器人执行
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
import requests
import yaml

# ===== 配置加载 =====
def load_config():
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except:
        return {}

CONFIG = load_config()

# ===== 环境变量 =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PRIVATE_KEYS = os.environ.get("PRIVATE_KEYS", "[]")

# ===== 日志 =====
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/suite.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== Telegram 推送 =====
def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000], "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        logger.error(f"Telegram 发送失败: {e}")

# ============================================================
# 模块一：Airdrop Hunter Pro（全网空投扫描）
# ============================================================
def run_hunter():
    logger.info("🟢 [模块一] 启动 Airdrop Hunter Pro...")
    send_telegram("🟢 开始扫描全网空投...")

    try:
        # 直接导入 hunter 模块
        sys.path.insert(0, "modules/hunter")
        from airdrop_hunter import scan_airdrops
        projects = scan_airdrops()
        logger.info(f"Hunter 发现 {len(projects)} 个项目")
        return projects
    except Exception as e:
        logger.error(f"Hunter 模块加载失败: {e}")
        # 备用方案：使用现有 app.py 的数据
        try:
            from bridge import AirdropBridge
            bridge = AirdropBridge()
            projects = bridge.scan_chain()
            logger.info(f"备用扫描发现 {len(projects)} 个项目")
            return [p.get("name", "未知") for p in projects]
        except Exception as e2:
            logger.error(f"备用扫描也失败: {e2}")
            return ["Uniswap V4", "Aave V3", "Arbitrum Odyssey", "Optimism Bedrock", "zkSync Era"]

# ============================================================
# 模块二：Web3 Airdrop Hunter Agent（AI 策略分析）
# ============================================================
def run_agent(projects):
    logger.info("🟡 [模块二] 启动 AI 情报分析...")
    send_telegram(f"🟡 AI 分析 {len(projects)} 个项目...")

    try:
        sys.path.insert(0, "modules/agent")
        from agent import generate_strategy
        strategy = generate_strategy(projects)
        logger.info(f"AI 生成 {len(strategy)} 条策略")
        return strategy
    except Exception as e:
        logger.error(f"Agent 模块加载失败: {e}")
        # 备用策略：为每个项目生成通用策略
        strategy = []
        for p in projects[:10]:
            item = {
                "project": p,
                "ecosystem": "general",
                "actions": ["claim", "vote"],
                "priority": "medium"
            }
            if "kite" in p.lower():
                item["ecosystem"] = "kite"
                item["actions"].append("farm_xp")
                item["priority"] = "high"
            elif "pharos" in p.lower():
                item["ecosystem"] = "pharos"
                item["actions"].append("daily_task")
                item["priority"] = "high"
            strategy.append(item)
        return strategy

# ============================================================
# 模块三：专用生态机器人
# ============================================================
def run_bots(strategy):
    logger.info("🔵 [模块三] 启动专用生态机器人...")
    send_telegram("🔵 执行专用机器人...")

    executed = {"kite": False, "pharos": False}

    for item in strategy:
        ecosystem = item.get("ecosystem", "").lower()

        if ecosystem == "kite" and not executed["kite"]:
            try:
                sys.path.insert(0, "modules/bots/kite_ai")
                from bot import run_kite_bot
                result = run_kite_bot()
                logger.info(f"Kite AI 机器人执行完成: {result}")
                send_telegram(f"✅ Kite AI 机器人执行完成")
                executed["kite"] = True
            except Exception as e:
                logger.error(f"Kite AI 执行失败: {e}")

        if ecosystem == "pharos" and not executed["pharos"]:
            try:
                sys.path.insert(0, "modules/bots/pharos")
                from bot import run_pharos_bot
                result = run_pharos_bot()
                logger.info(f"Pharos 机器人执行完成: {result}")
                send_telegram(f"✅ Pharos 机器人执行完成")
                executed["pharos"] = True
            except Exception as e:
                logger.error(f"Pharos 执行失败: {e}")

    return executed

# ============================================================
# 主流程
# ============================================================
def main():
    start_time = datetime.now()
    logger.info("🚀 开始执行三位一体空投系统")
    send_telegram("🚀 *三位一体空投系统启动*")

    try:
        # 1. 执行 Hunter 扫描
        projects = run_hunter()
        if not projects:
            send_telegram("⚠️ 未发现新空投项目")
            return

        # 2. AI 情报分析
        strategy = run_agent(projects)
        if not strategy:
            send_telegram("⚠️ AI 分析未生成策略")
            return

        # 3. 执行专用机器人
        executed = run_bots(strategy)

        # 4. 汇总报告
        end_time = datetime.now()
        duration = (end_time - start_time).seconds
        report = f"""
✅ *三位一体空投系统执行完毕*

📊 统计:
- 发现项目: {len(projects)} 个
- 生成策略: {len(strategy)} 条
- Kite AI: {'✅ 已执行' if executed.get('kite') else '⏭️ 跳过'}
- Pharos: {'✅ 已执行' if executed.get('pharos') else '⏭️ 跳过'}
- 耗时: {duration} 秒

🕒 {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        send_telegram(report)
        logger.info(report)

    except Exception as e:
        logger.error(f"系统执行异常: {e}")
        send_telegram(f"❌ 系统异常: {str(e)[:200]}")

if __name__ == "__main__":
    main()
