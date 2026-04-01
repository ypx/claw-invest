const express = require('express');
const router = express.Router();
const optionsController = require('../controllers/options.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');
const { getDb } = require('../models/db');
const crypto = require('crypto');

// 开发环境使用mock认证，生产环境使用真实认证
const authMiddleware = config.app.env === 'development' ? mockAuthenticate : authenticate;
router.use(authMiddleware);

// 获取动态期权策略推荐
router.get('/strategies', optionsController.getDynamicStrategies);

// GET /api/options/positions — 获取持仓列表
router.get('/positions', (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const positions = db.prepare(
      `SELECT * FROM option_positions WHERE user_id = ? ORDER BY opened_at DESC`
    ).all(userId);
    const openPositions = positions.filter(p => p.status === 'open');
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
      open_count: openPositions.length,
      total_open_contracts: openPositions.reduce((s, p) => s + p.contracts, 0),
      total_open_premium: openPositions.reduce((s, p) => s + p.premium * p.contracts * 100, 0),
      total_realized_pnl: parseFloat(totalRealizedPnl.toFixed(2)),
    };
    res.json({ positions, summary });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// GET /api/options/stats — 统计
router.get('/stats', (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const positions = db.prepare(`SELECT * FROM option_positions WHERE user_id = ?`).all(userId);
    const bySymbol = {};
    for (const p of positions) {
      if (!bySymbol[p.symbol]) bySymbol[p.symbol] = { symbol: p.symbol, count: 0, open_count: 0, premium: 0 };
      bySymbol[p.symbol].count++;
      bySymbol[p.symbol].premium += p.premium * p.contracts * 100;
      if (p.status === 'open') {
        bySymbol[p.symbol].open_count += (p.contracts || 1);
      }
    }
    const closed = positions.filter(p => p.status !== 'open');
    const wins = closed.filter(p => p.status === 'expired').length;
    let totalRealizedPnl = 0;
    for (const p of closed) {
      const grossPremium = p.premium * p.contracts * 100;
      if (p.status === 'expired') {
        totalRealizedPnl += grossPremium;
      } else if (p.status === 'closed') {
        const closeCost = (p.close_price || 0) * p.contracts * 100;
        const isShort = !p.direction || p.direction === 'sell';
        totalRealizedPnl += isShort ? (grossPremium - closeCost) : (closeCost - grossPremium);
      }
    }
    res.json({
      by_symbol: Object.values(bySymbol),
      win_rate: closed.length > 0 ? parseFloat((wins / closed.length * 100).toFixed(1)) : 0,
      total_count: positions.length,
      total_trades: closed.length,
      total_realized_pnl: parseFloat(totalRealizedPnl.toFixed(2)),
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// POST /api/options/positions — 记录开仓
router.post('/positions', (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const { symbol, option_type, direction, strike_price, expiration, contracts, premium, open_price, note } = req.body;
    if (!symbol || !option_type || !strike_price || !expiration || !contracts || premium === undefined) {
      return res.status(400).json({ detail: '缺少必要字段' });
    }
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    db.prepare(`
      INSERT INTO option_positions (id, user_id, symbol, option_type, direction, strike_price, expiration, contracts, premium, open_price, status, note, opened_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
    `).run(id, userId, symbol.toUpperCase(), option_type, direction || 'sell', strike_price, expiration, contracts, premium, open_price || null, note || null, now, now);
    res.json({ success: true, id });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// PATCH /api/options/positions/:id/close — 结束持仓
router.patch('/positions/:id/close', (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const { id } = req.params;
    const { close_price, status } = req.body;
    if (!status || !['closed', 'expired', 'assigned'].includes(status)) {
      return res.status(400).json({ detail: '无效的结束方式' });
    }
    const pos = db.prepare(`SELECT * FROM option_positions WHERE id = ? AND user_id = ?`).get(id, userId);
    if (!pos) {
      return res.status(404).json({ detail: '持仓不存在' });
    }
    if (pos.status !== 'open') {
      return res.status(400).json({ detail: '该持仓已结束' });
    }
    const now = new Date().toISOString();
    db.prepare(`
      UPDATE option_positions SET status = ?, close_price = ?, closed_at = ?, updated_at = ?
      WHERE id = ? AND user_id = ?
    `).run(status, close_price || 0, now, now, id, userId);
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

// DELETE /api/options/positions/:id — 删除记录
router.delete('/positions/:id', (req, res) => {
  try {
    const db = getDb();
    const userId = req.user?.id;
    const { id } = req.params;
    const result = db.prepare(`DELETE FROM option_positions WHERE id = ? AND user_id = ?`).run(id, userId);
    if (result.changes === 0) {
      return res.status(404).json({ detail: '记录不存在' });
    }
    res.json({ success: true });
  } catch (e) {
    res.status(500).json({ detail: e.message });
  }
});

module.exports = router;
