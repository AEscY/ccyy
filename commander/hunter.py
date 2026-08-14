"""
commander/hunter.py - 情报聚合与任务生成
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def analyze_project(project: Dict) -> Dict:
    """
    分析项目，返回评分和推荐任务
    """
    score = project.get("score", 50)
    tasks = []

    # 根据评分决定任务
    if score >= 80:
        tasks = ["claim_airdrop", "follow_twitter", "join_discord", "vote"]
    elif score >= 70:
        tasks = ["claim_airdrop", "follow_twitter"]
    elif score >= 60:
        tasks = ["visit_website"]

    # 检查是否有 URL
    if project.get("url"):
        tasks.append("visit")

    return {
        "project_name": project.get("name", "未知"),
        "score": score,
        "tasks": tasks,
        "priority": "high" if score >= 80 else "medium" if score >= 60 else "low"
    }


def batch_analyze(projects: List[Dict]) -> List[Dict]:
    """批量分析项目"""
    return [analyze_project(p) for p in projects]