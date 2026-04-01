"""
Finnhub API客户端 - 实时股票数据采集
API密钥：d70ka91r01ql6rnvjvggd70ka91r01ql6rnvjvh0
文档：https://finnhub.io/docs/api
"""

import logging
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json

logger = logging.getLogger(__name__)

class FinnhubClient:
    """Finnhub API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.headers = {"X-Finnhub-Token": api_key}
        
        # 请求计数器
        self.request_count = 0
        self.last_reset_time = time.time()
        
        # 缓存
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
    def _check_rate_limit(self):
        """检查API调用频率限制"""
        current_time = time.time()
        
        # Finnhub免费版限制：60次/分钟
        if current_time - self.last_reset_time > 60:
            self.request_count = 0
            self.last_reset_time = current_time
        
        if self.request_count >= 50:  # 留10次余量
            time_to_wait = 60 - (current_time - self.last_reset_time)
            if time_to_wait > 0:
                logger.info(f"Finnhub API频率限制，等待{time_to_wait:.1f}秒")
                time.sleep(time_to_wait)
                self.request_count = 0
                self.last_reset_time = time.time()
        
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Finnhub API请求失败: {endpoint}, 错误: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """获取实时报价"""
        cache_key = f"quote_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 60:  # 1分钟缓存
                return cached_data
        
        data = self._make_request("quote", {"symbol": symbol})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_stock_profile(self, symbol: str) -> Optional[Dict]:
        """获取公司基本信息"""
        cache_key = f"profile_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        data = self._make_request("stock/profile2", {"symbol": symbol})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_financials(self, symbol: str, statement: str = "bs", freq: str = "annual") -> Optional[Dict]:
        """获取财务报表"""
        cache_key = f"financials_{symbol}_{statement}_{freq}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        data = self._make_request(f"stock/financials", {"symbol": symbol, "statement": statement, "freq": freq})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_metric(self, symbol: str) -> Optional[Dict]:
        """获取关键财务指标"""
        cache_key = f"metric_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        data = self._make_request("stock/metric", {"symbol": symbol, "metric": "all"})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_news(self, symbol: str = None, category: str = "general") -> Optional[List[Dict]]:
        """获取新闻"""
        cache_key = f"news_{symbol}_{category}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 300:  # 5分钟缓存
                return cached_data
        
        params = {"category": category}
        if symbol:
            params["symbol"] = symbol
        
        # 获取最近7天的新闻
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        params["from"] = from_date
        params["to"] = to_date
        
        data = self._make_request("news", params)
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_recommendation_trends(self, symbol: str) -> Optional[List[Dict]]:
        """获取分析师推荐趋势"""
        cache_key = f"recommendation_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        data = self._make_request("stock/recommendation", {"symbol": symbol})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_price_target(self, symbol: str) -> Optional[Dict]:
        """获取价格目标"""
        cache_key = f"price_target_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        data = self._make_request("stock/price-target", {"symbol": symbol})
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_earnings_calendar(self, symbol: str = None) -> Optional[List[Dict]]:
        """获取财报日历"""
        cache_key = f"earnings_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 3600:  # 1小时缓存
                return cached_data
        
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        # 获取未来30天的财报
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        from_date = datetime.now().strftime("%Y-%m-%d")
        params["from"] = from_date
        params["to"] = to_date
        
        data = self._make_request("calendar/earnings", params)
        if data:
            self.cache[cache_key] = (data, time.time())
        return data
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """批量获取报价"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_quote(symbol)
            time.sleep(0.1)  # 避免频繁请求
        return results

# 主关注股票列表（基于Z的投资偏好）
PRIMARY_STOCKS = [
    # AI/科技股
    "NVDA",  # 英伟达 - AI算力龙头
    "GOOGL", # 谷歌 - AI搜索/云
    "AMZN",  # 亚马逊 - 云计算/AWS
    "META",  # Meta - AI社交/广告
    
    # 太空/前沿科技
    "IONQ",  # 量子计算
    "RKLB",  # Rocket Lab - 太空发射
    "ASTS",  # AST SpaceMobile - 太空通信
    
    # Z特别关注的
    "TSLA",  # 特斯拉 - Z常做sell put
    "AAPL",  # 苹果 - 老牌科技
    "MSFT",  # 微软 - AI/云
    
    # 加密货币相关
    "COIN",  # Coinbase - 加密货币交易所
    "MARA",  # Marathon Digital - 比特币矿企
    
    # 其他Mike提及的
    "CMBT",  # 细胞农业（未来食品）
]

def create_finnhub_client():
    """创建Finnhub客户端实例"""
    return FinnhubClient(api_key="d70ka91r01ql6rnvjvggd70ka91r01ql6rnvjvh0")