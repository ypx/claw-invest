const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const multer = require('multer');
const { getDb } = require('../models/db');
const { config } = require('../config/config');
const { logger } = require('../utils/logger');

const router = express.Router();
const upload = multer(); // 内存存储，仅解析字段

const JWT_SECRET = config.jwt?.secret || process.env.JWT_SECRET || 'claw-secret-key-2026';
const JWT_EXPIRES_IN = '7d';

/**
 * POST /api/auth/login
 * 支持 FormData (multipart/form-data) 和 JSON 两种格式
 */
router.post('/login', upload.none(), async (req, res) => {
  try {
    // multer 处理了 FormData，express.json 处理了 JSON
    const username = req.body?.username;
    const password = req.body?.password;

    if (!username || !password) {
      return res.status(400).json({ detail: '用户名和密码不能为空' });
    }

    const db = getDb();
    // 支持用用户名或邮箱登录
    const user = db.prepare(
      `SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1`
    ).get(username, username);

    if (!user) {
      return res.status(401).json({ detail: '用户名或密码错误' });
    }

    // 验证密码
    const isValid = await bcrypt.compare(password, user.hashed_pw);
    if (!isValid) {
      return res.status(401).json({ detail: '用户名或密码错误' });
    }

    // 更新最后登录时间
    db.prepare(`UPDATE users SET last_login = ? WHERE id = ?`)
      .run(new Date().toISOString(), user.id);

    // 生成 JWT
    const token = jwt.sign(
      { id: user.id, username: user.username, email: user.email, role: user.role },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    logger.info(`用户登录成功: ${user.username}`);

    return res.json({
      access_token: token,
      token_type: 'bearer',
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
      }
    });

  } catch (e) {
    logger.error('登录失败', { error: e.message });
    return res.status(500).json({ detail: '服务器内部错误' });
  }
});

/**
 * POST /api/auth/register
 * body: JSON { username, email, password }
 */
router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ detail: '用户名、邮箱和密码均为必填项' });
    }
    if (username.length < 2 || username.length > 20) {
      return res.status(400).json({ detail: '用户名需2-20位字符' });
    }
    if (password.length < 6) {
      return res.status(400).json({ detail: '密码至少6位' });
    }

    const db = getDb();

    // 检查用户名/邮箱是否重复
    const existing = db.prepare(
      `SELECT id FROM users WHERE username = ? OR email = ?`
    ).get(username, email);

    if (existing) {
      return res.status(409).json({ detail: '用户名或邮箱已被注册' });
    }

    // 哈希密码
    const hashed_pw = await bcrypt.hash(password, 12);
    const id = uuidv4();
    const now = new Date().toISOString();

    db.prepare(
      `INSERT INTO users (id, username, email, hashed_pw, role, created_at, is_active, profile)
       VALUES (?, ?, ?, ?, 'user', ?, 1, '{}')`
    ).run(id, username, email, hashed_pw, now);

    // 生成 JWT
    const token = jwt.sign(
      { id, username, email, role: 'user' },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    logger.info(`新用户注册: ${username}`);

    return res.status(201).json({
      access_token: token,
      token_type: 'bearer',
      user: { id, username, email, role: 'user' }
    });

  } catch (e) {
    logger.error('注册失败', { error: e.message });
    return res.status(500).json({ detail: '服务器内部错误' });
  }
});

/**
 * GET /api/auth/me
 * 需要 Authorization: Bearer <token>
 */
router.get('/me', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: '未登录' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const db = getDb();
    const user = db.prepare(`SELECT id, username, email, role FROM users WHERE id = ?`).get(decoded.id);
    if (!user) {
      return res.status(401).json({ detail: '用户不存在' });
    }
    return res.json(user);
  } catch (e) {
    return res.status(401).json({ detail: 'token 无效或已过期' });
  }
});

/**
 * POST /api/auth/logout
 */
router.post('/logout', (req, res) => {
  // JWT 是无状态的，客户端删除 token 即可
  return res.json({ message: '已登出' });
});

/**
 * POST /api/auth/change-password
 * 用户修改自己的密码（需登录）
 * body: JSON { current_password, new_password }
 */
router.post('/change-password', async (req, res) => {
  // 验证 token
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ detail: '未登录' });
  }
  const token = authHeader.split(' ')[1];
  let decoded;
  try {
    decoded = jwt.verify(token, JWT_SECRET);
  } catch (e) {
    return res.status(401).json({ detail: 'token 无效或已过期' });
  }

  try {
    const { current_password, new_password } = req.body;
    if (!current_password || !new_password) {
      return res.status(400).json({ detail: '当前密码和新密码不能为空' });
    }
    if (new_password.length < 6) {
      return res.status(400).json({ detail: '新密码至少6位' });
    }
    if (current_password === new_password) {
      return res.status(400).json({ detail: '新密码不能与当前密码相同' });
    }

    const db = getDb();
    const user = db.prepare(`SELECT * FROM users WHERE id = ?`).get(decoded.id);
    if (!user) {
      return res.status(404).json({ detail: '用户不存在' });
    }

    // 验证当前密码
    const isValid = await bcrypt.compare(current_password, user.hashed_pw);
    if (!isValid) {
      return res.status(401).json({ detail: '当前密码不正确' });
    }

    // 更新密码
    const hashed = await bcrypt.hash(new_password, 12);
    db.prepare(`UPDATE users SET hashed_pw = ? WHERE id = ?`).run(hashed, decoded.id);

    logger.info(`用户修改密码: ${user.username}`);
    return res.json({ message: '密码修改成功' });
  } catch (e) {
    logger.error('修改密码失败', { error: e.message });
    return res.status(500).json({ detail: '服务器内部错误' });
  }
});

module.exports = router;
