const express = require('express');
const stockRoutes = require('./stock.routes');
const optionsRoutes = require('./options.routes');
const strategyRoutes = require('./strategy.routes');
const dashboardRoutes = require('./dashboard.routes');
const portfolioRoutes = require('./portfolio.routes');
const userRoutes = require('./user.routes');
const tslaRoutes = require('./tsla.routes');
const authRoutes = require('./auth.routes');
const adminRoutes = require('./admin.routes');

const router = express.Router();

// 健康检查
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'Claw Advisor API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// 认证（无需 token）
router.use('/auth', authRoutes);                 // POST /api/auth/login, /register, GET /api/auth/me

// 管理员后台
router.use('/admin', adminRoutes);               // GET /api/admin/users, PATCH /api/admin/users/:id/...

// 核心数据路由
router.use('/dashboard', dashboardRoutes);      // GET /api/dashboard
router.use('/portfolio', portfolioRoutes);       // GET/POST/DELETE /api/portfolio/holdings
router.use('/user', userRoutes);                 // PATCH /api/user/profile
router.use('/tsla', tslaRoutes);                 // GET /api/tsla/intel

// 股票相关
router.use('/stocks', stockRoutes);

// 期权策略与持仓
router.use('/options', optionsRoutes);

// 期权持仓简化路由（直接在这里处理，从数据库读取）
const { getDb } = require('../models/db');
const { mockAuthenticate, authenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

const authMiddleware = config.app.env === 'development' ? mockAuthenticate : authenticate;

router.get('/options/positions', authMiddleware, (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const positions = db.prepare(
      `SELECT * FROM option_positions WHERE user_id = ? ORDER BY opened_at DESC`
    ).all(userId);
    const openPositions = positions.filter(p => p.status === 'open');
    // 计算已实现盈亏
    let totalRealizedPnl = 0;
    positions.filter(p => p.status !== 'open').forEach(p => {
      const grossPremium = p.premium * p.contracts * 100;
      if (p.status === 'expired') {
        totalRealizedPnl += grossPremium;
      } else if (p.status === 'closed') {
        const closeCost = (p.close_price || 0) * p.contracts * 100;
        const isShort = !p.direction || p.direction === 'sell';
        totalRealizedPnl += isShort ? (grossPremium - closeCost) : (closeCost - grossPremium);
      }
    });
    const summary = {
      open_count: openPositions.length,  // 修复：补充 open_count 字段
      total_open_contracts: openPositions.reduce((s, p) => s + p.contracts, 0),
      total_open_premium: openPositions.reduce((s, p) => s + p.premium * p.contracts * 100, 0),
      total_realized_pnl: parseFloat(totalRealizedPnl.toFixed(2)),
    };
    res.json({ positions, summary });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

router.get('/options/stats', authMiddleware, (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const positions = db.prepare(`SELECT * FROM option_positions WHERE user_id = ?`).all(userId);
    const bySymbol = {};
    for (const p of positions) {
      if (!bySymbol[p.symbol]) bySymbol[p.symbol] = { symbol: p.symbol, count: 0, premium: 0 };
      bySymbol[p.symbol].count++;
      bySymbol[p.symbol].premium += p.premium * p.contracts * 100;
    }
    const closed = positions.filter(p => p.status !== 'open');
    const wins = closed.filter(p => p.status === 'expired').length;

    // 计算已实现盈亏：到期归零 = 全收权利金；平仓 = 权利金 - 平仓成本；行权另计
    let totalRealizedPnl = 0;
    for (const p of closed) {
      const grossPremium = p.premium * p.contracts * 100;
      if (p.status === 'expired') {
        totalRealizedPnl += grossPremium; // 全部收入
      } else if (p.status === 'closed') {
        const closeCost = (p.close_price || 0) * p.contracts * 100;
        const isShort = !p.direction || p.direction === 'sell';
        totalRealizedPnl += isShort ? (grossPremium - closeCost) : (closeCost - grossPremium);
      }
      // assigned 暂不计入盈亏（需人工核算正股）
    }

    res.json({
      by_symbol: Object.values(bySymbol),
      win_rate: closed.length > 0 ? parseFloat((wins / closed.length * 100).toFixed(1)) : 0,
      total_count: positions.length,
      total_trades: closed.length,          // 前端需要：已结束交易数
      total_realized_pnl: parseFloat(totalRealizedPnl.toFixed(2)), // 前端需要：已实现盈亏
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 投资策略
router.use('/strategy', strategyRoutes);

module.exports = router;
