import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class ConservativeScoringAlgorithm:
    """
    保守评分算法
    
    核心公式：
    最终分数 = Mike权重 × (基本面分数 × 权重 + 技术面分数 × 权重) × 保守系数
    
    算法特点：
    1. 遵循Mike投资体系（AI/科技/太空优先）
    2. 叠加保守型投资者偏好（估值、稳定性、风险控制）
    3. 量化决策，避免情绪干扰
    """
    
    def __init__(self):
        # Mike推荐类型权重
        self.mike_weights = {
            "核心仓": 1.0,     # NVDA, GOOGL, AMZN
            "成长仓": 0.8,     # IONQ, META, Circle
            "关注仓": 0.6,     # 其他关注标的
            "加密资产": 0.7,   # BTC, ETH（风险较高但Mike看重）
        }
        
        # 保守系数计算参数
        self.conservative_params = {
            "pe_threshold_low": 20,    # PE < 20：保守系数1.2
            "pe_threshold_high": 40,   # PE > 40：保守系数0.8
            "beta_threshold": 1.0,     # Beta < 1.0：系数1.1
            "volatility_threshold": 0.3, # 30日波动率<30%：系数1.05
            "dividend_threshold": 0.02, # 股息率>2%：系数1.05
        }
        
        # 基本面评分权重
        self.fundamental_weights = {
            "valuation": 0.3,       # 估值（PE、PB、PS）
            "profitability": 0.3,   # 盈利能力（毛利率、净利率、ROE）
            "growth": 0.25,         # 成长性（营收增长、利润增长）
            "financial_health": 0.15 # 财务健康（负债率、现金流）
        }
        
        # 技术面评分权重
        self.technical_weights = {
            "trend": 0.4,           # 趋势（MA、趋势线）
            "momentum": 0.3,        # 动量（RSI、MACD）
            "volatility": 0.2,      # 波动率（ATR、Beta）
            "volume": 0.1           # 成交量（量价关系）
        }
        
        # 综合评分权重
        self.overall_weights = {
            "fundamental": 0.6,     # 基本面占60%
            "technical": 0.4        # 技术面占40%
        }
    
    def calculate_conservative_factor(self, stock_data: Dict[str, Any]) -> float:
        """
        计算保守系数
        
        原则：估值越低、波动越小、股息越高 → 系数越高（越保守）
        """
        factor = 1.0  # 基础系数
        
        # 1. PE估值因子
        pe_ratio = stock_data.get("pe_ratio")
        if pe_ratio:
            if pe_ratio < self.conservative_params["pe_threshold_low"]:
                factor *= 1.2  # 低估，保守投资者喜欢
            elif pe_ratio > self.conservative_params["pe_threshold_high"]:
                factor *= 0.8  # 高估，保守投资者谨慎
            else:
                factor *= 1.0  # 合理估值
        
        # 2. Beta波动因子
        beta = stock_data.get("beta")
        if beta:
            if beta < self.conservative_params["beta_threshold"]:
                factor *= 1.1  # 低波动，保守投资者喜欢
            else:
                factor *= 0.9  # 高波动，保守投资者谨慎
        
        # 3. 股息因子
        dividend_yield = stock_data.get("dividend_yield")
        if dividend_yield:
            if dividend_yield > self.conservative_params["dividend_threshold"]:
                factor *= 1.05  # 高股息，保守投资者喜欢
        
        # 4. 市值因子（大盘股更稳定）
        market_cap = stock_data.get("market_cap")
        if market_cap:
            if market_cap > 200 * 1e9:  # 2000亿美元以上
                factor *= 1.05
            elif market_cap < 10 * 1e9:  # 100亿美元以下
                factor *= 0.95
        
        # 系数范围限制在0.5-1.5之间
        factor = max(0.5, min(1.5, factor))
        
        logger.debug(f"保守系数计算: PE={pe_ratio}, Beta={beta}, 股息={dividend_yield}, 市值={market_cap} → 系数={factor:.2f}")
        return factor
    
    def calculate_fundamental_score(self, stock_data: Dict[str, Any], price_history: pd.DataFrame) -> float:
        """
        计算基本面分数（0-100）
        
        考虑因素：
        1. 估值水平（PE、PB、PS）
        2. 盈利能力（毛利率、净利率、ROE）
        3. 成长性（营收/利润增长）
        4. 财务健康（负债率、现金流）
        """
        score = 50.0  # 基础分
        
        # 简化版：主要看PE和市值
        pe_ratio = stock_data.get("pe_ratio")
        market_cap = stock_data.get("market_cap")
        
        if pe_ratio:
            # PE越低分数越高（对保守投资者）
            if pe_ratio < 15:
                score += 25
            elif pe_ratio < 25:
                score += 15
            elif pe_ratio < 40:
                score += 5
            else:
                score -= 10
        
        if market_cap:
            # 市值越大越稳定（对保守投资者）
            if market_cap > 500 * 1e9:  # 5000亿美元以上
                score += 15
            elif market_cap > 100 * 1e9:  # 1000亿美元以上
                score += 10
            elif market_cap > 10 * 1e9:  # 100亿美元以上
                score += 5
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        logger.debug(f"基本面分数: PE={pe_ratio}, 市值={market_cap} → 分数={score:.1f}")
        return score
    
    def calculate_technical_score(self, price_history: pd.DataFrame) -> float:
        """
        计算技术面分数（0-100）
        
        考虑因素：
        1. 趋势强度（均线排列）
        2. 动量指标（RSI、MACD）
        3. 支撑阻力位置
        4. 成交量确认
        """
        if price_history.empty or len(price_history) < 20:
            return 50.0  # 数据不足时返回中性分数
        
        score = 50.0
        
        try:
            close_prices = price_history['close'].values
            
            # 1. 计算短期趋势（20日MA vs 50日MA）
            if len(close_prices) >= 50:
                ma_20 = np.mean(close_prices[-20:])
                ma_50 = np.mean(close_prices[-50:])
                
                if ma_20 > ma_50:
                    score += 15  # 多头排列
                elif ma_20 < ma_50:
                    score -= 10  # 空头排列
                else:
                    score += 5   # 均线纠缠
            
            # 2. 计算相对位置（当前价格 vs 20日高低点）
            high_20 = np.max(close_prices[-20:])
            low_20 = np.min(close_prices[-20:])
            current_price = close_prices[-1]
            
            # 相对位置分数（0-1）
            position_score = (current_price - low_20) / (high_20 - low_20) if high_20 > low_20 else 0.5
            
            if position_score > 0.7:
                score += 10  # 接近高点，强势
            elif position_score < 0.3:
                score -= 10  # 接近低点，弱势
            else:
                score += 5   # 中间位置
            
            # 3. 简单动量计算（5日涨跌幅）
            if len(close_prices) >= 5:
                momentum_5d = (close_prices[-1] - close_prices[-5]) / close_prices[-5]
                
                if momentum_5d > 0.05:  # 5日涨幅>5%
                    score += 10
                elif momentum_5d < -0.05:  # 5日跌幅>5%
                    score -= 10
                else:
                    score += 5
        
        except Exception as e:
            logger.warning(f"技术面计算异常: {e}")
            return 50.0
        
        # 确保分数在0-100范围内
        score = max(0, min(100, score))
        
        logger.debug(f"技术面分数: 数据点={len(price_history)} → 分数={score:.1f}")
        return score
    
    def get_mike_weight(self, recommendation_type: Optional[str]) -> float:
        """
        获取Mike推荐权重
        
        核心仓（NVDA/GOOGL/AMZN）：权重最高
        成长仓：次高
        其他：基础权重
        """
        if recommendation_type in self.mike_weights:
            return self.mike_weights[recommendation_type]
        
        # 默认权重
        return 0.7
    
    def calculate_final_score(self, 
                             mike_recommendation: Dict[str, Any],
                             stock_data: Dict[str, Any],
                             price_history: pd.DataFrame) -> Dict[str, Any]:
        """
        计算最终分数和推荐
        
        返回：
        - 最终分数（0-100）
        - 推荐等级（强烈买入/买入/持有/卖出/强烈卖出）
        - sell put建议（行权价区间、收益率）
        - 详细推理过程
        """
        # 1. 获取Mike权重
        mike_weight = self.get_mike_weight(mike_recommendation.get("recommendation_type"))
        
        # 2. 计算基本面分数
        fundamental_score = self.calculate_fundamental_score(stock_data, price_history)
        
        # 3. 计算技术面分数
        technical_score = self.calculate_technical_score(price_history)
        
        # 4. 计算保守系数
        conservative_factor = self.calculate_conservative_factor(stock_data)
        
        # 5. 计算综合分数
        combined_score = (fundamental_score * self.overall_weights["fundamental"] + 
                          technical_score * self.overall_weights["technical"])
        
        # 6. 应用Mike权重和保守系数
        final_score = mike_weight * combined_score * conservative_factor
        
        # 确保分数在0-100范围内
        final_score = max(0, min(100, final_score))
        
        # 7. 生成推荐等级
        recommendation = self._generate_recommendation(final_score, stock_data)
        
        # 8. 生成sell put建议（如果适用）
        sell_put_suggestion = self._generate_sell_put_suggestion(stock_data, price_history, final_score)
        
        # 9. 构建详细推理
        reasoning = self._build_reasoning(
            mike_weight=mike_weight,
            fundamental_score=fundamental_score,
            technical_score=technical_score,
            conservative_factor=conservative_factor,
            combined_score=combined_score,
            final_score=final_score,
            stock_data=stock_data,
            recommendation_type=mike_recommendation.get("recommendation_type"),
            mike_reason=mike_recommendation.get("mike_reason")
        )
        
        result = {
            "final_score": round(final_score, 2),
            "recommendation": recommendation,
            "sell_put_suggestion": sell_put_suggestion,
            "reasoning": reasoning,
            "components": {
                "mike_weight": mike_weight,
                "fundamental_score": round(fundamental_score, 2),
                "technical_score": round(technical_score, 2),
                "conservative_factor": round(conservative_factor, 2),
                "combined_score": round(combined_score, 2)
            }
        }
        
        logger.info(f"评分完成: {stock_data.get('symbol')} → 分数={final_score:.1f}, 推荐={recommendation}")
        return result
    
    def _generate_recommendation(self, score: float, stock_data: Dict[str, Any]) -> str:
        """根据分数生成推荐等级"""
        if score >= 80:
            return "强烈买入"
        elif score >= 65:
            return "买入"
        elif score >= 40:
            return "持有"
        elif score >= 20:
            return "卖出"
        else:
            return "强烈卖出"
    
    def _generate_sell_put_suggestion(self, stock_data: Dict[str, Any], 
                                     price_history: pd.DataFrame,
                                     final_score: float) -> Optional[Dict[str, Any]]:
        """
        生成sell put建议
        
        保守投资者的sell put策略：
        1. 只卖深度虚值put（下行风险小）
        2. 选择低波动、高股息股票
        3. 避开高估值、高波动股票
        """
        # 只对分数>=60的股票生成sell put建议
        if final_score < 60:
            return None
        
        current_price = stock_data.get("current_price")
        if not current_price:
            if not price_history.empty:
                current_price = price_history['close'].iloc[-1]
            else:
                return None
        
        # 计算20日波动率
        volatility = 0.2  # 默认20%
        if len(price_history) >= 20:
            returns = price_history['close'].pct_change().dropna()
            if len(returns) > 0:
                volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 保守的sell put策略
        # 深度虚值：行权价比当前价低15-25%
        strike_range = {
            "very_conservative": current_price * 0.75,  # 25%虚值
            "conservative": current_price * 0.80,       # 20%虚值
            "moderate": current_price * 0.85,           # 15%虚值
        }
        
        # 预期年化收益率（简化计算）
        # 实际中需要期权定价模型
        expected_yield = max(0.08, min(0.20, 0.12 - volatility * 0.3))
        
        suggestion = {
            "current_price": round(current_price, 2),
            "volatility_pct": round(volatility * 100, 1),
            "strike_range": {k: round(v, 2) for k, v in strike_range.items()},
            "expected_yield_pct": round(expected_yield * 100, 1),
            "timeframe": "30-45天到期",
            "risk_level": "低" if volatility < 0.3 else "中",
            "suitability": "适合" if final_score >= 70 and volatility < 0.35 else "谨慎"
        }
        
        return suggestion
    
    def _build_reasoning(self, **components) -> str:
        """构建详细的推理说明"""
        reasoning_parts = []
        
        # Mike权重说明
        mike_weight = components.get("mike_weight", 1.0)
        recommendation_type = components.get("recommendation_type")
        
        if recommendation_type:
            if mike_weight >= 1.0:
                reasoning_parts.append(f"该股票是Mike推荐的【{recommendation_type}】，权重最高（{mike_weight}倍）")
            elif mike_weight >= 0.8:
                reasoning_parts.append(f"该股票是Mike推荐的【{recommendation_type}】，权重较高（{mike_weight}倍）")
            elif mike_weight >= 0.6:
                reasoning_parts.append(f"该股票是Mike推荐的【{recommendation_type}】，权重适中（{mike_weight}倍）")
        
        # 基本面说明
        fundamental_score = components.get("fundamental_score", 50)
        pe_ratio = components.get("stock_data", {}).get("pe_ratio")
        
        if pe_ratio:
            if pe_ratio < 15:
                reasoning_parts.append(f"估值极低（PE={pe_ratio:.1f}），基本面稳健")
            elif pe_ratio < 25:
                reasoning_parts.append(f"估值合理（PE={pe_ratio:.1f}），基本面良好")
            elif pe_ratio < 40:
                reasoning_parts.append(f"估值偏高（PE={pe_ratio:.1f}），需关注增长性")
            else:
                reasoning_parts.append(f"估值过高（PE={pe_ratio:.1f}），风险较大")
        
        # 技术面说明
        technical_score = components.get("technical_score", 50)
        if technical_score >= 70:
            reasoning_parts.append("技术面显示强劲上升趋势")
        elif technical_score >= 60:
            reasoning_parts.append("技术面偏正面，趋势向好")
        elif technical_score <= 40:
            reasoning_parts.append("技术面偏弱，需谨慎")
        
        # 保守系数说明
        conservative_factor = components.get("conservative_factor", 1.0)
        if conservative_factor > 1.1:
            reasoning_parts.append("该股票符合保守投资偏好（低估值、低波动、高股息）")
        elif conservative_factor < 0.9:
            reasoning_parts.append("该股票风险较高（高估值、高波动），保守投资者需谨慎")
        
        # 最终推荐
        final_score = components.get("final_score", 50)
        if final_score >= 80:
            reasoning_parts.append("综合评分极高，强烈建议买入并长期持有")
        elif final_score >= 65:
            reasoning_parts.append("评分良好，建议分批买入或sell put获取收益")
        elif final_score >= 40:
            reasoning_parts.append("评分中性，建议持有观望或少量配置")
        elif final_score >= 20:
            reasoning_parts.append("评分较低，建议减持或规避")
        else:
            reasoning_parts.append("评分极低，强烈建议卖出或避免投资")
        
        # 添加Mike的原始理由
        mike_reason = components.get("mike_reason")
        if mike_reason:
            reasoning_parts.append(f"Mike推荐理由：{mike_reason}")
        
        return " | ".join(reasoning_parts)