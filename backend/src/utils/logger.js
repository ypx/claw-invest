const winston = require('winston');
const path = require('path');
const { config } = require('../config/config');

// 创建日志目录
const logDir = path.join(__dirname, '../../logs');
require('fs').mkdirSync(logDir, { recursive: true });

// 日志格式
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
    const metaStr = Object.keys(meta).length ? ` | ${JSON.stringify(meta)}` : '';
    const stackStr = stack ? `\n${stack}` : '';
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${metaStr}${stackStr}`;
  })
);

// 创建日志记录器
const logger = winston.createLogger({
  level: config.logging.level,
  format: logFormat,
  transports: [
    // 控制台输出
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        logFormat
      ),
    }),
    // 文件输出 - 所有日志
    new winston.transports.File({
      filename: path.join(logDir, 'combined.log'),
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 10,
    }),
    // 文件输出 - 错误日志
    new winston.transports.File({
      filename: path.join(logDir, 'error.log'),
      level: 'error',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 10,
    }),
    // 文件输出 - 访问日志（按配置文件名）
    new winston.transports.File({
      filename: path.join(logDir, config.logging.file),
      level: 'info',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 10,
    }),
  ],
  // 开发环境下不退出进程
  exitOnError: config.app.env === 'production',
});

// 请求日志中间件
const requestLogger = (req, res, next) => {
  const startTime = Date.now();

  // 记录请求
  logger.info('收到请求', {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date().toISOString(),
  });

  // 响应完成时记录
  const originalSend = res.send;
  res.send = function(data) {
    const responseTime = Date.now() - startTime;
    
    logger.info('发送响应', {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      responseTime: `${responseTime}ms`,
      contentLength: res.get('Content-Length'),
      timestamp: new Date().toISOString(),
    });

    originalSend.call(this, data);
  };

  next();
};

// API调用日志
const apiLogger = (service, action, data) => {
  logger.info('API调用', {
    service,
    action,
    data: typeof data === 'object' ? JSON.stringify(data) : data,
    timestamp: new Date().toISOString(),
  });
};

// 错误日志
const errorLogger = (error, context = {}) => {
  logger.error('发生错误', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString(),
  });
};

// 性能日志
const performanceLogger = (operation, duration, meta = {}) => {
  logger.info('性能日志', {
    operation,
    duration: `${duration}ms`,
    ...meta,
    timestamp: new Date().toISOString(),
  });
};

module.exports = {
  logger,
  requestLogger,
  apiLogger,
  errorLogger,
  performanceLogger,
};