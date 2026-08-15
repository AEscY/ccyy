# -*- coding: utf-8 -*-
"""
mcp_client.py - MCP 服务器客户端
调用 Web3 Discover 的 3 个核心工具
"""

import requests
import json

MCP_ENDPOINT = "https://web3-discover.vercel.app/api/mcp"

def list_active_airdrops(limit=20, chain=None, risk=None, sort_by="added"):
    """
    列出活跃空投，支持按链、风险等级过滤
    返回 32 个经过人工审核的空投
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_active_airdrops",
            "arguments": {"limit": limit, "sort_by": sort_by}
        }
    }
    if chain:
        payload["params"]["arguments"]["chain"] = chain
    if risk:
        payload["params"]["arguments"]["risk"] = risk

    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_airdrop(slug):
    """
    获取单个空投的完整详情
    包含：操作步骤、每周工作量、成本估算、风险说明、官方链接
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_airdrop", "arguments": {"slug": slug}}
    }
    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def check_wallet(address):
    """
    检查钱包在 7 条链上的空投资格
    覆盖：Ethereum、Base、Linea、Arbitrum、Polygon、BSC、Solana
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "check_wallet", "arguments": {"addr": address}}
    }
    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_mcp_tools():
    """获取所有可用工具列表"""
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"error": "请求失败"}
    except Exception as e:
        return {"error": str(e)}