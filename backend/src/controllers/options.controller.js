const { config } = require('../config/config');
const { logger } = require('../utils/logger');

class OptionsController {
  constructor() {
    // 绑定方法以确保this上下文正确
    this.getDynamicStrategies = this.getDynamicStrategies.bind(this);
  }

  /**
   * 获取动态期权策略推荐
   * 基于用户画像和实时市场数据生成个性化的期权策略
   */
  async getDynamicStrategies(req, res) {
    try {
      const { user } = req;
      logger.info('获取动态期权策略请求', { user: user?.id, ip: req.ip });

      // 获取用户画像（如果有）
      const userProfile = user?.profile || {
        risk_tolerance: '中等',
        capital_scale: '中等',
        experience_level: '中级'
      };

      // 模拟实时价格数据（实际应从数据库或API获取）
      const mockPrices = OptionsController._getMockRealTimePrices();
      
      // 模拟VIX
      const vix = 16.8;

      // 生成动态策略
      const strategies = OptionsController._generateDynamicStrategies(userProfile, mockPrices, vix);

      res.status(200).json({
        success: true,
        count: strategies.length,
        strategies: strategies,
        vix: vix,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取动态期权策略失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取动态期权策略失败',
        message: error.message,
      });
    }
  }

  /**
   * 获取模拟实时价格（实际应从数据库或外部API获取）
   */
  static _getMockRealTimePrices() {
    // 基于当前市场情况的模拟价格
    const basePrices = {
      'TSLA': { price: 380, change: 2.5 },    // 特斯拉 ~$380
      'NVDA': { price: 115, change: 1.8 },    // 英伟达 ~$115
      'AAPL': { price: 225, change: 0.9 },    // 苹果 ~$225
      'GOOGL': { price: 178, change: 1.2 },   // 谷歌 ~$178
      'META': { price: 595, change: 2.1 },    // Meta ~$595
      'AMZN': { price: 198, change: 1.5 },    // 亚马逊 ~$198
      'MSFT': { price: 428, change: 0.8 },    // 微软 ~$428
      'IONQ': { price: 18.5, change: 3.2 },   // IonQ ~$18.5
    };

    const prices = {};
    for (const [symbol, data] of Object.entries(basePrices)) {
      // 添加小幅随机波动模拟实时变化
      const variation = (Math.random() - 0.5) * 0.005; // ±0.25%
      prices[symbol] = {
        price: parseFloat((data.price * (1 + variation)).toFixed(2)),
        change_percent: data.change + (Math.random() - 0.5) * 0.5,
      };
    }
    return prices;
  }

  /**
   * 生成动态期权策略
   * 核心逻辑：基于实时股价计算合理的OTM行权价
   */
  static _generateDynamicStrategies(profile, prices, vix) {
    const strategies = [];

    // 风险等级映射
    const riskLevel = profile.risk_tolerance || '中等';
    const experience = profile.experience_level || '中级';

    // 根据风险等级确定Delta和OTM距离
    let deltaTarget, otmPctBase, dteTarget;
    if (riskLevel === '保守') {
      deltaTarget = 0.15;
      otmPctBase = 0.15;  // 15% OTM
      dteTarget = 45;     // 45天到期
    } else if (riskLevel === '激进') {
      deltaTarget = 0.35;
      otmPctBase = 0.05;  // 5% OTM
      dteTarget = 21;     // 21天到期
    } else { // 中等/平衡
      deltaTarget = 0.25;
      otmPctBase = 0.10;  // 10% OTM
      dteTarget = 30;     // 30天到期
    }

    // 根据VIX调整策略
    let vixAdj = 1.0;
    let vixComment;
    if (vix < 15) {
      vixAdj = 0.8;
      vixComment = 'VIX低，权利金较少，建议等待';
    } else if (vix > 30) {
      vixAdj = 1.3;
      vixComment = 'VIX高，权利金丰厚，适合操作';
    } else {
      vixComment = 'VIX适中，正常操作';
    }

    // 选择标的：优先选择高流动性的大盘股
    const candidates = [];
    for (const [symbol, data] of Object.entries(prices)) {
      const price = data.price;
      if (price <= 0) continue;
      
      const changePct = data.change_percent;
      // 计算IV估算
      const ivEstimate = Math.max(0.25, Math.min(0.80, (vix / 100) * (1 + Math.abs(changePct) / 100)));
      
      candidates.push({
        symbol: symbol,
        price: price,
        change_pct: changePct,
        iv: ivEstimate,
      });
    }

    // 按流动性排序（优先推荐TSLA、NVDA、AAPL）
    const priorityOrder = ['TSLA', 'NVDA', 'AAPL', 'GOOGL', 'META', 'AMZN', 'MSFT'];
    candidates.sort((a, b) => {
      const idxA = priorityOrder.indexOf(a.symbol);
      const idxB = priorityOrder.indexOf(b.symbol);
      if (idxA !== -1 && idxB !== -1) return idxA - idxB;
      if (idxA !== -1) return -1;
      if (idxB !== -1) return 1;
      return b.price - a.price;
    });

    // 生成3个策略配置
    const strategyConfigs = [
      { name: '主推策略', otmMult: 1.0, dteMult: 1.0 },   // 标准参数
      { name: '进取策略', otmMult: 0.6, dteMult: 0.7 },   // 更激进的参数
      { name: '保守策略', otmMult: 1.5, dteMult: 1.3 },   // 更保守的参数
    ];

    for (let i = 0; i < Math.min(3, candidates.length); i++) {
      const stock = candidates[i];
      const sym = stock.symbol;
      const price = stock.price;
      const iv = stock.iv;

      const config = strategyConfigs[i];

      // 确定策略类型
      let strategyType, strategyName;
      if (i === 0) {
        strategyType = 'sell_put';
        strategyName = 'Sell Put';
      } else if (i === 1 && ['高级', '资深'].includes(experience)) {
        strategyType = 'covered_call';
        strategyName = 'Covered Call';
      } else {
        strategyType = 'sell_put';
        strategyName = 'Sell Put';
      }

      // 计算OTM百分比
      const otmPct = Math.min(0.25, Math.max(0.03, otmPctBase * config.otmMult));

      // 计算行权价：Sell Put用低于现价的行权价
      let strike;
      if (strategyType === 'sell_put') {
        strike = price * (1 - otmPct);
      } else {
        strike = price * (1 + otmPct);
      }

      // 标准化行权价
      if (strike >= 200) {
        strike = Math.round(strike / 5) * 5;  // 5美元精度
      } else if (strike >= 50) {
        strike = Math.round(strike / 2.5) * 2.5;  // 2.5美元精度
      } else {
        strike = Math.round(strike * 10) / 10;  // 0.1美元精度
      }

      // 确保Sell Put的行权价低于现价
      if (strategyType === 'sell_put' && strike >= price) {
        strike = Math.floor((price * 0.95) / 5) * 5; // 至少5% OTM
      }

      // 计算到期日
      const dte = Math.min(60, Math.max(14, Math.round(dteTarget * config.dteMult)));
      const expDate = new Date();
      expDate.setDate(expDate.getDate() + dte);
      const expiration = expDate.toISOString().split('T')[0];

      // 计算权利金（简化Black-Scholes近似）
      const timeFactor = Math.sqrt(dte / 365);
      let premium = price * iv * timeFactor * deltaTarget * vixAdj;

      // 标准化权利金
      const maxPremium = price * 0.10;
      premium = Math.min(premium, maxPremium);
      premium = Math.max(0.1, premium);
      premium = Math.round(premium * 100) / 100;

      // 计算年化收益
      let annualized = 0;
      if (strike > 0 && premium > 0) {
        annualized = (premium / strike) * (365 / dte) * 100;
        annualized = Math.min(annualized, 100);
      }

      // 计算盈利概率
      const probability = Math.min(95, Math.max(30, Math.round((1 - deltaTarget) * 100)));

      // 生成推荐语
      const distanceDesc = `${Math.round(otmPct * 100 * 10) / 10}%`;
      let rec;
      if (strategyType === 'sell_put') {
        if (otmPct >= 0.15) {
          rec = `深度价外(${distanceDesc})，胜率${probability}%，${vixComment}`;
        } else if (otmPct >= 0.08) {
          rec = `中度价外(${distanceDesc})，平衡收益风险，${vixComment}`;
        } else {
          rec = `轻度价外(${distanceDesc})，权利金收益${Math.round(annualized * 10) / 10}%年化，${vixComment}`;
        }
      } else {
        rec = `持有正股可额外收益${Math.round(annualized * 10) / 10}%年化，行权价距现价+${distanceDesc}`;
      }

      strategies.push({
        symbol: sym,
        type: strategyType,
        strategy_name: strategyName,
        strike_price: strike,
        current_price: Math.round(price * 100) / 100,
        expiration: expiration,
        dte: dte,
        premium: premium,
        probability: probability,
        annualized_return: Math.round(annualized * 10) / 10,
        implied_volatility: Math.round(iv * 1000) / 10,
        vix: Math.round(vix * 100) / 100,
        recommendation: rec,
        risk_level: riskLevel,
        distance_pct: Math.round(otmPct * 100 * 10) / 10,
        config_name: config.name,
      });
    }

    return strategies;
  }
}

module.exports = new OptionsController();
