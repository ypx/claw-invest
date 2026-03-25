const express = require('express');
const router = express.Router();
const stockController = require('../controllers/stock.controller');
const { authenticate } = require('../middleware/auth.middleware');

// 公开路由（无需认证）
router.get('/list', stockController.getAllStocks);
router.get('/symbols', stockController.getStockSymbols);
router.get('/info/:symbol', stockController.getStockInfo);
router.get('/prices/:symbol', stockController.getStockPrices);

// 需要认证的路由
router.use(authenticate);

router.get('/analysis/:symbol', stockController.analyzeStock);
router.get('/analysis', stockController.analyzeAllStocks);
router.get('/recommendations/top', stockController.getTopRecommendations);
router.get('/dashboard', stockController.getDashboardData);
router.post('/screener', stockController.runStockScreener);

module.exports = router;