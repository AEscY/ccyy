# -*- coding: utf-8 -*-
import requests
import logging

logger = logging.getLogger(__name__)

SOURCES = [
    "https://web3-discover.vercel.app/api/mcp",
    "https://airdrop-tracker-omega.vercel.app/api/airdrops",
]

def run_ai_agent():
    projects = []
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("data") or data.get("result") or data.get("airdrops") or []
            for item in items[:10]:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("project") or item.get("title")
                    if name:
                        projects.append(name)
                elif isinstance(item, str):
                    projects.append(item)
        except Exception as e:
            logger.warning(f"数据源 {url} 失败: {e}")
    return list(set(projects))[:20]
