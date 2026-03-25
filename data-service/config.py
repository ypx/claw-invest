import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://clawadmin:clawpassword123@localhost:5432/clawadvisor')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Alpha Vantage API
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'OH7TPNSBQONIAGBG')
    
    # 数据采集配置
    DATA_UPDATE_INTERVAL_HOURS = int(os.getenv('DATA_UPDATE_INTERVAL_HOURS', '6'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '5'))
    
    # 股票列表（Mike推荐）
    MIKE_STOCKS = os.getenv('MIKE_STOCKS', 'NVDA,GOOGL,AMZN,META,TSLA,IONQ,AAPL,MSFT').split(',')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'data_service.log')
    
    # 数据源优先级
    DATA_SOURCE_PRIORITY = ['alpha_vantage', 'yfinance', 'yahoo_finance']
    
    @staticmethod
    def get_stock_symbols():
        """获取所有需要监控的股票代码"""
        return [symbol.strip() for symbol in Config.MIKE_STOCKS if symbol.strip()]
    
    @staticmethod
    def validate():
        """验证配置是否完整"""
        required_vars = ['ALPHA_VANTAGE_API_KEY']
        missing = []
        
        for var in required_vars:
            if not getattr(Config, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing)}")
        
        return True

# 验证配置
try:
    Config.validate()
    print("配置验证通过")
except ValueError as e:
    print(f"配置错误: {e}")