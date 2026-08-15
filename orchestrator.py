# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 统一调度器
整合：Hunter扫描 → AI分析 → 执行器
"""

import os
import sys
import logging
from datetime import datetime
import requests
import yaml

# 导入现有模块
from scanner.cryptorank_radar import CryptoRankRadar
from commander.hunter import analyze_projects
from executor.farmer import execute_strategy

# ===== 配置 =====
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

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

# ===== 主流程 =====
def main():
    start_time = datetime.now()
    logger.info("🚀 开始执行三位一体空投系统")

    # 1. 扫描（调用现有 scanner）
    logger.info("🟢 步骤1: 扫描空投项目...")
    radar = CryptoRankRadar()
    projects = radar.get_airdrops(limit=20)
    if not projects:
        send_telegram("⚠️ 未发现新空投项目")
        return
    project_names = [p.get("name", "未知") for p in projects]
    logger.info(f"发现 {len(project_names)} 个项目")

    # 2. AI 分析（调用 commander）
    logger.info("🟡 步骤2: AI 策略分析...")
    strategy = analyze_projects(project_names)
    logger.info(f"生成 {len(strategy)} 条策略")

    # 3. 执行（调用 executor）
    logger.info("🔵 步骤3: 执行任务...")
    result = execute_strategy(strategy)

    # 4. 报告
    end_time = datetime.now()
    duration = (end_time - start_time).seconds
    report = f"""
✅ *三位一体空投系统执行完毕*
- 发现项目: {len(project_names)} 个
- 生成策略: {len(strategy)} 条
- 执行结果: 成功 {result['executed']} 个，失败 {result['failed']} 个
- 耗时: {duration} 秒
- 时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    send_telegram(report)
    logger.info(report)

if __name__ == "__main__":
    main()