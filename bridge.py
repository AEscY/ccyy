# -*- coding: utf-8 -*-
"""
bridge.py - Data integration layer
"""

import yaml
import logging
from typing import List, Dict

from scanner.cryptorank_radar import CryptoRankRadar
from scanner.onchain_monitor import monitor_chains

logger = logging.getLogger(__name__)

class AirdropBridge:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.cryptorank = CryptoRankRadar(
            base_url=self.config.get("cryptorank", {}).get("base_url", "https://api.cryptorank.io/v1"),
            api_key=self.config.get("cryptorank", {}).get("api_key", "")
        )
        self.use_mock = False
        self.last_projects = []

    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning("Failed to load config: " + str(e) + ", using defaults")
            return {
                "rpc": {
                    "ethereum": "https://eth.llamarpc.com",
                    "base": "https://base.llamarpc.com",
                    "bsc": "https://bsc.llamarpc.com"
                },
                "scanner": {"min_score": 70, "max_items": 10, "sources": ["cryptorank", "onchain", "mock"]}
            }

    def scan_chain(self) -> List[Dict]:
        # 如果 mock 开启，直接返回模拟数据
        if self.use_mock:
            return self._get_mock_data()

        all_projects = []
        sources = self.config.get("scanner", {}).get("sources", ["cryptorank", "onchain", "mock"])

        for source in sources:
            if source == "cryptorank":
                logger.info("Fetching data from CryptoRank...")
                try:
                    projects = self.cryptorank.get_airdrops(limit=10)
                    if projects and projects[0].get("source") != "fallback":
                        all_projects.extend(projects)
                        logger.info("Got " + str(len(projects)) + " projects from CryptoRank")
                    else:
                        logger.warning("CryptoRank data empty, trying next source")
                except Exception as e:
                    logger.error("CryptoRank fetch failed: " + str(e))

            elif source == "onchain":
                logger.info("Fetching data from on-chain monitor...")
                try:
                    rpc_config = self.config.get("rpc", {})
                    projects = monitor_chains(rpc_config, max_blocks=3)
                    if projects:
                        all_projects.extend(projects)
                        logger.info("Got " + str(len(projects)) + " projects from on-chain")
                    else:
                        logger.warning("No on-chain projects found")
                except Exception as e:
                    logger.error("On-chain monitor failed: " + str(e))

            elif source == "mock":
                logger.info("Using mock data (fallback)")
                all_projects.extend(self._get_mock_data())

            if len(all_projects) >= self.config.get("scanner", {}).get("max_items", 10):
                break

        # 如果所有来源都没获取到，使用模拟数据兜底
        if not all_projects:
            logger.warning("No data from any source, using mock data as fallback")
            all_projects = self._get_mock_data()

        # 去重
        seen = set()
        unique_projects = []
        for p in all_projects:
            key = p.get("contract") or p.get("name", "")
            if key and key not in seen:
                seen.add(key)
                unique_projects.append(p)

        unique_projects.sort(key=lambda x: x.get("score", 0), reverse=True)
        max_items = self.config.get("scanner", {}).get("max_items", 10)
        return unique_projects[:max_items]

    def evaluate_project(self, project_data: Dict) -> Dict:
        score = project_data.get("score", 0)
        tasks = []
        if score >= 80:
            tasks.append("claim")
            tasks.append("vote")
        elif score >= 70:
            tasks.append("claim")
        if project_data.get("url"):
            tasks.append("visit")
        return {"tasks": tasks, "score": score}

    def execute_tasks(self, task_list: List[str]) -> bool:
        if not task_list:
            return True
        logger.info("Executing tasks: " + str(task_list))
        return True

    def run_cycle(self) -> str:
        logger.info("Starting scan cycle...")
        projects = self.scan_chain()
        self.last_projects = projects
        if not projects:
            return "No eligible projects found"

        logger.info("Found " + str(len(projects)) + " projects")
        executed_count = 0
        for project in projects:
            result = self.evaluate_project(project)
            if result.get("tasks"):
                self.execute_tasks(result["tasks"])
                executed_count += 1

        summary = "Scan complete: found " + str(len(projects)) + " projects, executed " + str(executed_count) + " tasks"
        logger.info(summary)
        return summary

    def get_last_projects(self) -> List[Dict]:
        return self.last_projects

    def _get_mock_data(self) -> List[Dict]:
        return [
            {"name": "Mock Project 1", "url": "https://example1.com", "score": 85, "chain": "ethereum", "source": "mock"},
            {"name": "Mock Project 2", "url": "https://example2.com", "score": 70, "chain": "base", "source": "mock"},
            {"name": "Mock Project 3", "url": "https://example3.com", "score": 60, "chain": "bsc", "source": "mock"},
        ]