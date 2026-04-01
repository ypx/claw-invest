"""
Claw决策引擎 - 基于我的投资经验 + Z的保守偏好
核心逻辑：保守原则 + 科技趋势 + 量化分析
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class ClawDecisionEngine:
    """Claw决策引擎"""
    
    def __init__(self):
        # 我的投资原则
        self.investment_principles = {
            "conservative": {
                "max_position_size": 0.15,  # 单个持仓最大比例
                "min_cash_ratio": 0.30,     # 最小现金比例
                "max_pe_ratio": 25,         # 最大PE比例
                "min_profit_margin": 0.10,  # 最小利润率
                "max_beta": 1.5,            # 最大Beta系数
                "prefer_dividend": True,    # 偏好股息
            },
            "tech_focus": {
                "sectors": ["Technology", "Communication Services", "Consumer Cyclical"],
                "themes": ["AI", "Cloud Computing", "Quantum Computing", "Space", "Electric Vehicles"],
                "growth_required": True,    # 要求增长性
            },
            "risk_management": {
                "stop_loss": 0.15,          # 止损比例
                "take_profit": 0.30,        # 止盈比例
                "diversification": 8,       # 最小分散数量
                "rebalance_frequency": "quarterly",  # 再平衡频率
            }
        }
        
        # Z的特殊偏好
        self.z_preferences = {
            "favorite_stocks": ["TSLA"],      # 最熟悉的股票
            "preferred_action": "sell_put",   # 偏好操作
            "risk_tolerance": "low",          # 风险容忍度
            "time_horizon": "long_term",      # 投资期限
            "cash_reserve": 0.35,             # 现金储备目标
        }
        
        # 从历史经验中学习的权重
        self.learned_weights = {
            # 基本面权重（总计60%）
            "fundamentals": {
                "profitability": 0.25,    # 盈利能力
                "growth": 0.20,           # 增长性
                "valuation": 0.15,        # 估值
                "financial_health": 0.10, # 财务健康
            },
            # 技术面权重（总计40%）
            "technicals": {
                "momentum": 0.15,         # 动量
                "volatility": 0.10,       # 波动性
                "trend": 0.10,            # 趋势
                "sentiment": 0.05,        # 市场情绪
            }
        }
    
    def analyze_stock(self, stock_data: Dict, market_data: Dict = None) -> Dict[str, Any]:
        """分析单只股票"""
        symbol = stock_data.get("symbol", "")
        
        if not stock_data.get("quote"):
            return {"symbol": symbol, "error": "No quote data"}
        
        # 计算各维度分数
        fundamentals_score = self._calculate_fundamentals_score(stock_data)
        technicals_score = self._calculate_technicals_score(stock_data, market_data)
        sentiment_score = self._calculate_sentiment_score(stock_data)
        
        # 应用保守系数
        conservative_factor = self._calculate_conservative_factor(stock_data)
        
        # 计算综合分数
        total_score = (
            fundamentals_score * 0.6 + 
            technicals_score * 0.4
        ) * conservative_factor
        
        # 生成投资建议
        recommendation = self._generate_recommendation(
            total_score, stock_data, conservative_factor
        )
        
        return {
            "symbol": symbol,
            "name": stock_data.get("profile", {}).get("name", ""),
            "sector": stock_data.get("profile", {}).get("finnhubIndustry", ""),
            "score": {
                "total": round(total_score, 2),
                "fundamentals": round(fundamentals_score, 2),
                "technicals": round(technicals_score, 2),
                "sentiment": round(sentiment_score, 2),
                "conservative_factor": round(conservative_factor, 2),
            },
            "current_price": stock_data.get("quote", {}).get("c", 0),
            "recommendation": recommendation,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _calculate_fundamentals_score(self, stock_data: Dict) -> float:
        """计算基本面分数"""
        score = 50  # 基准分
        
        metrics = stock_data.get("metrics", {})
        profile = stock_data.get("profile", {})
        
        # 1. 盈利能力（25%）
        if metrics.get("profitMargin") and metrics["profitMargin"] > 0:
            profit_margin = metrics["profitMargin"]
            if profit_margin > 0.20:
                score += 15
            elif profit_margin > 0.10:
                score += 10
            elif profit_margin > 0.05:
                score += 5
            elif profit_margin <= 0:
                score -= 10
        
        # 2. 增长性（20%）
        if metrics.get("revenueGrowth") and metrics["revenueGrowth"] > 0:
            revenue_growth = metrics["revenueGrowth"]
            if revenue_growth > 0.20:
                score += 12
            elif revenue_growth > 0.10:
                score += 8
            elif revenue_growth > 0.05:
                score += 4
        
        # 3. 估值（15%）
        pe_ratio = stock_data.get("quote", {}).get("pe", 0) or metrics.get("peNormalizedAnnual", 0)
        if pe_ratio:
            if 0 < pe_ratio < 15:
                score += 12
            elif 15 <= pe_ratio < 25:
                score += 8
            elif 25 <= pe_ratio < 40:
                score += 2
            elif pe_ratio >= 40:
                score -= 5
        
        # 4. 财务健康（10%）
        if metrics.get("currentRatio"):
            current_ratio = metrics["currentRatio"]
            if current_ratio > 2.0:
                score += 7
            elif current_ratio > 1.5:
                score += 4
            elif current_ratio < 1.0:
                score -= 3
        
        # 5. 股息（加分项，对保守投资者重要）
        if profile.get("dividendYield"):
            dividend_yield = profile["dividendYield"]
            if dividend_yield > 0.03:
                score += 8
            elif dividend_yield > 0.02:
                score += 5
            elif dividend_yield > 0.01:
                score += 2
        
        return min(max(score, 0), 100)
    
    def _calculate_technicals_score(self, stock_data: Dict, market_data: Dict = None) -> float:
        """计算技术面分数"""
        score = 50  # 基准分
        
        quote = stock_data.get("quote", {})
        
        # 1. 动量（15%）
        price_change = quote.get("dp", 0)  # 日涨幅百分比
        if price_change:
            if price_change > 2.0:
                score += 8
            elif price_change > 0.5:
                score += 4
            elif price_change < -2.0:
                score -= 8
            elif price_change < -0.5:
                score -= 4
        
        # 2. 波动性（10%）
        beta = stock_data.get("metrics", {}).get("beta", 1.0)
        if beta:
            if beta < 0.8:
                score += 6  # 低波动，适合保守投资者
            elif beta < 1.2:
                score += 3
            elif beta > 1.8:
                score -= 6  # 高波动，保守投资者应谨慎
        
        # 3. 趋势（10%）
        # 简单趋势判断：如果当前价高于开盘价且高于昨日收盘价
        current = quote.get("c", 0)
        open_price = quote.get("o", 0)
        prev_close = quote.get("pc", 0)
        
        if current > open_price and current > prev_close:
            score += 6
        elif current < open_price and current < prev_close:
            score -= 4
        
        # 4. 相对强度（5%）
        if market_data:
            market_change = market_data.get("market_change", 0)
            if price_change and price_change > market_change:
                score += 3
        
        return min(max(score, 0), 100)
    
    def _calculate_sentiment_score(self, stock_data: Dict) -> float:
        """计算市场情绪分数"""
        score = 50  # 基准分
        
        # 分析师推荐
        recommendations = stock_data.get("recommendations", [])
        if recommendations:
            # 计算平均推荐（1=强烈卖出，5=强烈买入）
            avg_recommendation = sum(r.get("buy", 0) for r in recommendations) / len(recommendations)
            if avg_recommendation >= 4.0:
                score += 15
            elif avg_recommendation >= 3.0:
                score += 5
            elif avg_recommendation <= 2.0:
                score -= 10
        
        # 新闻情感
        sentiment = stock_data.get("sentiment", {})
        if sentiment.get("score"):
            sentiment_score = sentiment["score"]
            if sentiment_score > 0.3:
                score += 10
            elif sentiment_score > 0.1:
                score += 5
            elif sentiment_score < -0.3:
                score -= 10
            elif sentiment_score < -0.1:
                score -= 5
        
        return min(max(score, 0), 100)
    
    def _calculate_conservative_factor(self, stock_data: Dict) -> float:
        """计算保守系数（1.0为基准，>1.0更保守，<1.0更激进）"""
        factor = 1.0
        
        quote = stock_data.get("quote", {})
        metrics = stock_data.get("metrics", {})
        profile = stock_data.get("profile", {})
        
        # 1. 估值保守性
        pe_ratio = quote.get("pe", 0) or metrics.get("peNormalizedAnnual", 0)
        if pe_ratio:
            if pe_ratio < 15:
                factor *= 1.2  # 低估值，适合保守投资者
            elif pe_ratio < 25:
                factor *= 1.0
            elif pe_ratio >= 40:
                factor *= 0.8  # 高估值，保守投资者应减分
        
        # 2. 波动性保守性
        beta = metrics.get("beta", 1.0)
        if beta:
            if beta < 0.8:
                factor *= 1.15  # 低波动，适合保守投资者
            elif beta > 1.5:
                factor *= 0.85  # 高波动，保守投资者应减分
        
        # 3. 股息保守性
        dividend_yield = profile.get("dividendYield", 0)
        if dividend_yield > 0.02:
            factor *= 1.05  # 有股息，适合保守投资者
        
        # 4. 公司规模保守性
        market_cap = profile.get("marketCapitalization", 0)
        if market_cap > 100_000_000_000:  # 1000亿美元以上
            factor *= 1.1   # 大盘股，更稳定
        
        # Z的特殊偏好：如果他熟悉这只股票
        symbol = stock_data.get("symbol", "")
        if symbol in self.z_preferences["favorite_stocks"]:
            factor *= 1.1  # 熟悉的股票，可以稍微激进一点
        
        return round(factor, 2)
    
    def _generate_recommendation(self, total_score: float, stock_data: Dict, conservative_factor: float) -> Dict[str, Any]:
        """生成投资建议"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        # 确定建议类型
        if total_score >= 80:
            action = "strong_buy"
            confidence = "high"
        elif total_score >= 65:
            action = "buy"
            confidence = "medium"
        elif total_score >= 40:
            action = "hold"
            confidence = "low"
        elif total_score >= 20:
            action = "sell"
            confidence = "medium"
        else:
            action = "strong_sell"
            confidence = "high"
        
        # 生成具体操作建议
        if action in ["strong_buy", "buy"]:
            # 买入建议
            buy_price = current_price
            if conservative_factor > 1.1:
                # 非常保守：等待更好价格
                buy_price = round(current_price * 0.95, 2)
            
            # 对于Z偏好的sell put
            if symbol == "TSLA" and self.z_preferences["preferred_action"] == "sell_put":
                # 特斯拉sell put建议
                strike_price = round(current_price * 0.85, 2)  # 当前价的85%
                premium_estimate = round(current_price * 0.02, 2)  # 约2%权利金
                annualized_return = round((premium_estimate / strike_price) * 12 * 100, 1)  # 年化
                
                operation = {
                    "type": "sell_put",
                    "strike_price": strike_price,
                    "premium_estimate": premium_estimate,
                    "annualized_return": f"{annualized_return}%",
                    "timeframe": "30-45天",
                    "reason": "Z熟悉特斯拉，适合sell put策略"
                }
            else:
                # 普通买入建议
                operation = {
                    "type": "buy_stock",
                    "suggested_price": buy_price,
                    "position_size": "2-5% of portfolio",
                    "reason": "基本面强劲，估值合理"
                }
        elif action == "hold":
            operation = {
                "type": "hold",
                "reason": "当前持有，等待更好时机"
            }
        else:
            operation = {
                "type": "sell",
                "suggested_price": current_price,
                "reason": "基本面或估值出现风险"
            }
        
        # 生成理由
        reasons = self._generate_reasons(stock_data, total_score, conservative_factor)
        
        return {
            "action": action,
            "confidence": confidence,
            "operation": operation,
            "reasons": reasons,
            "score_explanation": self._get_score_explanation(total_score)
        }
    
    def _generate_reasons(self, stock_data: Dict, total_score: float, conservative_factor: float) -> List[str]:
        """生成投资理由"""
        reasons = []
        symbol = stock_data.get("symbol", "")
        
        # 基于分数
        if total_score >= 80:
            reasons.append("综合评分优秀，强烈推荐")
        elif total_score >= 65:
            reasons.append("评分良好，值得关注")
        
        # 基于保守系数
        if conservative_factor > 1.1:
            reasons.append("符合保守投资原则")
        elif conservative_factor < 0.9:
            reasons.append("相对激进，适合风险偏好较高的投资者")
        
        # 基于基本面
        metrics = stock_data.get("metrics", {})
        if metrics.get("profitMargin", 0) > 0.15:
            reasons.append("盈利能力强劲")
        if metrics.get("revenueGrowth", 0) > 0.15:
            reasons.append("营收增长快速")
        
        # 基于估值
        pe_ratio = stock_data.get("quote", {}).get("pe", 0) or metrics.get("peNormalizedAnnual", 0)
        if pe_ratio and pe_ratio < 20:
            reasons.append("估值合理")
        
        # 基于Z的偏好
        if symbol in self.z_preferences["favorite_stocks"]:
            reasons.append("Z熟悉该股票，操作更有把握")
        
        # 基于行业
        sector = stock_data.get("profile", {}).get("finnhubIndustry", "")
        if sector in ["Semiconductors", "Software", "Internet"]:
            reasons.append("属于科技成长行业")
        
        return reasons if reasons else ["暂无特别理由"]
    
    def _get_score_explanation(self, score: float) -> str:
        """获取分数解释"""
        if score >= 90:
            return "⭐️⭐️⭐️⭐️⭐️ 顶级投资机会"
        elif score >= 80:
            return "⭐️⭐️⭐️⭐️ 优秀投资标的"
        elif score >= 70:
            return "⭐️⭐️⭐️ 良好投资选择"
        elif score >= 60:
            return "⭐️⭐️ 一般投资机会"
        elif score >= 50:
            return "⭐️ 需要谨慎考虑"
        elif score >= 40:
            return "⚠️ 风险较高"
        elif score >= 30:
            return "⚠️⚠️ 不建议投资"
        else:
            return "🚫 高风险，应避免"
    
    def generate_daily_recommendations(self, stocks_data: Dict[str, Dict], market_data: Dict = None) -> Dict[str, Any]:
        """生成每日推荐"""
        analyzed_stocks = []
        
        for symbol, data in stocks_data.items():
            # 如果数据已经是分析结果（包含score字段），直接使用
            if isinstance(data, dict) and "score" in data:
                analyzed_stocks.append(data)
            else:
                # 否则重新分析
                analysis = self.analyze_stock(data, market_data)
                analyzed_stocks.append(analysis)
        
        # 按分数排序
        analyzed_stocks.sort(key=lambda x: x.get("score", {}).get("total", 0), reverse=True)
        
        # 筛选最佳操作
        buy_recommendations = [s for s in analyzed_stocks 
                              if s["recommendation"]["action"] in ["strong_buy", "buy"]]
        sell_recommendations = [s for s in analyzed_stocks 
                               if s["recommendation"]["action"] in ["strong_sell", "sell"]]
        
        # 选择最佳3个买入建议
        top_buys = buy_recommendations[:3]
        
        # 选择最佳sell put机会（优先Z熟悉的股票）
        sell_put_candidates = []
        for stock in analyzed_stocks:
            if stock["symbol"] in self.z_preferences["favorite_stocks"]:
                # 对于Z熟悉的股票，即使分数一般，也可以考虑sell put
                if stock["score"]["total"] >= 50:
                    sell_put_candidates.append(stock)
        
        if not sell_put_candidates:
            # 如果没有熟悉的股票，选择分数较高的
            sell_put_candidates = [s for s in analyzed_stocks if s["score"]["total"] >= 60]
        
        top_sell_puts = sell_put_candidates[:2]
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market_conditions": self._assess_market_conditions(market_data),
            "top_buy_recommendations": top_buys,
            "top_sell_put_opportunities": top_sell_puts,
            "sell_recommendations": sell_recommendations[:3],
            "portfolio_advice": self._generate_portfolio_advice(analyzed_stocks),
            "risk_warnings": self._generate_risk_warnings(market_data)
        }
    
    def _assess_market_conditions(self, market_data: Dict = None) -> Dict[str, Any]:
        """评估市场状况"""
        if not market_data:
            return {"overall": "unknown", "volatility": "unknown", "trend": "unknown"}
        
        # 这里可以添加更复杂的市场分析
        return {
            "overall": "neutral",
            "volatility": "medium",
            "trend": "sideways",
            "advice": "适合逐步建仓，避免一次性投入"
        }
    
    def _generate_portfolio_advice(self, analyzed_stocks: List[Dict]) -> List[str]:
        """生成投资组合建议"""
        advice = []
        
        # 检查是否有足够的分散
        tech_stocks = [s for s in analyzed_stocks 
                      if s.get("sector", "") in ["Technology", "Semiconductors"]]
        if len(tech_stocks) > 5:
            advice.append("科技股持仓可能过于集中，建议适当分散")
        
        # 检查估值水平
        high_pe_stocks = [s for s in analyzed_stocks 
                         if s.get("current_price", 0) > 0 and 
                         s.get("score", {}).get("conservative_factor", 1.0) < 0.9]
        if high_pe_stocks:
            advice.append("部分持仓估值偏高，注意风险")
        
        # 现金建议
        advice.append(f"建议保持{self.z_preferences['cash_reserve']*100:.0f}%现金比例，用于机会性投资")
        
        # 再平衡建议
        advice.append("每季度检查一次持仓，进行必要的再平衡")
        
        return advice
    
    def _generate_risk_warnings(self, market_data: Dict = None) -> List[str]:
        """生成风险警告"""
        warnings = []
        
        # 一般风险警告
        warnings.append("所有投资都有风险，过去表现不代表未来")
        warnings.append("建议分批建仓，避免一次性投入")
        
        # 基于Z的风险偏好
        if self.z_preferences["risk_tolerance"] == "low":
            warnings.append("根据你的保守偏好，建议优先选择低波动、有股息的大盘股")
        
        # 市场风险警告
        if market_data and market_data.get("volatility", 0) > 0.3:
            warnings.append("市场波动性较高，建议谨慎操作")
        
        return warnings