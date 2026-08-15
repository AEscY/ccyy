# mcp_client.py - MCP 服务器客户端
import requests
import json

MCP_ENDPOINT = "https://web3-discover.vercel.app/api/mcp"

def list_active_airdrops(limit=10, chain=None, risk=None, sort_by="added"):
    """列出活跃空投，支持按链、风险等级过滤"""
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
    resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
    return resp.json()

def get_airdrop(slug):
    """获取单个空投的完整详情"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_airdrop", "arguments": {"slug": slug}}
    }
    resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
    return resp.json()

def check_wallet(address):
    """检查钱包在 7 条链上的空投资格"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "check_wallet", "arguments": {"addr": address}}
    }
    resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
    return resp.json()
