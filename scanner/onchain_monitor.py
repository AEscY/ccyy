import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware

logger = logging.getLogger(__name__)

def monitor_chains(rpc_config: dict) -> list:
    """
    监控配置中的所有链，返回发现的潜在空投项目
    每个项目格式：{"contract": str, "score": int, "chain": str, "name": str}
    """
    results = []
    for chain_name, rpc_url in rpc_config.items():
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            # 某些链（如 BSC）需要 POA 中间件
            if "bsc" in chain_name.lower():
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if not w3.is_connected():
                logger.warning(f"无法连接 {chain_name} RPC: {rpc_url}")
                continue

            # 获取最新区块号
            latest = w3.eth.block_number
            # 简单示例：获取最近 10 个区块内的合约创建交易
            # 实际生产环境建议使用过滤器和事件监听
            for offset in range(0, 10):
                block_num = latest - offset
                if block_num < 0:
                    break
                block = w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    # 如果交易是合约创建（to 为空）
                    if tx.to is None:
                        contract_address = w3.eth.contract(tx.hash).address
                        # 这里可以添加更多判断，例如是否是新代币、是否有流动性等
                        results.append({
                            "contract": contract_address,
                            "score": 75,  # 可基于更复杂逻辑打分
                            "chain": chain_name,
                            "name": f"Contract on {chain_name} @ block {block_num}"
                        })
                        # 限制条目数
                        if len(results) >= 20:
                            return results
        except Exception as e:
            logger.error(f"监控 {chain_name} 失败: {e}")
    return results