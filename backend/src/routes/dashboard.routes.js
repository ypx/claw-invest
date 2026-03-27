const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboard.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

// 开发环境使用mock认证
if (config.app.env === 'development') {
  router.use(mockAuthenticate);
} else {
  router.use(authenticate);
}

// 主仪表板数据
router.get('/', dashboardController.getDashboard);

// TSLA 专项情报
router.get('/tsla', dashboardController.getTslaIntel);

module.exports = router;
