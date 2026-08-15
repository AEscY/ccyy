# -*- coding: utf-8 -*-
"""
scanner/cryptorank_radar.py - CryptoRank + 备用数据
（不再使用 three.ws）
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CryptoRankRadar:
    def __init__(self, base_url: str = "https://api.cryptorank.io/v1", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def get_airdrops(self, limit: int = 10) -> List[Dict]:
        if self.api_key:
            data = self._fetch_cryptorank(limit)
            if data:
                return data
        return self._get_fallback_airdrops()

    def _fetch_cryptorank(self, limit: int) -> Optional[List[Dict]]:
        try:
            url = f"{self.base_url}/airdrops"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"limit": limit, "status": "active"}
            resp = self.session.get(url, headers=headers, params=params, timeout=10)
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
        return [
            {"name": "Uniswap V4", "chain": "Ethereum", "score": 92, "url": "https://uniswap.org", "source": "备用"},
            {"name": "Aave V3", "chain": "Polygon", "score": 88, "url": "https://aave.com", "source": "备用"},
            {"name": "Arbitrum Odyssey", "chain": "Arbitrum", "score": 75, "url": "https://arbitrum.io", "source": "备用"},
            {"name": "Optimism Bedrock", "chain": "Optimism", "score": 82, "url": "https://optimism.io", "source": "备用"},
            {"name": "zkSync Era", "chain": "zkSync", "score": 79, "url": "https://zksync.io", "source": "备用"},
        ]