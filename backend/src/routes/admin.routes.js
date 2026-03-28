const express = require('express');
const bcrypt = require('bcrypt');
const { getDb } = require('../models/db');
const { authenticate, mockAuthenticate, authorize } = require('../middleware/auth.middleware');
const { config } = require('../config/config');
const { logger } = require('../utils/logger');

const router = express.Router();

// 认证 + 管理员权限
const authMiddleware = config.app.env === 'development' ? mockAuthenticate : authenticate;
router.use(authMiddleware);
router.use(authorize(['admin']));

/**
 * GET /api/admin/users
 * 获取所有用户列表及平台统计
 */
router.get('/users', (req, res) => {
  try {
    const db = getDb();
    const users = db.prepare(
      `SELECT id, username, email, role, is_active, last_login, created_at FROM users ORDER BY created_at DESC`
    ).all();

    const totalHoldings = db.prepare(`SELECT COUNT(*) as cnt FROM holdings`).get()?.cnt || 0;
    const totalOptions = db.prepare(`SELECT COUNT(*) as cnt FROM option_positions`).get()?.cnt || 0;

    res.json({
      users,
      stats: {
        total_users: users.length,
        total_holdings: totalHoldings,
        total_options: totalOptions,
      }
    });
  } catch (e) {
    logger.error('admin/users error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * PATCH /api/admin/users/:id/reset-password
 * 管理员重置指定用户密码
 */
router.patch('/users/:id/reset-password', async (req, res) => {
  try {
    const { new_password } = req.body;
    if (!new_password || new_password.length < 6) {
      return res.status(400).json({ detail: '密码至少6位' });
    }

    const db = getDb();
    const user = db.prepare(`SELECT id, username FROM users WHERE id = ?`).get(req.params.id);
    if (!user) {
      return res.status(404).json({ detail: '用户不存在' });
    }

    const hashed = await bcrypt.hash(new_password, 12);
    db.prepare(`UPDATE users SET hashed_pw = ? WHERE id = ?`).run(hashed, req.params.id);

    logger.info(`管理员重置密码: ${user.username} (操作者: ${req.user?.id})`);
    res.json({ message: `用户 ${user.username} 密码已重置` });
  } catch (e) {
    logger.error('reset-password error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * PATCH /api/admin/users/:id/toggle
 * 切换用户启用/禁用状态
 */
router.patch('/users/:id/toggle', (req, res) => {
  try {
    const db = getDb();
    const user = db.prepare(`SELECT id, username, is_active FROM users WHERE id = ?`).get(req.params.id);
    if (!user) {
      return res.status(404).json({ detail: '用户不存在' });
    }

    // 不允许禁用自己
    if (user.id === req.user?.id) {
      return res.status(400).json({ detail: '不能禁用自己的账号' });
    }

    const newActive = user.is_active ? 0 : 1;
    db.prepare(`UPDATE users SET is_active = ? WHERE id = ?`).run(newActive, req.params.id);

    logger.info(`管理员${newActive?'启用':'禁用'}用户: ${user.username}`);
    res.json({ message: `${newActive ? '已启用' : '已禁用'}用户 ${user.username}`, is_active: newActive });
  } catch (e) {
    logger.error('toggle user error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════════════════
// 持仓管理（管理员可管理所有用户的持仓）
// ═══════════════════════════════════════════════════════════════

/**
 * GET /api/admin/holdings
 * 获取所有用户的股票持仓列表
 */
router.get('/holdings', (req, res) => {
  try {
    const db = getDb();
    const holdings = db.prepare(`
      SELECT h.*, u.username 
      FROM holdings h 
      LEFT JOIN users u ON h.user_id = u.id 
      ORDER BY h.updated_at DESC
    `).all();
    res.json({ holdings });
  } catch (e) {
    logger.error('admin/holdings error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * POST /api/admin/holdings
 * 管理员为用户添加持仓
 */
router.post('/holdings', (req, res) => {
  try {
    const db = getDb();
    const { user_id, symbol, shares, avg_cost, sector, notes } = req.body;
    
    if (!user_id || !symbol || !shares || avg_cost === undefined) {
      return res.status(400).json({ detail: '缺少必要字段: user_id, symbol, shares, avg_cost' });
    }
    
    // 验证用户存在
    const user = db.prepare(`SELECT id FROM users WHERE id = ?`).get(user_id);
    if (!user) {
      return res.status(404).json({ detail: '用户不存在' });
    }
    
    const id = require('crypto').randomUUID();
    const now = new Date().toISOString();
    
    db.prepare(`
      INSERT INTO holdings (id, user_id, symbol, shares, avg_cost, sector, notes, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(id, user_id, symbol.toUpperCase(), shares, avg_cost, sector || null, notes || null, now, now);
    
    logger.info(`管理员添加持仓: ${symbol} for user ${user_id}`);
    res.json({ success: true, id, message: '持仓添加成功' });
  } catch (e) {
    logger.error('admin/holdings POST error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * PATCH /api/admin/holdings/:id
 * 管理员更新持仓
 */
router.patch('/holdings/:id', (req, res) => {
  try {
    const db = getDb();
    const { symbol, shares, avg_cost, sector, notes } = req.body;
    
    const holding = db.prepare(`SELECT * FROM holdings WHERE id = ?`).get(req.params.id);
    if (!holding) {
      return res.status(404).json({ detail: '持仓不存在' });
    }
    
    const now = new Date().toISOString();
    db.prepare(`
      UPDATE holdings 
      SET symbol = COALESCE(?, symbol), 
          shares = COALESCE(?, shares), 
          avg_cost = COALESCE(?, avg_cost),
          sector = COALESCE(?, sector),
          notes = COALESCE(?, notes),
          updated_at = ?
      WHERE id = ?
    `).run(
      symbol ? symbol.toUpperCase() : null,
      shares !== undefined ? shares : null,
      avg_cost !== undefined ? avg_cost : null,
      sector || null,
      notes !== undefined ? notes : null,
      now,
      req.params.id
    );
    
    logger.info(`管理员更新持仓: ${holding.symbol} (${req.params.id})`);
    res.json({ success: true, message: '持仓更新成功' });
  } catch (e) {
    logger.error('admin/holdings PATCH error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * DELETE /api/admin/holdings/:id
 * 管理员删除持仓
 */
router.delete('/holdings/:id', (req, res) => {
  try {
    const db = getDb();
    const holding = db.prepare(`SELECT * FROM holdings WHERE id = ?`).get(req.params.id);
    if (!holding) {
      return res.status(404).json({ detail: '持仓不存在' });
    }
    
    db.prepare(`DELETE FROM holdings WHERE id = ?`).run(req.params.id);
    logger.info(`管理员删除持仓: ${holding.symbol} (${req.params.id})`);
    res.json({ success: true, message: '持仓已删除' });
  } catch (e) {
    logger.error('admin/holdings DELETE error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

// ═══════════════════════════════════════════════════════════════
// 期权持仓管理（管理员可管理所有用户的期权持仓）
// ═══════════════════════════════════════════════════════════════

/**
 * GET /api/admin/options
 * 获取所有用户的期权持仓列表
 */
router.get('/options', (req, res) => {
  try {
    const db = getDb();
    const positions = db.prepare(`
      SELECT o.*, u.username 
      FROM option_positions o 
      LEFT JOIN users u ON o.user_id = u.id 
      ORDER BY o.opened_at DESC
    `).all();
    res.json({ positions });
  } catch (e) {
    logger.error('admin/options error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * POST /api/admin/options
 * 管理员为用户添加期权持仓
 */
router.post('/options', (req, res) => {
  try {
    const db = getDb();
    const { user_id, symbol, option_type, direction, strike_price, expiration, contracts, premium, open_price, note } = req.body;
    
    if (!user_id || !symbol || !option_type || !strike_price || !expiration || !contracts || premium === undefined) {
      return res.status(400).json({ detail: '缺少必要字段' });
    }
    
    // 验证用户存在
    const user = db.prepare(`SELECT id FROM users WHERE id = ?`).get(user_id);
    if (!user) {
      return res.status(404).json({ detail: '用户不存在' });
    }
    
    const id = require('crypto').randomUUID();
    const now = new Date().toISOString();
    
    db.prepare(`
      INSERT INTO option_positions (id, user_id, symbol, option_type, direction, strike_price, expiration, contracts, premium, open_price, status, note, opened_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
    `).run(id, user_id, symbol.toUpperCase(), option_type, direction || 'sell', strike_price, expiration, contracts, premium, open_price || null, note || null, now, now);
    
    logger.info(`管理员添加期权持仓: ${symbol} ${option_type} for user ${user_id}`);
    res.json({ success: true, id, message: '期权持仓添加成功' });
  } catch (e) {
    logger.error('admin/options POST error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * PATCH /api/admin/options/:id
 * 管理员更新期权持仓
 */
router.patch('/options/:id', (req, res) => {
  try {
    const db = getDb();
    const { symbol, option_type, direction, strike_price, expiration, contracts, premium, note } = req.body;
    
    const pos = db.prepare(`SELECT * FROM option_positions WHERE id = ?`).get(req.params.id);
    if (!pos) {
      return res.status(404).json({ detail: '期权持仓不存在' });
    }
    
    const now = new Date().toISOString();
    db.prepare(`
      UPDATE option_positions 
      SET symbol = COALESCE(?, symbol), 
          option_type = COALESCE(?, option_type), 
          direction = COALESCE(?, direction),
          strike_price = COALESCE(?, strike_price),
          expiration = COALESCE(?, expiration),
          contracts = COALESCE(?, contracts),
          premium = COALESCE(?, premium),
          note = COALESCE(?, note),
          updated_at = ?
      WHERE id = ?
    `).run(
      symbol ? symbol.toUpperCase() : null,
      option_type || null,
      direction || null,
      strike_price !== undefined ? strike_price : null,
      expiration || null,
      contracts !== undefined ? contracts : null,
      premium !== undefined ? premium : null,
      note !== undefined ? note : null,
      now,
      req.params.id
    );
    
    logger.info(`管理员更新期权持仓: ${pos.symbol} (${req.params.id})`);
    res.json({ success: true, message: '期权持仓更新成功' });
  } catch (e) {
    logger.error('admin/options PATCH error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

/**
 * DELETE /api/admin/options/:id
 * 管理员删除期权持仓
 */
router.delete('/options/:id', (req, res) => {
  try {
    const db = getDb();
    const pos = db.prepare(`SELECT * FROM option_positions WHERE id = ?`).get(req.params.id);
    if (!pos) {
      return res.status(404).json({ detail: '期权持仓不存在' });
    }
    
    db.prepare(`DELETE FROM option_positions WHERE id = ?`).run(req.params.id);
    logger.info(`管理员删除期权持仓: ${pos.symbol} (${req.params.id})`);
    res.json({ success: true, message: '期权持仓已删除' });
  } catch (e) {
    logger.error('admin/options DELETE error', { error: e.message });
    res.status(500).json({ error: e.message });
  }
});

module.exports = router;
