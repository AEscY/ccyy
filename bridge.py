import yaml
import logging
from typing import List, Dict, Any

# 导入真实的链上监控模块
from scanner.onchain_monitor import monitor_chains

logger = logging.getLogger(__name__)

class AirdropBridge:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        # 是否使用模拟数据（便于测试，可设为 False 启用真实扫描）
        self.use_mock = False  # 改为 False 即启用真实链上监控

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"无法加载配置文件 {path}: {e}，使用默认配置")
            return {
                "rpc": {
                    "ethereum": "https://eth.llamarpc.com",
                    "base": "https://base.llamarpc.com",
                    "bsc": "https://bsc.llamarpc.com"
                },
                "risk": {"max_gas_price": 50, "max_transaction_value": 0.1, "cooldown_seconds": 60},
                "scanner": {"min_score": 70, "max_items": 10}
            }

    def scan_chain(self) -> List[Dict]:
        """
        执行链上扫描，返回项目列表（每个项目包含 contract, score, chain, name 等）
        """
        if self.use_mock:
            # 模拟数据（用于测试）
            return [
                {"contract": "0x123...", "score": 85, "chain": "ethereum", "name": "Mock Project 1"},
                {"contract": "0x456...", "score": 60, "chain": "base", "name": "Mock Project 2"},
            ]
        else:
            # 调用真实的链上监控
            try:
                results = monitor_chains(self.config.get("rpc", {}))
                # 根据配置文件中的最低分数过滤
                min_score = self.config.get("scanner", {}).get("min_score", 70)
                filtered = [p for p in results if p.get("score", 0) >= min_score]
                # 限制数量
                max_items = self.config.get("scanner", {}).get("max_items", 10)
                return filtered[:max_items]
            except Exception as e:
                logger.error(f"链上扫描失败: {e}")
                # 扫描失败时返回空列表，而不是崩溃
                return []

    def evaluate_project(self, project_data: Dict) -> Dict:
        """
        评估项目，生成任务列表（目前为占位，未来可集成 commander/hunter）
        """
        # 这里可以调用 commander.hunter 的分析逻辑
        # 简单示例：根据分数决定任务
        score = project_data.get("score", 0)
        tasks = []
        if score > 80:
            tasks.append("claim")
        if score > 70:
            tasks.append("vote")
        return {"tasks": tasks}

    def execute_tasks(self, task_list: List[Dict]) -> bool:
        """
        执行任务（未来可集成 executor/farmer）
        """
        if not task_list:
            return True
        logger.info(f"执行任务: {task_list}")
        # 实际应调用 executor.farmer.execute(task_list)
        return True

    def run_cycle(self) -> str:
        """
        完整流水线：发现 → 评估 → 执行
        """
        logger.info("🔄 开始一轮扫描...")
        projects = self.scan_chain()
        if not projects:
            return "⚠️ 未发现符合条件的项目"

        for project in projects:
            tasks = self.evaluate_project(project)
            if tasks and tasks.get("tasks"):
                self.execute_tasks(tasks["tasks"])
        return f"✅ 本轮完成，共扫描 {len(projects)} 个项目"