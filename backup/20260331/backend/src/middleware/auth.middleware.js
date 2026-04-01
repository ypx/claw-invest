const jwt = require('jsonwebtoken');
const { config } = require('../config/config');
const { logger } = require('../utils/logger');

/**
 * 认证中间件
 * 验证JWT token并附加用户信息到request对象
 */
const authenticate = (req, res, next) => {
  try {
    // 从请求头获取token
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      logger.warn('认证失败: 缺少或格式错误的Authorization头', { ip: req.ip });
      return res.status(401).json({
        success: false,
        error: '未授权',
        message: '需要有效的Bearer token',
      });
    }

    const token = authHeader.split(' ')[1];
    
    try {
      // 验证token
      const decoded = jwt.verify(token, config.jwt.secret);
      
      // 检查token是否过期
      const now = Math.floor(Date.now() / 1000);
      if (decoded.exp && decoded.exp < now) {
        logger.warn('认证失败: token已过期', { userId: decoded.id, ip: req.ip });
        return res.status(401).json({
          success: false,
          error: '未授权',
          message: 'Token已过期',
        });
      }

      // 附加用户信息到request对象
      req.user = {
        id: decoded.id,
        email: decoded.email,
        role: decoded.role || 'user',
      };

      logger.debug('认证成功', { userId: decoded.id, ip: req.ip });
      next();
    } catch (jwtError) {
      logger.warn('认证失败: JWT验证错误', { error: jwtError.message, ip: req.ip });
      return res.status(401).json({
        success: false,
        error: '未授权',
        message: '无效的token',
      });
    }
  } catch (error) {
    logger.error('认证中间件错误', { error: error.message, ip: req.ip });
    return res.status(500).json({
      success: false,
      error: '服务器错误',
      message: '认证过程中发生错误',
    });
  }
};

/**
 * 角色检查中间件
 * 验证用户是否具有指定角色
 */
const authorize = (roles = []) => {
  return (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          success: false,
          error: '未授权',
          message: '需要先进行认证',
        });
      }

      if (roles.length > 0 && !roles.includes(req.user.role)) {
        logger.warn('权限不足', { 
          userId: req.user.id, 
          requiredRoles: roles, 
          userRole: req.user.role,
          ip: req.ip 
        });
        return res.status(403).json({
          success: false,
          error: '权限不足',
          message: '您没有执行此操作的权限',
        });
      }

      next();
    } catch (error) {
      logger.error('角色检查中间件错误', { error: error.message, ip: req.ip });
      return res.status(500).json({
        success: false,
        error: '服务器错误',
        message: '权限检查过程中发生错误',
      });
    }
  };
};

/**
 * 生成JWT token
 */
const generateToken = (user) => {
  const payload = {
    id: user.id,
    email: user.email,
    role: user.role || 'user',
  };

  return jwt.sign(payload, config.jwt.secret, {
    expiresIn: config.jwt.expiresIn,
    issuer: 'claw-advisor-api',
    audience: 'claw-advisor-web',
  });
};

/**
 * 开发环境模拟用户（用于测试）
 * 优先使用JWT token中的真实用户信息，如果没有token则使用默认用户
 */
const mockAuthenticate = (req, res, next) => {
  // 首先尝试读取 JWT token（如果有）
  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.split(' ')[1];
    try {
      const decoded = jwt.verify(token, config.jwt.secret);
      req.user = { 
        id: decoded.id, 
        email: decoded.email, 
        role: decoded.role || 'user' 
      };
      logger.debug('开发环境使用JWT认证', { userId: decoded.id, email: decoded.email });
      return next();
    } catch (e) {
      // token 无效，继续用默认 mock 用户
      logger.debug('JWT验证失败，使用默认mock用户', { error: e.message });
    }
  }

  // 开发环境：没有有效token时使用默认mock用户
  if (config.app.env === 'development') {
    // 检查是否是访问 admin 路由，如果是则使用 admin 角色
    const isAdminRoute = req.originalUrl?.includes('/admin') || req.path?.includes('/admin');
    req.user = {
      id: isAdminRoute ? 'admin-mock-id' : '5d67698d-132f-48f1-9e0c-fab1c4fa4479',
      email: isAdminRoute ? 'admin@claw.app' : 'z@claw.app',
      role: isAdminRoute ? 'admin' : 'user',
      name: isAdminRoute ? 'Admin' : 'Z',
    };
    logger.debug(`使用开发环境默认mock用户 (${isAdminRoute ? 'Admin' : 'Z用户'})`, { userId: req.user.id, ip: req.ip });
    return next();
  }

  // 生产环境：没有token则拒绝访问
  return res.status(401).json({
    success: false,
    error: '未授权',
    message: '需要有效的Bearer token',
  });
};

module.exports = {
  authenticate,
  authorize,
  generateToken,
  mockAuthenticate,
};