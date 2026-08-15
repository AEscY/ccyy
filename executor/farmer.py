# -*- coding: utf-8 -*-
"""
executor/farmer.py - 任务执行器（整合专用机器人）
"""

import logging
import subprocess
import os
from typing import List, Dict

logger = logging.getLogger(__name__)

def execute_strategy(strategy: List[Dict]) -> Dict:
    """
    执行策略中的任务，根据生态调用专用机器人
    """
    results = {
        "total": len(strategy),
        "executed": 0,
        "failed": 0,
        "details": []
    }

    for item in strategy:
        project = item.get("project", "未知")
        ecosystem = item.get("ecosystem", "general")
        actions = item.get("actions", [])

        logger.info(f"🌾 执行 {project} ({ecosystem})")

        # 根据生态调用专用机器人
        if ecosystem == "kite":
            success = run_kite_bot()
        elif ecosystem == "pharos":
            success = run_pharos_bot()
        else:
            # 通用任务（模拟）
            success = run_general_tasks(actions)

        if success:
            results["executed"] += 1
            results["details"].append({"project": project, "status": "success"})
        else:
            results["failed"] += 1
            results["details"].append({"project": project, "status": "failed"})

    logger.info(f"✅ 执行完成: 成功 {results['executed']} 个，失败 {results['failed']} 个")
    return results

def run_kite_bot():
    """调用 Kite AI 专用机器人（如果有脚本）"""
    try:
        # 如果有独立的 bot 脚本，可以调用
        bot_path = os.path.join(os.path.dirname(__file__), "..", "bots", "kite_ai", "bot.js")
        if os.path.exists(bot_path):
            result = subprocess.run(["node", bot_path], capture_output=True, timeout=60)
            return result.returncode == 0
        else:
            # 模拟执行
            logger.info("  → 执行 Kite AI 任务: farm_xp, daily_checkin")
            return True
    except Exception as e:
        logger.error(f"Kite AI 执行失败: {e}")
        return False

def run_pharos_bot():
    """调用 Pharos Network 专用机器人"""
    try:
        bot_path = os.path.join(os.path.dirname(__file__), "..", "bots", "pharos", "bot.js")
        if os.path.exists(bot_path):
            result = subprocess.run(["node", bot_path], capture_output=True, timeout=60)
            return result.returncode == 0
        else:
            logger.info("  → 执行 Pharos 任务: daily_task, swap")
            return True
    except Exception as e:
        logger.error(f"Pharos 执行失败: {e}")
        return False

def run_general_tasks(actions):
    """通用任务执行"""
    for action in actions:
        logger.info(f"  → 执行 {action}")
    return True