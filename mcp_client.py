# -*- coding: utf-8 -*-
import requests

MCP_ENDPOINT = "https://web3-discover.vercel.app/api/mcp"

def list_active_airdrops(limit=20):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "list_active_airdrops", "arguments": {"limit": limit}}
    }
    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        return resp.json() if resp.status_code == 200 else {"error": "HTTP " + str(resp.status_code)}
    except Exception as e:
        return {"error": str(e)}

def check_wallet(address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "check_wallet", "arguments": {"addr": address}}
    }
    try:
        resp = requests.post(MCP_ENDPOINT, json=payload, timeout=15)
        return resp.json() if resp.status_code == 200 else {"error": "HTTP " + str(resp.status_code)}
    except Exception as e:
        return {"error": str(e)}