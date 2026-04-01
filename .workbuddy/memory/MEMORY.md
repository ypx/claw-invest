# 长期记忆 — 用户偏好与项目知识

_最后更新：2026-03-23_

---

## 用户偏好

- 使用中文交流
- 工作区：`/Users/nn/WorkBuddy/Claw`
- 投资方向：关注美股、加密货币，参考 Mike是麥克（@mike1111）的投资体系
- **投资身份**：Z，个人美股投资者，保守型
- **投资风格**：
  - 长期持有AI/科技/太空正股
  - 保留现金
  - 常做sell put期权（尤其是特斯拉）
- **券商**：老虎证券
- **技术经验**：无代码经验，会Excel公式
- **系统期望**：网页版（手机/电脑都能用）
- **架构要求**：需要良好的技术架构（数据库、前后端分离等）
- **数据API**：Alpha Vantage API key: OH7TPNSBQONIAGBG（已获取）

---

## 投资顾问知识库：Mike是麥克 投资体系

> 来源：YouTube频道 @mike1111（Mike是麥克），美籍华人，财经作家，20.1万订阅，770个视频
> 分析时间：2026-03-23，共分析 300+ 视频标题 + 25 个核心视频详细描述
> 报告文件：`/Users/nn/WorkBuddy/Claw/mike_investment_report.html` 和 `.pdf`

### 核心投资原则（8条）

1. **只投美股，远离 A 股** — 认为 A 股是财富收割机，中国市场制度性风险高
2. **长期定投，不做短线** — 优质资产持有多年，忽略短期波动
3. **宏观先于个股** — 地缘政治 + 货币周期 + 行业赛道三重叠加判断方向
4. **仓位管理第一** — 重仓 ≠ All-in，分批建仓，留有余地
5. **危机即机会** — VIX 40~60 才是真正底部，恐慌时买入
6. **分散 + 核心持仓结合** — 核心仓（科技巨头稳定盈利）+ 成长仓（前沿赛道高弹性）
7. **弱美元时代增配硬资产** — BTC、优质美股是弱美元最大受益者
8. **国家战略即投资风向标** — 白宫政策/美国国家战略决定资本流向

### 投资逻辑框架（5层）

1. **宏观货币层**：美元周期（强→弱→再强），利率走向，财政赤字
2. **地缘政治层**：战争/制裁/贸易摩擦对资产的重新定价
3. **技术革命层**：AI → 量子计算 → 太空能源 → 稳定币，每波新技术周期
4. **安装期理论**：参考卡萝塔·佩雷兹"技术革命浪潮"，当前处于 AI 安装期，泡沫正常
5. **比特币主权逻辑**：BTC 是去美元化时代的数字黄金，各国央行迟早配置

### 核心持仓标的（实盘参考）

| 类别 | 标的 | 逻辑 |
|------|------|------|
| 核心仓（长期定投） | **NVDA** | AI 算力基础设施，不可替代的护城河 |
| 核心仓（长期定投） | **GOOGL** | AI + 搜索 + 云，低估的 AI 巨头 |
| 核心仓（长期定投） | **AMZN** | 云计算 AWS + 电商，现金流稳健 |
| 加密资产 | **BTC（通过 ARKB 配置）** | 数字黄金，主权资产，低成本 ETF 参与 |
| 加密资产 | **ETH** | 质押收益，Web3 基础设施 |
| 量子计算 | **IONQ** | 量子霸权前夜，高风险高回报 |
| AI 社交 | **Meta** | 广告 + AI + 元宇宙，被低估 |
| 稳定币/Web3 | **Circle（CRCL）** | 稳定币革命，美元链上霸权核心 |
| 比特币矿企 | **MARA 等** | BTC 高 Beta，逻辑转向（不仅挖矿） |
| 其他关注 | **CMBT、特斯拉** | 偶尔提及 |

### 重点关注赛道（优先级）

1. **AI 基础设施**（最高）— NVDA 为代表，算力稀缺
2. **加密货币/Web3**（最高）— BTC 主权化，ETH 质押，稳定币
3. **量子计算**（高）— IONQ 为代表，5-10 年赛道
4. **太空能源/电网**（高）— 太空时代投资逻辑
5. **军工/防务**（中高）— 地缘危机受益
6. **美股宽基 ETF**（基础配置）— 定投底仓

### 操作风格与禁忌

**该做的：**
- 每月定投核心仓，不管涨跌
- VIX 高于 40 时加仓
- 持有 3-5 年以上时间维度看待成长仓
- 分散到 8-12 个标的

**不该做的：**
- 追涨杀跌、频繁换仓
- 重仓单一标的超过 30%（有例外，NVDA 重仓）
- 被短期新闻情绪左右
- 投 A 股（Mike 明确反对）

### 风险提示（重要）

- Mike 是 **moomoo（富途）付费推广者**，部分内容有商业利益
- 最核心的实盘细节（精确仓位、买卖点）在**付费会员群**里
- 风格偏**激进成长型**，适合风险承受能力较高的投资者
- 对中国地缘风险持悲观态度，建议资产出海

---

## 技术栈偏好

- 开发方向：架构设计 + Full Stack
- 技术栈：FastAPI（Python）后端 + 原生 HTML/JS 前端 + SQLite（开发）/ PostgreSQL（生产）
- 服务入口：`/Users/nn/WorkBuddy/Claw/frontend/`，启动命令 `python start_dashboard.py`，端口 8000

## 已知问题与修复模式

### SPA 路由刷新问题（2026-03-31 修复）

**问题**：页面刷新后总是跳转到默认页面（投资总览），但地址栏URL保持不变

**根本原因**：路由初始化函数引用了未定义的路由映射变量

**修复模式**：
```javascript
// 错误方式：引用未定义的映射对象
function getHashPage() {
  const hash = location.hash.replace('#/', '').split('?')[0];
  return PAGE_TITLES[hash] ? hash : 'overview';  // PAGE_TITLES 未定义
}

// 正确方式：直接检查DOM元素
function getHashPage() {
  const hash = location.hash.replace('#/', '').split('?')[0];
  return document.getElementById('page-' + hash) ? hash : 'overview';
}
```

**应用场景**：单页应用（SPA）的浏览器刷新、前进/后退按钮

---

### JavaScript 变量未定义错误（2026-03-31 修复）

**问题**：期权持仓表格无法渲染，显示为空

**根本原因**：模板字符串中使用了未定义的变量 `pnlVal`，导致 JavaScript 运行时错误，阻止了后续代码执行

**错误示例**：
```javascript
// pnlVal 变量未定义
const pnl = isOpen ? (p.total_premium_received || 0) : (p.realized_pnl || 0);
const pnlColor = pnl >= 0 ? 'var(--success)' : 'var(--danger)';
// ...
${pnlVal>=0?'+':''}$${Math.abs(pnlVal).toFixed(2)}  // ❌ ReferenceError: pnlVal is not defined
```

**正确写法**：
```javascript
const pnl = isOpen ? (p.total_premium_received || 0) : (p.realized_pnl || 0);
const pnlColor = pnl >= 0 ? 'var(--success)' : 'var(--danger)';
// ...
${pnl>=0?'+':''}$${Math.abs(pnl).toFixed(2)}  // ✅ 使用正确的变量名
```

**调试方法**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 面板中的错误信息
3. 定位到具体行数和错误类型（ReferenceError）

**应用场景**：动态渲染表格、列表等复杂 DOM 结构时

---

### 后端生成内容的国际化（2026-03-31 修复）

**问题**：后端返回的中文文本在英文模式下仍显示中文

**根本原因**：后端API返回的文本是中文，前端缺少完整的翻译映射机制

**修复模式**：

#### 方案A：扩展翻译映射表
为后端返回的所有中文文本创建映射字典：
```javascript
const _healthTextMap = {
  '现金比例过高': 'health.txt.weaknessCashHigh',
  '科技股集中度过高': 'health.txt.weaknessTech',
  // ... 添加所有可能的中文文本
};

function translateHealthText(text) {
  const key = _healthTextMap[text];
  return key ? t(key, text) : text;
}
```

#### 方案B：TSLA页面的翻译实现
创建专门的TSLA内容翻译映射：
```javascript
const _tslaTextMap = {
  // 护城河
  '品牌与用户忠诚度': 'tsla.moatTitle1',
  '特斯拉车主复购率高达 70%...': 'tsla.moatDetail1',
  '全球电动车市占率 20%，美国 50%': 'tsla.moatData1',
  // ... 更多映射
};

function translateTslaText(text) {
  const key = _tslaTextMap[text];
  return key ? t(key, text) : text;
}
```

#### 方案C：更新渲染函数
在渲染时使用翻译函数：
```javascript
// 健康评估
h.strengths.forEach(s => {
  strEl.innerHTML += `<span>${translateHealthText(s)}</span>`;
});

// TSLA页面
grid.innerHTML = moat.map(m => `
  <span>${translateTslaText(m.title)}</span>
  <p>${translateTslaText(m.detail)}</p>
  <div>${translateTslaText(m.data_point)}</div>
`).join('');
```

**应用场景**：
- 后端返回的动态生成的文本内容
- 数据库中存储的多语言内容
- API返回的国际化数据

---

### i18n 国际化系统（2026-03-30 完成）

---

## 项目文档

- **PRD 产品需求文档**：`/Users/nn/WorkBuddy/Claw/CLAW_PRD.html`
  - 包含：产品概述、现有功能清单、18项功能缺口、竞品对比（Empower/Sharesight/Kubera/Delta）、4阶段路线图、上线方案
  - 生成时间：2026-03-24
- **Mike报告**：`/Users/nn/WorkBuddy/Claw/mike_investment_report.html` 和 `.pdf`

## i18n 国际化系统（2026-03-30 完成）

### 系统架构
- 翻译文件：`/Users/nn/WorkBuddy/Claw/frontend/i18n/en.json` 和 `zh.json`
- 核心库：`/Users/nn/WorkBuddy/Claw/frontend/i18n/i18n.js`
- 使用方式：
  - HTML: `data-i18n="key.path"` 属性
  - JavaScript: `t('key.path')` 函数

### 已知问题与修复模式
**问题1：硬编码中文文本**
- 现象：英文模式下仍显示中文
- 修复：添加 `data-i18n` 属性并补充翻译键到 en.json

**问题2：翻译键不一致**
- 现象：JavaScript使用 `options.ratio`，HTML期望 `dashboard.ratio`
- 修复：统一使用 `dashboard.ratio`（3处JS代码修复）

**问题3：缓存问题**
- 现象：修复后用户看到"未更改"
- 解决方案：必须清除浏览器缓存（Ctrl+Shift+R / Cmd+Shift+R）

### 最近修复汇总（2026-03-30）
1. **登录/注册页面**：补充 `clawLogin.*` 系列翻译键
2. **个人中心页面**：修复"算法解释"按钮、"账户统计"区域
3. **Dashboard页面**：修复现金比例显示、期权统计标签
4. **TSLA页面**：补充护城河描述翻译

---

## 已完成功能（2026-03-24）

- **TSLA综合情报模块**：护城河（7项）、业务前景（6项含风险）、Sell Put指南、收益计算器，4个Tab切换
  - 后端API：`GET /api/tsla/intel`（静态结构化知识库）
- **期权持仓功能**：
  - 数据库新增 `option_positions` 表（12个字段，含开仓/平仓/到期/行权状态）
  - 后端API：`GET/POST /api/options/positions`、`PATCH /api/options/positions/{id}/close`、`DELETE`、`GET /api/options/stats`
  - 前端：持仓管理页新增「期权持仓」Tab，支持开仓/平仓/到期归零/行权，实时盈亏预览
  - 计算逻辑：_calc_option_pnl 函数，支持sell/buy和closed/expired/assigned三种结束方式

---
