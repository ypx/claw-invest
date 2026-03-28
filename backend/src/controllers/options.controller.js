const { logger } = require('../utils/logger');
// 复用 dashboard 的多源实时价格获取函数
const { getLivePrices } = require('./dashboard.controller');

// 期权策略推荐标的（固定顺序，TSLA 必须第一位）
const OPTION_CANDIDATES = [
  { symbol: 'TSLA', sector: '电动车/能源/AI机器人',  ivBase: 0.55, otmMult: 1.0 },
  { symbol: 'NVDA', sector: 'AI算力基础设施',         ivBase: 0.50, otmMult: 1.1 },
  { symbol: 'GOOGL', sector: 'AI/搜索/云计算',        ivBase: 0.35, otmMult: 0.9 },
  { symbol: 'META',  sector: 'AI社交/广告双引擎',     ivBase: 0.38, otmMult: 0.9 },
  { symbol: 'IONQ',  sector: '量子计算（高弹性）',    ivBase: 0.80, otmMult: 1.4 },
];

class OptionsController {
  constructor() {
    this.getDynamicStrategies = this.getDynamicStrategies.bind(this);
  }

  /**
   * 获取动态期权策略推荐（3-5个标的，接入实时价格）
   */
  async getDynamicStrategies(req, res) {
    try {
      const { user } = req;
      logger.info('获取动态期权策略请求', { user: user?.id, ip: req.ip });

      // 获取用户画像
      const userProfile = user?.profile || {};
      const riskLevel = userProfile.risk_tolerance || '平衡';

      // OTM % 和 DTE 参数
      let otmPctBase, dte;
      if (riskLevel === '保守') { otmPctBase = 0.15; dte = 45; }
      else if (riskLevel === '激进') { otmPctBase = 0.05; dte = 21; }
      else { otmPctBase = 0.10; dte = 30; }

      // 获取所有候选标的的实时价格
      const symbols = OPTION_CANDIDATES.map(c => c.symbol);
      const prices = await getLivePrices(symbols);

      // 模拟VIX（实际可接入数据源）
      const vix = 18.5;

      const strategies = [];
      for (const candidate of OPTION_CANDIDATES) {
        const priceData = prices[candidate.symbol];
        const price = priceData?.price || (typeof priceData === 'number' ? priceData : 0);
        if (!price || price <= 0) {
          logger.warn(`期权策略: ${candidate.symbol} 无有效价格，跳过`);
          continue;
        }

        const thisOtm = otmPctBase * candidate.otmMult;

        // 计算行权价
        let strike = price * (1 - thisOtm);
        if (price >= 200) strike = Math.round(strike / 5) * 5;
        else if (price >= 50) strike = Math.round(strike / 2.5) * 2.5;
        else strike = Math.round(strike * 10) / 10;
        if (strike >= price) strike = Math.floor(price * 0.95 / 5) * 5;

        // 到期日
        const expDate = new Date();
        expDate.setDate(expDate.getDate() + dte);
        const expiration = expDate.toISOString().split('T')[0];

        // 权利金估算（简化 Black-Scholes）
        const timeFactor = Math.sqrt(dte / 365);
        const deltaTarget = riskLevel === '保守' ? 0.15 : riskLevel === '激进' ? 0.35 : 0.25;
        let premium = price * candidate.ivBase * timeFactor * deltaTarget;
        premium = Math.min(premium, price * 0.10);
        premium = Math.max(0.1, premium);
        premium = Math.round(premium * 100) / 100;

        // 年化收益
        const annualized = parseFloat(((premium / strike) * (365 / dte) * 100).toFixed(1));

        // 胜率
        const probability = riskLevel === '保守' ? 85 : riskLevel === '激进' ? 65 : 75;

        // OTM 距离
        const distancePct = parseFloat(((price - strike) / price * 100).toFixed(1));

        // VIX 备注
        let vixComment = vix < 15 ? '当前VIX低，权利金偏少' : vix > 30 ? '当前VIX高，权利金丰厚' : '市场波动适中';

        strategies.push({
          symbol: candidate.symbol,
          type: 'sell_put',
          strategy_name: 'Sell Put',
          sector: candidate.sector,
          current_price: parseFloat(price.toFixed(2)),
          strike_price: strike,
          expiration,
          dte,
          premium,
          probability,
          annualized_return: annualized,
          implied_volatility: Math.round(candidate.ivBase * 100),
          vix,
          distance_pct: distancePct,
          recommendation: `${distancePct}% OTM，胜率${probability}%，年化${annualized}%，${vixComment}`,
          risk_level: riskLevel,
        });
      }

      res.status(200).json({
        success: true,
        count: strategies.length,
        strategies,
        vix,
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
}

module.exports = new OptionsController();
