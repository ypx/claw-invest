const express = require('express');
const router = express.Router();
const stockController = require('../controllers/stock.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

// 开发环境使用mock认证，生产环境使用真实认证
if (config.app.env === 'development') {
  router.use(mockAuthenticate);
} else {
  router.use(authenticate);
}

// 公开路由（无需认证）
router.get('/list', stockController.getAllStocks);
router.get('/symbols', stockController.getStockSymbols);
router.get('/info/:symbol', stockController.getStockInfo);
router.get('/prices/:symbol', stockController.getStockPrices);

// 需要认证的路由
router.get('/analysis/:symbol', stockController.analyzeStock);
router.get('/analysis', stockController.analyzeAllStocks);
router.get('/recommendations/top', stockController.getTopRecommendations);
router.get('/dashboard', stockController.getDashboardData);
router.post('/screener', stockController.runStockScreener);

module.exports = router;