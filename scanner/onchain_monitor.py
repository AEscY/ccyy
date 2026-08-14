import requests
from web3 import Web3

# 使用免费 RPC
RPC_URLS = {
    "ethereum": "https://eth.llamarpc.com",
    "base": "https://base.llamarpc.com",
    "bsc": "https://bsc.llamarpc.com"
}

def monitor_chain():
    """监控链上新合约部署和活跃交易"""
    results = []
    for chain, rpc_url in RPC_URLS.items():
        try:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                continue
            # 获取最新区块
            latest_block = w3.eth.block_number
            # 这里可以添加更复杂的逻辑：监听新合约、大额转账等
            results.append({
                "contract": f"0x{latest_block}...",  # 示例
                "score": 80,
                "chain": chain,
                "name": f"New Activity on {chain}"
            })
        except Exception as e:
            print(f"监控 {chain} 失败: {e}")
    return results