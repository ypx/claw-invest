const express = require('express');
const router = express.Router();
const optionsController = require('../controllers/options.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

// 开发环境使用mock认证，生产环境使用真实认证
if (config.app.env === 'development') {
  router.use(mockAuthenticate);
} else {
  router.use(authenticate);
}

// 获取动态期权策略推荐
router.get('/strategies', optionsController.getDynamicStrategies);

module.exports = router;
