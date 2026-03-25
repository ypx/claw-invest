# Claw Advisor 后端API

基于Mike是麥克投资体系的保守型投资决策系统后端API。

## 🚀 快速开始

### 环境要求
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### 安装依赖
```bash
cd backend
npm install
```

### 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接等
```

### 启动服务
```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

服务将在 http://localhost:3000 启动。

## 📡 API端点

### 健康检查
- `GET /api/v1/health` - 服务健康状态
- `GET /api/v1/version` - API版本信息

### 股票相关
- `GET /api/v1/stocks/list` - 获取所有股票列表
- `GET /api/v1/stocks/symbols` - 获取股票代码列表
- `GET /api/v1/stocks/info/:symbol` - 获取单个股票信息
- `GET /api/v1/stocks/prices/:symbol` - 获取股票价格历史

### 分析相关（需要认证）
- `GET /api/v1/stocks/analysis/:symbol` - 分析单只股票
- `GET /api/v1/stocks/analysis` - 分析所有股票
- `GET /api/v1/stocks/recommendations/top` - 获取今日最高推荐
- `GET /api/v1/stocks/dashboard` - 获取仪表盘数据
- `POST /api/v1/stocks/screener` - 运行股票筛选器

### 持仓相关（需要认证）
- `GET /api/v1/portfolio` - 获取用户持仓
- `POST /api/v1/portfolio` - 添加/更新持仓
- `DELETE /api/v1/portfolio/:id` - 删除持仓
- `GET /api/v1/portfolio/performance` - 获取持仓表现
- `GET /api/v1/portfolio/dividends` - 获取股息记录

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/profile` - 获取用户资料
- `PUT /api/v1/auth/profile` - 更新用户资料

## 🔐 认证方式

使用Bearer Token认证：
```http
Authorization: Bearer <your_jwt_token>
```

## 📊 数据模型

### 用户 (users)
- id (UUID)
- email (String, unique)
- password_hash (String)
- role (enum: user, admin)
- created_at (Timestamp)
- updated_at (Timestamp)

### 股票 (stocks)
- id (UUID)
- symbol (String, unique)
- name (String)
- sector (String)
- industry (String)
- market_cap (BigInt)
- pe_ratio (Float)
- dividend_yield (Float)
- beta (Float)
- created_at (Timestamp)
- updated_at (Timestamp)

### 股票价格 (stock_prices)
- id (UUID)
- stock_id (UUID, foreign key)
- date (Date)
- open (Decimal)
- high (Decimal)
- low (Decimal)
- close (Decimal)
- volume (BigInt)
- created_at (Timestamp)

### Mike推荐 (mike_recommendations)
- id (UUID)
- stock_id (UUID, foreign key)
- recommendation_type (enum: 核心仓, 成长仓, 关注仓, 加密资产)
- mike_reason (Text)
- priority (Integer)
- is_active (Boolean)
- created_at (Timestamp)
- updated_at (Timestamp)

### 保守评分 (conservative_scores)
- id (UUID)
- stock_id (UUID, foreign key)
- score_date (Date)
- mike_weight (Decimal)
- fundamental_score (Decimal)
- technical_score (Decimal)
- conservative_factor (Decimal)
- final_score (Decimal)
- recommendation (enum: 强烈买入, 买入, 持有, 卖出, 强烈卖出)
- sell_put_suggestion (JSONB)
- reasoning (Text)
- created_at (Timestamp)

### 用户持仓 (user_portfolios)
- id (UUID)
- user_id (UUID, foreign key)
- stock_id (UUID, foreign key)
- quantity (Decimal)
- avg_cost (Decimal)
- purchase_date (Date)
- is_option (Boolean)
- option_type (enum: call, put, none)
- strike_price (Decimal)
- expiration_date (Date)
- created_at (Timestamp)
- updated_at (Timestamp)

## 🔧 开发指南

### 项目结构
```
src/
├── config/          # 配置文件
├── controllers/     # 控制器
├── middleware/      # 中间件
├── models/         # 数据模型
├── routes/         # 路由定义
├── utils/          # 工具函数
└── server.js       # 入口文件
```

### 添加新API
1. 在 `src/routes/` 中添加路由定义
2. 在 `src/controllers/` 中创建控制器
3. 在 `src/models/` 中定义数据模型（如果需要）
4. 更新 `src/routes/index.js` 中的路由映射

### 测试API
```bash
# 运行测试
npm test

# 使用curl测试
curl -X GET "http://localhost:3000/api/v1/health"
```

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t claw-advisor-backend .
```

### 运行容器
```bash
docker run -p 3000:3000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  claw-advisor-backend
```

## 📈 监控与日志

- 日志文件位于 `logs/` 目录
- 支持结构化日志记录
- 集成健康检查端点
- 请求速率限制

## 🔗 相关项目

- [前端界面](../frontend/) - React + TypeScript 前端应用
- [数据服务](../data-service/) - Python 数据采集服务
- [分析引擎](../analysis-engine/) - Python 分析算法

## 📄 许可证

MIT License