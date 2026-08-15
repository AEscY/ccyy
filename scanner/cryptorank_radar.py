# -*- coding: utf-8 -*-
"""
scanner/cryptorank_radar.py - 多数据源扫描器
集成：CryptoRank + Jeetdrops + 备用数据
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CryptoRankRadar:
    """多数据源空投雷达"""

    def __init__(self, base_url: str = "https://api.cryptorank.io/v1", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_airdrops(self, limit: int = 10) -> List[Dict]:
        """获取空投列表，优先 CryptoRank，失败时使用备用源"""
        # 尝试 CryptoRank
        data = self._fetch_cryptorank(limit)
        if data:
            return data

        # 备用：Web3 Discover MCP（通过 mcp_client）
        try:
            from mcp_client import list_active_airdrops
            result = list_active_airdrops(limit=limit, sort_by="added")
            if result and "result" in result:
                content = result["result"].get("content", [])
                projects = []
                for item in content[:limit]:
                    if isinstance(item, dict):
                        text = item.get("text", "")
                        try:
                            import json
                            parsed = json.loads(text)
                            if isinstance(parsed, list):
                                for p in parsed:
                                    projects.append({
                                        "name": p.get("name", "未知"),
                                        "chain": p.get("chain", "多链"),
                                        "score": p.get("score", 60),
                                        "url": p.get("url", ""),
                                        "source": "Web3 Discover"
                                    })
                                return projects
                        except:
                            pass
        except Exception as e:
            logger.warning(f"备用源失败: {e}")

        # 最终备用：模拟数据
        return self._get_fallback_airdrops()

    def _fetch_cryptorank(self, limit: int) -> Optional[List[Dict]]:
        """从 CryptoRank API 获取数据"""
        if not self.api_key:
            return None
        try:
            url = f"{self.base_url}/airdrops"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"limit": limit, "status": "active"}
            resp = self.session.get(url, headers=headers, params=params, timeout=15)

            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                if items:
                    projects = []
                    for item in items[:limit]:
                        chain = item.get("chain", "多链")
                        if isinstance(chain, list):
                            chain = chain[0] if chain else "多链"
                        projects.append({
                            "name": item.get("name", "未知"),
                            "chain": chain,
                            "score": min(int(item.get("popularity", 50)) + 10, 100),
                            "url": item.get("website", ""),
                            "source": "CryptoRank"
                        })
                    return projects
        except Exception as e:
            logger.error(f"CryptoRank 失败: {e}")
        return None

    def _get_fallback_airdrops(self) -> List[Dict]:
        """备用数据"""
        return [
            {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "备用"},
            {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "备用"},
            {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "备用"},
            {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "备用"},
            {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "备用"},
        ]