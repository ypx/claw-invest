"""
投资组合分析器 - 专门分析Z的实际持仓
基于Claw决策引擎和风险监控系统，提供个性化的持仓分析和优化建议
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from data_service.portfolio_manager import PortfolioManager
from analysis_engine.claw_decision_engine import create_decision_engine
from analysis_engine.risk_monitor import create_risk_monitor

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """投资组合分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.portfolio_manager = PortfolioManager()
        self.decision_engine = create_decision_engine()
        self.risk_monitor = create_risk_monitor()
        
        # Z的特殊偏好和约束
        self.z_preferences = {
            "risk_tolerance": "conservative",  # 保守型投资者
            "preferred_stocks": ["TSLA", "NVDA", "GOOGL"],  # 熟悉且偏好的股票
            "target_cash_ratio": 0.35,  # 现金比例目标
            "max_single_position": 0.15,  # 单一仓位最高比例
            "preferred_strategies": ["cash_secured_put"],  # 偏好的期权策略
            "investment_focus": ["AI", "Space", "Crypto"],  # 投资重点领域
            "holding_period": "long_term"  # 长期持有
        }
    
    def analyze_portfolio(self, market_data: Dict = None) -> Dict[str, Any]:
        """综合分析投资组合
        
        Args:
            market_data: 市场数据，如果为None则从决策引擎获取
            
        Returns:
            完整的分析结果
        """
        logger.info("开始分析Z的投资组合...")
        
        # 1. 获取持仓数据
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        portfolio_export = self.portfolio_manager.export_to_claw_format()
        
        # 2. 获取市场数据（如果需要）
        if not market_data:
            # 在实际系统中，这里应该从API获取实时市场数据
            # 现在使用决策引擎生成的市场数据
            market_data = self.decision_engine.get_market_data()
        
        # 3. 进行投资组合健康度评估
        logger.info("进行投资组合健康度评估...")
        health_analysis = self._analyze_portfolio_health(portfolio_export, market_data)
        
        # 4. 进行风险监控
        logger.info("进行风险监控分析...")
        risk_analysis = self.risk_monitor.monitor_portfolio_risk(portfolio_export, market_data)
        
        # 5. 生成个性化建议
        logger.info("生成个性化投资建议...")
        recommendations = self._generate_personalized_recommendations(
            portfolio_summary, health_analysis, risk_analysis, market_data
        )
        
        # 6. 构建完整分析报告
        analysis_report = {
            "metadata": {
                "analyzed_for": "Z",
                "analysis_type": "comprehensive",
                "analysis_date": datetime.now().isoformat(),
                "risk_profile": self.z_preferences["risk_tolerance"],
                "preferences_applied": self.z_preferences
            },
            "portfolio_summary": portfolio_summary,
            "health_analysis": health_analysis,
            "risk_analysis": risk_analysis,
            "personalized_recommendations": recommendations,
            "market_context": {
                "market_condition": market_data.get("condition", "normal"),
                "vix_level": market_data.get("vix", 0),
                "interest_rate": market_data.get("interest_rate", 0),
                "analysis_timeframe": "current"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 7. 记录分析结果
        self._log_analysis_results(analysis_report)
        
        logger.info(f"投资组合分析完成。总价值: ${portfolio_summary['performance']['total_value']:,.2f}")
        return analysis_report
    
    def _analyze_portfolio_health(self, portfolio_export: Dict, market_data: Dict) -> Dict:
        """分析投资组合健康度"""
        current_state = portfolio_export.get("current_state", {})
        
        # 1. 现金比例分析
        cash_ratio = current_state.get("cash_ratio", 0)
        target_cash = self.z_preferences["target_cash_ratio"] * 100
        
        cash_health = {
            "current_ratio": round(cash_ratio, 1),
            "target_ratio": round(target_cash, 1),
            "deviation": round(cash_ratio - target_cash, 1),
            "status": "正常" if abs(cash_ratio - target_cash) <= 10 else "需要调整"
        }
        
        # 2. 集中度分析
        positions = current_state.get("positions", [])
        position_count = len(positions)
        
        concentration_health = {
            "position_count": position_count,
            "ideal_count": 8,  # Z偏好的持仓数量
            "assessment": "足够分散" if position_count >= 6 else "可能过于集中",
            "top3_weight": 0
        }
        
        if position_count > 0:
            # 计算前三大持仓权重
            positions_sorted = sorted(positions, key=lambda x: x.get("current_value", 0), reverse=True)
            top3_value = sum(pos.get("current_value", 0) for pos in positions_sorted[:3])
            total_value = sum(pos.get("current_value", 0) for pos in positions)
            if total_value > 0:
                concentration_health["top3_weight"] = round((top3_value / total_value) * 100, 1)
        
        # 3. 行业分布分析
        sector_allocation = current_state.get("sector_allocation", {})
        preferred_sectors = ["Technology", "Communication Services", "Consumer Cyclical"]
        
        sector_health = {
            "sector_distribution": sector_allocation,
            "preferred_sectors": preferred_sectors,
            "diversification_score": self._calculate_diversification_score(sector_allocation),
            "recommendation": self._generate_sector_recommendation(sector_allocation, preferred_sectors)
        }
        
        # 4. 持仓质量分析
        quality_health = {
            "familiar_stocks_ratio": self._calculate_familiar_stocks_ratio(positions),
            "growth_focus_ratio": self._calculate_growth_focus_ratio(positions),
            "valuation_quality": self._assess_valuation_quality(positions, market_data)
        }
        
        # 5. 整体健康评分
        health_score = self._calculate_overall_health_score(
            cash_health, concentration_health, sector_health, quality_health
        )
        
        health_analysis = {
            "cash_analysis": cash_health,
            "concentration_analysis": concentration_health,
            "sector_analysis": sector_health,
            "quality_analysis": quality_health,
            "overall_health_score": health_score,
            "timestamp": datetime.now().isoformat()
        }
        
        return health_analysis
    
    def _calculate_diversification_score(self, sector_allocation: Dict) -> float:
        """计算行业分散度得分"""
        if not sector_allocation:
            return 100.0  # 无持仓视为完美分散
        
        # 使用熵的概念计算分散度
        total_allocation = sum(sector_allocation.values())
        if total_allocation <= 0:
            return 0.0
        
        # 归一化
        normalized_allocation = {k: v/total_allocation for k, v in sector_allocation.items()}
        
        # 计算熵（分散度越高，熵越大）
        entropy = 0
        for allocation in normalized_allocation.values():
            if allocation > 0:
                entropy -= allocation * np.log(allocation)
        
        # 最大可能熵（完全平均分布）
        n_sectors = len(sector_allocation)
        max_entropy = np.log(n_sectors) if n_sectors > 0 else 0
        
        # 转换为百分比得分
        score = (entropy / max_entropy * 100) if max_entropy > 0 else 100
        return round(score, 1)
    
    def _calculate_familiar_stocks_ratio(self, positions: List[Dict]) -> float:
        """计算熟悉股票占比"""
        if not positions:
            return 0.0
        
        familiar_stocks = self.z_preferences["preferred_stocks"]
        
        stock_positions = [pos for pos in positions if pos.get("type") == "stock"]
        if not stock_positions:
            return 0.0
        
        familiar_count = sum(1 for pos in stock_positions if pos.get("symbol") in familiar_stocks)
        
        return round((familiar_count / len(stock_positions)) * 100, 1)
    
    def _calculate_growth_focus_ratio(self, positions: List[Dict]) -> float:
        """计算成长股聚焦度"""
        if not positions:
            return 0.0
        
        growth_stocks = ["NVDA", "IONQ", "TSLA", "RKLB", "ASTS"]
        
        stock_positions = [pos for pos in positions if pos.get("type") == "stock"]
        if not stock_positions:
            return 0.0
        
        total_value = sum(pos.get("current_value", 0) for pos in stock_positions)
        if total_value <= 0:
            return 0.0
        
        growth_value = sum(
            pos.get("current_value", 0) for pos in stock_positions 
            if pos.get("symbol") in growth_stocks
        )
        
        return round((growth_value / total_value) * 100, 1)
    
    def _assess_valuation_quality(self, positions: List[Dict], market_data: Dict) -> Dict:
        """评估持仓估值质量"""
        # 在实际系统中，这里应该使用完整的估值模型
        # 现在使用简化的评估
        
        if not positions:
            return {"overall": "N/A", "details": []}
        
        stock_positions = [pos for pos in positions if pos.get("type") == "stock"]
        
        # 检查持仓是否在高估区域
        high_valuation_stocks = ["NVDA", "TSLA", "AAPL"]
        overvalued_count = sum(1 for pos in stock_positions if pos.get("symbol") in high_valuation_stocks)
        
        total_stocks = len(stock_positions)
        overvalued_ratio = overvalued_count / total_stocks if total_stocks > 0 else 0
        
        if overvalued_ratio > 0.5:
            overall_quality = "偏高 - 较多持仓在高估值区域"
        elif overvalued_ratio > 0.2:
            overall_quality = "适中 - 部分持仓估值偏高"
        else:
            overall_quality = "良好 - 大部分持仓估值合理"
        
        details = [
            f"共持仓{total_stocks}只股票，其中{overvalued_count}只可能估值偏高"
        ]
        
        return {
            "overall": overall_quality,
            "details": details
        }
    
    def _generate_sector_recommendation(self, sector_allocation: Dict, preferred_sectors: List[str]) -> str:
        """生成行业分布建议"""
        if not sector_allocation:
            return "建议从偏好行业（科技、通信、消费）开始配置"
        
        # 计算偏好行业占比
        preferred_total = sum(allocation for sector, allocation in sector_allocation.items() 
                             if sector in preferred_sectors)
        
        if preferred_total < 50:
            return f"偏好行业占比{preferred_total:.1f}%，建议增加至60%以上"
        elif preferred_total > 90:
            return f"偏好行业占比过高({preferred_total:.1f}%)，建议增加防御性行业配置"
        else:
            return f"行业分布合理，偏好行业占比{preferred_total:.1f}%"
    
    def _calculate_overall_health_score(self, cash_health: Dict, concentration_health: Dict,
                                      sector_health: Dict, quality_health: Dict) -> float:
        """计算整体健康评分"""
        scores = []
        
        # 1. 现金健康度评分（权重30%）
        cash_deviation = abs(cash_health.get("deviation", 0))
        if cash_deviation <= 5:
            cash_score = 95
        elif cash_deviation <= 10:
            cash_score = 85
        elif cash_deviation <= 15:
            cash_score = 75
        else:
            cash_score = 60
        scores.append(cash_score * 0.3)
        
        # 2. 集中度评分（权重25%）
        top3_weight = concentration_health.get("top3_weight", 0)
        if top3_weight == 0:
            conc_score = 100
        elif top3_weight <= 40:
            conc_score = 90
        elif top3_weight <= 60:
            conc_score = 80
        else:
            conc_score = 65
        scores.append(conc_score * 0.25)
        
        # 3. 行业分散度评分（权重25%）
        sector_score = sector_health.get("diversification_score", 100)
        scores.append(sector_score * 0.25)
        
        # 4. 持仓质量评分（权重20%）
        familiar_ratio = quality_health.get("familiar_stocks_ratio", 0)
        if familiar_ratio >= 70:
            quality_score = 90
        elif familiar_ratio >= 50:
            quality_score = 80
        else:
            quality_score = 70
        scores.append(quality_score * 0.2)
        
        total_score = sum(scores)
        return round(total_score, 1)
    
    def _generate_personalized_recommendations(self, portfolio_summary: Dict, 
                                             health_analysis: Dict, 
                                             risk_analysis: Dict,
                                             market_data: Dict) -> Dict:
        """生成个性化投资建议"""
        recommendations = {
            "cash_management": self._generate_cash_recommendations(health_analysis["cash_analysis"]),
            "diversification": self._generate_diversification_recommendations(
                health_analysis["concentration_analysis"],
                health_analysis["sector_analysis"]
            ),
            "risk_management": self._generate_risk_recommendations(risk_analysis),
            "opportunities": self._generate_opportunity_recommendations(
                portfolio_summary, market_data
            ),
            "action_items": self._generate_action_items(
                portfolio_summary, health_analysis, risk_analysis
            )
        }
        
        return recommendations
    
    def _generate_cash_recommendations(self, cash_analysis: Dict) -> List[str]:
        """生成现金管理建议"""
        recommendations = []
        
        current_ratio = cash_analysis.get("current_ratio", 0)
        target_ratio = cash_analysis.get("target_ratio", 0)
        deviation = cash_analysis.get("deviation", 0)
        
        if current_ratio < target_ratio * 0.8:
            recommendations.append(
                f"现金比例({current_ratio:.1f}%)低于目标({target_ratio:.1f}%)，建议保留35%现金应对市场波动"
            )
            recommendations.append(
                f"可考虑卖出部分高估值或非核心持仓，增加现金储备"
            )
        elif current_ratio > target_ratio * 1.3:
            recommendations.append(
                f"现金比例({current_ratio:.1f}%)明显高于目标({target_ratio:.1f}%)，可考虑分批配置优质标的"
            )
            recommendations.append(
                f"考虑使用现金开展sell put策略，在等待机会的同时获得权利金收入"
            )
        else:
            recommendations.append(
                f"现金比例({current_ratio:.1f}%)合理，接近目标({target_ratio:.1f}%)，维持现状"
            )
        
        return recommendations
    
    def _generate_diversification_recommendations(self, concentration_analysis: Dict, 
                                                sector_analysis: Dict) -> List[str]:
        """生成分散度建议"""
        recommendations = []
        
        # 持仓数量建议
        position_count = concentration_analysis.get("position_count", 0)
        ideal_count = concentration_analysis.get("ideal_count", 8)
        
        if position_count < ideal_count * 0.6:
            recommendations.append(
                f"持仓数量({position_count})较少，建议逐步增加至8只左右"
            )
        elif position_count > ideal_count * 1.5:
            recommendations.append(
                f"持仓数量({position_count})较多，可考虑精简至8只核心持仓"
            )
        
        # 行业分散建议
        sector_distribution = sector_analysis.get("sector_distribution", {})
        sector_score = sector_analysis.get("diversification_score", 100)
        
        if sector_score < 60:
            recommendations.append(
                f"行业分散度较低({sector_score:.1f}分)，建议增加其他行业配置"
            )
        
        # 前三大持仓检查
        top3_weight = concentration_analysis.get("top3_weight", 0)
        if top3_weight > 60:
            recommendations.append(
                f"前三大持仓权重({top3_weight:.1f}%)偏高，建议分散配置降低集中度"
            )
        
        if not recommendations:
            recommendations.append("投资组合分散度良好，继续维持当前配置")
        
        return recommendations
    
    def _generate_risk_recommendations(self, risk_analysis: Dict) -> List[str]:
        """生成风险管理建议"""
        recommendations = []
        
        risk_metrics = risk_analysis.get("risk_metrics", {})
        stress_tests = risk_analysis.get("stress_tests", {})
        
        # 波动率风险建议
        volatility = risk_metrics.get("annualized_volatility", 0)
        if volatility > 25:
            recommendations.append(f"组合波动率({volatility:.1f}%)偏高，建议增加防御性资产")
        elif volatility > 18:
            recommendations.append(f"组合波动率({volatility:.1f}%)适中，注意风险管理")
        
        # 压力测试建议
        overall_resilience = stress_tests.get("overall_resilience", {})
        resilience_score = overall_resilience.get("score", 0)
        
        if resilience_score < 50:
            recommendations.append("组合风险承受能力偏低，建议降低高风险资产配置")
        elif resilience_score < 70:
            recommendations.append("组合风险承受能力中等，注意控制仓位和分散")
        
        if not recommendations:
            recommendations.append("风险控制良好，继续关注市场变化")
        
        return recommendations
    
    def _generate_opportunity_recommendations(self, portfolio_summary: Dict, 
                                           market_data: Dict) -> List[str]:
        """生成机会发现建议"""
        recommendations = []
        
        # 基于市场环境的机会建议
        market_condition = market_data.get("condition", "normal")
        vix = market_data.get("vix", 15)
        
        if market_condition == "volatile" and vix > 30:
            recommendations.append("市场波动较大，sell put策略机会增多，可关注熟悉股票的期权机会")
        elif market_condition == "bullish":
            recommendations.append("市场趋势向好，可考虑在回调时增加核心持仓配置")
        
        # 基于Z偏好的建议
        familiar_stocks = self.z_preferences["preferred_stocks"]
        investment_focus = self.z_preferences["investment_focus"]
        
        for stock in familiar_stocks:
            if stock not in portfolio_summary.get("top_holdings", []):
                recommendations.append(f"考虑在合适价位增持熟悉股票 {stock}")
        
        return recommendations
    
    def _generate_action_items(self, portfolio_summary: Dict, 
                             health_analysis: Dict, 
                             risk_analysis: Dict) -> List[Dict]:
        """生成具体行动项"""
        action_items = []
        
        # 1. 现金管理行动
        cash_analysis = health_analysis.get("cash_analysis", {})
        current_cash = cash_analysis.get("current_ratio", 0)
        target_cash = cash_analysis.get("target_ratio", 0)
        
        if current_cash < target_cash * 0.8:
            action_items.append({
                "priority": "高",
                "action": "增加现金比例",
                "target": f"从{current_cash:.1f}%调整至{target_cash:.1f}%",
                "timeline": "本周内"
            })
        
        # 2. 分散度行动
        concentration = health_analysis.get("concentration_analysis", {})
        top3_weight = concentration.get("top3_weight", 0)
        
        if top3_weight > 60:
            action_items.append({
                "priority": "中",
                "action": "降低前三大持仓权重",
                "target": f"从{top3_weight:.1f}%降低至50%以下",
                "timeline": "下月内"
            })
        
        # 3. 风险管理行动
        risk_alerts = risk_analysis.get("alerts", [])
        if len(risk_alerts) >= 2:
            action_items.append({
                "priority": "高",
                "action": "处理风险警报",
                "target": f"解决{len(risk_alerts)}个风险警报",
                "timeline": "本周内"
            })
        
        # 默认行动项
        if not action_items:
            action_items.append({
                "priority": "低",
                "action": "定期监控投资组合",
                "target": "每日检查持仓和市场变化",
                "timeline": "每日"
            })
        
        return action_items
    
    def _log_analysis_results(self, analysis_report: Dict) -> None:
        """记录分析结果"""
        summary = analysis_report.get("portfolio_summary", {})
        health = analysis_report.get("health_analysis", {})
        
        total_value = summary.get("performance", {}).get("total_value", 0)
        health_score = health.get("overall_health_score", 0)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_value": total_value,
            "health_score": health_score,
            "cash_ratio": health.get("cash_analysis", {}).get("current_ratio", 0),
            "position_count": health.get("concentration_analysis", {}).get("position_count", 0),
            "sector_score": health.get("sector_analysis", {}).get("diversification_score", 0)
        }
        
        logger.info(f"投资组合分析记录: 总价值${total_value:,.2f}, 健康评分{health_score}分")
        
        # 在实际系统中，这里应该将log_entry保存到数据库
        # 现在使用日志记录


def create_portfolio_analyzer() -> PortfolioAnalyzer:
    """创建投资组合分析器实例"""
    return PortfolioAnalyzer()