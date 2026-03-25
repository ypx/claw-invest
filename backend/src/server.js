const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { config, validateConfig } = require('./config/config');
const { logger } = require('./utils/logger');
const routes = require('./routes');

// 创建Express应用
const app = express();

// 验证配置
try {
  validateConfig();
} catch (error) {
  logger.error(`配置验证失败: ${error.message}`);
  process.exit(1);
}

// 安全中间件
app.use(helmet(config.security.helmet));

// CORS配置
app.use(cors(config.cors));

// 请求日志
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));

// 请求体解析
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 速率限制
const limiter = rateLimit({
  windowMs: config.security.rateLimit.windowMs,
  max: config.security.rateLimit.max,
  message: { error: '请求过于频繁，请稍后再试' },
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: config.app.name,
    version: '1.0.0',
    environment: config.app.env,
  });
});

// API路由
app.use(config.api.prefix, routes);

// 404处理
app.use((req, res) => {
  res.status(404).json({
    error: '未找到请求的资源',
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString(),
  });
});

// 全局错误处理
app.use((err, req, res, next) => {
  logger.error(`全局错误: ${err.message}`, { stack: err.stack });

  const statusCode = err.statusCode || 500;
  const message = config.app.env === 'production' 
    ? '服务器内部错误' 
    : err.message;

  res.status(statusCode).json({
    error: message,
    ...(config.app.env === 'development' && { stack: err.stack }),
    timestamp: new Date().toISOString(),
  });
});

// 启动服务器
const startServer = () => {
  const server = app.listen(config.app.port, config.app.host, () => {
    logger.info(`
      🚀 ${config.app.name} 服务已启动
      📍 环境: ${config.app.env}
      🌐 地址: http://${config.app.host}:${config.app.port}
      📊 健康检查: http://${config.app.host}:${config.app.port}/health
      📡 API前缀: ${config.api.prefix}
      ⏰ 启动时间: ${new Date().toISOString()}
    `);
  });

  // 优雅关闭
  const shutdown = (signal) => {
    logger.info(`收到 ${signal} 信号，正在关闭服务...`);
    server.close(() => {
      logger.info('服务已关闭');
      process.exit(0);
    });

    // 强制关闭超时
    setTimeout(() => {
      logger.error('服务关闭超时，强制退出');
      process.exit(1);
    }, 10000);
  };

  // 监听关闭信号
  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));

  // 未捕获异常处理
  process.on('uncaughtException', (error) => {
    logger.error(`未捕获异常: ${error.message}`, { stack: error.stack });
    process.exit(1);
  });

  process.on('unhandledRejection', (reason, promise) => {
    logger.error(`未处理的Promise拒绝: ${reason}`);
    process.exit(1);
  });

  return server;
};

// 如果是直接运行此文件，则启动服务器
if (require.main === module) {
  startServer();
}

module.exports = { app, startServer };