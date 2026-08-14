"""
ai/agent.py - Web3 Airdrop Hunter Agent
基于 model-compose 的 Web3 Airdrop Hunter Agent 实现 [reference:1]
"""

import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Web3AirdropAgent:
    """
    Web3 空投狩猎 AI 代理
    自动发现空投机会并给出建议
    """

    def __init__(self):
        self.system_prompt = """你是一个专业的 Web3 空投和 DeFi 研究代理。
你的任务是：
1. 分析空投项目的质量和潜力
2. 评估参与风险
3. 给出具体的行动建议
4. 用中文回复，简洁明了"""

    def analyze_opportunity(self, project_data: Dict) -> Dict:
        """
        分析单个空投机会
        """
        name = project_data.get("name", "未知项目")
        score = project_data.get("score", 50)
        chain = project_data.get("chain", "未知链")
        url = project_data.get("url", "")

        # 基于规则的分析（无需 AI API）
        analysis = self._rule_based_analysis(project_data)

        return {
            "project": name,
            "chain": chain,
            "score": score,
            "verdict": analysis["verdict"],
            "risk_level": analysis["risk"],
            "actions": analysis["actions"],
            "reason": analysis["reason"],
            "timestamp": datetime.now().isoformat()
        }

    def _rule_based_analysis(self, project: Dict) -> Dict:
        """基于规则的分析引擎"""
        score = project.get("score", 50)
        name = project.get("name", "")
        source = project.get("source", "")

        # 判断 verdict
        if score >= 80:
            verdict = "🟢 强烈推荐"
            risk = "低"
            actions = ["立即参与", "多钱包操作"]
        elif score >= 70:
            verdict = "🟡 值得关注"
            risk = "中"
            actions = ["了解详情", "准备参与"]
        elif score >= 60:
            verdict = "🟠 可观望"
            risk = "中高"
            actions = ["收集信息", "等待进一步确认"]
        else:
            verdict = "🔴 不建议参与"
            risk = "高"
            actions = ["跳过"]

        # 生成理由
        reasons = []
        if source == "cryptorank":
            reasons.append("数据来自 CryptoRank 认证平台")
        if source == "onchain":
            reasons.append("链上检测到合约活动")
        if project.get("url"):
            reasons.append("有官方网站")

        if not reasons:
            reasons.append("信息不完整，建议进一步核实")

        return {
            "verdict": verdict,
            "risk": risk,
            "actions": actions,
            "reason": "；".join(reasons)
        }

    def batch_analyze(self, projects: List[Dict]) -> List[Dict]:
        """批量分析多个项目"""
        results = []
        for p in projects:
            results.append(self.analyze_opportunity(p))
        return results

    def generate_report(self, analyses: List[Dict]) -> str:
        """生成可读报告"""
        if not analyses:
            return "暂无分析结果"

        lines = ["📊 **空投雷达分析报告**", ""]

        for a in analyses[:5]:
            lines.append(f"### {a['project']}")
            lines.append(f"- 链: {a['chain']}")
            lines.append(f"- 评分: {a['score']}/100")
            lines.append(f"-  verdict: {a['verdict']}")
            lines.append(f"- 风险: {a['risk_level']}")
            lines.append(f"- 建议: {', '.join(a['actions'])}")
            lines.append(f"- 理由: {a['reason']}")
            lines.append("")

        lines.append(f"🕒 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(lines)


# ========== 便捷函数 ==========
def create_agent() -> Web3AirdropAgent:
    """创建 AI 代理实例"""
    return Web3AirdropAgent()


def analyze_airdrops(projects: List[Dict]) -> str:
    """分析空投列表并生成报告"""
    agent = Web3AirdropAgent()
    analyses = agent.batch_analyze(projects)
    return agent.generate_report(analyses)
