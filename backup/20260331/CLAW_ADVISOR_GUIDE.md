# 🦅 Claw Advisor 投资决策系统

## 📋 系统概述

Claw Advisor 是一个基于**我的投资经验 + 你的保守偏好**构建的智能决策系统。它不依赖任何外部投资顾问，而是融合了：

1. **我的投资哲学** - 保守原则 + 科技趋势 + 量化分析
2. **你的特殊偏好** - 保守型美股投资者，关注AI/太空股，常做特斯拉sell put
3. **实时市场数据** - 使用API获取最新行情和新闻

## 🚀 核心功能

### 🔥 今日最佳操作
- 基于评分算法推荐最佳买入机会
- 考虑保守系数，过滤高风险标的
- 提供具体操作建议（价格、仓位、理由）

### 💰 最佳期权机会
- 特别关注sell put机会
- 针对你熟悉的股票（如特斯拉）给出具体建议
- 计算预期收益和风险

### 📊 投资组合建议
- 分析持仓健康度
- 提供分散化建议
- 现金管理策略

### ⚠️ 风险提示
- 市场风险预警
- 基于你的风险偏好给出警告
- 重要事件提醒

## 🛠️ 技术架构

```
├── 数据层 (data-service/)
│   ├── finnhub_client.py      # Finnhub API客户端
│   ├── news_client.py         # News API客户端
│   └── 其他数据源接口
│
├── 分析层 (analysis-engine/)
│   ├── claw_decision_engine.py # 核心决策算法
│   └── 评分模型和算法
│
├── 展示层
│   ├── claw_advisor_main.py    # 主程序
│   ├── claw_advisor_latest.html # 生成的HTML报告
│   └── 可扩展的Web界面
│
└── 配置和依赖
    ├── venv/                  # Python虚拟环境
    ├── requirements.txt       # 依赖列表
    └── 配置文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /Users/nn/WorkBuddy/Claw
python3 -m venv venv
source venv/bin/activate
pip install requests pandas numpy
```

### 2. 运行系统
```bash
python3 claw_advisor_main.py
```

### 3. 查看结果
系统将生成 `claw_advisor_latest.html` 文件，用浏览器打开即可看到完整的投资建议。

### 4. 每日运行（建议）
```bash
# 可以设置定时任务，每天自动运行
0 9 * * * cd /Users/nn/WorkBuddy/Claw && source venv/bin/activate && python3 claw_advisor_main.py
```

## 🔧 自定义配置

### 修改关注股票
编辑 `data-service/finnhub_client.py` 中的 `PRIMARY_STOCKS` 列表：
```python
PRIMARY_STOCKS = [
    "NVDA", "GOOGL", "AMZN", "META",  # AI/科技
    "TSLA", "AAPL", "MSFT",           # Z特别关注的
    "IONQ", "RKLB", "ASTS",           # 太空/前沿
    "COIN", "MARA",                   # 加密货币
]
```

### 调整保守偏好
编辑 `analysis-engine/claw_decision_engine.py` 中的 `z_preferences`：
```python
self.z_preferences = {
    "favorite_stocks": ["TSLA"],      # 你最熟悉的股票
    "preferred_action": "sell_put",   # 偏好操作
    "risk_tolerance": "low",          # 风险容忍度
    "time_horizon": "long_term",      # 投资期限
    "cash_reserve": 0.35,             # 现金储备目标
}
```

### 修改API密钥
如果你需要更换API提供商，修改对应的客户端文件：
- Finnhub API: `data-service/finnhub_client.py`
- News API: `data-service/news_client.py`

## 📈 决策算法详解

### 综合评分公式
```
最终分数 = 基本面分数×60% + 技术面分数×40% × 保守系数
```

### 保守系数计算
- **低估值** (PE<15): ×1.2
- **低波动** (Beta<0.8): ×1.15  
- **有股息** (>2%): ×1.05
- **大盘股** (>1000亿市值): ×1.1
- **你熟悉的股票**: ×1.1

### 建议等级
- ≥80分: ⭐️⭐️⭐️⭐️⭐️ 强烈买入
- ≥65分: ⭐️⭐️⭐️⭐️ 买入
- ≥40分: ⭐️⭐️⭐️ 持有
- ≤20分: 🚫 卖出

## 🔄 后续开发计划

### 短期（1-2周）
1. **Web界面** - 开发React前端，提供更好交互
2. **持仓管理** - 导入你的实际持仓，给出个性化建议
3. **老虎证券集成** - 自动读取账户数据

### 中期（1-2月）
4. **回测系统** - 验证算法有效性
5. **实时监控** - 价格提醒、事件提醒
6. **多用户支持** - 为其他用户提供服务

### 长期（产品化）
7. **移动应用** - iOS/Android App
8. **付费订阅** - 高级功能收费
9. **社区功能** - 用户分享和讨论

## ⚠️ 注意事项

1. **数据延迟** - 免费API有频率限制，实时性有限
2. **算法局限** - 任何算法都有局限性，建议仅作为参考
3. **风险提示** - 投资有风险，决策需谨慎
4. **免责声明** - 本系统提供的建议仅供参考，不构成投资建议

## 📞 技术支持

如果你遇到问题或有改进建议：
1. 检查Python环境和依赖
2. 确认API密钥有效
3. 查看日志文件了解错误信息
4. 可以根据你的需求调整算法参数

---

**🦅 Claw Advisor - 让你的投资决策更智能、更自信**

*最后更新: 2026年3月23日*
*版本: 1.0.0*