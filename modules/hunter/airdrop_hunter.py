# -*- coding: utf-8 -*-
"""
模块一：Airdrop Hunter Pro - 全网空投扫描
支持多数据源自动切换
"""

import requests
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

# ===== 数据源列表（自动尝试） =====
SOURCES = [
    {
        "url": "https://web3-discover.vercel.app/api/mcp",
        "type": "json_rpc",
        "path": ["result", "content"]
    },
    {
        "url": "https://airdrop-tracker-omega.vercel.app/api/airdrops",
        "type": "list"
    },
    {
        "url": "https://api.airdrops.io/active/",
        "type": "dict",
        "path": ["data"]
    },
]

def scan_airdrops(limit: int = 20) -> List[str]:
    """
    扫描全网空投，返回项目名称列表
    """
    projects = []
    errors = []

    for source in SOURCES:
        try:
            resp = requests.get(source["url"], timeout=10)
            if resp.status_code != 200:
                errors.append(f"{source['url']} -> {resp.status_code}")
                continue

            data = resp.json()
            items = extract_items(data, source)
            if items:
                for item in items[:limit]:
                    name = extract_name(item)
                    if name and name not in projects:
                        projects.append(name)
                if len(projects) >= limit:
                    break

        except Exception as e:
            errors.append(f"{source['url']} -> {str(e)[:50]}")

    # 如果没有任何数据，返回兜底项目
    if not projects:
        logger.warning(f"所有数据源均失败: {errors}")
        projects = ["Uniswap V4", "Aave V3", "Arbitrum Odyssey", "Optimism Bedrock", "zkSync Era"]

    logger.info(f"扫描完成，发现 {len(projects)} 个项目")
    return projects[:limit]

def extract_items(data, source):
    """根据数据源类型提取项目列表"""
    source_type = source.get("type", "")
    path = source.get("path", [])

    if source_type == "list":
        return data if isinstance(data, list) else []

    if source_type == "dict":
        result = data
        for key in path:
            result = result.get(key, {}) if isinstance(result, dict) else {}
        return result if isinstance(result, list) else []

    if source_type == "json_rpc":
        result = data
        for key in path:
            result = result.get(key, {}) if isinstance(result, dict) else {}
        # 尝试解析 content 中的 text
        if isinstance(result, list):
            items = []
            for item in result:
                if isinstance(item, dict) and "text" in item:
                    try:
                        parsed = json.loads(item["text"])
                        if isinstance(parsed, list):
                            items.extend(parsed)
                    except:
                        pass
            return items
        return []

    return []

def extract_name(item):
    """从项目对象中提取名称"""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return item.get("name") or item.get("project") or item.get("title") or None
    return None
