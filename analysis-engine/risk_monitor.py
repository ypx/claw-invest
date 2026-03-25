"""
风险监控和预警系统 - 实时监控投资组合风险
提供预警、风险控制和应对建议
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class RiskMonitor:
    """风险监控和预警系统"""
    
    def __init__(self):
        # 风险阈值
        self.risk_thresholds = {
            "volatility": {
                "warning": 0.20,   # 年化波动率警告阈值
                "critical": 0.30,  # 年化波动率危险阈值
                "target": 0.18     # 目标波动率
            },
            "drawdown": {
                "warning": 0.10,   # 回撤警告阈值
                "critical": 0.20   # 回撤危险阈值
            },
            "concentration": {
                "single_stock": 0.15,  # 单只股票最大仓位
                "sector": 0.35,        # 单一行业最大仓位
                "cash_min": 0.25,      # 最小现金比例
                "cash_target": 0.35    # 目标现金比例
            },
            "correlation": {
                "high": 0.7,        # 高相关性阈值
                "critical": 0.85    # 极高相关性阈值
            }
        }
        
        # 预警级别
        self.alert_levels = {
            "normal": "🟢 正常",
            "watch": "🟡 关注",
            "warning": "🟠 警告",
            "critical": "🔴 危险",
            "emergency": "🛑 紧急"
        }
        
        # 历史风险数据（在实际系统中应该从数据库读取）
        self.risk_history = {}
        
        # 风险事件日志
        self.event_log = []
    
    def monitor_portfolio_risk(self, portfolio_analysis: Dict, market_data: Dict = None) -> Dict[str, Any]:
        """监控投资组合风险"""
        if not portfolio_analysis:
            return {"error": "无效的投资组合分析数据"}
        
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "alerts": self._check_risk_alerts(portfolio_analysis, market_data),
            "risk_metrics": self._calculate_risk_metrics(portfolio_analysis, market_data),
            "stress_tests": self._perform_stress_tests(portfolio_analysis),
            "recommendations": self._generate_risk_recommendations(portfolio_analysis),
            "action_plan": self._create_risk_action_plan(portfolio_analysis, market_data)
        }
        
        # 记录风险事件
        self._log_risk_events(monitoring_results)
        
        # 更新风险历史
        self._update_risk_history(monitoring_results)
        
        return monitoring_results
    
    def _check_risk_alerts(self, portfolio_analysis: Dict, market_data: Dict) -> List[Dict[str, Any]]:
        """检查风险警报"""
        alerts = []
        
        # 1. 波动率风险检查
        volatility_risk = self._check_volatility_risk(portfolio_analysis)
        if volatility_risk:
            alerts.append(volatility_risk)
        
        # 2. 回撤风险检查
        drawdown_risk = self._check_drawdown_risk(portfolio_analysis)
        if drawdown_risk:
            alerts.append(drawdown_risk)
        
        # 3. 集中度风险检查
        concentration_risk = self._check_concentration_risk(portfolio_analysis)
        if concentration_risk:
            alerts.append(concentration_risk)
        
        # 4. 流动性风险检查
        liquidity_risk = self._check_liquidity_risk(portfolio_analysis)
        if liquidity_risk:
            alerts.append(liquidity_risk)
        
        # 5. 市场风险检查
        market_risk = self._check_market_risk(market_data)
        if market_risk:
            alerts.append(market_risk)
        
        # 6. 相关性风险检查
        correlation_risk = self._check_correlation_risk(portfolio_analysis)
        if correlation_risk:
            alerts.append(correlation_risk)
        
        # 7. 宏观风险检查
        macro_risk = self._check_macro_risk(market_data)
        if macro_risk:
            alerts.append(macro_risk)
        
        return alerts
    
    def _check_volatility_risk(self, portfolio_analysis: Dict) -> Optional[Dict[str, Any]]:
        """检查波动率风险"""
        risk_indicators = portfolio_analysis.get("risk_assessment", {}).get("indicators", {})
        volatility = risk_indicators.get("annualized_volatility", 0) / 100
        
        if volatility >= self.risk_thresholds["volatility"]["critical"]:
            return {
                "type": "volatility_risk",
                "level": "critical",
                "message": f"组合波动率极高({volatility*100:.1f}%)，远超过危险阈值({self.risk_thresholds['volatility']['critical']*100:.0f}%)",
                "details": f"当前波动率: {volatility*100:.1f}% | 危险阈值: {self.risk_thresholds['volatility']['critical']*100:.0f}%",
                "severity": 9,
                "recommended_actions": [
                    "立即减持高波动性股票",
                    "增加防御性资产配置",
                    "考虑购买保护性期权"
                ]
            }
        elif volatility >= self.risk_thresholds["volatility"]["warning"]:
            return {
                "type": "volatility_risk",
                "level": "warning",
                "message": f"组合波动率偏高({volatility*100:.1f}%)，超过警告阈值({self.risk_thresholds['volatility']['warning']*100:.0f}%)",
                "details": f"当前波动率: {volatility*100:.1f}% | 警告阈值: {self.risk_thresholds['volatility']['warning']*100:.0f}% | 目标: {self.risk_thresholds['volatility']['target']*100:.0f}%",
                "severity": 6,
                "recommended_actions": [
                    "考虑降低高波动性股票仓位",
                    "增加低波动性防御股票",
                    "监控市场波动情况"
                ]
            }
        
        return None
    
    def _check_drawdown_risk(self, portfolio_analysis: Dict) -> Optional[Dict[str, Any]]:
        """检查回撤风险"""
        risk_indicators = portfolio_analysis.get("risk_assessment", {}).get("indicators", {})
        max_drawdown = risk_indicators.get("max_drawdown", 0)
        
        if max_drawdown >= self.risk_thresholds["drawdown"]["critical"]:
            return {
                "type": "drawdown_risk",
                "level": "critical",
                "message": f"组合潜在最大回撤极高({max_drawdown*100:.1f}%)，超过危险阈值({self.risk_thresholds['drawdown']['critical']*100:.0f}%)",
                "details": f"当前潜在最大回撤: {max_drawdown*100:.1f}% | 危险阈值: {self.risk_thresholds['drawdown']['critical']*100:.0f}%",
                "severity": 9,
                "recommended_actions": [
                    "立即实施止损策略",
                    "增加现金比例",
                    "考虑对冲策略"
                ]
            }
        elif max_drawdown >= self.risk_thresholds["drawdown"]["warning"]:
            return {
                "type": "drawdown_risk",
                "level": "warning",
                "message": f"组合潜在最大回撤偏高({max_drawdown*100:.1f}%)，超过警告阈值({self.risk_thresholds['drawdown']['warning']*100:.0f}%)",
                "details": f"当前潜在最大回撤: {max_drawdown*100:.1f}% | 警告阈值: {self.risk_thresholds['drawdown']['warning']*100:.0f}%",
                "severity": 6,
                "recommend_actions": [
                    "检查高回撤风险持仓",
                    "考虑增加防御性配置",
                    "设定止损位"
                ]
            }
        
        return None
    
    def _check_concentration_risk(self, portfolio_analysis: Dict) -> Optional[Dict[str, Any]]:
        """检查集中度风险"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        
        alerts = []
        
        # 检查单只股票集中度
        for pos in positions:
            position_ratio = pos.get("position_ratio", 0)
            if position_ratio > self.risk_thresholds["concentration"]["single_stock"]:
                alerts.append({
                    "symbol": pos.get("symbol", ""),
                    "current_ratio": position_ratio,
                    "threshold": self.risk_thresholds["concentration"]["single_stock"],
                    "risk": "单只股票过度集中"
                })
        
        # 检查行业集中度
        sector_allocation = current_state.get("sector_allocation", {})
        for sector, allocation in sector_allocation.items():
            allocation_pct = allocation / 100  # 转换为小数
            if allocation_pct > self.risk_thresholds["concentration"]["sector"]:
                alerts.append({
                    "sector": sector,
                    "current_allocation": allocation,
                    "threshold": self.risk_thresholds["concentration"]["sector"] * 100,
                    "risk": "单一行业过度集中"
                })
        
        # 检查现金比例
        cash_ratio = current_state.get("cash_ratio", 0) / 100
        if cash_ratio < self.risk_thresholds["concentration"]["cash_min"]:
            alerts.append({
                "type": "cash_concentration",
                "current_ratio": cash_ratio,
                "threshold": self.risk_thresholds["concentration"]["cash_min"],
                "risk": "现金储备不足"
            })
        
        if alerts:
            return {
                "type": "concentration_risk",
                "level": "warning" if len(alerts) <= 2 else "critical",
                "message": f"发现{len(alerts)}个集中度风险点",
                "alerts": alerts,
                "severity": 7 if len(alerts) <= 2 else 9,
                "recommended_actions": [
                    "调整高集中度持仓",
                    "增加行业分散",
                    "补充现金储备"
                ]
            }
        
        return None
    
    def _check_liquidity_risk(self, portfolio_analysis: Dict) -> Optional[Dict[str, Any]]:
        """检查流动性风险"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        
        # 识别潜在流动性问题股票
        illiquid_stocks = []
        
        for pos in positions:
            symbol = pos.get("symbol", "")
            current_price = pos.get("current_price", 0)
            current_value = pos.get("current_value", 0)
            
            # 简化流动性评估
            # 1. 股价低于10美元
            # 2. 市值较小（简化：股价<20且持仓价值<5000）
            # 3. 成交量小（需要实际数据，这里简化）
            
            if current_price < 10:
                illiquid_stocks.append({
                    "symbol": symbol,
                    "price": current_price,
                    "value": current_value,
                    "risk": "低价股，流动性可能受限"
                })
            elif current_price < 20 and current_value < 5000:
                illiquid_stocks.append({
                    "symbol": symbol,
                    "price": current_price,
                    "value": current_value,
                    "risk": "小市值股票，流动性一般"
                })
        
        if illiquid_stocks:
            total_value = sum(pos["value"] for pos in illiquid_stocks)
            portfolio_value = current_state.get("total_assets", 0)
            illiquid_ratio = total_value / portfolio_value if portfolio_value > 0 else 0
            
            return {
                "type": "liquidity_risk",
                "level": "warning" if illiquid_ratio < 0.1 else "critical",
                "message": f"发现{len(illiquid_stocks)}只潜在流动性受限股票",
                "illiquid_stocks": illiquid_stocks,
                "illiquid_ratio": round(illiquid_ratio * 100, 1),
                "severity": 6 if illiquid_ratio < 0.1 else 8,
                "recommended_actions": [
                    "考虑减少流动性受限股票的持仓",
                    "优先交易流动性好的大盘股",
                    "避免在流动性不足时大量买卖"
                ]
            }
        
        return None
    
    def _check_market_risk(self, market_data: Dict) -> Optional[Dict[str, Any]]:
        """检查市场风险"""
        if not market_data:
            return None
        
        alerts = []
        
        # 检查VIX水平
        vix_data = market_data.get("vix", {})
        vix_level = vix_data.get("c", 0)
        
        if vix_level >= 30:
            alerts.append({
                "type": "vix_risk",
                "level": "warning",
                "message": f"VIX恐慌指数偏高({vix_level:.1f})，显示市场情绪紧张",
                "details": f"当前VIX: {vix_level:.1f} | 警戒线: 30.0",
                "severity": 7,
                "action": "保持谨慎，控制仓位"
            })
        
        # 检查市场趋势
        sp500_data = market_data.get("sp500", {})
        sp500_change = sp500_data.get("dp", 0)  # 日涨跌幅
        
        if sp500_change < -3:
            alerts.append({
                "type": "market_trend_risk",
                "level": "warning",
                "message": f"市场大幅下跌({sp500_change:.1f}%)，需要关注系统性风险",
                "details": f"当日标普500跌幅: {sp500_change:.1f}%",
                "severity": 6,
                "action": "减少风险资产配置，增加现金"
            })
        
        if alerts:
            return {
                "type": "market_risk",
                "level": "warning",
                "message": f"发现{len(alerts)}个市场风险信号",
                "alerts": alerts,
                "overall_severity": max(alert.get("severity", 0) for alert in alerts),
                "recommended_actions": [
                    "监控市场新闻和事件",
                    "调整组合Beta暴露",
                    "准备应对市场波动"
                ]
            }
        
        return None
    
    def _check_correlation_risk(self, portfolio_analysis: Dict) -> Optional[Dict[str, Any]]:
        """检查相关性风险"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        
        if len(positions) < 3:
            return {
                "type": "correlation_risk",
                "level": "warning",
                "message": f"持仓数量过少({len(positions)}个)，无法有效分散风险",
                "details": f"当前持仓数: {len(positions)} | 建议最少: 8个",
                "severity": 7,
                "recommended_actions": [
                    "增加持仓数量",
                    "选择不同行业股票",
                    "考虑加入低相关性资产"
                ]
            }
        
        return None
    
    def _check_macro_risk(self, market_data: Dict) -> Optional[Dict[str, Any]]:
        """检查宏观风险"""
        # 在实际系统中，这里应该分析宏观经济指标
        # 现在使用简化版
        return None
    
    def _calculate_risk_metrics(self, portfolio_analysis: Dict, market_data: Dict) -> Dict[str, Any]:
        """计算风险指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "volatility_metrics": self._calculate_volatility_metrics(portfolio_analysis),
            "liquidity_metrics": self._calculate_liquidity_metrics(portfolio_analysis),
            "concentration_metrics": self._calculate_concentration_metrics(portfolio_analysis),
            "correlation_metrics": self._calculate_correlation_metrics(portfolio_analysis),
            "risk_adjusted_returns": self._calculate_risk_adjusted_returns(portfolio_analysis)
        }
        
        return metrics
    
    def _calculate_volatility_metrics(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """计算波动率指标"""
        risk_indicators = portfolio_analysis.get("risk_assessment", {}).get("indicators", {})
        volatility = risk_indicators.get("annualized_volatility", 0)
        
        return {
            "annualized_volatility": volatility,
            "daily_volatility": round(volatility / math.sqrt(252), 2),
            "volatility_percentile": self._estimate_volatility_percentile(volatility),
            "volatility_trend": "稳定"  # 在实际系统中应该分析趋势
        }
    
    def _calculate_liquidity_metrics(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """计算流动性指标"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        
        total_value = current_state.get("total_assets", 0)
        cash_value = current_state.get("cash", 0)
        
        # 识别流动性受限股票
        illiquid_value = 0
        for pos in positions:
            price = pos.get("current_price", 0)
            if price < 15:  # 简化：股价<15认为流动性可能受限
                illiquid_value += pos.get("current_value", 0)
        
        cash_ratio = (cash_value / total_value) * 100 if total_value > 0 else 0
        illiquid_ratio = (illiquid_value / total_value) * 100 if total_value > 0 else 0
        
        return {
            "cash_ratio": round(cash_ratio, 1),
            "illiquid_ratio": round(illiquid_ratio, 1),
            "liquidity_score": self._calculate_liquidity_score(cash_ratio, illiquid_ratio),
            "liquidity_risk": "低" if illiquid_ratio < 5 else "中" if illiquid_ratio < 15 else "高"
        }
    
    def _calculate_concentration_metrics(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """计算集中度指标"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        sector_allocation = current_state.get("sector_allocation", {})
        
        # 个股集中度
        if positions:
            max_position = max(positions, key=lambda x: x.get("position_ratio", 0))
            top3_ratio = sum(sorted([p.get("position_ratio", 0) for p in positions], reverse=True)[:3])
        else:
            max_position = {"symbol": "", "position_ratio": 0}
            top3_ratio = 0
        
        # 行业集中度
        if sector_allocation:
            max_sector = max(sector_allocation.items(), key=lambda x: x[1])
            top3_sectors_ratio = sum(sorted(sector_allocation.values(), reverse=True)[:3])
        else:
            max_sector = ("", 0)
            top3_sectors_ratio = 0
        
        return {
            "max_stock_concentration": round(max_position.get("position_ratio", 0) * 100, 1),
            "top3_stocks_ratio": round(top3_ratio * 100, 1),
            "max_sector_concentration": max_sector[1],
            "top3_sectors_ratio": top3_sectors_ratio,
            "concentration_score": self._calculate_concentration_score(
                max_position.get("position_ratio", 0), 
                max_sector[1] / 100 if max_sector[1] > 0 else 0
            )
        }
    
    def _calculate_correlation_metrics(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """计算相关性指标"""
        # 在实际系统中应该计算实际相关性
        # 现在使用简化估计
        return {
            "estimated_portfolio_correlation": 0.65,
            "diversification_score": 75,
            "sector_diversification": "中等",
            "recommended_improvements": [
                "增加非科技行业股票",
                "考虑加入固定收益或另类资产"
            ]
        }
    
    def _calculate_risk_adjusted_returns(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """计算风险调整后收益"""
        # 简化版
        return {
            "estimated_sharpe_ratio": 1.2,
            "estimated_sortino_ratio": 1.8,
            "risk_adjusted_return_score": 70,
            "improvement_suggestions": [
                "提高组合夏普比率至1.5以上",
                "优化风险调整后收益"
            ]
        }
    
    def _perform_stress_tests(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """执行压力测试"""
        tests = {
            "market_crash_scenario": self._test_market_crash_scenario(portfolio_analysis),
            "interest_rate_shock": self._test_interest_rate_shock(portfolio_analysis),
            "liquidity_crisis": self._test_liquidity_crisis(portfolio_analysis),
            "sector_specific_shock": self._test_sector_specific_shock(portfolio_analysis)
        }
        
        # 综合风险承受能力评估
        tests["overall_resilience"] = self._evaluate_overall_resilience(tests)
        
        return tests
    
    def _test_market_crash_scenario(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """测试市场崩盘情景"""
        current_state = portfolio_analysis.get("current_state", {})
        total_assets = current_state.get("total_assets", 0)
        
        # 假设市场下跌20%
        market_drop = 0.20
        
        # 假设组合Beta为1.1（科技股偏重）
        portfolio_beta = 1.1
        
        estimated_loss = total_assets * market_drop * portfolio_beta
        
        return {
            "scenario": "市场下跌20%",
            "estimated_loss": round(estimated_loss, 2),
            "loss_percentage": round((estimated_loss / total_assets) * 100, 1) if total_assets > 0 else 0,
            "severity": "高",
            "recovery_actions": [
                "立即增加现金比例",
                "减持高Beta股票",
                "考虑对冲策略"
            ]
        }
    
    def _test_interest_rate_shock(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """测试利率冲击情景"""
        current_state = portfolio_analysis.get("current_state", {})
        
        # 假设利率上升2%
        rate_increase = 0.02
        
        # 科技股对利率敏感，假设影响为-10%
        tech_impact = -0.10
        
        # 计算受影响价值（简化）
        positions = current_state.get("positions", [])
        tech_value = sum(pos.get("current_value", 0) for pos in positions)
        # 检查股票是否属于科技行业
        # 在实际系统中应该有行业分类数据
        return {
            "scenario": "利率上升2%",
            "impact": "科技股下跌约10%",
            "severity": "中",
            "suggested_actions": [
                "减少对利率敏感股票的配置",
                "增加防御性行业股票",
                "监控美联储政策变化"
            ]
        }
    
    def _test_liquidity_crisis(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """测试流动性危机情景"""
        current_state = portfolio_analysis.get("current_state", {})
        positions = current_state.get("positions", [])
        
        # 识别流动性受限股票
        illiquid_positions = []
        for pos in positions:
            price = pos.get("current_price", 0)
            if price < 15:
                illiquid_positions.append(pos)
        
        return {
            "scenario": "市场流动性下降",
            "affected_positions": len(illiquid_positions),
            "severity": "中低",
            "suggested_actions": [
                "优先减持小盘股",
                "增加大盘股配置",
                "保持充足现金应对"
            ]
        }
    
    def _test_sector_specific_shock(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """测试行业特定冲击情景"""
        current_state = portfolio_analysis.get("current_state", {})
        sector_allocation = current_state.get("sector_allocation", {})
        
        # 假设科技行业受冲击
        tech_allocation = sector_allocation.get("Technology", 0)
        
        return {
            "scenario": "科技行业下跌30%",
            "estimated_impact": round(tech_allocation * 0.30, 1),
            "severity": "高" if tech_allocation > 30 else "中",
            "suggested_actions": [
                "降低科技股仓位",
                "增加非科技行业分散",
                "考虑行业对冲策略"
            ]
        }
    
    def _evaluate_overall_resilience(self, stress_tests: Dict) -> Dict[str, Any]:
        """评估整体风险承受能力"""
        # 综合各情景风险
        resilience_score = 65  # 基准分
        
        # 在实际系统中应该更详细分析
        return {
            "score": resilience_score,
            "rating": "中等",
            "strengths": [
                "现金储备提供缓冲",
                "持仓质量总体良好"
            ],
            "weaknesses": [
                "科技行业集中度过高",
                "对利率变化敏感"
            ],
            "improvement_plan": [
                "将科技行业仓位降低至30%以下",
                "增加防御性行业配置",
                "提高现金比例至目标水平"
            ]
        }
    
    def _generate_risk_recommendations(self, portfolio_analysis: Dict) -> List[Dict[str, Any]]:
        """生成风险建议"""        
        recommendations = []
        
        # 基于风险分析生成建议        
        # 1. 波动率管理建议        
        volatility = portfolio_analysis.get("risk_assessment", {}).get("indicators", {}).get("annualized_volatility", 0)
        if volatility > 20:
            recommendations.append({
                "type": "volatility_management",
                "priority": "high",
                "title": "降低组合波动率",
                "details": f"当前组合年化波动率为{volatility:.1f}%，高于目标水平(18%)",
                "actions": [
                    "减持高Beta股票（如部分科技股）",
                    "增加低波动性股票（如消费品、公用事业）",
                    "考虑加入债券或黄金等低相关资产"
                ],
                "expected_benefit": "预计可将组合波动率降低至18%左右"
            })
        
        # 2. 集中度风险建议
        current_state = portfolio_analysis.get("current_state", {})
        max_position = max((p.get("position_ratio", 0) for p in current_state.get("positions", [])), default=0)
        if max_position > self.risk_thresholds["concentration"]["single_stock"]:
            recommendations.append({
                "type": "concentration_management",
                "priority": "high",
                "title": "降低单只股票集中度",
                "details": f"有股票持仓比例超过{self.risk_thresholds['concentration']['single_stock']*100:.0f}%限制",
                "actions": [
                    "识别并减持最高集中度的股票",
                    "将部分仓位分散到其他优质标的",
                    "设定个股仓位上限并严格执行"
                ],
                "expected_benefit": "降低单一股票风险暴露，提高组合稳定性"
            })
        
        # 3. 流动性风险建议
        liquidity_risk = self._check_liquidity_risk(portfolio_analysis)
        if liquidity_risk:
            recommendations.append({
                "type": "liquidity_management",
                "priority": "medium",
                "title": "改善组合流动性",
                "details": f"发现{liquidity_risk.get('illiquid_ratio', 0):.1f}%的资产可能存在流动性风险",
                "actions": [
                    "优先减持低价小盘股",
                    "增加流动性好的大盘股配置",
                    "保持一定比例高流动性资产（现金、货币基金）"
                ],
                "expected_benefit": "提高组合流动性，降低交易成本"
            })
        
        return recommendations
    
    def _create_risk_action_plan(self, portfolio_analysis: Dict, market_data: Dict) -> Dict[str, Any]:
        """创建风险应对计划"""
        alerts = self._check_risk_alerts(portfolio_analysis, market_data)
        critical_alerts = [alert for alert in alerts if alert.get("level") in ["critical", "emergency"]]
        
        if critical_alerts:
            # 有紧急风险，需要立即行动
            actions = [
                {
                    "action": "立即增加现金比例",
                    "priority": "urgent",
                    "target": f"现金比例达到{self.risk_thresholds['concentration']['cash_target']*100:.0f}%",
                    "timeline": "1-2个交易日内"
                },
                {
                    "action": "减持高波动性股票",
                    "priority": "urgent",
                    "target": "降低组合Beta至1.0以下",
                    "timeline": "本周内完成"
                },
                {
                    "action": "暂停新增风险投资",
                    "priority": "high",
                    "target": "避免新增风险敞口",
                    "timeline": "立即执行，持续至风险缓解"
                }
            ]
            response_level = "emergency"
        elif alerts:
            # 有警告性风险，需要关注
            actions = [
                {
                    "action": "调整高集中度持仓",
                    "priority": "high",
                    "target": "单只股票仓位不超过15%",
                    "timeline": "本月内完成调整"
                },
                {
                    "action": "增加防御性行业配置",
                    "priority": "medium",
                    "target": "将防御性行业（必需消费品、医疗）配置提高至20%",
                    "timeline": "季度内逐步实施"
                },
                {
                    "action": "设定风险监控阈值",
                    "priority": "medium",
                    "target": "设定波动率、回撤等风险指标的自动监控和预警",
                    "timeline": "本周内完成设置"
                }
            ]
            response_level = "warning"
        else:
            # 风险正常，建议维持并优化
            actions = [
                {
                    "action": "维持现有风险控制水平",
                    "priority": "low",
                    "target": "保持现有分散度和现金比例",
                    "timeline": "持续监控"
                },
                {
                    "action": "优化风险调整后收益",
                    "priority": "medium",
                    "target": "提高夏普比率至1.5以上",
                    "timeline": "季度内完成"
                },
                {
                    "action": "定期压力测试",
                    "priority": "low",
                    "target": "每季度执行一次全面压力测试",
                    "timeline": "按季度执行"
                }
            ]
            response_level = "normal"
        
        return {
            "response_level": response_level,
            "actions": actions,
            "monitoring_requirements": [
                "每日检查风险指标",
                "每周全面评估组合风险",
                "每月执行压力测试"
            ],
            "escalation_triggers": [
                "波动率超过25%",
                "最大回撤超过15%",
                "现金比例低于25%",
                "单只股票仓位超过18%"
            ],
            "review_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    
    def _log_risk_events(self, monitoring_results: Dict):
        """记录风险事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "alerts": monitoring_results.get("alerts", []),
            "risk_level": self._determine_overall_risk_level(monitoring_results),
            "action_plan": monitoring_results.get("action_plan", {})
        }
        
        self.event_log.append(event)
        
        # 在实际系统中应该写入数据库
        logger.info(f"风险监控事件记录: 警报数={len(event['alerts'])}")
    
    def _update_risk_history(self, monitoring_results: Dict):
        """更新风险历史"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        self.risk_history[date_str] = {
            "alerts_count": len(monitoring_results.get("alerts", [])),
            "risk_metrics": monitoring_results.get("risk_metrics", {}),
            "stress_test_results": monitoring_results.get("stress_tests", {})
        }
    
    def _determine_overall_risk_level(self, monitoring_results: Dict) -> str:
        """确定整体风险等级"""
        alerts = monitoring_results.get("alerts", [])
        
        if any(alert.get("level") == "critical" for alert in alerts):
            return "critical"
        elif any(alert.get("level") == "warning" for alert in alerts):
            return "warning"
        else:
            return "normal"
    
    def _estimate_volatility_percentile(self, volatility: float) -> str:
        """估计波动率百分位"""
        if volatility < 10:
            return "极低 (前10%)"
        elif volatility < 15:
            return "低 (前30%)"
        elif volatility < 20:
            return "中等 (50%)"
        elif volatility < 25:
            return "高 (前70%)"
        else:
            return "极高 (前90%)"
    
    def _calculate_liquidity_score(self, cash_ratio: float, illiquid_ratio: float) -> int:
        """计算流动性评分"""
        score = 50
        
        # 现金比例
        if cash_ratio > 35:
            score += 20
        elif cash_ratio > 25:
            score += 10
        
        # 非流动性资产比例
        if illiquid_ratio < 5:
            score += 25
        elif illiquid_ratio < 10:
            score += 15
        elif illiquid_ratio > 20:
            score -= 20
        
        return min(max(score, 0), 100)
    
    def _calculate_concentration_score(self, max_stock_ratio: float, max_sector_ratio: float) -> int:
        """计算集中度评分"""
        score = 50
        
        # 个股集中度
        if max_stock_ratio < 0.10:
            score += 25
        elif max_stock_ratio < 0.15:
            score += 10
        elif max_stock_ratio > 0.20:
            score -= 20
        
        # 行业集中度
        if max_sector_ratio < 0.25:
            score += 25
        elif max_sector_ratio < 0.35:
            score += 10
        elif max_sector_ratio > 0.45:
            score -= 20
        
        return min(max(score, 0), 100)

def create_risk_monitor():
    """创建风险监控器实例"""
    return RiskMonitor()