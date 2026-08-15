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

# ===== 配置 =====
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PRIVATE_KEYS = os.environ.get("PRIVATE_KEYS", "[]")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== Telegram 推送 =====
def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text[:4000]}, timeout=10)
    except Exception as e:
        logger.error(f"Telegram 发送失败: {e}")

# ===== 模块一：Airdrop Hunter Pro =====
def run_hunter():
    logger.info("🟢 启动 Airdrop Hunter Pro...")
    try:
        # 尝试导入 scanner 模块进行扫描
        sys.path.insert(0, os.getcwd())
        from scanner.cryptorank_radar import CryptoRankRadar
        radar = CryptoRankRadar()
        projects = radar.get_airdrops(limit=20)
        if projects:
            project_names = [p.get("name", "未知") for p in projects]
            logger.info(f"Hunter 发现 {len(project_names)} 个项目")
            return project_names
        return []
    except Exception as e:
        logger.error(f"Hunter 错误: {e}")
        return []

# ===== 模块二：AI 情报分析 =====
def run_agent(projects):
    logger.info("🟡 启动 AI 情报分析...")
    try:
        from commander.hunter import analyze_projects
        strategy = analyze_projects(projects)
        logger.info(f"AI 生成 {len(strategy)} 条策略")
        return strategy
    except Exception as e:
        logger.error(f"Agent 错误: {e}")
        return []

# ===== 模块三：专用生态机器人 =====
def run_bots(strategy):
    logger.info("🔵 启动专用生态机器人...")
    try:
        from executor.farmer import execute_strategy
        result = execute_strategy(strategy)
        logger.info(f"机器人执行完成: {result}")
        return result
    except Exception as e:
        logger.error(f"机器人执行失败: {e}")
        return None

# ===== 主流程 =====
def main():
    start_time = datetime.now()
    logger.info("🚀 开始执行三位一体空投系统")

    # 1. 执行 Hunter 扫描
    projects = run_hunter()
    if not projects:
        send_telegram("⚠️ 未发现新空投项目，跳过后续步骤")
        return

    # 2. AI 情报分析
    strategy = run_agent(projects)
    if not strategy:
        send_telegram("⚠️ AI 分析未生成策略，跳过机器人执行")
        return

    # 3. 执行专用机器人
    run_bots(strategy)

    # 4. 汇总报告
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    report = f"""
✅ *三位一体空投系统执行完毕*
- 发现项目: {len(projects)} 个
- 生成策略: {len(strategy)} 条
- 耗时: {duration} 秒
- 时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    send_telegram(report)
    logger.info(report)

if __name__ == "__main__":
    main()