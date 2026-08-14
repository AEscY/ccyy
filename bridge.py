# 在 bridge.py 顶部添加导入
from ai.agent import Web3AirdropAgent

# 在 run_cycle 方法中，扫描完成后添加：
def run_cycle(self) -> str:
    logger.info("🔄 开始一轮扫描...")

    projects = self.scan_chain()
    if not projects:
        return "⚠️ 未发现符合条件的项目"

    # 🆕 AI 分析
    agent = Web3AirdropAgent()
    analyses = agent.batch_analyze(projects)

    # 生成报告
    report = agent.generate_report(analyses)

    # 发送报告（在原有消息之后）
    send_telegram_message(report)

    # 执行任务
    for project in projects:
        result = self.evaluate_project(project)
        if result.get("tasks"):
            self.execute_tasks(result["tasks"])

    return f"✅ 扫描完成：发现 {len(projects)} 个项目，AI 分析已发送"

bridge.py - 数据整合层（升级版）
整合 CryptoRank Radar + 链上监控 + 备用数据
"""

import yaml
import logging
from typing import List, Dict

from scanner.cryptorank_radar import CryptoRankRadar, get_airdrop_radar
from scanner.onchain_monitor import monitor_chains

logger = logging.getLogger(__name__)

class AirdropBridge:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.cryptorank = CryptoRankRadar(
            base_url=self.config.get("cryptorank", {}).get("base_url", "https://api.cryptorank.io/v1"),
            api_key=self.config.get("cryptorank", {}).get("api_key", "")
        )
        # 是否启用模拟模式（调试用）
        self.use_mock = False

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"无法加载配置文件: {e}，使用默认配置")
            return {
                "rpc": {
                    "ethereum": "https://eth.llamarpc.com",
                    "base": "https://base.llamarpc.com",
                    "bsc": "https://bsc.llamarpc.com"
                },
                "scanner": {"min_score": 70, "max_items": 10, "sources": ["cryptorank", "onchain", "mock"]}
            }

    def scan_chain(self) -> List[Dict]:
        """
        执行多源扫描，按优先级获取数据
        """
        if self.use_mock:
            return self._get_mock_data()

        all_projects = []
        sources = self.config.get("scanner", {}).get("sources", ["cryptorank", "onchain", "mock"])

        for source in sources:
            if source == "cryptorank":
                logger.info("📡 正在从 CryptoRank 获取空投数据...")
                try:
                    projects = self.cryptorank.get_airdrops(limit=10)
                    if projects and projects[0].get("source") != "fallback":
                        all_projects.extend(projects)
                        logger.info(f"✅ CryptoRank 获取到 {len(projects)} 个项目")
                    else:
                        logger.warning("⚠️ CryptoRank 数据为空，尝试下一个数据源")
                except Exception as e:
                    logger.error(f"❌ CryptoRank 获取失败: {e}")

            elif source == "onchain":
                logger.info("📡 正在从链上监控获取数据...")
                try:
                    rpc_config = self.config.get("rpc", {})
                    projects = monitor_chains(rpc_config, max_blocks=3)
                    if projects:
                        all_projects.extend(projects)
                        logger.info(f"✅ 链上监控获取到 {len(projects)} 个项目")
                    else:
                        logger.warning("⚠️ 链上监控未发现新项目")
                except Exception as e:
                    logger.error(f"❌ 链上监控失败: {e}")

            elif source == "mock":
                logger.info("📡 使用模拟数据（兜底）")
                all_projects.extend(self._get_mock_data())

            # 如果已有足够数据，提前结束
            if len(all_projects) >= self.config.get("scanner", {}).get("max_items", 10):
                break

        # 去重（按合约地址或名称）
        seen = set()
        unique_projects = []
        for p in all_projects:
            key = p.get("contract") or p.get("name", "")
            if key and key not in seen:
                seen.add(key)
                unique_projects.append(p)

        # 按评分排序
        unique_projects.sort(key=lambda x: x.get("score", 0), reverse=True)

        # 限制数量
        max_items = self.config.get("scanner", {}).get("max_items", 10)
        return unique_projects[:max_items]

    def evaluate_project(self, project_data: Dict) -> Dict:
        """评估项目，生成任务列表"""
        score = project_data.get("score", 0)
        tasks = []

        if score >= 80:
            tasks.append("claim")
            tasks.append("vote")
        elif score >= 70:
            tasks.append("claim")

        # 如果有 URL，添加访问任务
        if project_data.get("url"):
            tasks.append("visit")

        return {"tasks": tasks, "score": score}

    def execute_tasks(self, task_list: List[str]) -> bool:
        """执行任务（占位，第三阶段接入 HarvestKit）"""
        if not task_list:
            return True
        logger.info(f"📋 执行任务: {task_list}")
        # TODO: 第三阶段接入 HarvestKit executor
        return True

    def run_cycle(self) -> str:
        """完整流水线：发现 → 评估 → 执行"""
        logger.info("🔄 开始一轮扫描...")

        projects = self.scan_chain()
        if not projects:
            return "⚠️ 未发现符合条件的项目"

        logger.info(f"📊 发现 {len(projects)} 个项目")

        executed_count = 0
        for project in projects:
            result = self.evaluate_project(project)
            if result.get("tasks"):
                self.execute_tasks(result["tasks"])
                executed_count += 1

        # 生成摘要
        summary = f"✅ 扫描完成：发现 {len(projects)} 个项目，执行 {executed_count} 个任务"
        logger.info(summary)
        return summary

    def _get_mock_data(self) -> List[Dict]:
        """模拟数据（兜底用）"""
        return [
            {"name": "🔵 空投雷达已就绪", "url": "", "score": 50, "source": "mock"},
            {"name": "📌 正在等待数据源响应", "url": "", "score": 0, "source": "mock"},
        ]