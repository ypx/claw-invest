const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

const config = {
  // 应用配置
  app: {
    name: process.env.APP_NAME || 'Claw Advisor',
    env: process.env.NODE_ENV || 'development',
    port: parseInt(process.env.PORT, 10) || 3000,
    host: process.env.HOST || 'localhost',
    url: process.env.APP_URL || 'http://localhost:3000',
  },

  // 数据库配置
  database: {
    url: process.env.DATABASE_URL || 'postgresql://clawadmin:clawpassword123@localhost:5432/clawadvisor',
    pool: {
      max: parseInt(process.env.DB_POOL_MAX, 10) || 10,
      min: parseInt(process.env.DB_POOL_MIN, 10) || 2,
      acquire: parseInt(process.env.DB_POOL_ACQUIRE, 10) || 30000,
      idle: parseInt(process.env.DB_POOL_IDLE, 10) || 10000,
    },
  },

  // Redis配置
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
  },

  // JWT配置
  jwt: {
    secret: process.env.JWT_SECRET || 'your_super_secret_jwt_key_change_this_in_production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },

  // CORS配置
  cors: {
    origin: process.env.CORS_ORIGIN 
      ? process.env.CORS_ORIGIN.split(',')
      : ['http://localhost:3001', 'http://localhost:3000'],
    credentials: true,
  },

  // 安全配置
  security: {
    rateLimit: {
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS, 10) || 15 * 60 * 1000, // 15分钟
      max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS, 10) || 100,
    },
    helmet: {
      contentSecurityPolicy: false, // 在开发阶段禁用，生产环境需要配置
    },
  },

  // 日志配置
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || 'backend.log',
  },

  // 外部服务配置
  services: {
    analysis: process.env.ANALYSIS_SERVICE_URL || 'http://localhost:8000',
    data: process.env.DATA_SERVICE_URL || 'http://localhost:8001',
  },

  // Mike推荐股票列表（核心关注）
  mikeStocks: [
    'NVDA',  // 英伟达 - AI算力基础设施
    'GOOGL', // 谷歌 - AI+搜索+云
    'AMZN',  // 亚马逊 - 云计算+电商
    'META',  // Meta - AI+广告+元宇宙
    'TSLA',  // 特斯拉 - 电动车龙头（sell put机会）
    'IONQ',  // IonQ - 量子计算
    'AAPL',  // 苹果 - 消费电子巨头
    'MSFT',  // 微软 - 软件+云计算
    // 加密资产（通过ETF配置）
    'ARKB',  // BTC ETF
    'ETH',   // 以太坊（直接或通过相关产品）
  ],

  // API路径前缀
  api: {
    prefix: '/api/v1',
  },

  // 股票数据源配置
  dataSources: {
    alphaVantage: {
      apiKey: process.env.ALPHA_VANTAGE_API_KEY || 'OH7TPNSBQONIAGBG',
      baseUrl: 'https://www.alphavantage.co/query',
      rateLimit: 5, // 每分钟最多5次调用
    },
    yahooFinance: {
      baseUrl: 'https://query1.finance.yahoo.com/v8/finance/chart',
    },
  },
};

// 验证必要配置
const validateConfig = () => {
  const required = ['DATABASE_URL', 'JWT_SECRET'];
  const missing = [];

  required.forEach(key => {
    if (!process.env[key]) {
      missing.push(key);
    }
  });

  if (missing.length > 0) {
    throw new Error(`缺少必要的环境变量: ${missing.join(', ')}`);
  }

  console.log(`✅ 配置验证通过 - 环境: ${config.app.env}, 端口: ${config.app.port}`);
  return true;
};

// 开发环境重写配置
if (config.app.env === 'development') {
  console.log('🔧 运行在开发环境，启用开发配置');
  // 可以在这里添加开发环境特定的配置
}

module.exports = { config, validateConfig };