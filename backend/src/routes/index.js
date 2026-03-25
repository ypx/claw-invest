const express = require('express');
const stockRoutes = require('./stock.routes');
const portfolioRoutes = require('./portfolio.routes');
const authRoutes = require('./auth.routes');

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

// API版本信息
router.get('/version', (req, res) => {
  res.status(200).json({
    api: 'Claw Advisor Investment API',
    version: 'v1.0.0',
    description: '基于Mike是麥克投资体系的保守型投资决策系统',
    author: 'A (AI Assistant) for Z',
    updatedAt: '2026-03-23',
  });
});

// 模块路由
router.use('/stocks', stockRoutes);
router.use('/portfolio', portfolioRoutes);
router.use('/auth', authRoutes);

module.exports = router;