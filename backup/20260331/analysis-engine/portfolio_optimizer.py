"""
投资组合优化器 - 基于Z的持仓和保守偏好
提供个性化投资组合建议和风险管理
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """投资组合优化器"""
    
    def __init__(self):
        # Z的投资偏好和约束
        self.z_constraints = {
            "risk_tolerance": "low",          # 低风险容忍度
            "cash_reserve_target": 0.35,      # 现金储备目标比例
            "max_single_position": 0.15,      # 单一标的最高仓位
            "max_sector_exposure": 0.35,      # 单一行业最高暴露
            "portfolio_size_target": 8,       # 组合标的数量目标
            "rebalance_frequency": "quarterly", # 再平衡频率
            "preferred_sectors": ["Technology", "Communication Services", "Consumer Cyclical"]
        }
        
        # 风险管理参数
        self.risk_params = {
            "var_confidence": 0.95,           # VaR置信水平
            "max_drawdown_limit": 0.20,       # 最大回撤限制
            "volatility_target": 0.18,        # 目标年化波动率
            "sharpe_ratio_target": 1.5,       # 目标夏普比率
            "correlation_threshold": 0.7,     # 相关性阈值
        }
        
        # Z的模拟持仓（在实际系统中应该从数据库读取）
        self.sample_portfolio = {
            "cash": 100000,  # 现金（美元）
            "positions": [
                {"symbol": "NVDA", "shares": 50, "avg_cost": 150.00},
                {"symbol": "GOOGL", "shares": 100, "avg_cost": 280.00},
                {"symbol": "TSLA", "shares": 20, "avg_cost": 350.00},
                {"symbol": "AAPL", "shares": 50, "avg_cost": 220.00},
                {"symbol": "META", "shares": 30, "avg_cost": 550.00}
            ]
        }
    
    def analyze_portfolio(self, portfolio_data: Dict, stock_analyses: Dict) -> Dict[str, Any]:
        """分析投资组合"""
        if not portfolio_data:
            portfolio_data = self.sample_portfolio
        
        analysis = {
            "current_state": self._analyze_current_state(portfolio_data, stock_analyses),
            "health_assessment": self._assess_portfolio_health(portfolio_data, stock_analyses),
            "optimization_suggestions": self._generate_optimization_suggestions(portfolio_data, stock_analyses),
            "risk_assessment": self._assess_portfolio_risk(portfolio_data, stock_analyses),
            "rebalancing_plan": self._generate_rebalancing_plan(portfolio_data, stock_analyses),
            "timestamp": datetime.now().isoformat()
        }
        
        # 综合健康评分
        analysis["overall_score"] = self._calculate_overall_score(analysis)
        
        return analysis
    
    def _analyze_current_state(self, portfolio_data: Dict, stock_analyses: Dict) -> Dict[str, Any]:
        """分析当前投资组合状态"""
        cash = portfolio_data.get("cash", 0)
        positions = portfolio_data.get("positions", [])
        
        # 计算持仓价值
        position_values = []
        sector_exposure = {}
        position_details = []
        
        total_position_value = 0
        
        for pos in positions:
            symbol = pos.get("symbol", "")
            shares = pos.get("shares", 0)
            avg_cost = pos.get("avg_cost", 0)
            
            current_price = self._get_current_price(symbol, stock_analyses)
            current_value = shares * current_price
            
            total_position_value += current_value
            
            # 计算盈亏
            cost_basis = shares * avg_cost
            pnl = current_value - cost_basis
            pnl_percentage = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            # 行业分布
            sector = self._get_sector(symbol, stock_analyses)
            sector_exposure[sector] = sector_exposure.get(sector, 0) + current_value
            
            position_details.append({
                "symbol": symbol,
                "shares": shares,
                "avg_cost": round(avg_cost, 2),
                "current_price": round(current_price, 2),
                "current_value": round(current_value, 2),
                "pnl": round(pnl, 2),
                "pnl_percentage": round(pnl_percentage, 2),
                "sector": sector,
                "allocation": round((current_value / (total_position_value + cash)) * 100, 1)
            })
        
        # 总资产
        total_assets = cash + total_position_value
        
        # 现金比例
        cash_ratio = cash / total_assets if total_assets > 0 else 1.0
        
        # 个股仓位比例
        for detail in position_details:
            detail["position_ratio"] = detail["current_value"] / total_position_value if total_position_value > 0 else 0
        
        # 行业分布百分比
        sector_allocation = {}
        for sector, value in sector_exposure.items():
            sector_allocation[sector] = round((value / total_position_value) * 100, 1) if total_position_value > 0 else 0
        
        return {
            "total_assets": round(total_assets, 2),
            "cash": round(cash, 2),
            "cash_ratio": round(cash_ratio * 100, 1),
            "total_positions_value": round(total_position_value, 2),
            "positions": position_details,
            "sector_allocation": sector_allocation,
            "position_count": len(positions),
            "analysis_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _assess_portfolio_health(self, portfolio_data: Dict, stock_analyses: Dict) -> Dict[str, Any]:
        """评估投资组合健康度"""
        current_state = self._analyze_current_state(portfolio_data, stock_analyses)
        
        health_score = 100  # 初始满分
        
        # 1. 现金比例检查（权重30%）
        cash_ratio = current_state.get("cash_ratio", 0) / 100
        target_cash = self.z_constraints["cash_reserve_target"]
        cash_deviation = abs(cash_ratio - target_cash) / target_cash
        cash_health = 100 - (cash_deviation * 50)  # 偏差每10%扣5分
        
        # Z偏好保守，现金充足时加分
        if cash_ratio > target_cash:
            cash_health = min(cash_health + 10, 100)  # 现金充足，加10分
        
        health_score = (health_score * 0.7) + (cash_health * 0.3)
        
        # 2. 分散度检查（权重25%）
        position_count = current_state.get("position_count", 0)
        target_count = self.z_constraints["portfolio_size_target"]
        
        if position_count < target_count * 0.5:
            diversification_health = 60  # 过于集中
        elif position_count < target_count:
            diversification_health = 80  # 一般集中
        elif position_count == target_count:
            diversification_health = 90  # 良好
        else:
            diversification_health = 85  # 略多
        
        # 检查最大单一仓位
        positions = current_state.get("positions", [])
        max_position_ratio = 0
        for pos in positions:
            ratio = pos.get("position_ratio", 0)
            if ratio > max_position_ratio:
                max_position_ratio = ratio
        
        if max_position_ratio > self.z_constraints["max_single_position"]:
            diversification_health -= 20  # 单个仓位过大
        
        health_score = (health_score * 0.75) + (diversification_health * 0.25)
        
        # 3. 行业分布检查（权重20%）
        sector_allocation = current_state.get("sector_allocation", {})
        preferred_sectors = self.z_constraints["preferred_sectors"]
        
        # 检查是否过度集中于非偏好行业
        non_preferred_exposure = 0
        for sector, allocation in sector_allocation.items():
            if sector not in preferred_sectors:
                non_preferred_exposure += allocation
        
        if non_preferred_exposure > 40:  # 非偏好行业占比超过40%
            sector_health = 70
        elif non_preferred_exposure > 20:
            sector_health = 85
        else:
            sector_health = 95
        
        # 检查单一行业暴露
        max_sector_exposure = max(sector_allocation.values(), default=0)
        if max_sector_exposure > self.z_constraints["max_sector_exposure"] * 100:
            sector_health -= 15
        
        health_score = (health_score * 0.8) + (sector_health * 0.2)
        
        # 4. 风险指标检查（权重25%）
        risk_assessment = self._assess_portfolio_risk(portfolio_data, stock_analyses)
        risk_indicators = risk_assessment.get("indicators", {})
        
        # 波动率
        volatility = risk_indicators.get("annualized_volatility", 0)
        target_vol = self.risk_params["volatility_target"]
        
        if volatility > target_vol * 1.3:
            volatility_health = 60
        elif volatility > target_vol:
            volatility_health = 75
        elif volatility > target_vol * 0.7:
            volatility_health = 90
        else:
            volatility_health = 85  # 波动率过低可能收益也低
        
        # 最大回撤
        max_drawdown = risk_indicators.get("max_drawdown", 0)
        drawdown_limit = self.risk_params["max_drawdown_limit"]
        
        if max_drawdown > drawdown_limit:
            drawdown_health = 60
        elif max_drawdown > drawdown_limit * 0.7:
            drawdown_health = 80
        else:
            drawdown_health = 95
        
        risk_health = (volatility_health + drawdown_health) / 2
        health_score = (health_score * 0.75) + (risk_health * 0.25)
        
        # 健康评级
        if health_score >= 90:
            health_rating = "⭐️⭐️⭐️⭐️⭐️ 非常健康"
        elif health_score >= 80:
            health_rating = "⭐️⭐️⭐️⭐️ 健康"
        elif health_score >= 70:
            health_rating = "⭐️⭐️⭐️ 一般"
        elif health_score >= 60:
            health_rating = "⭐️⭐️ 需要关注"
        else:
            health_rating = "⚠️ 需要调整"
        
        return {
            "overall_score": round(health_score, 1),
            "rating": health_rating,
            "components": {
                "cash_health": round(cash_health, 1),
                "diversification_health": round(diversification_health, 1),
                "sector_health": round(sector_health, 1),
                "risk_health": round(risk_health, 1)
            },
            "key_concerns": self._identify_health_concerns(current_state, risk_assessment),
            "strengths": self._identify_health_strengths(current_state, risk_assessment)
        }
    
    def _generate_optimization_suggestions(self, portfolio_data: Dict, stock_analyses: Dict) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = []
        
        current_state = self._analyze_current_state(portfolio_data, stock_analyses)
        health_assessment = self._assess_portfolio_health(portfolio_data, stock_analyses)
        
        # 1. 现金调整建议
        cash_ratio = current_state.get("cash_ratio", 0) / 100
        target_cash = self.z_constraints["cash_reserve_target"]
        
        if cash_ratio < target_cash * 0.8:
            suggestions.append({
                "type": "cash_adjustment",
                "priority": "high",
                "action": "增加现金储备",
                "reason": f"现金比例偏低({cash_ratio*100:.1f}% < 目标{target_cash*100:.0f}%)",
                "details": f"建议卖出部分持仓，使现金比例达到{target_cash*100:.0f}%",
                "implementation": "优先考虑减持涨幅较大或基本面转弱的股票"
            })
        elif cash_ratio > target_cash * 1.3:
            suggestions.append({
                "type": "cash_adjustment",
                "priority": "medium",
                "action": "减少现金储备",
                "reason": f"现金比例偏高({cash_ratio*100:.1f}% > 目标{target_cash*100:.0f}%)",
                "details": f"建议将部分现金投入优质标的，使现金比例达到{target_cash*100:.0f}%",
                "implementation": "考虑买入近期推荐的高分股票或增加现有优质持仓"
            })
        
        # 2. 分散度建议
        position_count = current_state.get("position_count", 0)
        target_count = self.z_constraints["portfolio_size_target"]
        
        if position_count < target_count * 0.6:
            suggestions.append({
                "type": "diversification",
                "priority": "high",
                "action": "增加持仓数量",
                "reason": f"持仓数量偏少({position_count}个 < 目标{target_count}个)",
                "details": f"建议增加{target_count - position_count}个优质标的",
                "implementation": "参考今日最佳操作推荐，选择不同行业的优质股票"
            })
        elif position_count > target_count * 1.5:
            suggestions.append({
                "type": "diversification",
                "priority": "low",
                "action": "减少持仓数量",
                "reason": f"持仓数量偏多({position_count}个 > 目标{target_count}个)",
                "details": "持仓过多可能导致管理困难",
                "implementation": "考虑合并相似持仓或削减边缘持仓"
            })
        
        # 3. 个股仓位调整
        positions = current_state.get("positions", [])
        for pos in positions:
            symbol = pos.get("symbol", "")
            position_ratio = pos.get("position_ratio", 0)
            allocation = pos.get("allocation", 0)
            
            # 检查是否超过单只股票限制
            if position_ratio > self.z_constraints["max_single_position"]:
                suggestions.append({
                    "type": "position_adjustment",
                    "priority": "high",
                    "symbol": symbol,
                    "action": "减持",
                    "reason": f"单个仓位过大({position_ratio*100:.1f}% > 限制{self.z_constraints['max_single_position']*100:.0f}%)",
                    "details": f"建议减持{position_ratio*100 - self.z_constraints['max_single_position']*100:.1f}%的仓位",
                    "implementation": "分批卖出，避免冲击成本"
                })
            
            # 检查是否有股票占比过大
            if allocation > 20:  # 单只股票占总资产超过20%
                suggestions.append({
                    "type": "position_adjustment",
                    "priority": "high",
                    "symbol": symbol,
                    "action": "减持",
                    "reason": f"单个标的占总资产比例过高({allocation:.1f}%)",
                    "details": "过度集中可能带来过高风险",
                    "implementation": "分批减持至15%以下"
                })
        
        # 4. 行业分布调整
        sector_allocation = current_state.get("sector_allocation", {})
        preferred_sectors = self.z_constraints["preferred_sectors"]
        max_sector_exposure = self.z_constraints["max_sector_exposure"] * 100
        
        for sector, allocation in sector_allocation.items():
            # 检查单一行业暴露
            if allocation > max_sector_exposure:
                suggestions.append({
                    "type": "sector_adjustment",
                    "priority": "high",
                    "sector": sector,
                    "action": "减少行业暴露",
                    "reason": f"单一行业占比过大({allocation:.1f}% > 限制{max_sector_exposure:.0f}%)",
                    "details": f"建议减持{sector}行业的持仓",
                    "implementation": "选择该行业内持仓进行调整"
                })
            
            # 鼓励增加偏好行业的配置
            if sector in preferred_sectors and allocation < 15:
                suggestions.append({
                    "type": "sector_adjustment",
                    "priority": "low",
                    "sector": sector,
                    "action": "适度增加",
                    "reason": f"偏好行业但配置不足({allocation:.1f}% < 建议15%)",
                    "details": f"可考虑增加{sector}行业优质标的",
                    "implementation": "参考近期高分推荐"
                })
        
        return suggestions
    
    def _assess_portfolio_risk(self, portfolio_data: Dict, stock_analyses: Dict) -> Dict[str, Any]:
        """评估投资组合风险"""
        # 简化版风险评估
        current_state = self._analyze_current_state(portfolio_data, stock_analyses)
        
        # 计算波动率（简化）
        volatility = self._estimate_portfolio_volatility(current_state, stock_analyses)
        
        # 计算VaR（简化）
        var_95 = current_state.get("total_assets", 0) * volatility * 1.65 / math.sqrt(252)
        
        # 相关性分析（简化）
        correlation_risk = self._assess_correlation_risk(current_state, stock_analyses)
        
        # 流动性风险（简化）
        liquidity_risk = self._assess_liquidity_risk(current_state)
        
        return {
            "indicators": {
                "annualized_volatility": round(volatility * 100, 1),
                "var_95_daily": round(var_95, 2),
                "max_drawdown": self._estimate_max_drawdown(current_state, stock_analyses),
                "beta_to_market": self._estimate_portfolio_beta(current_state, stock_analyses),
                "correlation_risk": correlation_risk,
                "liquidity_risk": liquidity_risk
            },
            "risk_profile": self._determine_risk_profile(volatility, correlation_risk),
            "risk_limits_check": self._check_risk_limits(volatility, correlation_risk),
            "mitigation_suggestions": self._generate_risk_mitigation_suggestions(volatility, correlation_risk)
        }
    
    def _generate_rebalancing_plan(self, portfolio_data: Dict, stock_analyses: Dict) -> Dict[str, Any]:
        """生成再平衡计划"""
        current_state = self._analyze_current_state(portfolio_data, stock_analyses)
        total_assets = current_state.get("total_assets", 0)
        
        # 计算目标仓位
        target_cash = total_assets * self.z_constraints["cash_reserve_target"]
        current_cash = current_state.get("cash", 0)
        
        cash_adjustment = target_cash - current_cash
        
        # 计算现有持仓的目标价值
        target_position_value = total_assets - target_cash
        
        # 根据个股评分分配目标仓位
        positions = current_state.get("positions", [])
        position_actions = []
        
        for pos in positions:
            symbol = pos.get("symbol", "")
            current_value = pos.get("current_value", 0)
            current_allocation = pos.get("allocation", 0)
            
            # 基于个股评分确定目标仓位（简化）
            stock_score = self._get_stock_score(symbol, stock_analyses)
            
            # 目标仓位 = 总持仓价值 * (个股评分 / 总评分)
            # 这里简化处理
            if stock_score >= 80:
                target_ratio = 0.20  # 高分股票占20%持仓
            elif stock_score >= 65:
                target_ratio = 0.15
            elif stock_score >= 50:
                target_ratio = 0.10
            else:
                target_ratio = 0.05
            
            target_value = target_position_value * target_ratio
            adjustment = target_value - current_value
            
            # 确定操作类型
            if abs(adjustment) < total_assets * 0.01:  # 小于总资产的1%，不需要调整
                action_type = "hold"
                action_desc = "保持现有仓位"
            elif adjustment > 0:
                action_type = "buy"
                action_desc = f"增加${abs(adjustment):.0f}仓位"
            else:
                action_type = "sell"
                action_desc = f"减持${abs(adjustment):.0f}仓位"
            
            position_actions.append({
                "symbol": symbol,
                "current_value": round(current_value, 2),
                "target_value": round(target_value, 2),
                "adjustment": round(adjustment, 2),
                "action": action_type,
                "description": action_desc,
                "reason": f"基于评分{stock_score:.1f}确定目标仓位"
            })
        
        return {
            "rebalancing_date": datetime.now().strftime("%Y-%m-%d"),
            "total_assets": round(total_assets, 2),
            "cash_adjustment": round(cash_adjustment, 2),
            "target_cash": round(target_cash, 2),
            "target_position_value": round(target_position_value, 2),
            "position_actions": position_actions,
            "implementation_guidelines": [
                "优先调整现金比例至目标水平",
                "分批执行，避免冲击成本",
                "关注税务影响（如在美国需考虑资本利得税）",
                "再平衡后等待至少一个季度再进行下一次调整"
            ],
            "next_rebalancing_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        }
    
    def _calculate_overall_score(self, analysis: Dict) -> float:
        """计算综合评分"""
        health_score = analysis.get("health_assessment", {}).get("overall_score", 50)
        risk_score = 100 - analysis.get("risk_assessment", {}).get("indicators", {}).get("annualized_volatility", 20)
        
        # 综合评分 = 健康度×60% + 风险控制×40%
        overall_score = health_score * 0.6 + risk_score * 0.4
        
        return round(overall_score, 1)
    
    # 以下是一些辅助方法（在实际系统中应该完整实现）
    def _get_current_price(self, symbol: str, stock_analyses: Dict) -> float:
        """获取当前价格"""
        if symbol in stock_analyses:
            return stock_analyses[symbol].get("quote", {}).get("c", 0)
        return 0
    
    def _get_sector(self, symbol: str, stock_analyses: Dict) -> str:
        """获取行业分类"""
        if symbol in stock_analyses:
            return stock_analyses[symbol].get("profile", {}).get("finnhubIndustry", "Unknown")
        return "Unknown"
    
    def _get_stock_score(self, symbol: str, stock_analyses: Dict) -> float:
        """获取股票评分"""
        if symbol in stock_analyses and "score" in stock_analyses[symbol]:
            return stock_analyses[symbol]["score"].get("total", 50)
        return 50
    
    def _estimate_portfolio_volatility(self, current_state: Dict, stock_analyses: Dict) -> float:
        """估算投资组合波动率"""
        # 简化：假设组合波动率为个股波动率的加权平均
        positions = current_state.get("positions", [])
        
        if not positions:
            return 0.2  # 默认20%波动率
        
        total_vol = 0
        total_weight = 0
        
        for pos in positions:
            symbol = pos.get("symbol", "")
            weight = pos.get("position_ratio", 0)
            
            # 获取个股波动率估计
            stock_vol = stock_analyses.get(symbol, {}).get("metrics", {}).get("beta", 1.0) * 0.2
            
            total_vol += stock_vol * weight
            total_weight += weight
        
        return total_vol / total_weight if total_weight > 0 else 0.2
    
    def _estimate_max_drawdown(self, current_state: Dict, stock_analyses: Dict) -> float:
        """估算最大回撤"""
        # 简化估计
        positions = current_state.get("positions", [])
        
        if not positions:
            return 0.15  # 默认15%回撤
        
        # 假设高风险股票可能带来较大回撤
        high_risk_count = 0
        for pos in positions:
            symbol = pos.get("symbol", "")
            stock_score = self._get_stock_score(symbol, stock_analyses)
            if stock_score < 50:
                high_risk_count += 1
        
        if high_risk_count > 1:
            return 0.25
        elif high_risk_count == 1:
            return 0.20
        else:
            return 0.15
    
    def _assess_correlation_risk(self, current_state: Dict, stock_analyses: Dict) -> str:
        """评估相关性风险"""
        positions = current_state.get("positions", [])
        
        if len(positions) <= 2:
            return "高 - 持仓过少，无法有效分散"
        
        # 检查行业集中度
        sector_allocation = current_state.get("sector_allocation", {})
        if len(sector_allocation) <= 2:
            return "中高 - 行业过于集中"
        
        # 检查是否有高度相关股票
        tech_stocks = [p for p in positions if self._get_sector(p["symbol"], stock_analyses) == "Technology"]
        if len(tech_stocks) > 2:
            return "中 - 科技股可能高度相关"
        
        return "低 - 分散度良好"
    
    def _assess_liquidity_risk(self, current_state: Dict) -> str:
        """评估流动性风险"""
        positions = current_state.get("positions", [])
        
        # 检查是否有小盘股
        small_cap_count = 0
        for pos in positions:
            symbol = pos.get("symbol", "")
            price = pos.get("current_price", 0)
            
            # 简化：股价低于10美元或成交额小的股票可能流动性较差
            if price < 10:
                small_cap_count += 1
        
        if small_cap_count > 1:
            return "中 - 包含小盘股，流动性可能受限"
        
        return "低 - 主要为大盘股，流动性好"
    
    def _determine_risk_profile(self, volatility: float, correlation_risk: str) -> str:
        """确定风险特征"""
        if volatility > 0.25 or correlation_risk.startswith("高"):
            return "高风险组合"
        elif volatility > 0.18 or correlation_risk.startswith("中"):
            return "中等风险组合"
        else:
            return "低风险组合"
    
    def _check_risk_limits(self, volatility: float, correlation_risk: str) -> Dict[str, bool]:
        """检查风险限制"""
        volatility_limit = volatility <= self.risk_params["volatility_target"]
        correlation_limit = not correlation_risk.startswith("高")
        
        return {
            "volatility_limit_ok": volatility_limit,
            "correlation_limit_ok": correlation_limit,
            "all_limits_ok": volatility_limit and correlation_limit
        }
    
    def _generate_risk_mitigation_suggestions(self, volatility: float, correlation_risk: str) -> List[str]:
        """生成风险缓释建议"""
        suggestions = []
        
        if volatility > self.risk_params["volatility_target"]:
            suggestions.append(f"波动率偏高({volatility*100:.1f}%)，建议增加防御性股票或债券配置")
        
        if correlation_risk.startswith("高"):
            suggestions.append("相关性风险高，建议增加不同行业的股票以分散风险")
        
        return suggestions
    
    def _identify_health_concerns(self, current_state: Dict, risk_assessment: Dict) -> List[str]:
        """识别健康度关注点"""
        concerns = []
        
        cash_ratio = current_state.get("cash_ratio", 0) / 100
        target_cash = self.z_constraints["cash_reserve_target"]
        
        if cash_ratio < target_cash * 0.8:
            concerns.append(f"现金比例偏低({cash_ratio*100:.1f}%)，建议增加现金储备")
        
        if len(current_state.get("positions", [])) < 5:
            concerns.append("持仓数量不足，分散度不够")
        
        risk_indicators = risk_assessment.get("indicators", {})
        if risk_indicators.get("annualized_volatility", 0) > 20:
            concerns.append("组合波动率偏高，需关注风险控制")
        
        return concerns
    
    def _estimate_portfolio_beta(self, current_state: Dict, stock_analyses: Dict) -> float:
        """估算投资组合的Beta值"""
        positions = current_state.get("positions", [])
        if not positions:
            return 1.0  # 默认市场Beta
        
        total_value = sum(pos.get("current_value", 0) for pos in positions)
        if total_value <= 0:
            return 1.0
        
        weighted_beta_sum = 0
        for pos in positions:
            symbol = pos.get("symbol", "")
            position_value = pos.get("current_value", 0)
            
            # 获取股票的Beta值
            stock_beta = 1.0  # 默认值
            if symbol in stock_analyses:
                stock_data = stock_analyses[symbol].get("raw_data", {})
                stock_beta = stock_data.get("metrics", {}).get("beta", 1.0)
            
            # 计算权重
            weight = position_value / total_value
            weighted_beta_sum += weight * stock_beta
        
        return round(weighted_beta_sum, 2)

    def _identify_health_strengths(self, current_state: Dict, risk_assessment: Dict) -> List[str]:
        """识别健康度优势"""
        strengths = []

        cash_ratio = current_state.get("cash_ratio", 0) / 100
        if cash_ratio > 0.3:
            strengths.append("现金充足，应对市场波动能力强")

        if len(current_state.get("positions", [])) >= 8:
            strengths.append("持仓数量充足，分散度良好")

        risk_indicators = risk_assessment.get("indicators", {})
        if risk_indicators.get("annualized_volatility", 0) < 15:
            strengths.append("组合波动率低，风险控制良好")

        return strengths

def create_portfolio_optimizer():
    """创建投资组合优化器实例"""
    return PortfolioOptimizer()