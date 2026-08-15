# -*- coding: utf-8 -*-
"""
AI 情报模块 - 使用 MCP 数据源
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

# 使用 MCP 作为主数据源
MCP_ENDPOINT = "https://web3-discover.vercel.app/api/mcp"

def run_ai_agent():
    """
    运行 AI 代理，返回项目名称列表
    """
    logger.info("AI 代理启动...")
    projects = []

    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "list_active_airdrops",
                "arguments": {"limit": 20, "sort_by": "added"}
            }
        }
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if "result" in data:
                content = data["result"].get("content", [])
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text", "")
                        try:
                            parsed = json.loads(text)
                            if isinstance(parsed, list):
                                for p in parsed:
                                    name = p.get("name")
                                    if name:
                                        projects.append(name)
                        except:
                            pass
    except Exception as e:
        logger.error(f"MCP 调用失败: {e}")

    if not projects:
        # 使用备用模拟数据
        logger.warning("MCP 无数据，使用本地备用列表")
        projects = [
            "Uniswap V4", "Aave V3", "Arbitrum Odyssey",
            "Optimism Bedrock", "zkSync Era", "Base Network",
            "Avalanche", "Kite AI Testnet", "Pharos Network"
        ]

    return list(set(projects))[:20]