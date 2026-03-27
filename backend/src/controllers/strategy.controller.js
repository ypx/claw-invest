const { config } = require('../config/config');
const { logger } = require('../utils/logger');
const { getDb } = require('../models/db');
const { v4: uuidv4 } = require('uuid');

/**
 * 策略数据 - 基于Mike投资体系的策略配置
 */
const STRATEGIES = [
  {
    id: 'conservative-core',
    name: '保守核心配置',
    description: '以美股核心科技股为主，强调长期持有和现金管理，适合风险厌恶型投资者。配置重点在NVDA、GOOGL等优质标的，保留充足现金应对波动。',
    risk_level: 1,
    min_capital: '10万+',
    expected_return: '8-12%',
    tags: ['长期持有', '核心资产', '现金管理'],
    suitable_profiles: ['保守型', '稳健型', '长期投资者'],
    allocations: [
      { type: '核心科技股', ratio: 50, symbols: ['NVDA', 'GOOGL', 'MSFT'] },
      { type: '现金流资产', ratio: 30, symbols: ['AMZN', 'AAPL'] },
      { type: '现金储备', ratio: 20, symbols: ['现金'] }
    ]
  },
  {
    id: 'balanced-growth',
    name: '平衡增长策略',
    description: '核心仓位+成长仓位的平衡配置，在稳健基础上追求增长。包含AI基础设施、云计算等前沿赛道，同时通过sell put策略增强收益。',
    risk_level: 3,
    min_capital: '15万+',
    expected_return: '12-18%',
    tags: ['平衡配置', 'sell put', 'AI赛道'],
    suitable_profiles: ['平衡型', '有经验', '中期投资'],
    allocations: [
      { type: 'AI核心仓', ratio: 40, symbols: ['NVDA', 'GOOGL', 'META'] },
      { type: '成长赛道', ratio: 25, symbols: ['IONQ', 'TSLA'] },
      { type: '期权增强', ratio: 20, symbols: ['Sell Put策略'] },
      { type: '现金储备', ratio: 15, symbols: ['现金'] }
    ]
  },
  {
    id: 'aggressive-tech',
    name: '科技激进策略',
    description: '重仓AI和前沿科技，追求高回报。适合能承受较大波动的投资者，包含量子计算、加密货币等高风险高回报标的。',
    risk_level: 4,
    min_capital: '20万+',
    expected_return: '20-35%',
    tags: ['高成长', '量子计算', '加密货币'],
    suitable_profiles: ['激进型', '专业投资者', '高回报追求'],
    allocations: [
      { type: 'AI龙头', ratio: 35, symbols: ['NVDA', 'GOOGL'] },
      { type: '量子计算', ratio: 20, symbols: ['IONQ'] },
      { type: '加密货币', ratio: 20, symbols: ['BTC', 'ETH'] },
      { type: '高Beta科技股', ratio: 15, symbols: ['TSLA', 'MARA'] },
      { type: '现金', ratio: 10, symbols: ['现金'] }
    ]
  },
  {
    id: 'sell-put-income',
    name: 'Sell Put收益策略',
    description: '专注于通过sell put期权策略获取权利金收入，特别适合震荡市或温和上涨市场。优先选择TSLA等高流动性标的，设置合理行权价。',
    risk_level: 2,
    min_capital: '15万+',
    expected_return: '10-15%',
    tags: ['期权策略', '权利金收入', 'TSLA'],
    suitable_profiles: ['稳健型', '有经验', '现金流需求'],
    allocations: [
      { type: 'Sell Put标的', ratio: 60, symbols: ['TSLA', 'NVDA', 'AAPL'] },
      { type: '备兑现金', ratio: 30, symbols: ['现金储备'] },
      { type: '核心持股', ratio: 10, symbols: ['GOOGL'] }
    ]
  },
  {
    id: 'crypto-hedge',
    name: '加密资产配置',
    description: '将加密货币作为资产配置的一部分，通过BTC和ETH获取数字黄金收益。建议通过ETF或小额直接配置，控制总体仓位。',
    risk_level: 4,
    min_capital: '10万+',
    expected_return: '25-50%',
    tags: ['加密货币', 'BTC', 'ETH', '数字黄金'],
    suitable_profiles: ['激进型', '长期投资者', '多元化配置'],
    allocations: [
      { type: '比特币', ratio: 50, symbols: ['BTC', 'ARKB'] },
      { type: '以太坊', ratio: 30, symbols: ['ETH'] },
      { type: '稳定币收益', ratio: 20, symbols: ['USDC', '稳定币理财'] }
    ]
  },
  {
    id: 'quantum-future',
    name: '量子计算前瞻',
    description: '提前布局量子计算赛道，以IONQ为核心标的。这是5-10年的长期赛道，适合能承受高波动、追求爆发性增长的投资者。',
    risk_level: 5,
    min_capital: '5万+',
    expected_return: '50%+',
    tags: ['量子计算', 'IONQ', '前沿科技', '高风险'],
    suitable_profiles: ['激进型', '专业投资者', '长期持有'],
    allocations: [
      { type: '量子计算核心', ratio: 60, symbols: ['IONQ'] },
      { type: 'AI配套', ratio: 25, symbols: ['NVDA', 'GOOGL'] },
      { type: '现金储备', ratio: 15, symbols: ['现金'] }
    ]
  }
];

class StrategyController {
  constructor() {
    // 绑定方法
    this.getStrategies = this.getStrategies.bind(this);
    this.getStrategy = this.getStrategy.bind(this);
    this.getProfile = this.getProfile.bind(this);
    this.saveProfile = this.saveProfile.bind(this);
    this.getRecommendations = this.getRecommendations.bind(this);
  }

  /**
   * 获取所有策略列表
   */
  async getStrategies(req, res) {
    try {
      const { user } = req;
      logger.info('获取策略列表', { user: user?.id });

      // 获取用户画像用于计算匹配度
      const profile = await this._getUserProfile(user?.id);

      // 计算每个策略的匹配度
      const strategies = STRATEGIES.map(s => ({
        ...s,
        match_score: this._calculateMatchScore(s, profile)
      }));

      res.status(200).json({
        success: true,
        count: strategies.length,
        strategies: strategies
      });
    } catch (error) {
      logger.error('获取策略列表失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取策略列表失败'
      });
    }
  }

  /**
   * 获取单个策略详情
   */
  async getStrategy(req, res) {
    try {
      const { id } = req.params;
      const { user } = req;

      logger.info('获取策略详情', { strategyId: id, user: user?.id });

      const strategy = STRATEGIES.find(s => s.id === id);
      if (!strategy) {
        return res.status(404).json({
          success: false,
          error: '策略不存在'
        });
      }

      // 获取用户画像
      const profile = await this._getUserProfile(user?.id);

      res.status(200).json({
        ...strategy,
        match_score: this._calculateMatchScore(strategy, profile),
        is_subscribed: false // 订阅功能已隐藏
      });
    } catch (error) {
      logger.error('获取策略详情失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取策略详情失败'
      });
    }
  }

  /**
   * 获取用户画像
   */
  async getProfile(req, res) {
    try {
      const { user } = req;
      const profile = await this._getUserProfile(user?.id);
      res.status(200).json({ success: true, ...profile });
    } catch (error) {
      logger.error('获取用户画像失败', { error: error.message });
      res.status(500).json({ success: false, error: '获取用户画像失败' });
    }
  }

  /**
   * 保存用户画像 - 持久化到数据库
   */
  async saveProfile(req, res) {
    try {
      const { user } = req;
      const profileData = req.body;
      const userId = user?.id;

      logger.info('保存用户画像', { user: userId, profile: profileData });

      const db = getDb();
      const now = new Date().toISOString();
      const existing = db.prepare(`SELECT id FROM user_profiles WHERE user_id = ?`).get(userId);

      if (existing) {
        db.prepare(`UPDATE user_profiles SET
          capital_scale = ?, risk_tolerance = ?, investment_goal = ?,
          experience_level = ?, time_horizon = ?, is_completed = 1, updated_at = ?
          WHERE user_id = ?`
        ).run(
          profileData.capital_scale || '中等',
          profileData.risk_tolerance || '平衡',
          profileData.investment_goal || '增值',
          profileData.experience_level || '有经验',
          profileData.time_horizon || '长期',
          now,
          userId
        );
      } else {
        db.prepare(`INSERT INTO user_profiles
          (id, user_id, capital_scale, risk_tolerance, investment_goal, experience_level, time_horizon, is_completed, created_at, updated_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)`
        ).run(
          (typeof uuidv4 === 'function' ? uuidv4() : `profile_${Date.now()}`),
          userId,
          profileData.capital_scale || '中等',
          profileData.risk_tolerance || '平衡',
          profileData.investment_goal || '增值',
          profileData.experience_level || '有经验',
          profileData.time_horizon || '长期',
          now, now
        );
      }

      const savedProfile = await this._getUserProfile(userId);
      res.status(200).json({ success: true, message: '画像保存成功', profile: savedProfile });
    } catch (error) {
      logger.error('保存用户画像失败', { error: error.message });
      res.status(500).json({ success: false, error: '保存用户画像失败' });
    }
  }

  /**
   * 获取推荐策略
   */
  async getRecommendations(req, res) {
    try {
      const { user } = req;
      const profile = await this._getUserProfile(user?.id);

      logger.info('获取推荐策略', { user: user?.id, profile });

      // 计算所有策略的匹配度并排序
      const strategies = STRATEGIES.map(s => ({
        ...s,
        match_score: this._calculateMatchScore(s, profile)
      })).sort((a, b) => b.match_score - a.match_score);

      // 返回前3个推荐
      const recommendations = strategies.slice(0, 3);

      res.status(200).json({
        success: true,
        count: recommendations.length,
        recommendations: recommendations
      });
    } catch (error) {
      logger.error('获取推荐策略失败', { error: error.message });
      res.status(500).json({
        success: false,
        error: '获取推荐策略失败'
      });
    }
  }

  /**
   * 获取用户画像（内部方法）- 从数据库读取
   */
  async _getUserProfile(userId) {
    try {
      const db = getDb();
      const row = db.prepare(`SELECT * FROM user_profiles WHERE user_id = ?`).get(userId);
      if (row && row.is_completed) {
        return {
          has_profile: true,
          is_completed: true,
          risk_tolerance: row.risk_tolerance || '平衡',
          capital_scale: row.capital_scale || '中等',
          experience_level: row.experience_level || '有经验',
          investment_goal: row.investment_goal || '增值',
          time_horizon: row.time_horizon || '长期',
          updated_at: row.updated_at,
        };
      }
    } catch (e) {
      logger.error('读取用户画像失败', { error: e.message });
    }
    // 默认画像（未完成测评）
    return {
      has_profile: false,
      is_completed: false,
      risk_tolerance: '平衡',
      capital_scale: '中等',
      experience_level: '有经验',
      investment_goal: '增值',
      time_horizon: '长期'
    };
  }

  /**
   * 计算策略匹配度
   */
  _calculateMatchScore(strategy, profile) {
    if (!profile || !profile.has_profile) {
      return Math.floor(Math.random() * 20) + 60; // 默认60-80分
    }

    let score = 70;

    // 风险等级匹配
    const riskMap = { '保守': 1, '稳健': 2, '平衡': 3, '激进': 4 };
    const userRisk = riskMap[profile.risk_tolerance] || 3;
    const riskDiff = Math.abs(strategy.risk_level - userRisk);
    score -= riskDiff * 10;

    // 资金规模匹配
    if (profile.capital_scale === '小资金' && strategy.min_capital.includes('20万')) {
      score -= 15;
    }

    // 经验水平匹配
    if (profile.experience_level === '小白' && strategy.risk_level >= 4) {
      score -= 15;
    }

    // 投资目标匹配
    if (profile.investment_goal === '保值' && strategy.risk_level <= 2) {
      score += 10;
    }
    if (profile.investment_goal === '高回报' && strategy.risk_level >= 4) {
      score += 10;
    }

    // 确保分数在合理范围
    return Math.max(50, Math.min(95, score));
  }
}

module.exports = new StrategyController();
