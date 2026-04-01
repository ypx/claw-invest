import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentals import Fundamentals
import yfinance as yf

from config import Config
from database import db_manager

logger = logging.getLogger(__name__)

class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.api_key = Config.ALPHA_VANTAGE_API_KEY
        self.stock_symbols = Config.get_stock_symbols()
        
        # 初始化Alpha Vantage客户端
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        self.fundamentals = Fundamentals(key=self.api_key, output_format='pandas')
        
        # 请求计数器（避免超出API限制）
        self.request_count = 0
        self.last_reset_time = time.time()
    
    def _check_rate_limit(self):
        """检查API调用频率限制"""
        current_time = time.time()
        
        # 重置计数器（每60分钟重置）
        if current_time - self.last_reset_time > 3600:
            self.request_count = 0
            self.last_reset_time = current_time
        
        # Alpha Vantage免费版限制：5次/分钟，500次/天
        if self.request_count >= 5:
            time_to_wait = 60 - (current_time - self.last_reset_time)
            if time_to_wait > 0:
                logger.info(f"API调用频率限制，等待{time_to_wait:.1f}秒")
                time.sleep(time_to_wait)
                self.request_count = 0
                self.last_reset_time = time.time()
        
        self.request_count += 1
    
    def get_stock_info_from_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从Alpha Vantage获取股票基本信息"""
        try:
            self._check_rate_limit()
            
            # 获取概览信息
            data, meta_data = self.fundamentals.get_company_overview(symbol=symbol)
            
            if data is None or data.empty:
                logger.warning(f"Alpha Vantage未找到股票信息: {symbol}")
                return None
            
            # 提取关键信息
            info = {
                'symbol': symbol,
                'name': data.get('Name', [''])[0],
                'sector': data.get('Sector', [''])[0],
                'industry': data.get('Industry', [''])[0],
                'market_cap': float(data.get('MarketCapitalization', [0])[0]) if data.get('MarketCapitalization') else None,
                'pe_ratio': float(data.get('PERatio', [0])[0]) if data.get('PERatio') else None,
                'dividend_yield': float(data.get('DividendYield', [0])[0]) * 100 if data.get('DividendYield') else None,
                'beta': float(data.get('Beta', [0])[0]) if data.get('Beta') else None,
            }
            
            logger.debug(f"从Alpha Vantage获取股票信息: {symbol}")
            return info
            
        except Exception as e:
            logger.error(f"获取Alpha Vantage股票信息失败 {symbol}: {e}")
            return None
    
    def get_stock_prices_from_alpha_vantage(self, symbol: str, output_size: str = 'compact') -> Optional[pd.DataFrame]:
        """从Alpha Vantage获取股票价格历史"""
        try:
            self._check_rate_limit()
            
            # 获取每日价格
            data, meta_data = self.ts.get_daily(symbol=symbol, outputsize=output_size)
            
            if data is None or data.empty:
                logger.warning(f"Alpha Vantage未找到价格数据: {symbol}")
                return None
            
            # 重命名列
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            data.index.name = 'date'
            
            logger.debug(f"从Alpha Vantage获取价格数据: {symbol}, 数据量: {len(data)}")
            return data
            
        except Exception as e:
            logger.error(f"获取Alpha Vantage价格数据失败 {symbol}: {e}")
            return None
    
    def get_stock_info_from_yfinance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从Yahoo Finance获取股票信息（备用数据源）"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                logger.warning(f"Yahoo Finance未找到股票信息: {symbol}")
                return None
            
            result = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield') * 100 if info.get('dividendYield') else None,
                'beta': info.get('beta'),
            }
            
            logger.debug(f"从Yahoo Finance获取股票信息: {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"获取Yahoo Finance股票信息失败 {symbol}: {e}")
            return None
    
    def get_stock_prices_from_yfinance(self, symbol: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """从Yahoo Finance获取股票价格历史（备用数据源）"""
        try:
            stock = yf.Ticker(symbol)
            history = stock.history(period=period)
            
            if history is None or history.empty:
                logger.warning(f"Yahoo Finance未找到价格数据: {symbol}")
                return None
            
            # 重命名列以匹配数据库结构
            history = history.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            history.index.name = 'date'
            
            logger.debug(f"从Yahoo Finance获取价格数据: {symbol}, 数据量: {len(history)}")
            return history
            
        except Exception as e:
            logger.error(f"获取Yahoo Finance价格数据失败 {symbol}: {e}")
            return None
    
    def collect_stock_info(self, symbol: str) -> bool:
        """收集股票基本信息"""
        try:
            logger.info(f"开始收集股票信息: {symbol}")
            
            # 优先使用Alpha Vantage
            info = self.get_stock_info_from_alpha_vantage(symbol)
            
            # 如果失败，尝试Yahoo Finance
            if not info:
                info = self.get_stock_info_from_yfinance(symbol)
            
            if not info:
                logger.error(f"所有数据源都未找到股票信息: {symbol}")
                return False
            
            # 更新数据库
            db_manager.update_stock_info(
                symbol=info['symbol'],
                name=info['name'],
                sector=info['sector'],
                industry=info['industry'],
                market_cap=info['market_cap'],
                pe_ratio=info['pe_ratio'],
                dividend_yield=info['dividend_yield'],
                beta=info['beta']
            )
            
            logger.info(f"股票信息收集完成: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"收集股票信息失败 {symbol}: {e}")
            return False
    
    def collect_stock_prices(self, symbol: str) -> bool:
        """收集股票价格数据"""
        try:
            logger.info(f"开始收集价格数据: {symbol}")
            
            # 获取股票ID
            stock_id = db_manager.get_stock_id_by_symbol(symbol)
            if not stock_id:
                logger.error(f"数据库中没有找到股票: {symbol}")
                return False
            
            # 检查最新数据日期
            latest_date = db_manager.get_latest_price_date(symbol)
            
            # 如果已有今天的数据，跳过
            today = datetime.now().date()
            if latest_date and latest_date >= today:
                logger.info(f"价格数据已是最新: {symbol}")
                return True
            
            # 优先使用Alpha Vantage
            prices_df = self.get_stock_prices_from_alpha_vantage(symbol)
            
            # 如果失败，尝试Yahoo Finance
            if prices_df is None or prices_df.empty:
                prices_df = self.get_stock_prices_from_yfinance(symbol, period='3mo')
            
            if prices_df is None or prices_df.empty:
                logger.error(f"所有数据源都未找到价格数据: {symbol}")
                return False
            
            # 插入数据库
            for date, row in prices_df.iterrows():
                # 确保日期是datetime.date类型
                if isinstance(date, str):
                    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                elif isinstance(date, pd.Timestamp):
                    date_obj = date.date()
                else:
                    date_obj = date
                
                # 只插入缺失的数据
                if latest_date and date_obj <= latest_date:
                    continue
                
                db_manager.insert_stock_price(
                    stock_id=stock_id,
                    date=date_obj,
                    open_price=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close_price=float(row['close']),
                    volume=int(row['volume']) if not pd.isna(row['volume']) else 0
                )
            
            logger.info(f"价格数据收集完成: {symbol}, 新增{len(prices_df)}条记录")
            return True
            
        except Exception as e:
            logger.error(f"收集价格数据失败 {symbol}: {e}")
            return False
    
    def collect_all_stocks_info(self):
        """收集所有股票的基本信息"""
        logger.info("开始收集所有股票基本信息")
        
        success_count = 0
        for symbol in self.stock_symbols:
            if self.collect_stock_info(symbol):
                success_count += 1
            time.sleep(1)  # 避免API限制
        
        logger.info(f"股票基本信息收集完成: {success_count}/{len(self.stock_symbols)} 成功")
        return success_count
    
    def collect_all_stocks_prices(self):
        """收集所有股票的价格数据"""
        logger.info("开始收集所有股票价格数据")
        
        success_count = 0
        for symbol in self.stock_symbols:
            if self.collect_stock_prices(symbol):
                success_count += 1
            time.sleep(12)  # Alpha Vantage限制5次/分钟，所以12秒间隔
        
        logger.info(f"股票价格数据收集完成: {success_count}/{len(self.stock_symbols)} 成功")
        return success_count
    
    def run_collection(self):
        """运行完整的数据收集流程"""
        logger.info("=" * 60)
        logger.info("开始数据收集流程")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 收集基本信息
        info_success = self.collect_all_stocks_info()
        
        # 收集价格数据
        price_success = self.collect_all_stocks_prices()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logger.info("=" * 60)
        logger.info(f"数据收集流程完成")
        logger.info(f"耗时: {elapsed_time:.1f}秒")
        logger.info(f"基本信息: {info_success}/{len(self.stock_symbols)} 成功")
        logger.info(f"价格数据: {price_success}/{len(self.stock_symbols)} 成功")
        logger.info("=" * 60)
        
        return {
            "info_success": info_success,
            "price_success": price_success,
            "total_stocks": len(self.stock_symbols),
            "elapsed_time": elapsed_time
        }