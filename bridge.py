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