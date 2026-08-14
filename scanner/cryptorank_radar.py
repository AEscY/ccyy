"""
CryptoRank Radar - 免费层数据采集
将 CryptoRank 公开数据转为结构化空投情报
参考: https://clawhub.ai/0xcii/skills/crypto-rank [reference:0]
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CryptoRankRadar:
    """CryptoRank 免费层雷达"""

    def __init__(self, base_url: str = "https://api.cryptorank.io/v1", api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """发送 GET 请求"""
        url = f"{self.base_url}/{endpoint}"
        if self.api_key:
            params = params or {}
            params["api_key"] = self.api_key
        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(f"CryptoRank API 返回 {resp.status_code}: {resp.text[:100]}")
                return None
        except Exception as e:
            logger.error(f"CryptoRank 请求失败: {e}")
            return None

    def get_airdrops(self, limit: int = 10) -> List[Dict]:
        """
        获取空投列表（免费层）
        返回格式: [{"name": str, "url": str, "status": str, "chain": str, ...}]
        """
        # CryptoRank 免费层端点 - 获取进行中的空投
        data = self._get("airdrops", {"limit": limit, "status": "active"})
        if not data:
            return self._get_fallback_airdrops()

        items = data.get("data", []) if isinstance(data, dict) else data
        if not items:
            return self._get_fallback_airdrops()

        results = []
        for item in items[:limit]:
            results.append({
                "name": item.get("name") or item.get("title") or "未知项目",
                "url": item.get("url") or item.get("website") or "",
                "status": item.get("status") or "进行中",
                "chain": item.get("chain") or item.get("network") or "多链",
                "score": self._calc_score(item),
                "source": "cryptorank"
            })
        return results

    def get_funding(self, limit: int = 5) -> List[Dict]:
        """获取融资事件（可作为空投预判信号）"""
        data = self._get("funding", {"limit": limit})
        if not data:
            return []

        items = data.get("data", []) if isinstance(data, dict) else data
        results = []
        for item in items[:limit]:
            results.append({
                "project": item.get("project") or item.get("name") or "未知",
                "amount": item.get("amount") or "未知",
                "round": item.get("round") or "种子轮",
                "investors": item.get("investors", [])[:3],
                "source": "cryptorank_funding"
            })
        return results

    def _calc_score(self, item: Dict) -> int:
        """根据项目信息计算评分"""
        score = 60  # 基础分

        # 有官网链接加分
        if item.get("url") or item.get("website"):
            score += 10

        # 有明确链信息加分
        if item.get("chain") or item.get("network"):
            score += 5

        # 状态为"进行中"加分
        if item.get("status") and "进行" in str(item.get("status")):
            score += 10

        # 有融资信息加分
        if item.get("funding") or item.get("raised"):
            score += 15

        return min(score, 100)

    def _get_fallback_airdrops(self) -> List[Dict]:
        """备用数据：当 API 不可用时返回模拟数据"""
        logger.warning("CryptoRank API 不可用，使用备用数据")
        return [
            {"name": "🔄 CryptoRank 数据加载中", "url": "", "status": "待更新", "chain": "-", "score": 50, "source": "fallback"},
            {"name": "📡 请稍后重试或检查网络", "url": "", "status": "-", "chain": "-", "score": 0, "source": "fallback"},
        ]


# ========== 便捷函数 ==========
def get_airdrop_radar(limit: int = 10) -> List[Dict]:
    """获取空投雷达数据（便捷调用）"""
    radar = CryptoRankRadar()
    return radar.get_airdrops(limit)


def get_funding_radar(limit: int = 5) -> List[Dict]:
    """获取融资雷达数据（便捷调用）"""
    radar = CryptoRankRadar()
    return radar.get_funding(limit)
