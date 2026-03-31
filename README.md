# Claw Advisor - 智能投资决策系统

## 📋 项目简介
保守型个人投资者需求构建的智能投资决策系统。

### 用户画像：Z
- **投资风格**：保守型美股投资者
- **投资偏好**：AI科技股、太空股、老牌科技股
- **操作模式**：长期持有正股 + sell put期权（特爱特斯拉）
- **技术能力**：无代码经验，会Excel公式
- **目标系统**：网页版（手机/电脑都能用）

### 核心原则
1. 遵循保本优先投资体系
2. 叠加保守型投资者风险偏好
3. 数据驱动决策（AI科技股、太空股分析）

## 🏗️ 技术架构

### 系统组件
```
├── backend/           # API网关 (Node.js + Express)
├── frontend/          # 前端界面 (React + TypeScript)
├── analysis-engine/   # 分析引擎 (Python + Pandas)
├── data-service/      # 数据采集服务 (Python)
└── docker/           # 容器化配置
```

### 数据流
1. **数据采集** → Alpha Vantage API → PostgreSQL
2. **分析引擎** → 保守评分算法 → 决策建议
3. **API网关** → 提供RESTful接口
4. **前端界面** → 可视化展示 + 用户交互

## 📊 核心算法

### 保守评分模型
```
保守分数 = 权重 × (基本面分数 + 技术面分数) × 保守系数
```

### 权重分配
- 核心仓（NVDA/GOOGL/AMZN）：权重 1.0
- 成长仓（IONQ/BTC/META）：权重 0.8
- 关注标的：权重 0.6

### 保守系数计算
- PE < 20: 系数 1.2
- 20 ≤ PE ≤ 40: 系数 1.0
- PE > 40: 系数 0.8
- 波动率（Beta）< 1: 系数 1.1
- 波动率 ≥ 1: 系数 0.9

## 🚀 开发路线图

### 第一阶段：MVP（1-2周）
- [ ] 基础架构搭建
- [ ] 数据采集服务
- [ ] 保守评分算法
- [ ] 简单仪表盘

### 第二阶段：产品化（2-3周）
- [ ] 用户系统
- [ ] 持仓管理
- [ ] 决策记录
- [ ] 通知提醒

### 第三阶段：商业化（4-6周）
- [ ] 多用户支持
- [ ] 高级分析
- [ ] 社区功能
- [ ] 付费订阅

## 🔧 环境要求

### 后端
- Node.js 18+
- Python 3.9+
- PostgreSQL 14+
- Redis 6+

### 前端
- React 18+
- TypeScript 5+
- Node.js 18+

## 📁 目录说明

| 目录 | 说明 |
|------|------|
| `backend/` | API网关，用户认证，业务逻辑 |
| `frontend/` | 前端界面，数据可视化 |
| `analysis-engine/` | 数据分析，评分算法 |
| `data-service/` | 数据采集，清洗，存储 |
| `docker/` | 容器化配置，一键部署 |

## 🔐 配置文件

**环境变量**（`.env`）
```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/clawadvisor
REDIS_URL=redis://localhost:6379

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=OH7TPNSBQONIAGBG

# JWT
JWT_SECRET=your_jwt_secret_key
```

## 📞 联系方式

**开发者**：A（AI助手）
**用户**：Z（保守型美股投资者）
**项目状态**：开发中（2026-03-23开始）
