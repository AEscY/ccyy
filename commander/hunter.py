# -*- coding: utf-8 -*-
"""
commander/hunter.py - AI 情报分析与策略生成
集成 MCP 数据源
"""

import logging
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

def analyze_projects(projects: List[str]) -> List[Dict]:
    """
    根据项目列表生成执行策略
    支持生态识别、优先级排序、任务生成
    """
    strategy = []

    # 预定义生态关键词映射
    ECOSYSTEM_MAP = {
        "kite": {"ecosystem": "kite", "actions": ["farm_xp", "daily_checkin", "claim", "ai_interact"], "priority": "high"},
        "pharos": {"ecosystem": "pharos", "actions": ["daily_task", "swap", "claim", "bridge"], "priority": "high"},
        "arbitrum": {"ecosystem": "arbitrum", "actions": ["claim", "vote", "stake"], "priority": "high"},
        "arb": {"ecosystem": "arbitrum", "actions": ["claim", "vote", "stake"], "priority": "high"},
        "optimism": {"ecosystem": "optimism", "actions": ["claim", "vote", "delegate"], "priority": "medium"},
        "op": {"ecosystem": "optimism", "actions": ["claim", "vote", "delegate"], "priority": "medium"},
        "zksync": {"ecosystem": "zksync", "actions": ["claim", "bridge", "swap"], "priority": "medium"},
        "zk": {"ecosystem": "zksync", "actions": ["claim", "bridge", "swap"], "priority": "medium"},
        "base": {"ecosystem": "base", "actions": ["claim", "swap", "bridge"], "priority": "medium"},
        "solana": {"ecosystem": "solana", "actions": ["claim", "stake", "swap"], "priority": "medium"},
        "linea": {"ecosystem": "linea", "actions": ["claim", "bridge"], "priority": "medium"},
        "polygon": {"ecosystem": "polygon", "actions": ["claim", "vote"], "priority": "low"},
    }

    for p in projects:
        lower_p = p.lower()
        matched = False

        for keyword, config in ECOSYSTEM_MAP.items():
            if keyword in lower_p:
                strategy.append({
                    "project": p,
                    "ecosystem": config["ecosystem"],
                    "actions": config["actions"],
                    "priority": config["priority"],
                    "confidence": 85 if config["priority"] == "high" else 70
                })
                matched = True
                break

        if not matched:
            strategy.append({
                "project": p,
                "ecosystem": "general",
                "actions": ["research", "claim"],
                "priority": "low",
                "confidence": 50
            })

    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    strategy.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))

    return strategy

def get_project_score(project: str) -> int:
    """基于项目名称计算评分"""
    # 简单评分逻辑，可扩展
    score = 50
    high_priority_keywords = ["kite", "pharos", "arbitrum", "optimism", "zksync"]
    for kw in high_priority_keywords:
        if kw in project.lower():
            score += 20
            break
    if any(c.isupper() for c in project[:3]):
        score += 10
    return min(score, 100)