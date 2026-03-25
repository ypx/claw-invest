"""
News API客户端 - 财经新闻和情感分析
API密钥：1f4ed63bccb54bba9ec439aef21a3982
文档：https://newsapi.org/docs
"""

import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class NewsAPIClient:
    """News API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        
        # 请求计数器
        self.request_count = 0
        self.last_reset_time = time.time()
        
        # 缓存
        self.cache = {}
        self.cache_ttl = 600  # 10分钟缓存
    
    def _check_rate_limit(self):
        """检查API调用频率限制"""
        current_time = time.time()
        
        # News API免费版限制：100次/天
        if current_time - self.last_reset_time > 86400:  # 24小时
            self.request_count = 0
            self.last_reset_time = current_time
        
        if self.request_count >= 90:  # 留10次余量
            logger.warning("News API每日调用次数接近限制")
        
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        
        params["apiKey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"News API请求失败: {endpoint}, 错误: {e}")
            return None
    
    def get_top_headlines(self, category: str = "business", country: str = "us") -> Optional[List[Dict]]:
        """获取头条新闻"""
        cache_key = f"headlines_{category}_{country}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 300:  # 5分钟缓存
                return cached_data
        
        params = {
            "category": category,
            "country": country,
            "pageSize": 20
        }
        
        data = self._make_request("top-headlines", params)
        if data and data.get("status") == "ok":
            articles = data.get("articles", [])
            self.cache[cache_key] = (articles, time.time())
            return articles
        return None
    
    def get_everything(self, q: str = "stock market", language: str = "en") -> Optional[List[Dict]]:
        """搜索所有新闻"""
        cache_key = f"everything_{q}_{language}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 300:
                return cached_data
        
        # 获取最近24小时的新闻
        to_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        from_date = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "q": q,
            "language": language,
            "from": from_date,
            "to": to_date,
            "sortBy": "relevancy",
            "pageSize": 20
        }
        
        data = self._make_request("everything", params)
        if data and data.get("status") == "ok":
            articles = data.get("articles", [])
            self.cache[cache_key] = (articles, time.time())
            return articles
        return None
    
    def get_stock_news(self, symbol: str) -> Optional[List[Dict]]:
        """获取特定股票的新闻"""
        cache_key = f"stock_news_{symbol}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 300:
                return cached_data
        
        # 搜索股票相关新闻
        company_name = self._get_company_name(symbol)
        if company_name:
            q = f"{company_name} OR {symbol} stock"
        else:
            q = f"{symbol} stock"
        
        articles = self.get_everything(q=q)
        if articles:
            self.cache[cache_key] = (articles, time.time())
        return articles
    
    def _get_company_name(self, symbol: str) -> Optional[str]:
        """获取公司名称（简化版）"""
        company_names = {
            "NVDA": "Nvidia",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "META": "Meta Platforms",
            "TSLA": "Tesla",
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "IONQ": "IonQ",
            "RKLB": "Rocket Lab",
            "ASTS": "AST SpaceMobile",
            "COIN": "Coinbase",
            "MARA": "Marathon Digital",
            "CMBT": "Cibus"
        }
        return company_names.get(symbol)
    
    def analyze_sentiment(self, articles: List[Dict]) -> Dict[str, Any]:
        """简单情感分析"""
        if not articles:
            return {"sentiment": "neutral", "score": 0, "positive": 0, "negative": 0, "total": 0}
        
        positive_keywords = [
            "up", "gain", "rise", "surge", "bullish", "beat", "exceed", "growth",
            "profit", "win", "success", "positive", "optimistic", "strong", "record"
        ]
        
        negative_keywords = [
            "down", "fall", "drop", "plunge", "bearish", "miss", "disappoint", "decline",
            "loss", "fail", "worry", "negative", "pessimistic", "weak", "concern"
        ]
        
        positive_count = 0
        negative_count = 0
        
        for article in articles:
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            content = f"{title} {description}"
            
            for keyword in positive_keywords:
                if keyword in content:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in content:
                    negative_count += 1
        
        total = positive_count + negative_count
        if total == 0:
            return {"sentiment": "neutral", "score": 0, "positive": 0, "negative": 0, "total": 0}
        
        score = (positive_count - negative_count) / total
        sentiment = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive": positive_count,
            "negative": negative_count,
            "total": total
        }

def create_news_client():
    """创建News API客户端实例"""
    return NewsAPIClient(api_key="1f4ed63bccb54bba9ec439aef21a3982")