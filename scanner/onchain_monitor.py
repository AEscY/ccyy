"""
链上监控模块 - 监控多链合约活动
"""

import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from typing import List, Dict

logger = logging.getLogger(__name__)

def monitor_chains(rpc_config: dict, max_blocks: int = 5) -> List[Dict]:
    """
    监控配置中的所有链，返回发现的潜在空投项目
    """
    results = []

    for chain_name, rpc_url in rpc_config.items():
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            # BSC 等链需要 POA 中间件
            if "bsc" in chain_name.lower() or "polygon" in chain_name.lower():
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            if not w3.is_connected():
                logger.warning(f"无法连接 {chain_name}: {rpc_url}")
                continue

            latest = w3.eth.block_number
            logger.info(f"✅ {chain_name} 已连接，当前区块: {latest}")

            # 扫描最近 N 个区块的合约创建
            for offset in range(max_blocks):
                block_num = latest - offset
                if block_num < 0:
                    break

                try:
                    block = w3.eth.get_block(block_num, full_transactions=True)
                    for tx in block.transactions:
                        # 合约创建交易: to 为空
                        if tx.to is None:
                            try:
                                # 获取合约地址
                                contract_addr = w3.eth.contract(tx.hash).address
                                # 获取合约代码，判断是否为空
                                code = w3.eth.get_code(contract_addr)
                                if code and len(code) > 0:
                                    results.append({
                                        "contract": contract_addr,
                                        "tx_hash": tx.hash.hex(),
                                        "chain": chain_name,
                                        "block": block_num,
                                        "score": 75,
                                        "name": f"New Contract on {chain_name}",
                                        "source": "onchain"
                                    })
                                    if len(results) >= 20:
                                        return results
                            except Exception as e:
                                logger.debug(f"处理交易失败: {e}")
                                continue
                except Exception as e:
                    logger.debug(f"获取区块 {block_num} 失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"监控 {chain_name} 失败: {e}")

    return results


def monitor_single_chain(chain_name: str, rpc_url: str, max_blocks: int = 5) -> List[Dict]:
    """监控单条链"""
    return monitor_chains({chain_name: rpc_url}, max_blocks)