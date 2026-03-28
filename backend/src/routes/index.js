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

// 期权策略与持仓（包含 /positions, /stats, /strategies 等）
router.use('/options', optionsRoutes);

// 投资策略
router.use('/strategy', strategyRoutes);

module.exports = router;
