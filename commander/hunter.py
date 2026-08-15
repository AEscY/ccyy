# -*- coding: utf-8 -*-
"""
commander/hunter.py - AI 情报分析与策略生成
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def analyze_projects(projects: List[str]) -> List[Dict]:
    """
    根据项目列表生成执行策略
    """
    strategy = []
    for p in projects:
        item = {
            "project": p,
            "ecosystem": "general",
            "actions": ["claim", "vote"],
            "priority": "medium"
        }
        # 根据项目名关键词识别生态
        if "kite" in p.lower():
            item["ecosystem"] = "kite"
            item["actions"] = ["farm_xp", "daily_checkin", "claim"]
            item["priority"] = "high"
        elif "pharos" in p.lower():
            item["ecosystem"] = "pharos"
            item["actions"] = ["daily_task", "swap", "claim"]
            item["priority"] = "high"
        elif "arbitrum" in p.lower() or "arb" in p.lower():
            item["ecosystem"] = "arbitrum"
            item["actions"] = ["claim", "vote"]
            item["priority"] = "high"
        elif "optimism" in p.lower() or "op" in p.lower():
            item["ecosystem"] = "optimism"
            item["actions"] = ["claim", "vote"]
            item["priority"] = "medium"
        elif "zksync" in p.lower() or "zk" in p.lower():
            item["ecosystem"] = "zksync"
            item["actions"] = ["claim", "bridge"]
            item["priority"] = "medium"
        strategy.append(item)
    return strategy