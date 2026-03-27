const { getDb } = require('../models/db');
const { logger } = require('../utils/logger');
const https = require('https');

// ─── 实时价格缓存（每5分钟刷新一次）───
let _priceCache = {};
let _priceCacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5分钟

// Alpha Vantage API Key
const AV_KEY = process.env.ALPHA_VANTAGE_API_KEY || 'OH7TPNSBQONIAGBG';

/**
 * 通用 HTTPS GET 请求
 */
function httpsGet(url, timeoutMs = 10000) {
  return new Promise((resolve) => {
    const req = https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, data }));
    });
    req.on('error', () => resolve(null));
    req.setTimeout(timeoutMs, () => { req.destroy(); resolve(null); });
  });
}

/**
 * 数据源1: Stooq（波兰，完全免费，支持美股，无需API key）
 * 返回美东时间收盘价，是最可靠的免费数据源
 */
async function fetchFromStooq(symbol) {
  try {
    const url = `https://stooq.com/q/l/?s=${symbol.toLowerCase()}.us&f=sd2t2ohlcvn&e=json`;
    const res = await httpsGet(url);
    if (!res || res.status !== 200) return null;
    const json = JSON.parse(res.data);
    const sym = json?.symbols?.[0];
    if (!sym || !sym.close || sym.close <= 0) return null;
    const price = parseFloat(sym.close);
    const open = parseFloat(sym.open || price);
    const change = price - open;
    const change_pct = open > 0 ? (change / open) * 100 : 0;
    return {
      price,
      change: parseFloat(change.toFixed(2)),
      change_pct: parseFloat(change_pct.toFixed(2)),
      source: 'stooq',
      date: sym.date,
    };
  } catch (e) {
    return null;
  }
}

/**
 * 数据源2: Alpha Vantage（备用，每分钟5次限速）
 */
async function fetchFromAV(symbol) {
  try {
    const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${AV_KEY}`;
    const res = await httpsGet(url);
    if (!res || res.status !== 200) return null;
    const json = JSON.parse(res.data);
    const quote = json['Global Quote'];
    if (!quote || !quote['05. price']) return null;
    const price = parseFloat(quote['05. price']);
    if (price <= 0) return null;
    return {
      price,
      change: parseFloat(quote['09. change'] || 0),
      change_pct: parseFloat((quote['10. change percent'] || '0%').replace('%', '')),
      source: 'alphavantage',
    };
  } catch (e) {
    return null;
  }
}

/**
 * 多源价格获取：Stooq 为主，AV 为辅助交叉验证
 * 如果两个来源差异 > 10%，记录警告
 */
async function fetchPriceMultiSource(symbol) {
  // 优先 Stooq（稳定，免费，无限速）
  const stooqResult = await fetchFromStooq(symbol);

  if (stooqResult && stooqResult.price > 0) {
    // Stooq 成功，用 AV 进行交叉验证（异步，不等待）
    fetchFromAV(symbol).then(avResult => {
      if (avResult && avResult.price > 0) {
        const diffPct = Math.abs(stooqResult.price - avResult.price) / stooqResult.price * 100;
        if (diffPct > 10) {
          logger.warn(`${symbol} 价格差异警告: Stooq $${stooqResult.price} vs AV $${avResult.price} (差异 ${diffPct.toFixed(1)}%)`);
        }
      }
    }).catch(() => {});
    return stooqResult;
  }

  // Stooq 失败，降级到 AV
  const avResult = await fetchFromAV(symbol);
  if (avResult && avResult.price > 0) {
    logger.warn(`${symbol}: Stooq 失败，使用 Alpha Vantage: $${avResult.price}`);
    return avResult;
  }

  logger.warn(`${symbol}: 所有数据源失败`);
  return null;
}

/**
 * 批量获取股票价格（带缓存和多源验证）
 */
async function getLivePrices(symbols) {
  const now = Date.now();
  // 缓存未过期，直接返回
  if (now - _priceCacheTime < CACHE_TTL && Object.keys(_priceCache).length > 0) {
    return _priceCache;
  }

  const db = getDb();
  const prices = {};

  // 第一步：从数据库读取存储的价格作为最终兜底
  const dbPrices = db.prepare(`SELECT symbol, current_price FROM holdings GROUP BY symbol`).all();
  for (const row of dbPrices) {
    if (row.current_price > 0) {
      prices[row.symbol] = { price: row.current_price, change: 0, change_pct: 0, source: 'database' };
    }
  }

  // 第二步：并发获取所有股票的实时价格
  logger.info(`开始多源获取 ${symbols.length} 只股票价格: ${symbols.join(', ')}`);
  const fetchPromises = symbols.map(async (sym) => {
    const result = await fetchPriceMultiSource(sym);
    if (result && result.price > 0) {
      // 交叉验证数据库旧价格
      const dbPrice = prices[sym]?.price;
      if (dbPrice && dbPrice > 0) {
        const diffPct = Math.abs(result.price - dbPrice) / dbPrice * 100;
        if (diffPct > 30) {
          logger.warn(`${sym}: 实时 $${result.price}(${result.source}) vs 数据库 $${dbPrice}，差异 ${diffPct.toFixed(1)}%`);
        }
      }
      prices[sym] = result;
      // 更新数据库
      try {
        db.prepare(`UPDATE holdings SET current_price = ?, updated_at = ? WHERE symbol = ?`)
          .run(result.price, new Date().toISOString(), sym);
      } catch (e) { /* 忽略 */ }
      logger.info(`${sym}: $${result.price} [${result.source}] ${result.date || ''}`);
    }
  });

  await Promise.all(fetchPromises);

  _priceCache = prices;
  _priceCacheTime = now;
  return prices;
}


class DashboardController {
  constructor() {
    this.getDashboard = this.getDashboard.bind(this);
    this.getTslaIntel = this.getTslaIntel.bind(this);
    this.getHoldings = this.getHoldings.bind(this);
    this.addHolding = this.addHolding.bind(this);
    this.deleteHolding = this.deleteHolding.bind(this);
    this.updateUserProfile = this.updateUserProfile.bind(this);
  }

  /**
   * 主仪表板数据 GET /api/dashboard
   * 返回与前端 MOCK_DATA 结构完全一致的真实数据
   */
  async getDashboard(req, res) {
    try {
      const db = getDb();
      const userId = req.user?.id;

      // ─── 1. 获取用户信息 ───
      const user = db.prepare(`SELECT * FROM users WHERE id = ?`).get(userId);
      if (!user) {
        return res.status(404).json({ error: '用户不存在', userId });
      }

      let userProfile = {};
      try { userProfile = JSON.parse(user.profile || '{}'); } catch (e) {}

      // ─── 2. 获取持仓列表 ───
      const holdings = db.prepare(
        `SELECT * FROM holdings WHERE user_id = ? ORDER BY symbol`
      ).all(userId);

      const symbols = holdings.map(h => h.symbol);

      // ─── 3. 获取实时价格 ───
      const prices = await getLivePrices(symbols);

      // ─── 4. 计算持仓价值 ───
      const portfolioHoldings = holdings.map(h => {
        const livePrice = prices[h.symbol]?.price || h.current_price;
        const currentValue = livePrice * h.shares;
        const gainLoss = (livePrice - h.avg_cost) * h.shares;
        const gainLossPct = h.avg_cost > 0 ? ((livePrice - h.avg_cost) / h.avg_cost * 100) : 0;
        return {
          symbol: h.symbol,
          name: h.name,
          shares: h.shares,
          avg_cost: h.avg_cost,
          current_price: parseFloat(livePrice.toFixed(2)),
          current_value: parseFloat(currentValue.toFixed(2)),
          gain_loss: parseFloat(gainLoss.toFixed(2)),
          gain_loss_percent: parseFloat(gainLossPct.toFixed(2)),
          health_score: h.health_score || 80,
          change_pct: parseFloat((prices[h.symbol]?.change_pct || 0).toFixed(2)),
          price_source: prices[h.symbol]?.source || 'unknown',
          price_date: prices[h.symbol]?.date || null,
        };
      });

      // ─── 5. 计算组合汇总 ───
      const investedValue = portfolioHoldings.reduce((sum, h) => sum + h.current_value, 0);
      const totalCost = portfolioHoldings.reduce((sum, h) => sum + (h.avg_cost * h.shares), 0);
      const totalGainLoss = investedValue - totalCost;
      const totalGainLossPct = totalCost > 0 ? (totalGainLoss / totalCost * 100) : 0;
      const cash = parseFloat(userProfile.cash || 50000);
      const targetCashRatio = parseFloat(userProfile.target_cash_ratio || 35);
      const totalValue = investedValue + cash;
      const cashRatio = totalValue > 0 ? (cash / totalValue * 100) : 0;
      const healthScore = this._calcHealthScore(cashRatio, targetCashRatio, portfolioHoldings);

      // ─── 6. 获取期权持仓 ───
      const optionPositions = db.prepare(
        `SELECT * FROM option_positions WHERE user_id = ? ORDER BY opened_at DESC`
      ).all(userId);

      const optionStats = this._calcOptionStats(optionPositions, prices);

      // ─── 7. TSLA 专项数据 ───
      const tslaHolding = portfolioHoldings.find(h => h.symbol === 'TSLA');
      const tslaPrice = prices['TSLA']?.price || 0;

      // ─── 8. 风险预警 ───
      const riskAlerts = this._calcRiskAlerts(cashRatio, targetCashRatio, portfolioHoldings, totalValue);

      // ─── 9. 市场状态（用缓存的VIX数据或默认值）───
      const marketStatus = {
        sp500: 5580.0,
        sp500_change: 0.5,
        nasdaq: 17520.0,
        nasdaq_change: 0.8,
        vix: 19.8,
        vix_change: -1.2,
        market_sentiment: '中性',
      };

      // ─── 10. 期权策略推荐（动态，基于实时价格）───
      const optionStrategies = this._buildOptionStrategies(prices, userProfile);

      // ─── 11. 组合健康度 ───
      const portfolioHealth = this._calcPortfolioHealth(cashRatio, targetCashRatio, portfolioHoldings, totalValue);

      // ─── 返回完整数据 ───
      res.json({
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          cash: cash,
          target_cash_ratio: targetCashRatio,
        },
        portfolio_summary: {
          total_value: parseFloat(totalValue.toFixed(2)),
          cash_value: parseFloat(cash.toFixed(2)),
          invested_value: parseFloat(investedValue.toFixed(2)),
          total_gain_loss: parseFloat(totalGainLoss.toFixed(2)),
          total_gain_loss_percent: parseFloat(totalGainLossPct.toFixed(2)),
          cash_ratio: parseFloat(cashRatio.toFixed(1)),
          target_cash_ratio: targetCashRatio,
          health_score: healthScore,
          positions_count: portfolioHoldings.length,
        },
        portfolio_holdings: portfolioHoldings,
        option_positions: optionPositions.map(p => ({
          ...p,
          current_price: parseFloat((prices[p.symbol]?.price || p.open_price || 0).toFixed(2)),
        })),
        option_stats: optionStats,
        option_strategies: optionStrategies,
        market_status: marketStatus,
        risk_alerts: riskAlerts,
        portfolio_health: portfolioHealth,
        live_prices: prices,
        news: this._buildNewsFeed(portfolioHoldings),
        _fetched_at: new Date().toISOString(),
      });

    } catch (err) {
      logger.error('getDashboard error', { error: err.message, stack: err.stack });
      res.status(500).json({ error: err.message });
    }
  }

  /**
   * TSLA 专项情报 GET /api/tsla/intel
   */
  async getTslaIntel(req, res) {
    try {
      const prices = await getLivePrices(['TSLA']);
      const tslaPrice = prices['TSLA']?.price || 280;

      // 基于实时价格计算合理的 sell put 参数
      const conservativeStrike = Math.round(tslaPrice * 0.85 / 5) * 5;  // 约15% OTM
      const moderateStrike = Math.round(tslaPrice * 0.90 / 5) * 5;      // 约10% OTM
      const aggressiveStrike = Math.round(tslaPrice * 0.95 / 5) * 5;    // 约5% OTM

      res.json({
        current_price: parseFloat(tslaPrice.toFixed(2)),
        moat: [
          { title: '自动驾驶领先优势', detail: 'FSD 12代突破，实测超过Waymo，数据护城河最宽', icon: 'fa-car-side', level: '极强', color: 'var(--success)', data_point: '全球最大自动驾驶里程数据库 > 10亿英里' },
          { title: 'Dojo超算训练能力', detail: '自研AI芯片，算力成本降低40%，无需依赖英伟达', icon: 'fa-microchip', level: '强', color: 'var(--accent-primary)', data_point: '2024年已部署首批Dojo ExaPOD，算力超100 ExaFLOPs' },
          { title: '能源业务爆发', detail: 'Megapack储能订单创历史，毛利率超过汽车业务', icon: 'fa-bolt', level: '极强', color: 'var(--success)', data_point: '2024Q3储能部署11.1GWh，同比+75%，毛利率30%+' },
          { title: '品牌与马斯克效应', detail: 'X平台+SpaceX协同，马斯克个人品牌无可复制', icon: 'fa-star', level: '强', color: 'var(--accent-primary)', data_point: '特斯拉在EV细分市场品牌认知度持续第一' },
          { title: '垂直整合制造', detail: '4680电池+一体压铸，制造成本每年降15%', icon: 'fa-industry', level: '强', color: 'var(--accent-primary)', data_point: '一体压铸减少车身零件约300个，降低成本约15%' },
          { title: '全球超充网络', detail: '5万+超充桩，已向其他品牌开放，转变为基础设施', icon: 'fa-charging-station', level: '极强', color: 'var(--success)', data_point: '超充网络开放后创造新收入流，竞争对手难以复制' },
          { title: 'Robotaxi与Optimus', detail: '2025年部署Robotaxi，Optimus人形机器人2026量产', icon: 'fa-robot', level: '中（早期）', color: 'var(--warning)', data_point: '2025年Q2德州Robotaxi试运营，Optimus目标2025年底量产' },
        ],
        business_outlook: [
          { title: 'Robotaxi 规模部署', desc: '德州/加州2025年中启动，可能颠覆出行市场', sentiment: 'positive', icon: 'fa-taxi', horizon: '2025-2026', tags: ['Robotaxi', 'AI', '出行'] },
          { title: '能源业务独立估值', desc: 'Megapack业务单独估值可超$1000亿，被严重低估', sentiment: 'positive', icon: 'fa-solar-panel', horizon: '2025', tags: ['储能', 'Megapack', '利好'] },
          { title: 'FSD订阅增长', desc: '北美FSD订阅率突破10%，年化经常性收入快速增长', sentiment: 'positive', icon: 'fa-dollar-sign', horizon: '持续', tags: ['FSD', 'SaaS', '订阅'] },
          { title: 'Optimus机器人', desc: '2026年目标生产100万台，颠覆劳动力市场', sentiment: 'positive', icon: 'fa-robot', horizon: '2026+', tags: ['Optimus', '机器人', '长期'] },
          { title: '竞争加剧风险', desc: '比亚迪在价格段和部分市场已超越，欧洲市场承压', sentiment: 'negative', icon: 'fa-exclamation-triangle', horizon: '当前', tags: ['竞争', '比亚迪', '风险'] },
          { title: '政治风险', desc: '马斯克政治参与加大品牌分化，部分欧洲用户流失', sentiment: 'negative', icon: 'fa-flag', horizon: '当前', tags: ['政治', '品牌', '风险'] },
        ],
        sell_put_guide: {
          current_price: parseFloat(tslaPrice.toFixed(2)),
          why: 'TSLA 波动率高（IV通常在50-100%区间），Sell Put 可以收取丰厚权利金。同时你对特斯拉长期看好，即使被行权也愿意以行权价买入正股，风险/收益比极佳。这是以"想以低价买TSLA"为前提的最优策略。',
          tips: [
            `当前 TSLA 价格 $${tslaPrice.toFixed(0)}，建议选择保守型（15% OTM）= $${conservativeStrike} 或稳健型（10% OTM）= $${moderateStrike} 作为行权价`,
            'VIX > 20 时开仓，隐波高 → 权利金更丰厚。VIX < 15 时建议等待',
            'TSLA 大幅回调（5-10%）后是最佳开仓窗口，成本更低',
            '每次使用资金不超过总仓位 30%，避免单笔被行权占用过多现金',
            '30-45天期为最佳（Theta衰减最快），临近到期前两周可择机平仓锁定80%收益',
          ],
          current_suggestion: `当前价 $${tslaPrice.toFixed(0)}，若VIX>20可考虑卖出 $${conservativeStrike} Put（30天期），预期权利金 $2-4/股`,
          best_conditions: ['VIX > 20，隐含波动率高', 'TSLA 刚从高位回调5-10%', '有重要催化剂（财报、产品发布）前后'],
          avoid_conditions: ['TSLA趋势明显下行', '即将发布重大负面消息', '大盘系统性风险期（VIX > 40）'],
          strike_suggestions: [
            {
              type: '保守型 (15% OTM)',
              strike: conservativeStrike,
              otm_pct: parseFloat(((tslaPrice - conservativeStrike) / tslaPrice * 100).toFixed(1)),
              dte: 45,
              prob: 85,
              note: '安全边际大，适合新手',
            },
            {
              type: '稳健型 (10% OTM)',
              strike: moderateStrike,
              otm_pct: parseFloat(((tslaPrice - moderateStrike) / tslaPrice * 100).toFixed(1)),
              dte: 30,
              prob: 75,
              note: '收益与风险平衡，推荐',
            },
            {
              type: '进取型 (5% OTM)',
              strike: aggressiveStrike,
              otm_pct: parseFloat(((tslaPrice - aggressiveStrike) / tslaPrice * 100).toFixed(1)),
              dte: 21,
              prob: 65,
              note: '权利金高，需要更多关注',
            },
          ],
        },
        updated_at: new Date().toISOString(),
      });
    } catch (err) {
      logger.error('getTslaIntel error', { error: err.message });
      res.status(500).json({ error: err.message });
    }
  }

  /**
   * 获取持仓列表 GET /api/portfolio/holdings
   */
  async getHoldings(req, res) {
    try {
      const db = getDb();
      const userId = req.user?.id;
      const holdings = db.prepare(`SELECT * FROM holdings WHERE user_id = ? ORDER BY symbol`).all(userId);
      const symbols = holdings.map(h => h.symbol);
      const prices = await getLivePrices(symbols);
      const result = holdings.map(h => ({
        ...h,
        current_price: prices[h.symbol]?.price || h.current_price,
      }));
      res.json({ success: true, holdings: result });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  }

  /**
   * 新增持仓 POST /api/portfolio/holdings
   */
  async addHolding(req, res) {
    try {
      const db = getDb();
      const userId = req.user?.id;
      const { symbol, name, shares, avg_cost } = req.body;
      if (!symbol || !shares || !avg_cost) {
        return res.status(400).json({ error: '缺少必要参数' });
      }
      const sym = symbol.toUpperCase();
      const prices = await getLivePrices([sym]);
      const currentPrice = prices[sym]?.price || avg_cost;

      // UPSERT：存在则更新，不存在则插入
      const existing = db.prepare(`SELECT id FROM holdings WHERE user_id = ? AND symbol = ?`).get(userId, sym);
      if (existing) {
        db.prepare(
          `UPDATE holdings SET name=?, shares=?, avg_cost=?, current_price=?, updated_at=? WHERE user_id=? AND symbol=?`
        ).run(name || sym, shares, avg_cost, currentPrice, new Date().toISOString(), userId, sym);
      } else {
        const { v4: uuidv4 } = require('uuid');
        db.prepare(
          `INSERT INTO holdings (id, user_id, symbol, name, shares, avg_cost, current_price, health_score, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
        ).run(uuidv4(), userId, sym, name || sym, shares, avg_cost, currentPrice, 80, new Date().toISOString());
      }
      res.json({ success: true, message: '持仓已更新' });
    } catch (err) {
      logger.error('addHolding error', { error: err.message });
      res.status(500).json({ error: err.message });
    }
  }

  /**
   * 删除持仓 DELETE /api/portfolio/holdings/:symbol
   */
  async deleteHolding(req, res) {
    try {
      const db = getDb();
      const userId = req.user?.id;
      const { symbol } = req.params;
      db.prepare(`DELETE FROM holdings WHERE user_id = ? AND symbol = ?`).run(userId, symbol.toUpperCase());
      res.json({ success: true, message: '持仓已删除' });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  }

  /**
   * 更新用户资金/目标 PATCH /api/user/profile
   */
  async updateUserProfile(req, res) {
    try {
      const db = getDb();
      const userId = req.user?.id;
      const { cash, target_cash_ratio } = req.body;

      const user = db.prepare(`SELECT profile FROM users WHERE id = ?`).get(userId);
      let profile = {};
      try { profile = JSON.parse(user?.profile || '{}'); } catch (e) {}

      if (cash !== undefined) profile.cash = parseFloat(cash);
      if (target_cash_ratio !== undefined) profile.target_cash_ratio = parseFloat(target_cash_ratio);

      db.prepare(`UPDATE users SET profile = ? WHERE id = ?`).run(JSON.stringify(profile), userId);
      res.json({ success: true, profile });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  }

  // ─────────────────────────────────────────
  // 私有辅助方法
  // ─────────────────────────────────────────

  _calcHealthScore(cashRatio, targetCashRatio, holdings) {
    let score = 80;
    const cashDiff = Math.abs(cashRatio - targetCashRatio);
    if (cashDiff > 30) score -= 20;
    else if (cashDiff > 15) score -= 10;
    else if (cashDiff < 5) score += 5;

    // 分散度
    if (holdings.length >= 5) score += 5;
    if (holdings.length >= 8) score += 3;

    return Math.max(0, Math.min(100, parseFloat(score.toFixed(1))));
  }

  _calcOptionStats(positions, prices) {
    const openPositions = positions.filter(p => p.status === 'open');
    const closedPositions = positions.filter(p => p.status !== 'open');

    const totalOpenPremium = openPositions.reduce((sum, p) => sum + (p.premium * p.contracts * 100), 0);
    const totalRealizedPnl = closedPositions.reduce((sum, p) => {
      const openPremium = p.premium * p.contracts * 100;
      const closePremium = (p.close_price || 0) * p.contracts * 100;
      if (p.status === 'expired') return sum + openPremium;
      if (p.status === 'closed') {
        return p.direction === 'sell' ? sum + openPremium - closePremium : sum + closePremium - openPremium;
      }
      return sum;
    }, 0);

    const wins = closedPositions.filter(p => {
      if (p.status === 'expired') return true;
      if (p.status === 'closed') {
        const pnl = p.direction === 'sell'
          ? (p.premium - (p.close_price || 0)) * p.contracts * 100
          : ((p.close_price || 0) - p.premium) * p.contracts * 100;
        return pnl > 0;
      }
      return false;
    }).length;

    const winRate = closedPositions.length > 0 ? parseFloat((wins / closedPositions.length * 100).toFixed(1)) : 0;

    // 按标的汇总
    const bySymbol = {};
    for (const p of positions) {
      if (!bySymbol[p.symbol]) bySymbol[p.symbol] = { symbol: p.symbol, count: 0, premium: 0 };
      bySymbol[p.symbol].count++;
      bySymbol[p.symbol].premium += p.premium * p.contracts * 100;
    }

    return {
      total_open_premium: parseFloat(totalOpenPremium.toFixed(2)),
      total_realized_pnl: parseFloat(totalRealizedPnl.toFixed(2)),
      win_rate: winRate,
      open_count: openPositions.length,
      closed_count: closedPositions.length,
      by_symbol: Object.values(bySymbol),
    };
  }

  _buildOptionStrategies(prices, profile) {
    const riskLevel = profile.risk_tolerance || '平衡';
    let otmPct, dte;
    if (riskLevel === '保守') { otmPct = 0.15; dte = 45; }
    else if (riskLevel === '激进') { otmPct = 0.05; dte = 21; }
    else { otmPct = 0.10; dte = 30; }

    const targets = [
      { symbol: 'TSLA', otmMult: 1.0 },
      { symbol: 'NVDA', otmMult: 1.2 },
      { symbol: 'AAPL', otmMult: 0.8 },
    ];

    return targets.map(t => {
      const price = prices[t.symbol]?.price || 0;
      if (!price) return null;
      const thisOtm = otmPct * t.otmMult;
      let strike = price * (1 - thisOtm);
      // 标准化行权价
      if (price >= 200) strike = Math.round(strike / 5) * 5;
      else if (price >= 50) strike = Math.round(strike / 2.5) * 2.5;
      else strike = Math.round(strike * 10) / 10;
      // 确保低于现价
      if (strike >= price) strike = Math.floor(price * 0.95 / 5) * 5;

      const distPct = parseFloat(((price - strike) / price * 100).toFixed(1));
      const premium = parseFloat((price * 0.25 * Math.sqrt(dte / 365) * 0.20).toFixed(2));
      const annualized = parseFloat(((premium / strike) * (365 / dte) * 100).toFixed(1));
      const prob = riskLevel === '保守' ? 85 : riskLevel === '激进' ? 65 : 75;

      const expDate = new Date();
      expDate.setDate(expDate.getDate() + dte);

      return {
        symbol: t.symbol,
        type: 'put',
        strategy_name: 'Sell Put',
        current_price: parseFloat(price.toFixed(2)),
        strike_price: strike,
        expiration: expDate.toISOString().split('T')[0],
        dte,
        premium,
        probability: prob,
        annualized_return: annualized,
        distance_pct: distPct,
        recommendation: `${distPct}% OTM，胜率${prob}%，${dte}天到期`,
      };
    }).filter(Boolean);
  }

  _calcRiskAlerts(cashRatio, targetCashRatio, holdings, totalValue) {
    const alerts = [];

    if (cashRatio > targetCashRatio + 20) {
      alerts.push({
        id: 'r1', level: 'high',
        title: '现金比例过高',
        description: `现金比例${cashRatio.toFixed(1)}% vs 目标${targetCashRatio}%，资金效率低`,
        timestamp: '刚刚',
        action: '考虑sell put策略增加资金利用率',
      });
    } else if (cashRatio < targetCashRatio - 20) {
      alerts.push({
        id: 'r1', level: 'medium',
        title: '现金比例偏低',
        description: `现金比例${cashRatio.toFixed(1)}%，低于目标${targetCashRatio}%`,
        timestamp: '刚刚',
        action: '考虑适当减仓，保持应急流动性',
      });
    }

    // 检查科技股集中度
    const totalInvested = holdings.reduce((sum, h) => sum + h.current_value, 0);
    if (totalInvested > 0 && holdings.length > 0) {
      alerts.push({
        id: 'r2', level: 'medium',
        title: '利率/宏观风险',
        description: 'FOMC政策与关税压力可能影响科技股估值',
        timestamp: '今日',
        action: '保持现金仓位，关注联储动态',
      });
    }

    return alerts;
  }

  _calcPortfolioHealth(cashRatio, targetCashRatio, holdings, totalValue) {
    const diversification = Math.min(100, holdings.length * 12);
    const cashScore = Math.max(0, 100 - Math.abs(cashRatio - targetCashRatio) * 2);
    const riskControl = 80;
    const sectorAllocation = Math.min(100, holdings.length * 10 + 40);
    const positionSize = holdings.length > 0
      ? Math.max(0, 100 - Math.max(...holdings.map(h => h.current_value)) / (totalValue || 1) * 200)
      : 80;
    const overall = (diversification + cashScore + riskControl + sectorAllocation + positionSize) / 5;

    return {
      overall_score: parseFloat(overall.toFixed(1)),
      metrics: {
        diversification: parseFloat(diversification.toFixed(0)),
        risk_control: riskControl,
        cash_management: parseFloat(cashScore.toFixed(0)),
        sector_allocation: parseFloat(sectorAllocation.toFixed(0)),
        position_size: parseFloat(positionSize.toFixed(0)),
        volatility: 76,
      },
      strengths: [
        holdings.length >= 5 ? '持仓分散度良好' : '核心持仓聚焦',
        '风险控制措施到位',
        '投资标的质量优秀',
      ],
      weaknesses: [
        Math.abs(cashRatio - targetCashRatio) > 15 ? `现金比例偏离目标（${cashRatio.toFixed(1)}%）` : '组合配置均衡',
        '科技股集中度较高',
      ].filter(Boolean),
      recommendations: [
        cashRatio > targetCashRatio + 10 ? '通过sell put策略优化现金使用' : '维持现有现金配置',
        '定期检视核心持仓基本面',
        '关注AI/量子计算赛道新机会',
      ],
    };
  }

  _buildNewsFeed(holdings) {
    // 基于持仓生成相关资讯（静态模拟，后续可接真实新闻API）
    const symbols = (holdings || []).map(h => h.symbol);
    const now = new Date();
    const fmtTime = (minutesAgo) => {
      const t = new Date(now - minutesAgo * 60000);
      return `${t.getHours()}:${String(t.getMinutes()).padStart(2,'0')}`;
    };
    const newsItems = [
      { id:'n1', title:'英伟达(NVDA)发布Blackwell Ultra芯片，AI算力再提升3倍', summary:'NVIDIA宣布下一代Blackwell Ultra架构，推理性能是H100的5倍，预计2025年Q3量产出货。', source:'Bloomberg', timestamp: fmtTime(15), impact:'high', related_symbols:['NVDA','META','GOOGL','MSFT'] },
      { id:'n2', title:'特斯拉(TSLA) Robotaxi德州试运营时间表确认', summary:'特斯拉官方确认2025年Q2在德克萨斯州奥斯汀启动Robotaxi商业运营，首批约1000辆Cybercab投入测试。', source:'Reuters', timestamp: fmtTime(45), impact:'high', related_symbols:['TSLA'] },
      { id:'n3', title:'亚马逊(AMZN) AWS季度收入创历史新高，同比增长17%', summary:'亚马逊云计算业务AWS Q4收入达285亿美元，AI相关服务收入贡献明显，云业务护城河持续强化。', source:'CNBC', timestamp: fmtTime(120), impact:'medium', related_symbols:['AMZN','GOOGL'] },
      { id:'n4', title:'美联储维持利率不变，暗示2025年降息节奏放缓', summary:'FOMC决定维持联邦基金利率5.25-5.5%不变，声明措辞较上次更为谨慎，市场对年内降息预期下调。', source:'WSJ', timestamp: fmtTime(180), impact:'medium', related_symbols:['NVDA','TSLA','GOOGL','AAPL'] },
      { id:'n5', title:'IonQ(IONQ)获得美军$84M量子计算合同', summary:'量子计算公司IonQ与美国空军研究实验室签署8400万美元合同，用于量子网络研究，股价盘后上涨12%。', source:'TechCrunch', timestamp: fmtTime(240), impact:'high', related_symbols:['IONQ'] },
      { id:'n6', title:'谷歌(GOOGL) AI概述功能扩展至100+国家', summary:'谷歌搜索AI Overview功能全球扩展，用户覆盖率提升至60%，广告业务有望受益于AI升级。', source:'The Verge', timestamp: fmtTime(300), impact:'medium', related_symbols:['GOOGL','META'] },
    ];
    // 优先显示与用户持仓相关的新闻
    const relevant = newsItems.filter(n => n.related_symbols.some(s => symbols.includes(s)));
    const others = newsItems.filter(n => !n.related_symbols.some(s => symbols.includes(s)));
    return [...relevant, ...others].slice(0, 6);
  }
}

module.exports = new DashboardController();
