"""
宏观经济数据模块 - 获取市场宏观指标
包括：利率、通胀、GDP、VIX、美元指数等
"""

import logging
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class MacroDataCollector:
    """宏观经济数据收集器"""
    
    def __init__(self):
        # 宏观经济数据API端点
        self.data_sources = {
            # 美联储数据
            "fed_funds_rate": "https://api.stlouisfed.org/fred/series/observations",
            "cpi": "https://api.stlouisfed.org/fred/series/observations",
            "gdp": "https://api.stlouisfed.org/fred/series/observations",
            
            # 市场数据
            "vix": None,  # 通过Finnhub获取
            "dxy": None,  # 美元指数
            "treasury_yield": None,  # 国债收益率
        }
        
        # 缓存
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪指标"""
        sentiment_data = {
            "overall": "neutral",
            "indicators": {},
            "analysis": "",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 1. VIX恐慌指数（通过Finnhub）
            vix_data = self._get_vix_data()
            if vix_data:
                vix_value = vix_data.get("c", 0)
                sentiment_data["indicators"]["vix"] = {
                    "value": vix_value,
                    "level": self._classify_vix_level(vix_value)
                }
            
            # 2. 市场涨跌比（简化版）
            market_breadth = self._estimate_market_breadth()
            sentiment_data["indicators"]["breadth"] = market_breadth
            
            # 3. 新闻情绪（通过News API）
            news_sentiment = self._get_news_sentiment()
            sentiment_data["indicators"]["news_sentiment"] = news_sentiment
            
            # 综合分析
            sentiment_data["overall"] = self._analyze_overall_sentiment(
                sentiment_data["indicators"]
            )
            sentiment_data["analysis"] = self._generate_sentiment_analysis(
                sentiment_data["indicators"]
            )
            
        except Exception as e:
            logger.error(f"获取市场情绪失败: {e}")
            sentiment_data["error"] = str(e)
        
        return sentiment_data
    
    def _get_vix_data(self) -> Optional[Dict]:
        """获取VIX数据"""
        # 这里可以集成Finnhub API，暂时返回模拟数据
        return {
            "c": 18.5,  # 当前VIX值
            "h": 19.2,
            "l": 17.8,
            "o": 18.1,
            "pc": 17.9,
            "t": int(time.time())
        }
    
    def _classify_vix_level(self, vix_value: float) -> str:
        """分类VIX水平"""
        if vix_value < 15:
            return "极低恐慌"
        elif vix_value < 20:
            return "低恐慌"
        elif vix_value < 25:
            return "正常"
        elif vix_value < 30:
            return "中等恐慌"
        elif vix_value < 40:
            return "高恐慌"
        else:
            return "极高恐慌"
    
    def _estimate_market_breadth(self) -> Dict[str, Any]:
        """估算市场涨跌比（简化版）"""
        # 在实际系统中，这里应该获取全市场数据
        # 现在返回一个合理的估计值
        return {
            "advancing": 55,  # 上涨股票比例
            "declining": 35,  # 下跌股票比例
            "unchanged": 10,  # 平盘比例
            "ratio": 1.57,    # 涨跌比
            "interpretation": "市场情绪偏积极"
        }
    
    def _get_news_sentiment(self) -> Dict[str, Any]:
        """获取新闻情绪"""
        # 在实际系统中，这里应该调用News API
        return {
            "positive": 45,
            "negative": 30,
            "neutral": 25,
            "score": 0.15,  # 正负差
            "trend": "slightly_positive"
        }
    
    def _analyze_overall_sentiment(self, indicators: Dict) -> str:
        """分析整体情绪"""
        vix_level = indicators.get("vix", {}).get("level", "正常")
        breadth_ratio = indicators.get("breadth", {}).get("ratio", 1.0)
        news_score = indicators.get("news_sentiment", {}).get("score", 0)
        
        # 简单的决策逻辑
        if vix_level in ["高恐慌", "极高恐慌"]:
            return "bearish"
        elif breadth_ratio > 1.5 and news_score > 0.1:
            return "bullish"
        elif breadth_ratio < 0.7 or news_score < -0.1:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_sentiment_analysis(self, indicators: Dict) -> str:
        """生成情绪分析报告"""
        vix_level = indicators.get("vix", {}).get("level", "正常")
        vix_value = indicators.get("vix", {}).get("value", 0)
        breadth = indicators.get("breadth", {})
        news = indicators.get("news_sentiment", {})
        
        analysis_parts = []
        
        # VIX分析
        if vix_level == "极低恐慌":
            analysis_parts.append("市场极度乐观，需注意回调风险")
        elif vix_level in ["低恐慌", "正常"]:
            analysis_parts.append("市场情绪稳定，适合正常投资")
        elif vix_level == "中等恐慌":
            analysis_parts.append("市场出现恐慌，可能是买入机会")
        elif vix_level in ["高恐慌", "极高恐慌"]:
            analysis_parts.append("市场极度恐慌，保守投资者应等待")
        
        # 涨跌比分析
        breadth_ratio = breadth.get("ratio", 1.0)
        if breadth_ratio > 2.0:
            analysis_parts.append("市场广度极好，上涨动力强劲")
        elif breadth_ratio > 1.2:
            analysis_parts.append("市场广度良好")
        elif breadth_ratio < 0.8:
            analysis_parts.append("市场广度较差，上涨动力不足")
        
        # 新闻情绪分析
        news_score = news.get("score", 0)
        if news_score > 0.2:
            analysis_parts.append("新闻情绪非常积极")
        elif news_score < -0.2:
            analysis_parts.append("新闻情绪非常消极")
        
        # 投资建议
        if vix_value > 30:
            analysis_parts.append("💡 建议：VIX高于30，适合逐步建仓")
        elif vix_value < 15:
            analysis_parts.append("💡 建议：VIX低于15，避免追高")
        else:
            analysis_parts.append("💡 建议：市场情绪正常，按计划投资")
        
        return " | ".join(analysis_parts) if analysis_parts else "市场情绪分析数据不足"
    
    def get_economic_indicators(self) -> Dict[str, Any]:
        """获取经济指标"""
        indicators = {
            "interest_rates": self._get_interest_rates(),
            "inflation": self._get_inflation_data(),
            "gdp_growth": self._get_gdp_growth(),
            "unemployment": self._get_unemployment_rate(),
            "timestamp": datetime.now().isoformat()
        }
        
        # 生成经济展望
        indicators["outlook"] = self._generate_economic_outlook(indicators)
        
        return indicators
    
    def _get_interest_rates(self) -> Dict[str, Any]:
        """获取利率数据"""
        return {
            "fed_funds_rate": 4.75,  # 美联储基准利率
            "treasury_10y": 4.25,    # 10年期国债收益率
            "treasury_2y": 4.50,     # 2年期国债收益率
            "yield_curve": "inverted",  # 收益率曲线形态
            "trend": "stable"        # 趋势
        }
    
    def _get_inflation_data(self) -> Dict[str, Any]:
        """获取通胀数据"""
        return {
            "cpi_yoy": 3.2,          # CPI同比
            "core_cpi_yoy": 3.5,     # 核心CPI同比
            "pce_yoy": 2.8,          # PCE同比
            "trend": "declining"     # 趋势
        }
    
    def _get_gdp_growth(self) -> Dict[str, Any]:
        """获取GDP增长数据"""
        return {
            "qoq": 0.8,              # 季度环比
            "yoy": 2.5,              # 年度同比
            "forecast_next_q": 0.7,  # 下季度预测
            "trend": "moderate"      # 趋势
        }
    
    def _get_unemployment_rate(self) -> Dict[str, Any]:
        """获取失业率数据"""
        return {
            "rate": 3.8,             # 失业率
            "trend": "stable"        # 趋势
        }
    
    def _generate_economic_outlook(self, indicators: Dict) -> str:
        """生成经济展望"""
        parts = []
        
        # 利率分析
        interest_rates = indicators.get("interest_rates", {})
        if interest_rates.get("yield_curve") == "inverted":
            parts.append("收益率曲线倒挂，预示经济可能放缓")
        
        fed_rate = interest_rates.get("fed_funds_rate", 0)
        if fed_rate > 5.0:
            parts.append("利率处于高位，对成长股有压力")
        elif fed_rate < 2.0:
            parts.append("利率处于低位，有利于成长股")
        
        # 通胀分析
        inflation = indicators.get("inflation", {})
        cpi = inflation.get("cpi_yoy", 0)
        if cpi > 4.0:
            parts.append("通胀仍高于目标，美联储可能维持紧缩")
        elif cpi < 2.0:
            parts.append("通胀接近目标，美联储可能考虑宽松")
        
        # GDP分析
        gdp = indicators.get("gdp_growth", {})
        gdp_growth = gdp.get("yoy", 0)
        if gdp_growth > 3.0:
            parts.append("经济增长强劲，有利于企业盈利")
        elif gdp_growth < 1.0:
            parts.append("经济增长放缓，需谨慎投资")
        
        # 综合建议
        if len(parts) > 0:
            outlook = " | ".join(parts)
            # 添加投资建议
            if cpi > 4.0 and fed_rate > 5.0:
                outlook += " | 💡 建议：高通胀高利率环境，优先配置现金和防御性股票"
            elif cpi < 2.5 and fed_rate < 3.0:
                outlook += " | 💡 建议：低通胀低利率环境，适合投资成长股"
            else:
                outlook += " | 💡 建议：经济环境正常，按资产配置计划投资"
        else:
            outlook = "经济数据正常，无明显风险信号"
        
        return outlook
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """获取行业表现"""
        # 在实际系统中，这里应该获取各行业ETF数据
        sectors = {
            "technology": {
                "performance": 15.2,
                "momentum": "strong",
                "valuation": "fair",
                "recommendation": "overweight"
            },
            "healthcare": {
                "performance": 8.7,
                "momentum": "moderate",
                "valuation": "attractive",
                "recommendation": "overweight"
            },
            "financials": {
                "performance": 5.3,
                "momentum": "weak",
                "valuation": "cheap",
                "recommendation": "neutral"
            },
            "energy": {
                "performance": -2.1,
                "momentum": "weak",
                "valuation": "expensive",
                "recommendation": "underweight"
            },
            "consumer_discretionary": {
                "performance": 12.5,
                "momentum": "strong",
                "valuation": "fair",
                "recommendation": "overweight"
            },
            "communication_services": {
                "performance": 18.3,
                "momentum": "very_strong",
                "valuation": "expensive",
                "recommendation": "neutral"
            }
        }
        
        # 找出表现最佳和最差的行业
        best_sector = max(sectors.items(), key=lambda x: x[1]["performance"])
        worst_sector = min(sectors.items(), key=lambda x: x[1]["performance"])
        
        return {
            "sectors": sectors,
            "best_performer": {
                "sector": best_sector[0],
                "performance": best_sector[1]["performance"]
            },
            "worst_performer": {
                "sector": worst_sector[0],
                "performance": worst_sector[1]["performance"]
            },
            "analysis": self._generate_sector_analysis(sectors),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_sector_analysis(self, sectors: Dict) -> str:
        """生成行业分析"""
        tech_perf = sectors.get("technology", {}).get("performance", 0)
        comm_perf = sectors.get("communication_services", {}).get("performance", 0)
        
        analysis_parts = []
        
        if tech_perf > 10 and comm_perf > 10:
            analysis_parts.append("科技和通信行业领涨，显示市场偏好成长股")
        
        # 检查是否有行业大幅下跌
        for sector, data in sectors.items():
            if data.get("performance", 0) < -5:
                analysis_parts.append(f"{sector}行业表现疲弱，需谨慎")
        
        # 投资建议
        overweight_sectors = [s for s, d in sectors.items() if d.get("recommendation") == "overweight"]
        if overweight_sectors:
            analysis_parts.append(f"💡 建议超配：{', '.join(overweight_sectors)}")
        
        underweight_sectors = [s for s, d in sectors.items() if d.get("recommendation") == "underweight"]
        if underweight_sectors:
            analysis_parts.append(f"💡 建议低配：{', '.join(underweight_sectors)}")
        
        return " | ".join(analysis_parts) if analysis_parts else "行业表现分化不明显"

def create_macro_collector():
    """创建宏观经济数据收集器"""
    return MacroDataCollector()