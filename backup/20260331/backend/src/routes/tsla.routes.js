const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboard.controller');
const { authenticate, mockAuthenticate } = require('../middleware/auth.middleware');
const { config } = require('../config/config');

if (config.app.env === 'development') {
  router.use(mockAuthenticate);
} else {
  router.use(authenticate);
}

router.get('/intel', dashboardController.getTslaIntel);

module.exports = router;
