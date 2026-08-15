# -*- coding: utf-8 -*-
"""
模块二：Web3 Airdrop Hunter Agent - AI 策略分析
根据项目列表生成执行策略
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ===== 关键词 -> 生态映射 =====
ECOSYSTEM_KEYWORDS = {
    "kite": ["kite", "ki"],
    "pharos": ["pharos", "pha"],
    "arbitrum": ["arbitrum", "arb"],
    "optimism": ["optimism", "op"],
    "base": ["base"],
    "zksync": ["zksync", "zk"],
}

def generate_strategy(projects: List[str]) -> List[Dict]:
    """
    为每个项目生成执行策略
    """
    strategy = []
    for p in projects[:15]:
        item = {
            "project": p,
            "ecosystem": detect_ecosystem(p),
            "actions": ["claim", "vote"],
            "priority": "medium"
        }

        # 根据生态调整动作
        if item["ecosystem"] == "kite":
            item["actions"].append("farm_xp")
            item["actions"].append("daily_checkin")
            item["priority"] = "high"
        elif item["ecosystem"] == "pharos":
            item["actions"].append("daily_task")
            item["actions"].append("swap")
            item["priority"] = "high"
        elif item["ecosystem"] in ["arbitrum", "optimism", "base", "zksync"]:
            item["actions"].append("bridge")
            item["actions"].append("swap")
            item["priority"] = "medium"
        else:
            item["actions"].append("visit_website")
            item["priority"] = "low"

        strategy.append(item)

    logger.info(f"生成 {len(strategy)} 条策略")
    return strategy

def detect_ecosystem(name: str) -> str:
    """根据项目名检测生态"""
    name_lower = name.lower()
    for eco, keywords in ECOSYSTEM_KEYWORDS.items():
        for kw in keywords:
            if kw in name_lower:
                return eco
    return "general"
