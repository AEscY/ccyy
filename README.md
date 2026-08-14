airdrop-radar/
├── .github/workflows/deploy.yml    # CI/CD（已有）
├── scanner/                         # On-Chain Alpha Radar 核心
│   ├── __init__.py
│   ├── onchain_monitor.py           # 链上监控
│   └── filters.py                   # 信号过滤
├── commander/                       # Airdrop Hunter Pro 逻辑
│   ├── __init__.py
│   └── hunter.py                    # 情报聚合与任务生成
├── executor/                        # HarvestKit 执行模块
│   ├── __init__.py
│   └── farmer.py                    # 自动化执行
├── bridge.py                        # 数据流整合层（核心）
├── app.py                           # 主入口（已有，需升级）
├── requirements.txt                 # 全部依赖
└── config.yaml                      # 统一配置文件