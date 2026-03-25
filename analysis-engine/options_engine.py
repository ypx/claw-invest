"""
期权策略引擎 - 多种期权策略分析和推荐
特别针对Z的sell put偏好优化
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class OptionsEngine:
    """期权策略引擎"""
    
    def __init__(self):
        # 期权策略库
        self.strategies = {
            "sell_put": {
                "name": "卖出看跌期权",
                "risk_level": "中等",
                "capital_required": "高",
                "time_decay": "有利",
                "volatility_impact": "有利",
                "description": "适合看好股票但想以更低价格买入的投资者"
            },
            "covered_call": {
                "name": "备兑看涨期权",
                "risk_level": "低",
                "capital_required": "高",
                "time_decay": "有利",
                "volatility_impact": "有利",
                "description": "适合持有股票并想增加收益的投资者"
            },
            "cash_secured_put": {
                "name": "现金担保看跌期权",
                "risk_level": "中等",
                "capital_required": "高",
                "time_decay": "有利",
                "volatility_impact": "有利",
                "description": "Z最常用的策略，用现金担保卖出看跌期权"
            },
            "protective_put": {
                "name": "保护性看跌期权",
                "risk_level": "低",
                "capital_required": "低",
                "time_decay": "不利",
                "volatility_impact": "有利",
                "description": "为现有持仓提供下跌保护"
            },
            "bull_call_spread": {
                "name": "牛市看涨价差",
                "risk_level": "中等",
                "capital_required": "低",
                "time_decay": "有利",
                "volatility_impact": "不利",
                "description": "看涨但想降低成本的策略"
            },
            "iron_condor": {
                "name": "铁鹰策略",
                "risk_level": "中等",
                "capital_required": "低",
                "time_decay": "有利",
                "volatility_impact": "不利",
                "description": "预期股票在特定区间波动的策略"
            }
        }
        
        # Z的特殊偏好
        self.z_preferences = {
            "preferred_strategy": "cash_secured_put",
            "favorite_stock": "TSLA",
            "risk_tolerance": "low",
            "typical_dte": 30,  # 典型到期天数
            "typical_delta": 0.3,  # 典型Delta值
            "cash_reserve_ratio": 0.35
        }
        
        # 希腊字母计算参数
        self.greek_params = {
            "risk_free_rate": 0.04,
            "dividend_yield": 0.02,
            "days_per_year": 252
        }
    
    def analyze_options_opportunities(self, stock_data: Dict, market_data: Dict = None) -> Dict[str, Any]:
        """分析期权机会"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        volatility = stock_data.get("metrics", {}).get("beta", 1.5) * 0.3  # 简化波动率估计
        
        if current_price <= 0:
            return {"symbol": symbol, "error": "无效的股票价格"}
        
        opportunities = {
            "symbol": symbol,
            "current_price": current_price,
            "implied_volatility": volatility,
            "strategies": {},
            "best_strategy": None,
            "z_special_recommendation": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # 分析各种策略
        for strategy_id, strategy_info in self.strategies.items():
            strategy_analysis = self._analyze_strategy(
                strategy_id, stock_data, market_data
            )
            opportunities["strategies"][strategy_id] = strategy_analysis
        
        # 找出最佳策略
        opportunities["best_strategy"] = self._select_best_strategy(opportunities["strategies"])
        
        # Z的特殊推荐（针对他偏好的策略）
        opportunities["z_special_recommendation"] = self._generate_z_recommendation(
            stock_data, opportunities["strategies"]
        )
        
        return opportunities
    
    def _analyze_strategy(self, strategy_id: str, stock_data: Dict, market_data: Dict) -> Dict[str, Any]:
        """分析特定策略"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        volatility = stock_data.get("metrics", {}).get("beta", 1.5) * 0.3
        
        strategy_info = self.strategies.get(strategy_id, {})
        
        if strategy_id == "cash_secured_put":
            return self._analyze_cash_secured_put(stock_data, volatility)
        elif strategy_id == "covered_call":
            return self._analyze_covered_call(stock_data, volatility)
        elif strategy_id == "protective_put":
            return self._analyze_protective_put(stock_data, volatility)
        elif strategy_id == "bull_call_spread":
            return self._analyze_bull_call_spread(stock_data, volatility)
        elif strategy_id == "iron_condor":
            return self._analyze_iron_condor(stock_data, volatility)
        else:
            return {
                "name": strategy_info.get("name", ""),
                "applicable": False,
                "reason": "策略分析未实现",
                "risk_level": strategy_info.get("risk_level", ""),
                "description": strategy_info.get("description", "")
            }
    
    def _analyze_cash_secured_put(self, stock_data: Dict, volatility: float) -> Dict[str, Any]:
        """分析现金担保看跌期权（Z最爱的策略）"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if current_price <= 0:
            return {
                "name": "现金担保看跌期权",
                "applicable": False,
                "reason": "无效的股票价格",
                "risk_level": "中等"
            }
        
        # 计算建议的行权价（当前价的85%）
        strike_price = round(current_price * 0.85, 2)
        
        # 计算预期权利金（简化：基于波动率和时间）
        days_to_expiry = self.z_preferences["typical_dte"]
        premium_estimate = self._calculate_put_premium(
            current_price, strike_price, volatility, days_to_expiry
        )
        
        # 计算年化收益
        collateral = strike_price * 100  # 每手需要的现金担保
        premium_per_contract = premium_estimate * 100
        annualized_return = (premium_per_contract / collateral) * (365 / days_to_expiry) * 100
        
        # 风险评估
        probability_of_assignment = self._calculate_assignment_probability(
            current_price, strike_price, volatility, days_to_expiry
        )
        
        # 最大风险（如果被行权）
        max_risk = (strike_price - 0) * 100  # 理论上最大损失是行权价
        max_risk_percentage = (strike_price - current_price) / current_price * 100 if current_price > 0 else 0
        
        return {
            "name": "现金担保看跌期权",
            "applicable": True,
            "recommended": symbol == self.z_preferences["favorite_stock"],
            "parameters": {
                "strike_price": strike_price,
                "days_to_expiry": days_to_expiry,
                "premium_estimate": round(premium_estimate, 2),
                "premium_per_contract": round(premium_per_contract, 2),
                "collateral_per_contract": round(collateral, 2),
                "delta": 0.3,  # 目标Delta值
                "probability_otm": round((1 - probability_of_assignment) * 100, 1)
            },
            "returns": {
                "premium_yield": round((premium_estimate / strike_price) * 100, 2),
                "annualized_return": round(annualized_return, 2),
                "breakeven_price": round(strike_price - premium_estimate, 2)
            },
            "risk": {
                "probability_of_assignment": round(probability_of_assignment * 100, 1),
                "max_risk_per_contract": round(max_risk, 2),
                "max_risk_percentage": round(max_risk_percentage, 2),
                "risk_reward_ratio": round(premium_estimate / (strike_price - current_price + premium_estimate), 2) if strike_price > current_price else 0
            },
            "suitability": self._assess_strategy_suitability("cash_secured_put", stock_data),
            "z_notes": self._generate_z_notes("cash_secured_put", stock_data, strike_price, premium_estimate),
            "execution_plan": self._generate_execution_plan("cash_secured_put", strike_price, days_to_expiry)
        }
    
    def _analyze_covered_call(self, stock_data: Dict, volatility: float) -> Dict[str, Any]:
        """分析备兑看涨期权"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if current_price <= 0:
            return {
                "name": "备兑看涨期权",
                "applicable": False,
                "reason": "无效的股票价格"
            }
        
        # 计算建议的行权价（当前价的110%）
        strike_price = round(current_price * 1.10, 2)
        days_to_expiry = 45  # 45天到期
        
        # 计算预期权利金
        premium_estimate = self._calculate_call_premium(
            current_price, strike_price, volatility, days_to_expiry
        )
        
        # 计算收益
        premium_yield = (premium_estimate / current_price) * 100
        upside_capture = ((strike_price - current_price) / current_price) * 100
        total_return_if_assigned = premium_yield + upside_capture
        
        return {
            "name": "备兑看涨期权",
            "applicable": True,
            "recommended": current_price > 50,  # 股价较高时更适合
            "parameters": {
                "strike_price": strike_price,
                "days_to_expiry": days_to_expiry,
                "premium_estimate": round(premium_estimate, 2),
                "delta": 0.3
            },
            "returns": {
                "premium_yield": round(premium_yield, 2),
                "upside_capture": round(upside_capture, 2),
                "total_return_if_assigned": round(total_return_if_assigned, 2),
                "annualized_return": round(premium_yield * (365 / days_to_expiry), 2)
            },
            "risk": {
                "opportunity_cost": "可能错失大涨机会",
                "downside_risk": "股票下跌风险依然存在",
                "assignment_risk": "中等"
            },
            "suitability": self._assess_strategy_suitability("covered_call", stock_data),
            "execution_plan": "持有100股正股，同时卖出1张看涨期权"
        }
    
    def _analyze_protective_put(self, stock_data: Dict, volatility: float) -> Dict[str, Any]:
        """分析保护性看跌期权"""
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if current_price <= 0:
            return {
                "name": "保护性看跌期权",
                "applicable": False,
                "reason": "无效的股票价格"
            }
        
        # 计算保护性看跌期权的行权价（当前价的90%）
        strike_price = round(current_price * 0.90, 2)
        days_to_expiry = 60  # 60天到期
        
        # 计算权利金成本
        premium_cost = self._calculate_put_premium(
            current_price, strike_price, volatility, days_to_expiry
        )
        
        # 保护效果分析
        protection_cost_percentage = (premium_cost / current_price) * 100
        protected_downside = current_price - strike_price
        
        return {
            "name": "保护性看跌期权",
            "applicable": True,
            "recommended": volatility > 0.4,  # 高波动时更适合
            "parameters": {
                "strike_price": strike_price,
                "days_to_expiry": days_to_expiry,
                "premium_cost": round(premium_cost, 2),
                "protection_level": "90% of current price"
            },
            "protection": {
                "max_loss": round(protected_downside + premium_cost, 2),
                "protection_cost_percentage": round(protection_cost_percentage, 2),
                "effective_protection_price": round(strike_price - premium_cost, 2)
            },
            "suitability": self._assess_strategy_suitability("protective_put", stock_data),
            "best_for": "已持有股票，担心短期下跌，想保护利润"
        }
    
    def _analyze_bull_call_spread(self, stock_data: Dict, volatility: float) -> Dict[str, Any]:
        """分析牛市看涨价差"""
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if current_price <= 0:
            return {
                "name": "牛市看涨价差",
                "applicable": False,
                "reason": "无效的股票价格"
            }
        
        # 牛市价差：买入较低行权价看涨，卖出较高行权价看涨
        buy_strike = round(current_price * 1.05, 2)
        sell_strike = round(current_price * 1.15, 2)
        days_to_expiry = 60
        
        # 计算净成本
        buy_premium = self._calculate_call_premium(current_price, buy_strike, volatility, days_to_expiry)
        sell_premium = self._calculate_call_premium(current_price, sell_strike, volatility, days_to_expiry)
        net_cost = buy_premium - sell_premium
        
        # 最大收益和风险
        max_profit = (sell_strike - buy_strike) - net_cost
        max_loss = net_cost
        breakeven_price = buy_strike + net_cost
        
        return {
            "name": "牛市看涨价差",
            "applicable": True,
            "recommended": current_price < 200,  # 适合中等价位股票
            "parameters": {
                "buy_strike": buy_strike,
                "sell_strike": sell_strike,
                "days_to_expiry": days_to_expiry,
                "net_cost": round(net_cost, 2)
            },
            "returns": {
                "max_profit": round(max_profit, 2),
                "max_loss": round(max_loss, 2),
                "breakeven_price": round(breakeven_price, 2),
                "profit_potential": round((max_profit / net_cost) * 100, 1) if net_cost > 0 else 0
            },
            "risk": {
                "risk_reward_ratio": round(max_profit / max_loss, 2) if max_loss > 0 else 0,
                "capital_at_risk": round(max_loss * 100, 2)
            },
            "suitability": self._assess_strategy_suitability("bull_call_spread", stock_data),
            "best_for": "温和看涨，想降低成本，限制风险"
        }
    
    def _analyze_iron_condor(self, stock_data: Dict, volatility: float) -> Dict[str, Any]:
        """分析铁鹰策略"""
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if current_price <= 0:
            return {
                "name": "铁鹰策略",
                "applicable": False,
                "reason": "无效的股票价格"
            }
        
        # 铁鹰：卖出价外看涨+看跌，买入更价外看涨+看跌
        put_sell_strike = round(current_price * 0.90, 2)
        put_buy_strike = round(current_price * 0.85, 2)
        call_sell_strike = round(current_price * 1.10, 2)
        call_buy_strike = round(current_price * 1.15, 2)
        days_to_expiry = 45
        
        # 计算净权利金收入
        put_sell_premium = self._calculate_put_premium(current_price, put_sell_strike, volatility, days_to_expiry)
        put_buy_premium = self._calculate_put_premium(current_price, put_buy_strike, volatility, days_to_expiry)
        call_sell_premium = self._calculate_call_premium(current_price, call_sell_strike, volatility, days_to_expiry)
        call_buy_premium = self._calculate_call_premium(current_price, call_buy_strike, volatility, days_to_expiry)
        
        net_credit = (put_sell_premium + call_sell_premium) - (put_buy_premium + call_buy_premium)
        
        # 最大收益和风险
        max_profit = net_credit
        max_loss = (call_buy_strike - call_sell_strike) - net_credit  # 两边宽度相同
        profit_range = (put_sell_strike, call_sell_strike)
        
        return {
            "name": "铁鹰策略",
            "applicable": True,
            "recommended": volatility > 0.25,  # 有一定波动性时更适合
            "parameters": {
                "put_sell_strike": put_sell_strike,
                "put_buy_strike": put_buy_strike,
                "call_sell_strike": call_sell_strike,
                "call_buy_strike": call_buy_strike,
                "days_to_expiry": days_to_expiry,
                "net_credit": round(net_credit, 2)
            },
            "returns": {
                "max_profit": round(max_profit, 2),
                "max_loss": round(max_loss, 2),
                "profit_range": profit_range,
                "probability_of_profit": round(self._calculate_condor_probability(current_price, profit_range, volatility, days_to_expiry) * 100, 1)
            },
            "risk": {
                "risk_reward_ratio": round(max_profit / max_loss, 2) if max_loss > 0 else 0,
                "margin_required": round(max_loss * 100, 2)
            },
            "suitability": self._assess_strategy_suitability("iron_condor", stock_data),
            "best_for": "预期股票在区间内波动，想赚取时间价值"
        }
    
    def _calculate_put_premium(self, spot: float, strike: float, volatility: float, days: int) -> float:
        """计算看跌期权权利金（简化Black-Scholes）"""
        if spot <= 0 or strike <= 0 or days <= 0:
            return 0
        
        # 简化的权利金计算：内在价值 + 时间价值
        intrinsic_value = max(strike - spot, 0)
        time_value = spot * volatility * math.sqrt(days / 365) * 0.4
        
        return round(intrinsic_value + time_value, 2)
    
    def _calculate_call_premium(self, spot: float, strike: float, volatility: float, days: int) -> float:
        """计算看涨期权权利金（简化）"""
        if spot <= 0 or strike <= 0 or days <= 0:
            return 0
        
        # 简化的权利金计算
        intrinsic_value = max(spot - strike, 0)
        time_value = spot * volatility * math.sqrt(days / 365) * 0.4
        
        return round(intrinsic_value + time_value, 2)
    
    def _calculate_assignment_probability(self, spot: float, strike: float, volatility: float, days: int) -> float:
        """计算被行权概率（简化）"""
        if spot <= 0 or strike <= 0:
            return 0
        
        # 简化的概率计算：基于Delta值
        # 对于看跌期权，Delta约等于N(d1) - 1
        # 这里用简化公式
        moneyness = strike / spot
        time_factor = math.sqrt(days / 365)
        
        if moneyness > 1:  # 价内
            probability = 0.7 + 0.2 * (moneyness - 1)
        else:  # 价外
            probability = 0.3 * math.exp(-(1 - moneyness) / (volatility * time_factor))
        
        return min(max(probability, 0), 1)
    
    def _calculate_condor_probability(self, spot: float, profit_range: Tuple[float, float], volatility: float, days: int) -> float:
        """计算铁鹰策略盈利概率"""
        lower, upper = profit_range
        if spot <= 0 or lower >= upper:
            return 0
        
        # 简化：假设价格服从对数正态分布
        # 计算价格落在区间内的概率
        std_dev = volatility * math.sqrt(days / 365)
        z_lower = (math.log(lower) - math.log(spot)) / std_dev if lower > 0 else -3
        z_upper = (math.log(upper) - math.log(spot)) / std_dev if upper > 0 else 3
        
        # 标准正态分布累积概率
        from scipy.stats import norm
        try:
            prob = norm.cdf(z_upper) - norm.cdf(z_lower)
        except:
            # 如果scipy不可用，使用简化估计
            prob = 0.6  # 保守估计
        
        return min(max(prob, 0), 1)
    
    def _assess_strategy_suitability(self, strategy_id: str, stock_data: Dict) -> Dict[str, Any]:
        """评估策略适用性"""
        symbol = stock_data.get("symbol", "")
        current_price = stock_data.get("quote", {}).get("c", 0)
        volatility = stock_data.get("metrics", {}).get("beta", 1.5) * 0.3
        
        suitability = {
            "score": 50,  # 基准分
            "factors": [],
            "recommendation": "谨慎考虑"
        }
        
        # 基于策略类型评分
        if strategy_id == "cash_secured_put":
            if symbol == self.z_preferences["favorite_stock"]:
                suitability["score"] += 20
                suitability["factors"].append("Z最熟悉的股票")
            
            if current_price > 100:  # 高价股适合sell put
                suitability["score"] += 10
                suitability["factors"].append("股价较高，权利金收益好")
            
            if volatility > 0.3:  # 波动率高，权利金高
                suitability["score"] += 15
                suitability["factors"].append("波动率高，权利金收益高")
        
        elif strategy_id == "covered_call":
            if current_price > 50:  # 适合有一定价格的股票
                suitability["score"] += 10
                suitability["factors"].append("股价适中，适合备兑")
            
            # 检查是否有股息（有股息的股票更适合covered call）
            dividend_yield = stock_data.get("profile", {}).get("dividendYield", 0)
            if dividend_yield > 0.02:
                suitability["score"] += 15
                suitability["factors"].append("有股息，增加总收益")
        
        # 根据分数给出建议
        if suitability["score"] >= 70:
            suitability["recommendation"] = "强烈推荐"
        elif suitability["score"] >= 50:
            suitability["recommendation"] = "推荐"
        elif suitability["score"] >= 30:
            suitability["recommendation"] = "谨慎考虑"
        else:
            suitability["recommendation"] = "不推荐"
        
        return suitability
    
    def _generate_z_notes(self, strategy_id: str, stock_data: Dict, strike_price: float, premium: float) -> List[str]:
        """生成Z的特殊注意事项"""
        symbol = stock_data.get("symbol", "")
        notes = []
        
        if strategy_id == "cash_secured_put":
            if symbol == "TSLA":
                notes.append("✅ 这是你最熟悉的股票，操作更有把握")
                notes.append("💡 特斯拉波动性大，权利金收益通常较高")
                notes.append("⚠️ 特斯拉新闻多，注意财报和产品发布日期")
            
            notes.append(f"💰 预期权利金：${premium:.2f}/股，约${premium*100:.0f}/手")
            notes.append(f"🏦 需要现金担保：${strike_price*100:.0f}/手")
            notes.append("📅 建议到期时间：30-45天，平衡收益和时间价值")
        
        return notes
    
    def _generate_execution_plan(self, strategy_id: str, strike_price: float, days_to_expiry: int) -> str:
        """生成执行计划"""
        if strategy_id == "cash_secured_put":
            return f"""
            执行计划：
            1. 准备现金：${strike_price*100:.0f}（每手）
            2. 卖出看跌期权：行权价${strike_price:.2f}
            3. 到期时间：{days_to_expiry}天
            4. 目标Delta：0.3
            5. 管理策略：如果股价接近行权价，考虑展期或平仓
            """
        return "请参考具体策略参数执行"
    
    def _select_best_strategy(self, strategies: Dict) -> Dict[str, Any]:
        """选择最佳策略"""
        best_score = -1
        best_strategy = None
        
        for strategy_id, analysis in strategies.items():
            if analysis.get("applicable", False):
                suitability = analysis.get("suitability", {})
                score = suitability.get("score", 0)
                
                # 如果是Z偏好的策略，适当加分
                if strategy_id == self.z_preferences["preferred_strategy"]:
                    score += 10
                
                if score > best_score:
                    best_score = score
                    best_strategy = {
                        "strategy_id": strategy_id,
                        "name": analysis.get("name", ""),
                        "score": score,
                        "recommendation": suitability.get("recommendation", ""),
                        "key_parameters": analysis.get("parameters", {}),
                        "returns": analysis.get("returns", {})
                    }
        
        return best_strategy
    
    def _generate_z_recommendation(self, stock_data: Dict, strategies: Dict) -> Optional[Dict[str, Any]]:
        """生成Z的特殊推荐"""
        symbol = stock_data.get("symbol", "")
        
        # 如果是Z最爱的股票，给出特别建议
        if symbol == self.z_preferences["favorite_stock"]:
            cash_secured_put = strategies.get("cash_secured_put")
            if cash_secured_put and cash_secured_put.get("applicable", False):
                return {
                    "special_note": "⭐️ Z的特斯拉专属建议 ⭐️",
                    "strategy": "cash_secured_put",
                    "reason": "你最熟悉特斯拉，sell put策略最适合",
                    "parameters": cash_secured_put.get("parameters", {}),
                    "expected_annual_return": cash_secured_put.get("returns", {}).get("annualized_return", 0),
                    "risk_notes": [
                        "特斯拉波动大，权利金高但风险也高",
                        "注意马斯克的推特和财报日期",
                        "建议只分配部分现金做特斯拉sell put"
                    ],
                    "allocation_suggestion": "建议用10-20%的现金储备做特斯拉sell put"
                }
        
        return None
    
    def generate_options_summary(self, stock_opportunities: Dict[str, Dict]) -> Dict[str, Any]:
        """生成期权机会摘要"""
        opportunities_by_stock = {}
        best_overall = None
        best_score = -1
        
        for symbol, data in stock_opportunities.items():
            if data.get("best_strategy"):
                score = data["best_strategy"].get("score", 0)
                opportunities_by_stock[symbol] = {
                    "best_strategy": data["best_strategy"],
                    "current_price": data.get("current_price", 0),
                    "z_recommendation": data.get("z_special_recommendation")
                }
                
                # 更新最佳机会
                if score > best_score:
                    best_score = score
                    best_overall = {
                        "symbol": symbol,
                        "strategy": data["best_strategy"],
                        "price": data.get("current_price", 0),
                        "z_special": data.get("z_special_recommendation")
                    }
        
        return {
            "summary_date": datetime.now().strftime("%Y-%m-%d"),
            "opportunities_count": len(opportunities_by_stock),
            "best_overall_opportunity": best_overall,
            "opportunities_by_stock": opportunities_by_stock,
            "market_conditions": self._assess_options_market_conditions(stock_opportunities),
            "z_portfolio_suggestion": self._generate_z_portfolio_suggestion(opportunities_by_stock)
        }
    
    def _assess_options_market_conditions(self, stock_opportunities: Dict[str, Dict]) -> Dict[str, Any]:
        """评估期权市场环境"""
        # 计算平均隐含波动率
        total_vol = 0
        count = 0
        
        for data in stock_opportunities.values():
            vol = data.get("implied_volatility", 0)
            if vol > 0:
                total_vol += vol
                count += 1
        
        avg_vol = total_vol / count if count > 0 else 0.3
        
        # 市场环境判断
        if avg_vol > 0.4:
            environment = "high_volatility"
            advice = "波动率高，适合卖方策略（sell put/covered call），权利金收益高"
        elif avg_vol > 0.25:
            environment = "moderate_volatility"
            advice = "波动率适中，各种策略都可行"
        else:
            environment = "low_volatility"
            advice = "波动率低，适合买方策略或铁鹰策略"
        
        return {
            "average_implied_volatility": round(avg_vol, 3),
            "environment": environment,
            "advice": advice,
            "z_specific_advice": "高波动时增加sell put仓位，低波动时减少或转向其他策略"
        }
    
    def _generate_z_portfolio_suggestion(self, opportunities: Dict[str, Dict]) -> Dict[str, Any]:
        """生成Z的投资组合建议"""
        suggestions = []
        cash_allocation = 0
        
        # 检查特斯拉机会
        tsla_opportunity = opportunities.get("TSLA")
        if tsla_opportunity and tsla_opportunity.get("z_recommendation"):
            suggestions.append({
                "symbol": "TSLA",
                "action": "重点配置",
                "allocation": "10-20%现金",
                "strategy": "现金担保看跌期权",
                "reason": "你最熟悉，长期看好"
            })
            cash_allocation += 0.15  # 15%现金分配给特斯拉
        
        # 其他机会
        other_opportunities = []
        for symbol, data in opportunities.items():
            if symbol != "TSLA" and data.get("best_strategy", {}).get("score", 0) > 60:
                strategy = data["best_strategy"]
                other_opportunities.append({
                    "symbol": symbol,
                    "strategy": strategy.get("name", ""),
                    "score": strategy.get("score", 0),
                    "expected_return": strategy.get("returns", {}).get("annualized_return", 0)
                })
        
        # 选择前3个其他机会
        other_opportunities.sort(key=lambda x: x["score"], reverse=True)
        for opp in other_opportunities[:3]:
            suggestions.append({
                "symbol": opp["symbol"],
                "action": "适度配置",
                "allocation": "5-10%现金",
                "strategy": opp["strategy"],
                "reason": f"评分高({opp['score']})，预期年化{opp['expected_return']}%"
            })
            cash_allocation += 0.075  # 7.5%现金分配给每个机会
        
        return {
            "suggestions": suggestions,
            "total_cash_allocation": round(cash_allocation * 100, 1),
            "cash_reserve_remaining": round((self.z_preferences["cash_reserve_ratio"] - cash_allocation) * 100, 1),
            "advice": f"建议使用{cash_allocation*100:.1f}%的现金做期权策略，保留{100-cash_allocation*100:.1f}%现金应对市场波动"
        }

def create_options_engine():
    """创建期权策略引擎实例"""
    return OptionsEngine()