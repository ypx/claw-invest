# Claw 投资决策中心 · UI 设计系统

> 版本：v1.0  
> 创建日期：2026-03-24  
> 设计目标：为个人美股投资者打造专业、直观、可信赖的投资管理界面

---

## 🎨 设计概述

### 设计理念

Claw 的 UI 设计遵循 **"专业金融感 + 现代科技美学"** 的核心原则：

1. **信息密度适中** - 投资数据丰富但不杂乱，关键指标一目了然
2. **视觉层次分明** - 通过颜色、字号、间距建立清晰的信息层级
3. **即时反馈** - 所有交互操作都有明确的视觉反馈
4. **暗色优先** - 以深色主题为主，减少长时间盯盘的视觉疲劳
5. **响应式适配** - 手机、平板、桌面三端完美适配

### 用户画像

- **主用户**：个人美股投资者（保守型，长期持有）
- **使用场景**：每日查看持仓、分析盈亏、制定期权策略
- **技术背景**：无代码经验，习惯 Excel，需要直观的中文界面
- **设备偏好**：手机（随时查看）+ 电脑（深度分析）

---

## 🧩 设计令牌（Design Tokens）

### 色彩系统

#### 主色调（Brand Colors）

```css
/* 品牌渐变 - 用于 Logo、主按钮、重点强调 */
--brand-gradient: linear-gradient(135deg, #388bfd 0%, #a371f7 100%);

/* 主色 - 科技蓝 */
--primary-50:  #e6f0ff;
--primary-100: #cce0ff;
--primary-200: #99c2ff;
--primary-300: #66a3ff;
--primary-400: #3385ff;
--primary-500: #388bfd;  /* 主色 */
--primary-600: #2a6fd4;
--primary-700: #1f53aa;
--primary-800: #153880;
--primary-900: #0a1c55;

/* 辅助色 - 紫罗兰 */
--secondary-500: #a371f7;
--secondary-600: #8b5cf6;
```

#### 功能色（Semantic Colors）

```css
/* 成功/上涨 - 中国红（A股习惯）*/
--success-500: #f85149;
--success-100: rgba(248, 81, 73, 0.1);
--success-border: rgba(248, 81, 73, 0.3);

/* 下跌/危险 - 绿色 */
--danger-500: #3fb950;
--danger-100: rgba(63, 185, 80, 0.1);
--danger-border: rgba(63, 185, 80, 0.3);

/* 警告 - 琥珀 */
--warning-500: #d29922;
--warning-100: rgba(210, 153, 34, 0.1);
--warning-border: rgba(210, 153, 34, 0.3);

/* 信息 - 天蓝 */
--info-500: #58a6ff;
--info-100: rgba(88, 166, 255, 0.1);
--info-border: rgba(88, 166, 255, 0.3);
```

#### 中性色（Neutral Colors）

```css
/* 背景色 */
--bg-page:      #0d1117;  /* 页面背景 - 深邃黑 */
--bg-sidebar:   #161b22;  /* 侧边栏背景 */
--bg-card:      #161b22;  /* 卡片背景 */
--bg-card2:     #1c2230;  /* 卡片悬停/次级背景 */
--bg-hover:     #21262d;  /* 悬停状态 */
--bg-input:     #0d1117;  /* 输入框背景 */

/* 边框色 */
--border:       #30363d;  /* 主边框 */
--border-light: #21262d;  /* 浅色边框 */
--border-focus: #388bfd;  /* 聚焦边框 */

/* 文字色 */
--text-primary:   #e6edf3;  /* 主文字 */
--text-secondary: #c9d1d9;  /* 次级文字 */
--text-muted:     #7d8590;  /* 辅助文字 */
--text-dim:       #484f58;  /* 禁用/占位文字 */
--text-inverse:   #0d1117;  /* 反色文字（用于按钮）*/
```

#### 行业分类色

```css
/* 用于行业分布饼图 */
--sector-tech:     #388bfd;  /* 科技 - 蓝 */
--sector-finance:  #a371f7;  /* 金融 - 紫 */
--sector-health:   #f85149;  /* 医疗 - 红 */
--sector-consumer: #3fb950;  /* 消费 - 绿 */
--sector-energy:   #d29922;  /* 能源 - 黄 */
--sector-industry: #f0883e;  /* 工业 - 橙 */
--sector-others:   #7d8590;  /* 其他 - 灰 */
```

### 字体系统

#### 字体族

```css
/* 主字体 - 系统字体栈，确保跨平台一致性 */
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;

/* 数字/等宽 - 用于价格、百分比显示 */
--font-mono: 'SF Mono', 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
```

#### 字号比例（Type Scale）

| 层级 | 名称 | 大小 | 字重 | 行高 | 用途 |
|------|------|------|------|------|------|
| H1 | 页面标题 | 24px | 700 | 1.3 | 页面主标题 |
| H2 | 区块标题 | 18px | 600 | 1.4 | 区块标题 |
| H3 | 卡片标题 | 15px | 600 | 1.4 | 卡片标题 |
| H4 | 小标题 | 13px | 600 | 1.5 | 列表标题 |
| Body | 正文 | 14px | 400 | 1.6 | 普通文本 |
| Small | 小字 | 12px | 400 | 1.5 | 辅助说明 |
| XSmall | 超小 | 11px | 500 | 1.4 | 标签、徽章 |
| Tiny | 极小 | 10px | 600 | 1.3 | 微标签 |

```css
/* CSS 变量定义 */
--text-h1: 700 24px/1.3 var(--font-primary);
--text-h2: 600 18px/1.4 var(--font-primary);
--text-h3: 600 15px/1.4 var(--font-primary);
--text-h4: 600 13px/1.5 var(--font-primary);
--text-body: 400 14px/1.6 var(--font-primary);
--text-small: 400 12px/1.5 var(--font-primary);
--text-xsmall: 500 11px/1.4 var(--font-primary);
--text-tiny: 600 10px/1.3 var(--font-primary);
```

### 间距系统

#### 基础单位：4px

```css
--space-0:  0;
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

#### 组件间距规范

| 场景 | 间距值 | 说明 |
|------|--------|------|
| 卡片内边距 | 16px - 20px | 根据卡片大小调整 |
| 卡片间隙 | 16px | grid/flex gap |
| 表单元素间距 | 16px | 表单项之间 |
| 按钮内边距 | 8px 16px | 标准按钮 |
| 按钮间隙 | 8px | 按钮组之间 |
| 列表项间距 | 8px | 列表项之间 |
| 区块间距 | 24px | 大区块之间 |

### 圆角系统

```css
--radius-none: 0;
--radius-sm:   4px;   /* 小标签、徽章 */
--radius-md:   6px;   /* 按钮、输入框 */
--radius-lg:   8px;   /* 卡片、弹窗 */
--radius-xl:   10px;  /* 大卡片、模态框 */
--radius-2xl:  12px;  /* 特殊容器 */
--radius-full: 9999px; /* 圆形、胶囊 */
```

### 阴影系统

```css
/* 暗色主题下的阴影（使用亮色叠加模拟） */
--shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md:  0 4px 6px rgba(0, 0, 0, 0.4);
--shadow-lg:  0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-xl:  0 20px 25px rgba(0, 0, 0, 0.6);

/* 光晕效果 - 用于强调 */
--glow-blue:  0 0 20px rgba(56, 139, 253, 0.3);
--glow-green: 0 0 20px rgba(63, 185, 80, 0.3);
--glow-red:   0 0 20px rgba(248, 81, 73, 0.3);
```

### 过渡动画

```css
/* 时长 */
--duration-fast:   150ms;  /* 悬停、焦点 */
--duration-normal: 200ms;  /* 按钮点击、展开 */
--duration-slow:   300ms;  /* 页面切换、模态框 */

/* 缓动函数 */
--ease-default:   cubic-bezier(0.4, 0, 0.2, 1);
--ease-in:        cubic-bezier(0.4, 0, 1, 1);
--ease-out:       cubic-bezier(0, 0, 0.2, 1);
--ease-bounce:    cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* 预设 */
--transition-fast:   all var(--duration-fast) var(--ease-default);
--transition-normal: all var(--duration-normal) var(--ease-default);
--transition-slow:   all var(--duration-slow) var(--ease-default);
```

---

## 🧱 组件库规范

### 1. 按钮（Button）

#### 变体

| 变体 | 背景 | 文字 | 边框 | 用途 |
|------|------|------|------|------|
| Primary | 品牌渐变 | 白色 | 无 | 主要操作 |
| Secondary | transparent | 主色 | 1px 主色 | 次要操作 |
| Ghost | transparent | 文字色 | 无 | 低优先级 |
| Danger | danger-100 | danger-500 | danger-border | 删除、危险操作 |

#### 尺寸

| 尺寸 | 高度 | 内边距 | 字号 | 用途 |
|------|------|--------|------|------|
| Small | 28px | 6px 12px | 12px | 紧凑空间 |
| Medium | 36px | 8px 16px | 14px | 标准按钮 |
| Large | 44px | 12px 24px | 15px | 强调操作 |

#### 状态样式

```css
/* 悬停 */
.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* 点击 */
.btn:active {
  transform: scale(0.98);
}

/* 禁用 */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 聚焦 */
.btn:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### 2. 卡片（Card）

#### 基础样式

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: var(--space-4) var(--space-5);
  transition: var(--transition-fast);
}

.card:hover {
  border-color: var(--border-light);
  box-shadow: var(--shadow-md);
}
```

#### 变体

| 变体 | 背景 | 边框 | 用途 |
|------|------|------|------|
| Default | bg-card | border | 标准卡片 |
| Elevated | bg-card | border-light | 强调卡片（带阴影）|
| Interactive | bg-card | border | 可点击卡片（悬停效果更强）|
| Highlight | bg-card2 | border | 高亮卡片 |

#### 卡片内容结构

```
┌─────────────────────────────┐
│ [图标] 卡片标题          [操作] │  ← Header（可选）
├─────────────────────────────┤
│                             │
│        主要内容区域          │  ← Body
│                             │
├─────────────────────────────┤
│ 辅助信息/底部操作            │  ← Footer（可选）
└─────────────────────────────┘
```

### 3. 输入框（Input）

#### 基础样式

```css
.input {
  width: 100%;
  height: 40px;
  padding: 8px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 14px;
  transition: var(--transition-fast);
}

.input:hover {
  border-color: var(--border-light);
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(56, 139, 253, 0.1);
}

.input::placeholder {
  color: var(--text-dim);
}
```

#### 带图标的输入框

```
┌─────────────────────────────┐
│ 👤 输入内容            [图标] │
└─────────────────────────────┘
```

### 4. 表格（Table）

#### 样式规范

```css
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.table th {
  background: var(--bg-card2);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
}

.table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.table tr:last-child td {
  border-bottom: none;
}
```

### 5. 徽章（Badge）

#### 变体

| 变体 | 背景 | 文字 | 用途 |
|------|------|------|------|
| Default | bg-card2 | text-muted | 默认状态 |
| Primary | primary-100 | primary-500 | 主色强调 |
| Success | success-100 | success-500 | 上涨/成功 |
| Danger | danger-100 | danger-500 | 下跌/危险 |
| Warning | warning-100 | warning-500 | 警告 |

#### 样式

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
}

.badge-success {
  background: var(--success-100);
  color: var(--success-500);
  border-color: var(--success-border);
}
```

### 6. 导航（Navigation）

#### 侧边栏导航项

```css
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  transition: var(--transition-fast);
  cursor: pointer;
  position: relative;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(56, 139, 253, 0.1);
  color: var(--primary-500);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 3px;
  background: var(--primary-500);
  border-radius: 0 2px 2px 0;
}
```

### 7. 数据指标卡片（Metric Card）

#### 结构

```
┌─────────────────────────────┐
│ 指标名称                     │  ← Label（11px 大写）
│ $125,680.50                 │  ← Value（26px 粗体）
│ ▲ +5.2% 较上月              │  ← Change（带趋势图标）
└─────────────────────────────┘
```

#### 样式

```css
.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.metric-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.metric-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-change.up {
  color: var(--success-500);
}

.metric-change.down {
  color: var(--danger-500);
}
```

### 8. 标签页（Tabs）

#### 样式

```css
.tabs {
  display: flex;
  background: var(--bg-page);
  border-radius: var(--radius-md);
  padding: 3px;
  gap: 3px;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  transition: var(--transition-fast);
}

.tab:hover {
  color: var(--text-primary);
}

.tab.active {
  background: var(--bg-card);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
```

### 9. 提示框（Alert/Toast）

#### 变体

| 类型 | 图标 | 边框色 | 背景色 | 用途 |
|------|------|--------|--------|------|
| Info | ℹ️ | info-border | info-100 | 普通信息 |
| Success | ✓ | success-border | success-100 | 操作成功 |
| Warning | ⚠️ | warning-border | warning-100 | 警告提示 |
| Error | ✕ | danger-border | danger-100 | 错误提示 |

#### 样式

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  font-size: 13px;
  border: 1px solid;
}

.alert-info {
  background: var(--info-100);
  border-color: var(--info-border);
  color: var(--info-500);
}

.alert-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 1px;
}
```

### 10. 模态框（Modal）

#### 结构

```
┌─────────────────────────────────────────┐
│ 模态框标题                         [×]  │  ← Header
├─────────────────────────────────────────┤
│                                         │
│              内容区域                    │  ← Body
│                                         │
├─────────────────────────────────────────┤
│          [取消]        [确认]           │  ← Footer
└─────────────────────────────────────────┘
```

#### 样式

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: var(--shadow-xl);
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
```

---

## 📐 布局系统

### 页面结构

```
┌─────────────────────────────────────────────────────────────┐
│  [≡]  Claw              市场数据          [🔔] [👤] [⚙️]     │  ← Topbar (56px)
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  导航     │              主内容区域                          │
│  (220px) │                                                  │
│          │                                                  │
│          │                                                  │
│  用户     │                                                  │
│  信息     │                                                  │
│          │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

### 栅格系统

```css
/* 12 列栅格 */
.grid { display: grid; gap: 16px; }
.grid-1  { grid-template-columns: repeat(1, 1fr); }
.grid-2  { grid-template-columns: repeat(2, 1fr); }
.grid-3  { grid-template-columns: repeat(3, 1fr); }
.grid-4  { grid-template-columns: repeat(4, 1fr); }
.grid-6  { grid-template-columns: repeat(6, 1fr); }
.grid-12 { grid-template-columns: repeat(12, 1fr); }

/* 响应式 */
@media (max-width: 1024px) {
  .grid-lg-2 { grid-template-columns: repeat(2, 1fr); }
  .grid-lg-1 { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .grid-md-1 { grid-template-columns: 1fr; }
  .grid-md-2 { grid-template-columns: repeat(2, 1fr); }
}
```

### 响应式断点

| 断点 | 宽度 | 设备类型 | 侧边栏 | 布局调整 |
|------|------|----------|--------|----------|
| Mobile | < 640px | 手机 | 隐藏（汉堡菜单）| 单列布局 |
| Tablet | 640px - 1023px | 平板 | 隐藏（抽屉式）| 2列网格 |
| Desktop | 1024px - 1279px | 桌面 | 显示 | 3-4列网格 |
| Large | ≥ 1280px | 大屏 | 显示 | 4列网格 |

---

## 🎯 界面设计原则

### 1. 信息层级

使用 **字体大小 + 颜色对比 + 间距** 建立清晰的视觉层级：

- **一级信息**：24px 粗体，主文字色（总资产、主要盈亏）
- **二级信息**：16-18px 中等字重，次文字色（持仓名称、指标名称）
- **三级信息**：13-14px 常规，辅助文字色（详细数据、说明）
- **四级信息**：11-12px，弱化文字色（时间戳、标签）

### 2. 色彩语义

- **红色（#f85149）** = 上涨、盈利、买入（符合中国投资者习惯）
- **绿色（#3fb950）** = 下跌、亏损、卖出
- **蓝色（#388bfd）** = 主操作、链接、信息
- **黄色（#d29922）** = 警告、注意、待处理

### 3. 数据展示规范

#### 金额显示

```
$125,680.50      ← 大金额，保留两位小数
$1,234.56        ← 常规金额
$0.00            ← 零值
—                ← 无数据/加载中
```

#### 百分比显示

```
+15.32%          ← 上涨（红色）
-8.45%           ← 下跌（绿色）
0.00%            ← 持平（灰色）
```

#### 价格显示

```
$185.42          ← 美股价格
0.0523 BTC       ← 加密货币
```

### 4. 空状态设计

当没有数据时，显示友好的空状态：

```
┌─────────────────────────────┐
│                             │
│         [插图图标]          │
│                             │
│      暂无持仓记录           │
│   点击添加你的第一笔持仓     │
│                             │
│      [+ 添加持仓]           │
│                             │
└─────────────────────────────┘
```

### 5. 加载状态

- **骨架屏**：用于卡片、列表的初始加载
- **旋转器**：用于按钮操作、小范围刷新
- **进度条**：用于文件上传、批量操作

---

## ♿ 可访问性规范

### 色彩对比度

- 文字与背景对比度 ≥ 4.5:1（符合 WCAG AA）
- 大号文字（≥18px 粗体）对比度 ≥ 3:1

### 焦点管理

```css
/* 所有可交互元素必须有焦点样式 */
:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
}
```

### 触摸目标

- 移动端最小触摸目标：44px × 44px
- 按钮、链接、图标按钮需满足此尺寸

### 动画偏好

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 📱 响应式适配

### 移动端适配要点

1. **侧边栏隐藏**：使用汉堡菜单触发抽屉式导航
2. **卡片堆叠**：4列 → 2列 → 1列
3. **表格横向滚动**：保持表格完整，容器可滚动
4. **底部固定操作**：重要按钮固定在屏幕底部
5. **字体微调**：标题字号适当缩小，保持可读性

### 移动端布局示例

```
┌─────────────────────────────┐
│ [≡] Claw              [👤]  │
├─────────────────────────────┤
│                             │
│      资产总览卡片            │
│                             │
├─────────────────────────────┤
│ 指标1    │    指标2         │
├──────────┼──────────────────┤
│ 指标3    │    指标4         │
├─────────────────────────────┤
│                             │
│      持仓列表               │
│                             │
├─────────────────────────────┤
│      [+ 添加持仓]           │  ← 底部固定
└─────────────────────────────┘
```

---

## 🚀 实施建议

### 优先级

1. **P0 - 核心样式**：颜色、字体、间距令牌 → 按钮、卡片、输入框
2. **P1 - 组件完善**：表格、徽章、导航、标签页
3. **P2 - 高级组件**：模态框、图表、数据可视化

### 代码组织

```
frontend/
├── styles/
│   ├── tokens.css      # 设计令牌
│   ├── components.css  # 组件样式
│   ├── layout.css      # 布局系统
│   └── utilities.css   # 工具类
├── components/
│   ├── Button.js
│   ├── Card.js
│   ├── Input.js
│   └── ...
└── pages/
    └── ...
```

### 与现有代码整合

当前 `claw_dashboard_enhanced.html` 已使用类似的暗色主题，建议：

1. 将现有 CSS 变量替换为设计令牌
2. 统一组件样式，确保一致性
3. 逐步迁移页面到新的设计系统

---

## 📋 设计检查清单

### 视觉一致性

- [ ] 所有颜色使用设计令牌
- [ ] 字体大小符合类型比例
- [ ] 间距使用 4px 倍数
- [ ] 圆角符合规范
- [ ] 阴影/光晕效果一致

### 交互体验

- [ ] 所有可点击元素有悬停效果
- [ ] 焦点状态清晰可见
- [ ] 加载状态有反馈
- [ ] 错误状态有提示
- [ ] 空状态有引导

### 响应式

- [ ] 移动端布局正确
- [ ] 触摸目标 ≥ 44px
- [ ] 文字大小可读（≥12px）
- [ ] 表格可横向滚动
- [ ] 图片自适应

### 可访问性

- [ ] 色彩对比度 ≥ 4.5:1
- [ ] 支持键盘导航
- [ ] 图片有 alt 文本
- [ ] 表单有关联标签
- [ ] 尊重减少动画偏好

---

*本文档由 UI 设计师创建，用于指导 Claw 投资决策中心的界面开发。*
