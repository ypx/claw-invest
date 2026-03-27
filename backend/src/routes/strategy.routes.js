const express = require('express');
const router = express.Router();
const strategyController = require('../controllers/strategy.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

// 开发环境使用mock认证，生产环境使用真实认证
if (config.app.env === 'development') {
  router.use(mockAuthenticate);
} else {
  router.use(authenticate);
}

// 获取所有策略列表
router.get('/list', strategyController.getStrategies);

// 获取推荐策略
router.get('/recommend', strategyController.getRecommendations);

// 获取用户画像
router.get('/profile', strategyController.getProfile);

// 保存用户画像
router.post('/profile', strategyController.saveProfile);

// 获取单个策略详情
router.get('/:id', strategyController.getStrategy);

module.exports = router;
