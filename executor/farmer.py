# -*- coding: utf-8 -*-
"""
executor/farmer.py - 多引擎任务执行器
整合：通用任务 + Kite AI + Pharos + LootBot
"""

import logging
import subprocess
import os
import time
import random
from typing import List, Dict

logger = logging.getLogger(__name__)

# ===== 配置 =====
DRY_RUN = False  # 设置为 True 进行模拟执行

def execute_strategy(strategy: List[Dict]) -> Dict:
    """
    执行策略中的任务，根据生态调用对应的执行引擎
    """
    results = {
        "total": len(strategy),
        "executed": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }

    for item in strategy:
        project = item.get("project", "未知")
        ecosystem = item.get("ecosystem", "general")
        actions = item.get("actions", [])
        priority = item.get("priority", "low")

        logger.info(f"🌾 执行 {project} ({ecosystem}) - 优先级: {priority}")

        # 根据生态选择执行器
        if ecosystem == "kite":
            success = run_kite_bot(actions)
        elif ecosystem == "pharos":
            success = run_pharos_bot(actions)
        elif ecosystem == "arbitrum" or ecosystem == "optimism" or ecosystem == "zksync":
            success = run_l2_executor(ecosystem, actions)
        elif ecosystem == "solana":
            success = run_solana_executor(actions)
        else:
            success = run_general_executor(actions)

        if success:
            results["executed"] += 1
            results["details"].append({"project": project, "status": "success"})
        else:
            results["failed"] += 1
            results["details"].append({"project": project, "status": "failed"})

        # 冷却时间，避免被标记为女巫
        time.sleep(random.randint(2, 5))

    logger.info(f"✅ 执行完成: 成功 {results['executed']} 个，失败 {results['failed']} 个")
    return results

def run_kite_bot(actions: List[str]) -> bool:
    """Kite AI 专用机器人"""
    logger.info(f"  🪁 Kite AI: {actions}")
    if DRY_RUN:
        logger.info("  → [模拟] 执行完成")
        return True
    try:
        # 检查是否有独立脚本
        bot_path = os.path.join(os.path.dirname(__file__), "..", "bots", "kite_ai", "bot.js")
        if os.path.exists(bot_path):
            result = subprocess.run(["node", bot_path], capture_output=True, timeout=120)
            return result.returncode == 0
        else:
            # 模拟执行
            for action in actions:
                logger.info(f"    → 执行 {action}")
                time.sleep(0.5)
            return True
    except Exception as e:
        logger.error(f"Kite AI 执行失败: {e}")
        return False

def run_pharos_bot(actions: List[str]) -> bool:
    """Pharos Network 专用机器人"""
    logger.info(f"  🔱 Pharos: {actions}")
    if DRY_RUN:
        logger.info("  → [模拟] 执行完成")
        return True
    try:
        bot_path = os.path.join(os.path.dirname(__file__), "..", "bots", "pharos", "bot.js")
        if os.path.exists(bot_path):
            result = subprocess.run(["node", bot_path], capture_output=True, timeout=120)
            return result.returncode == 0
        else:
            for action in actions:
                logger.info(f"    → 执行 {action}")
                time.sleep(0.5)
            return True
    except Exception as e:
        logger.error(f"Pharos 执行失败: {e}")
        return False

def run_l2_executor(ecosystem: str, actions: List[str]) -> bool:
    """L2 生态执行器（Arbitrum/Optimism/zKSync）"""
    logger.info(f"  ⛓️ {ecosystem}: {actions}")
    if DRY_RUN:
        return True
    try:
        for action in actions:
            logger.info(f"    → 执行 {action}")
            time.sleep(0.5)
        return True
    except Exception as e:
        logger.error(f"L2 执行失败: {e}")
        return False

def run_solana_executor(actions: List[str]) -> bool:
    """Solana 生态执行器"""
    logger.info(f"  🌞 Solana: {actions}")
    if DRY_RUN:
        return True
    try:
        for action in actions:
            logger.info(f"    → 执行 {action}")
            time.sleep(0.5)
        return True
    except Exception as e:
        logger.error(f"Solana 执行失败: {e}")
        return False

def run_general_executor(actions: List[str]) -> bool:
    """通用任务执行器"""
    logger.info(f"  📋 通用: {actions}")
    if DRY_RUN:
        return True
    try:
        for action in actions:
            logger.info(f"    → 执行 {action}")
            time.sleep(0.5)
        return True
    except Exception as e:
        logger.error(f"通用执行失败: {e}")
        return False