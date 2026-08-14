"""
executor/farmer.py - 任务执行（占位）
第三阶段接入 HarvestKit 后替换
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

def execute(task_list: List[str]) -> bool:
    """执行任务列表"""
    if not task_list:
        return True

    logger.info(f"🌾 执行任务: {task_list}")
    # TODO: 第三阶段接入 HarvestKit
    return True


def execute_with_retry(task_list: List[str], max_retries: int = 3) -> bool:
    """带重试的任务执行"""
    for attempt in range(max_retries):
        try:
            return execute(task_list)
        except Exception as e:
            logger.warning(f"执行失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return False
    return False