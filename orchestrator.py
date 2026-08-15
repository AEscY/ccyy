# -*- coding: utf-8 -*-
"""
三位一体空投系统 - 统一调度器（顶尖版）
整合：MCP发现 → AI分析 → 多引擎执行 → Telegram推送
"""

import os
import sys
import logging
from datetime import datetime
import requests
import yaml
import json

# 导入现有模块
from scanner.cryptorank_radar import CryptoRankRadar
from commander.hunter import analyze_projects
from executor.farmer import execute_strategy
from mcp_client import list_active_airdrops, get_airdrop, check_wallet

# ===== 配置 =====
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
WALLET_ADDRESS = os.environ.get("WALLET_ADDRESS", "")

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

# ===== 步骤1：MCP 发现（Web3 Discover） =====
def discover_with_mcp():
    """使用 MCP 客户端发现空投"""
    logger.info("🟢 步骤1: MCP 发现空投...")
    try:
        # 调用 list_active_airdrops
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
                        projects.append(text[:50])
            logger.info(f"MCP 发现 {len(projects)} 个项目")
            return projects
        return []
    except Exception as e:
        logger.error(f"MCP 发现失败: {e}")
        return []

# ===== 步骤2：传统扫描（备用） =====
def scan_with_cryptorank():
    """使用 CryptoRank 扫描（备用）"""
    logger.info("🟡 步骤2: CryptoRank 扫描...")
    try:
        radar = CryptoRankRadar()
        projects = radar.get_airdrops(limit=20)
        if projects:
            names = [p.get("name", "未知") for p in projects]
            logger.info(f"CryptoRank 发现 {len(names)} 个项目")
            return names
        return []
    except Exception as e:
        logger.error(f"CryptoRank 扫描失败: {e}")
        return []

# ===== 步骤3：钱包资格检查（可选） =====
def check_wallet_eligibility():
    """检查钱包空投资格"""
    if not WALLET_ADDRESS:
        return None
    logger.info(f"🔵 步骤3: 检查钱包 {WALLET_ADDRESS} 的空投资格...")
    try:
        result = check_wallet(WALLET_ADDRESS)
        if result and "result" in result:
            content = result["result"].get("content", [])
            return content
        return None
    except Exception as e:
        logger.error(f"钱包检查失败: {e}")
        return None

# ===== 主流程 =====
def main():
    start_time = datetime.now()
    logger.info("🚀 开始执行三位一体空投系统（顶尖版）")

    # 1. MCP 发现
    projects = discover_with_mcp()
    if not projects:
        # 备用：CryptoRank 扫描
        projects = scan_with_cryptorank()

    if not projects:
        send_telegram("⚠️ 未发现新空投项目")
        return

    # 2. 去重
    projects = list(set(projects))
    logger.info(f"去重后共 {len(projects)} 个项目")

    # 3. AI 分析
    logger.info("🟣 步骤4: AI 策略分析...")
    strategy = analyze_projects(projects)
    logger.info(f"生成 {len(strategy)} 条策略")

    # 4. 执行
    logger.info("🔴 步骤5: 执行任务...")
    result = execute_strategy(strategy)

    # 5. 钱包检查（可选）
    wallet_result = check_wallet_eligibility()

    # 6. 汇总报告
    end_time = datetime.now()
    duration = (end_time - start_time).seconds

    report = f"""
✅ *三位一体空投系统执行完毕*
- 发现项目: {len(projects)} 个
- 生成策略: {len(strategy)} 条
- 执行结果: 成功 {result['executed']} 个，失败 {result['failed']} 个
- 耗时: {duration} 秒
- 时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    if wallet_result:
        report += f"\n📊 *钱包检查结果*\n{json.dumps(wallet_result, ensure_ascii=False)[:500]}"

    send_telegram(report)
    logger.info(report)

if __name__ == "__main__":
    main()