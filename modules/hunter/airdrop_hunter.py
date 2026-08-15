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
            errors.append(f"{source['url']} -> {str
