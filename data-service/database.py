import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import redis
from config import Config

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.redis_client = None
        self._init_connections()
    
    def _init_connections(self):
        """初始化数据库连接"""
        try:
            # PostgreSQL连接
            self.engine = create_engine(
                Config.DATABASE_URL,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                echo=False
            )
            
            # 创建会话工厂
            self.SessionLocal = scoped_session(
                sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            )
            
            # Redis连接
            self.redis_client = redis.from_url(Config.REDIS_URL)
            
            # 测试连接
            self.test_connections()
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise
    
    def test_connections(self):
        """测试数据库连接"""
        # 测试PostgreSQL
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.debug("PostgreSQL连接测试通过")
        except Exception as e:
            logger.error(f"PostgreSQL连接测试失败: {e}")
            raise
        
        # 测试Redis
        try:
            self.redis_client.ping()
            logger.debug("Redis连接测试通过")
        except Exception as e:
            logger.error(f"Redis连接测试失败: {e}")
            raise
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close_session(self):
        """关闭当前会话"""
        if self.SessionLocal:
            self.SessionLocal.remove()
    
    def execute_raw_sql(self, sql, params=None):
        """执行原始SQL语句"""
        session = self.get_session()
        try:
            result = session.execute(text(sql), params or {})
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"SQL执行失败: {e}, SQL: {sql}")
            raise
        finally:
            self.close_session()
    
    def get_stock_id_by_symbol(self, symbol):
        """根据股票代码获取ID"""
        session = self.get_session()
        try:
            result = session.execute(
                text("SELECT id FROM stocks WHERE symbol = :symbol"),
                {"symbol": symbol}
            ).fetchone()
            return result[0] if result else None
        finally:
            self.close_session()
    
    def insert_stock_price(self, stock_id, date, open_price, high, low, close_price, volume, adj_close=None):
        """插入股票价格数据"""
        sql = """
        INSERT INTO stock_prices (stock_id, date, open, high, low, close, volume, adj_close)
        VALUES (:stock_id, :date, :open, :high, :low, :close, :volume, :adj_close)
        ON CONFLICT (stock_id, date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            adj_close = EXCLUDED.adj_close
        """
        
        params = {
            "stock_id": stock_id,
            "date": date,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price,
            "volume": volume,
            "adj_close": adj_close or close_price
        }
        
        self.execute_raw_sql(sql, params)
        logger.debug(f"插入/更新股票价格: stock_id={stock_id}, date={date}, close={close_price}")
    
    def update_stock_info(self, symbol, name=None, sector=None, industry=None, 
                         market_cap=None, pe_ratio=None, dividend_yield=None, beta=None):
        """更新股票基本信息"""
        # 先检查股票是否存在
        stock_id = self.get_stock_id_by_symbol(symbol)
        
        if not stock_id:
            # 插入新股票
            sql = """
            INSERT INTO stocks (symbol, name, sector, industry, market_cap, pe_ratio, dividend_yield, beta)
            VALUES (:symbol, :name, :sector, :industry, :market_cap, :pe_ratio, :dividend_yield, :beta)
            RETURNING id
            """
        else:
            # 更新现有股票
            sql = """
            UPDATE stocks 
            SET name = COALESCE(:name, name),
                sector = COALESCE(:sector, sector),
                industry = COALESCE(:industry, industry),
                market_cap = COALESCE(:market_cap, market_cap),
                pe_ratio = COALESCE(:pe_ratio, pe_ratio),
                dividend_yield = COALESCE(:dividend_yield, dividend_yield),
                beta = COALESCE(:beta, beta),
                updated_at = CURRENT_TIMESTAMP
            WHERE symbol = :symbol
            """
        
        params = {
            "symbol": symbol,
            "name": name or symbol,
            "sector": sector,
            "industry": industry,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "beta": beta
        }
        
        self.execute_raw_sql(sql, params)
        logger.info(f"更新股票信息: {symbol}")
    
    def cache_set(self, key, value, ttl=3600):
        """设置缓存"""
        try:
            self.redis_client.set(key, value, ex=ttl)
        except Exception as e:
            logger.warning(f"Redis缓存设置失败: {e}")
    
    def cache_get(self, key):
        """获取缓存"""
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.warning(f"Redis缓存获取失败: {e}")
            return None
    
    def cache_delete(self, key):
        """删除缓存"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.warning(f"Redis缓存删除失败: {e}")
    
    def get_latest_price_date(self, stock_symbol):
        """获取股票最新价格日期"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                SELECT MAX(date) 
                FROM stock_prices sp
                JOIN stocks s ON sp.stock_id = s.id
                WHERE s.symbol = :symbol
                """),
                {"symbol": stock_symbol}
            ).fetchone()
            return result[0] if result else None
        finally:
            self.close_session()
    
    def get_mike_recommendations(self):
        """获取Mike推荐清单"""
        session = self.get_session()
        try:
            result = session.execute(
                text("""
                SELECT s.symbol, s.name, mr.recommendation_type, mr.priority, mr.mike_reason
                FROM mike_recommendations mr
                JOIN stocks s ON mr.stock_id = s.id
                WHERE mr.is_active = TRUE
                ORDER BY mr.priority, s.symbol
                """)
            ).fetchall()
            
            return [
                {
                    "symbol": row[0],
                    "name": row[1],
                    "type": row[2],
                    "priority": row[3],
                    "reason": row[4]
                }
                for row in result
            ]
        finally:
            self.close_session()

# 全局数据库管理器实例
db_manager = DatabaseManager()