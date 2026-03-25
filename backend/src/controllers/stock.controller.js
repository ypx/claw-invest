const { config } = require('../config/config');
const { logger } = require('../utils/logger');

class StockController {
  /**
   * 获取所有股票列表
   */
  async getAllStocks(req, res) {
    try {
      logger.info('获取所有股票列表请求', { ip: req.ip });
      
      // 这里应该从数据库查询，暂时返回静态数据
      const stocks = config.mikeStocks.map(symbol => ({
        symbol,
        name: this.getStockName(symbol),
        sector: this.getSector(symbol),
      }));
      
      res.status(200).json({
        success: true,
        count: stocks.length,
        data: stocks,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取股票列表失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取股票列表失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 获取股票代码列表
   */
  async getStockSymbols(req, res) {
    try {
      logger.info('获取股票代码列表请求', { ip: req.ip });
      
      res.status(200).json({
        success: true,
        count: config.mikeStocks.length,
        symbols: config.mikeStocks,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取股票代码列表失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取股票代码列表失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 获取单个股票信息
   */
  async getStockInfo(req, res) {
    try {
      const { symbol } = req.params;
      logger.info('获取股票信息请求', { symbol, ip: req.ip });
      
      // 这里应该从数据库查询，暂时返回模拟数据
      const stockInfo = {
        symbol: symbol.toUpperCase(),
        name: this.getStockName(symbol),
        sector: this.getSector(symbol),
        industry: this.getIndustry(symbol),
        currentPrice: this.getRandomPrice(symbol),
        marketCap: this.getRandomMarketCap(symbol),
        peRatio: this.getRandomPE(symbol),
        dividendYield: this.getRandomDividend(symbol),
        beta: this.getRandomBeta(symbol),
        updatedAt: new Date().toISOString(),
      };
      
      res.status(200).json({
        success: true,
        data: stockInfo,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取股票信息失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取股票信息失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 获取股票价格历史
   */
  async getStockPrices(req, res) {
    try {
      const { symbol } = req.params;
      const { period = '3month', interval = 'daily' } = req.query;
      
      logger.info('获取股票价格历史请求', { symbol, period, interval, ip: req.ip });
      
      // 这里应该从数据库查询，暂时返回模拟数据
      const prices = this.generateMockPrices(symbol, period);
      
      res.status(200).json({
        success: true,
        symbol: symbol.toUpperCase(),
        period,
        interval,
        count: prices.length,
        data: prices,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取股票价格历史失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取股票价格历史失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 分析单只股票
   */
  async analyzeStock(req, res) {
    try {
      const { symbol } = req.params;
      const { user } = req;
      
      logger.info('分析股票请求', { symbol, user: user?.id, ip: req.ip });
      
      // 这里应该调用Python分析服务，暂时返回模拟分析结果
      const analysis = await this.performMockAnalysis(symbol, user);
      
      res.status(200).json({
        success: true,
        symbol: symbol.toUpperCase(),
        data: analysis,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('分析股票失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '分析股票失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 分析所有股票
   */
  async analyzeAllStocks(req, res) {
    try {
      const { user } = req;
      
      logger.info('分析所有股票请求', { user: user?.id, ip: req.ip });
      
      // 分析所有Mike推荐股票
      const analyses = await Promise.all(
        config.mikeStocks.map(async symbol => {
          const analysis = await this.performMockAnalysis(symbol, user);
          return {
            symbol,
            name: this.getStockName(symbol),
            ...analysis,
          };
        })
      );
      
      // 按分数排序
      analyses.sort((a, b) => b.analysis.final_score - a.analysis.final_score);
      
      res.status(200).json({
        success: true,
        count: analyses.length,
        data: analyses,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('分析所有股票失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '分析所有股票失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 获取今日最高推荐股票
   */
  async getTopRecommendations(req, res) {
    try {
      const { limit = 10 } = req.query;
      const { user } = req;
      
      logger.info('获取最高推荐股票请求', { limit, user: user?.id, ip: req.ip });
      
      // 这里应该从数据库查询最新的分析结果，暂时返回模拟数据
      const recommendations = config.mikeStocks
        .slice(0, Math.min(limit, config.mikeStocks.length))
        .map((symbol, index) => ({
          rank: index + 1,
          symbol,
          name: this.getStockName(symbol),
          final_score: 85 - index * 2, // 模拟递减分数
          recommendation: index < 3 ? '强烈买入' : index < 7 ? '买入' : '持有',
          reasoning: `Mike推荐${this.getMikeType(symbol)}，当前估值合理，技术面${index % 2 === 0 ? '向好' : '中性'}`,
          current_price: this.getRandomPrice(symbol),
          sell_put_suggestion: index < 5 ? {
            strike_range: { conservative: this.getRandomPrice(symbol) * 0.85 },
            expected_yield_pct: 10 + index,
            timeframe: '30天到期',
            risk_level: '低',
          } : null,
        }));
      
      res.status(200).json({
        success: true,
        date: new Date().toISOString().split('T')[0],
        count: recommendations.length,
        data: recommendations,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取最高推荐股票失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取最高推荐股票失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 获取仪表盘数据
   */
  async getDashboardData(req, res) {
    try {
      const { user } = req;
      
      logger.info('获取仪表盘数据请求', { user: user?.id, ip: req.ip });
      
      // 模拟仪表盘数据
      const dashboard = {
        summary: {
          total_stocks: config.mikeStocks.length,
          avg_score: 78.5,
          recommendation_distribution: {
            strong_buy: 4,
            buy: 3,
            hold: 2,
            sell: 1,
            strong_sell: 0,
          },
        },
        market_sentiment: {
          overall: 'bullish',
          vix: 16.8,
          fear_greed_index: 72, // 贪婪
        },
        top_opportunities: [
          {
            symbol: 'NVDA',
            name: '英伟达',
            score: 92,
            reasoning: 'AI算力龙头，估值相对合理，技术面强势',
            action: '买入或sell put @ $850-900',
          },
          {
            symbol: 'GOOGL',
            name: '谷歌',
            score: 85,
            reasoning: 'AI搜索+云，被低估，财务稳健',
            action: '分批买入',
          },
        ],
        watchlist: config.mikeStocks.slice(0, 5).map(symbol => ({
          symbol,
          name: this.getStockName(symbol),
          current_price: this.getRandomPrice(symbol),
          change: (Math.random() - 0.5) * 5, // -2.5% 到 +2.5%
        })),
        updated_at: new Date().toISOString(),
      };
      
      res.status(200).json({
        success: true,
        data: dashboard,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('获取仪表盘数据失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取仪表盘数据失败',
        message: error.message,
      });
    }
  }
  
  /**
   * 运行股票筛选器
   */
  async runStockScreener(req, res) {
    try {
      const { criteria } = req.body;
      const { user } = req;
      
      logger.info('运行股票筛选器请求', { criteria, user: user?.id, ip: req.ip });
      
      // 模拟筛选结果
      const results = config.mikeStocks
        .filter(symbol => {
          // 简单的筛选逻辑
          if (criteria?.sector && this.getSector(symbol) !== criteria.sector) {
            return false;
          }
          if (criteria?.max_pe) {
            const pe = this.getRandomPE(symbol);
            if (pe > criteria.max_pe) return false;
          }
          return true;
        })
        .map(symbol => ({
          symbol,
          name: this.getStockName(symbol),
          pe_ratio: this.getRandomPE(symbol),
          current_price: this.getRandomPrice(symbol),
          score: Math.floor(Math.random() * 30) + 70, // 70-100
        }));
      
      res.status(200).json({
        success: true,
        criteria,
        count: results.length,
        data: results,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      logger.error('运行股票筛选器失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '运行股票筛选器失败',
        message: error.message,
      });
    }
  }
  
  // 辅助方法
  
  getStockName(symbol) {
    const names = {
      'NVDA': '英伟达',
      'GOOGL': '谷歌',
      'AMZN': '亚马逊',
      'META': 'Meta',
      'TSLA': '特斯拉',
      'IONQ': 'IonQ',
      'AAPL': '苹果',
      'MSFT': '微软',
      'ARKB': 'ARK 21Shares Bitcoin ETF',
      'ETH': '以太坊',
    };
    return names[symbol] || symbol;
  }
  
  getSector(symbol) {
    const sectors = {
      'NVDA': '科技',
      'GOOGL': '科技',
      'AMZN': '科技',
      'META': '科技',
      'TSLA': '消费类',
      'IONQ': '科技',
      'AAPL': '科技',
      'MSFT': '科技',
      'ARKB': '金融',
      'ETH': '金融',
    };
    return sectors[symbol] || '未知';
  }
  
  getIndustry(symbol) {
    const industries = {
      'NVDA': '半导体',
      'GOOGL': '互联网服务',
      'AMZN': '电商/云计算',
      'META': '社交媒体',
      'TSLA': '汽车制造',
      'IONQ': '量子计算',
      'AAPL': '消费电子',
      'MSFT': '软件/云计算',
      'ARKB': 'ETF/数字资产',
      'ETH': '区块链/加密货币',
    };
    return industries[symbol] || '未知';
  }
  
  getMikeType(symbol) {
    const types = {
      'NVDA': '核心仓',
      'GOOGL': '核心仓',
      'AMZN': '核心仓',
      'META': '成长仓',
      'TSLA': '关注仓',
      'IONQ': '成长仓',
      'AAPL': '核心仓',
      'MSFT': '核心仓',
      'ARKB': '加密资产',
      'ETH': '加密资产',
    };
    return types[symbol] || '关注仓';
  }
  
  getRandomPrice(symbol) {
    const basePrices = {
      'NVDA': 950,
      'GOOGL': 180,
      'AMZN': 175,
      'META': 520,
      'TSLA': 220,
      'IONQ': 12,
      'AAPL': 210,
      'MSFT': 420,
      'ARKB': 48,
      'ETH': 3500,
    };
    const base = basePrices[symbol] || 100;
    const variation = (Math.random() - 0.5) * 0.1; // ±5%
    return parseFloat((base * (1 + variation)).toFixed(2));
  }
  
  getRandomMarketCap(symbol) {
    const baseCaps = {
      'NVDA': 2300 * 1e9,
      'GOOGL': 2200 * 1e9,
      'AMZN': 1800 * 1e9,
      'META': 1300 * 1e9,
      'TSLA': 700 * 1e9,
      'IONQ': 2.5 * 1e9,
      'AAPL': 3200 * 1e9,
      'MSFT': 3100 * 1e9,
      'ARKB': 10 * 1e9,
      'ETH': 420 * 1e9,
    };
    const base = baseCaps[symbol] || 100 * 1e9;
    return parseFloat(base.toFixed(0));
  }
  
  getRandomPE(symbol) {
    const basePEs = {
      'NVDA': 65,
      'GOOGL': 25,
      'AMZN': 60,
      'META': 32,
      'TSLA': 70,
      'IONQ': -1, // 亏损
      'AAPL': 28,
      'MSFT': 35,
      'ARKB': 18,
      'ETH': 45,
    };
    const base = basePEs[symbol] || 20;
    if (base < 0) return base;
    const variation = (Math.random() - 0.5) * 0.2; // ±10%
    return parseFloat((base * (1 + variation)).toFixed(1));
  }
  
  getRandomDividend(symbol) {
    const baseDividends = {
      'NVDA': 0.03,
      'GOOGL': 0,
      'AMZN': 0,
      'META': 0.5,
      'TSLA': 0,
      'IONQ': 0,
      'AAPL': 0.5,
      'MSFT': 0.8,
      'ARKB': 1.2,
      'ETH': 3.5, // 质押收益
    };
    const base = baseDividends[symbol] || 0;
    if (base === 0) return 0;
    const variation = (Math.random() - 0.5) * 0.3; // ±15%
    return parseFloat((base * (1 + variation)).toFixed(2));
  }
  
  getRandomBeta(symbol) {
    const baseBetas = {
      'NVDA': 1.8,
      'GOOGL': 1.05,
      'AMZN': 1.2,
      'META': 1.35,
      'TSLA': 2.1,
      'IONQ': 2.5,
      'AAPL': 1.28,
      'MSFT': 0.95,
      'ARKB': 1.6,
      'ETH': 2.2,
    };
    const base = baseBetas[symbol] || 1.0;
    const variation = (Math.random() - 0.5) * 0.15; // ±7.5%
    return parseFloat((base * (1 + variation)).toFixed(2));
  }
  
  generateMockPrices(symbol, period) {
    const days = period === '1week' ? 7 : period === '1month' ? 30 : 90;
    const basePrice = this.getRandomPrice(symbol);
    const volatility = this.getRandomBeta(symbol) * 0.015; // 基于Beta的日波动率
    
    const prices = [];
    let currentPrice = basePrice;
    const today = new Date();
    
    for (let i = days; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      
      // 随机价格变化
      const change = (Math.random() - 0.5) * 2 * volatility;
      currentPrice = currentPrice * (1 + change);
      
      const high = currentPrice * (1 + Math.random() * 0.02); // 0-2%
      const low = currentPrice * (1 - Math.random() * 0.02); // 0-2%
      const volume = Math.floor(Math.random() * 10000000) + 1000000;
      
      prices.push({
        date: date.toISOString().split('T')[0],
        open: parseFloat(currentPrice.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(currentPrice.toFixed(2)),
        volume,
      });
    }
    
    return prices;
  }
  
  async performMockAnalysis(symbol, user) {
    // 模拟分析过程
    const stockInfo = {
      symbol,
      name: this.getStockName(symbol),
      pe_ratio: this.getRandomPE(symbol),
      market_cap: this.getRandomMarketCap(symbol),
      dividend_yield: this.getRandomDividend(symbol),
      beta: this.getRandomBeta(symbol),
    };
    
    const mikeType = this.getMikeType(symbol);
    const mikeWeight = mikeType === '核心仓' ? 1.0 : mikeType === '成长仓' ? 0.8 : 0.7;
    
    // 模拟保守系数
    let conservativeFactor = 1.0;
    if (stockInfo.pe_ratio < 20) conservativeFactor *= 1.2;
    if (stockInfo.beta < 1.2) conservativeFactor *= 1.1;
    if (stockInfo.dividend_yield > 1) conservativeFactor *= 1.05;
    conservativeFactor = Math.max(0.5, Math.min(1.5, conservativeFactor));
    
    // 模拟基本面分数
    let fundamentalScore = 50;
    if (stockInfo.pe_ratio < 25) fundamentalScore += 20;
    if (stockInfo.market_cap > 100 * 1e9) fundamentalScore += 15;
    fundamentalScore = Math.max(0, Math.min(100, fundamentalScore));
    
    // 模拟技术面分数（随机）
    const technicalScore = Math.floor(Math.random() * 40) + 60; // 60-100
    
    const combinedScore = (fundamentalScore * 0.6 + technicalScore * 0.4);
    const finalScore = mikeWeight * combinedScore * conservativeFactor;
    const finalScoreClipped = Math.max(0, Math.min(100, finalScore));
    
    // 生成推荐
    let recommendation = '持有';
    if (finalScoreClipped >= 80) recommendation = '强烈买入';
    else if (finalScoreClipped >= 65) recommendation = '买入';
    else if (finalScoreClipped <= 20) recommendation = '强烈卖出';
    else if (finalScoreClipped <= 40) recommendation = '卖出';
    
    // 生成sell put建议
    let sellPutSuggestion = null;
    if (finalScoreClipped >= 70 && stockInfo.beta < 1.5) {
      sellPutSuggestion = {
        current_price: parseFloat(this.getRandomPrice(symbol).toFixed(2)),
        volatility_pct: (stockInfo.beta * 15).toFixed(1),
        strike_range: {
          very_conservative: parseFloat((this.getRandomPrice(symbol) * 0.75).toFixed(2)),
          conservative: parseFloat((this.getRandomPrice(symbol) * 0.80).toFixed(2)),
          moderate: parseFloat((this.getRandomPrice(symbol) * 0.85).toFixed(2)),
        },
        expected_yield_pct: (12 - stockInfo.beta * 2).toFixed(1),
        timeframe: '30-45天到期',
        risk_level: stockInfo.beta < 1.0 ? '低' : '中',
        suitability: '适合',
      };
    }
    
    return {
      stock_info: stockInfo,
      mike_recommendation: {
        type: mikeType,
        reason: `Mike推荐${mikeType}，认为具有长期成长潜力`,
      },
      analysis: {
        final_score: parseFloat(finalScoreClipped.toFixed(2)),
        recommendation,
        components: {
          mike_weight: mikeWeight,
          fundamental_score: fundamentalScore,
          technical_score: technicalScore,
          conservative_factor: parseFloat(conservativeFactor.toFixed(2)),
          combined_score: parseFloat(combinedScore.toFixed(2)),
        },
        sell_put_suggestion: sellPutSuggestion,
        reasoning: `该股票是Mike推荐的${mikeType}，权重${mikeWeight}。基本面${fundamentalScore > 60 ? '良好' : '一般'}，技术面${technicalScore > 70 ? '强劲' : '中性'}。保守系数${conservativeFactor.toFixed(2)}，最终评分${finalScoreClipped.toFixed(1)}。`,
      },
    };
  }
}

module.exports = new StockController();