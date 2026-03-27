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

module.exports = router;
