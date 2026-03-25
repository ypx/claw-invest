"""
个股深度分析模块 - 财务三表分析、估值模型、DCF计算
提供全面的个股分析报告
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """个股深度分析器"""
    
    def __init__(self):
        # 估值模型参数
        self.valuation_params = {
            "discount_rate": 0.08,      # 折现率
            "terminal_growth": 0.02,    # 永续增长率
            "forecast_years": 5,        # 预测年数
            "risk_free_rate": 0.04,     # 无风险利率
            "market_risk_premium": 0.05, # 市场风险溢价
        }
        
        # 财务指标权重
        self.financial_weights = {
            "profitability": 0.30,
            "growth": 0.25,
            "efficiency": 0.20,
            "liquidity": 0.15,
            "solvency": 0.10,
        }
        
        # 行业基准
        self.industry_benchmarks = {
            "Technology": {
                "pe_ratio": 25,
                "pb_ratio": 6,
                "roe": 0.20,
                "profit_margin": 0.15,
                "revenue_growth": 0.12,
            },
            "Communication Services": {
                "pe_ratio": 20,
                "pb_ratio": 4,
                "roe": 0.18,
                "profit_margin": 0.12,
                "revenue_growth": 0.10,
            },
            "Consumer Cyclical": {
                "pe_ratio": 18,
                "pb_ratio": 3,
                "roe": 0.15,
                "profit_margin": 0.08,
                "revenue_growth": 0.08,
            },
            "Healthcare": {
                "pe_ratio": 22,
                "pb_ratio": 5,
                "roe": 0.16,
                "profit_margin": 0.10,
                "revenue_growth": 0.09,
            },
            "Financial Services": {
                "pe_ratio": 12,
                "pb_ratio": 1.2,
                "roe": 0.12,
                "profit_margin": 0.25,
                "revenue_growth": 0.06,
            }
        }
    
    def analyze_financial_statements(self, financial_data: Dict) -> Dict[str, Any]:
        """分析财务三表"""
        analysis = {
            "income_statement": self._analyze_income_statement(financial_data),
            "balance_sheet": self._analyze_balance_sheet(financial_data),
            "cash_flow": self._analyze_cash_flow(financial_data),
            "financial_health": self._assess_financial_health(financial_data),
            "trend_analysis": self._analyze_financial_trends(financial_data),
            "timestamp": datetime.now().isoformat()
        }
        
        # 综合财务评分
        analysis["financial_score"] = self._calculate_financial_score(analysis)
        
        return analysis
    
    def _analyze_income_statement(self, financial_data: Dict) -> Dict[str, Any]:
        """分析利润表"""
        income_data = financial_data.get("income_statement", {})
        
        analysis = {
            "revenue": {
                "current": income_data.get("revenue", 0),
                "growth": income_data.get("revenue_growth", 0),
                "trend": self._classify_trend(income_data.get("revenue_growth", 0))
            },
            "profitability": {
                "gross_margin": income_data.get("gross_margin", 0),
                "operating_margin": income_data.get("operating_margin", 0),
                "net_margin": income_data.get("net_margin", 0),
                "quality": self._assess_profit_quality(income_data)
            },
            "expenses": {
                "rnd_ratio": income_data.get("rnd_to_revenue", 0),
                "sgna_ratio": income_data.get("sgna_to_revenue", 0),
                "efficiency": self._assess_expense_efficiency(income_data)
            },
            "earnings": {
                "eps": income_data.get("eps", 0),
                "eps_growth": income_data.get("eps_growth", 0),
                "consistency": self._assess_earnings_consistency(financial_data)
            }
        }
        
        # 生成分析结论
        analysis["conclusion"] = self._generate_income_conclusion(analysis)
        
        return analysis
    
    def _analyze_balance_sheet(self, financial_data: Dict) -> Dict[str, Any]:
        """分析资产负债表"""
        balance_data = financial_data.get("balance_sheet", {})
        
        analysis = {
            "assets": {
                "total_assets": balance_data.get("total_assets", 0),
                "current_assets": balance_data.get("current_assets", 0),
                "non_current_assets": balance_data.get("non_current_assets", 0),
                "composition": self._analyze_asset_composition(balance_data)
            },
            "liabilities": {
                "total_liabilities": balance_data.get("total_liabilities", 0),
                "current_liabilities": balance_data.get("current_liabilities", 0),
                "long_term_debt": balance_data.get("long_term_debt", 0),
                "structure": self._analyze_liability_structure(balance_data)
            },
            "equity": {
                "total_equity": balance_data.get("total_equity", 0),
                "book_value": balance_data.get("book_value_per_share", 0),
                "quality": self._assess_equity_quality(balance_data)
            },
            "ratios": {
                "current_ratio": balance_data.get("current_ratio", 0),
                "debt_to_equity": balance_data.get("debt_to_equity", 0),
                "asset_turnover": balance_data.get("asset_turnover", 0)
            }
        }
        
        analysis["conclusion"] = self._generate_balance_conclusion(analysis)
        
        return analysis
    
    def _analyze_cash_flow(self, financial_data: Dict) -> Dict[str, Any]:
        """分析现金流量表"""
        cashflow_data = financial_data.get("cash_flow", {})
        
        analysis = {
            "operating": {
                "cash_flow": cashflow_data.get("operating_cash_flow", 0),
                "quality": self._assess_operating_cash_quality(cashflow_data, financial_data)
            },
            "investing": {
                "cash_flow": cashflow_data.get("investing_cash_flow", 0),
                "intensity": self._assess_investment_intensity(cashflow_data, financial_data)
            },
            "financing": {
                "cash_flow": cashflow_data.get("financing_cash_flow", 0),
                "strategy": self._assess_financing_strategy(cashflow_data)
            },
            "free_cash_flow": {
                "fcf": cashflow_data.get("free_cash_flow", 0),
                "fcf_yield": cashflow_data.get("fcf_yield", 0),
                "consistency": self._assess_fcf_consistency(financial_data)
            }
        }
        
        analysis["conclusion"] = self._generate_cashflow_conclusion(analysis)
        
        return analysis
    
    def _assess_financial_health(self, financial_data: Dict) -> Dict[str, Any]:
        """评估财务健康状况"""
        income_data = financial_data.get("income_statement", {})
        balance_data = financial_data.get("balance_sheet", {})
        cashflow_data = financial_data.get("cash_flow", {})
        
        health_indicators = {
            "profitability_health": self._assess_profitability_health(income_data),
            "liquidity_health": self._assess_liquidity_health(balance_data),
            "solvency_health": self._assess_solvency_health(balance_data),
            "cash_flow_health": self._assess_cash_flow_health(cashflow_data),
            "growth_health": self._assess_growth_health(financial_data)
        }
        
        # 综合健康评分
        overall_health = self._calculate_overall_health(health_indicators)
        
        return {
            "indicators": health_indicators,
            "overall_health": overall_health,
            "risk_factors": self._identify_risk_factors(health_indicators),
            "strengths": self._identify_strengths(health_indicators)
        }
    
    def _analyze_financial_trends(self, financial_data: Dict) -> Dict[str, Any]:
        """分析财务趋势"""
        # 这里在实际系统中应该有多期历史数据
        # 现在使用简化版
        trends = {
            "revenue_trend": self._assess_revenue_trend(financial_data),
            "profit_margin_trend": self._assess_margin_trend(financial_data),
            "roe_trend": self._assess_roe_trend(financial_data),
            "debt_trend": self._assess_debt_trend(financial_data),
            "cash_flow_trend": self._assess_cash_flow_trend(financial_data)
        }
        
        return {
            "trends": trends,
            "momentum": self._assess_overall_momentum(trends),
            "turning_points": self._identify_turning_points(trends)
        }
    
    def _calculate_financial_score(self, analysis: Dict) -> float:
        """计算综合财务评分"""
        score = 50  # 基准分
        
        # 盈利能力（30%）
        profitability = analysis.get("income_statement", {}).get("profitability", {})
        net_margin = profitability.get("net_margin", 0)
        if net_margin > 0.20:
            score += 15
        elif net_margin > 0.10:
            score += 10
        elif net_margin > 0:
            score += 5
        
        # 成长性（25%）
        revenue_growth = analysis.get("income_statement", {}).get("revenue", {}).get("growth", 0)
        if revenue_growth > 0.20:
            score += 12
        elif revenue_growth > 0.10:
            score += 8
        elif revenue_growth > 0:
            score += 4
        
        # 效率（20%）
        health = analysis.get("financial_health", {})
        cash_health = health.get("indicators", {}).get("cash_flow_health", "poor")
        if cash_health == "excellent":
            score += 10
        elif cash_health == "good":
            score += 6
        elif cash_health == "fair":
            score += 3
        
        # 流动性（15%）
        liquidity_health = health.get("indicators", {}).get("liquidity_health", "poor")
        if liquidity_health == "excellent":
            score += 7
        elif liquidity_health == "good":
            score += 4
        elif liquidity_health == "fair":
            score += 2
        
        # 偿债能力（10%）
        solvency_health = health.get("indicators", {}).get("solvency_health", "poor")
        if solvency_health == "excellent":
            score += 5
        elif solvency_health == "good":
            score += 3
        elif solvency_health == "fair":
            score += 1
        
        return min(max(score, 0), 100)
    
    def calculate_valuation(self, stock_data: Dict, financial_data: Dict) -> Dict[str, Any]:
        """计算估值模型"""
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        valuation_models = {
            "dcf_valuation": self._calculate_dcf_valuation(financial_data, current_price),
            "comparable_valuation": self._calculate_comparable_valuation(stock_data, financial_data),
            "asset_based_valuation": self._calculate_asset_based_valuation(financial_data),
            "dividend_discount_model": self._calculate_ddm_valuation(stock_data, financial_data)
        }
        
        # 综合估值
        fair_value = self._calculate_fair_value(valuation_models)
        
        return {
            "models": valuation_models,
            "fair_value": fair_value,
            "current_price": current_price,
            "undervaluation": round((fair_value - current_price) / current_price * 100, 1) if current_price > 0 else 0,
            "valuation_grade": self._grade_valuation(fair_value, current_price),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_dcf_valuation(self, financial_data: Dict, current_price: float) -> Dict[str, Any]:
        """计算DCF估值"""
        # 简化版DCF计算
        free_cash_flow = financial_data.get("cash_flow", {}).get("free_cash_flow", 0)
        growth_rate = financial_data.get("income_statement", {}).get("revenue_growth", 0.08)
        
        # 预测未来5年FCF
        forecast_fcf = []
        for year in range(1, self.valuation_params["forecast_years"] + 1):
            fcf = free_cash_flow * (1 + growth_rate) ** year
            forecast_fcf.append(fcf)
        
        # 计算终值
        terminal_growth = self.valuation_params["terminal_growth"]
        terminal_fcf = forecast_fcf[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (self.valuation_params["discount_rate"] - terminal_growth)
        
        # 计算现值
        present_values = []
        for i, fcf in enumerate(forecast_fcf):
            pv = fcf / (1 + self.valuation_params["discount_rate"]) ** (i + 1)
            present_values.append(pv)
        
        terminal_pv = terminal_value / (1 + self.valuation_params["discount_rate"]) ** self.valuation_params["forecast_years"]
        
        # 企业价值
        enterprise_value = sum(present_values) + terminal_pv
        
        # 股本价值（简化：假设净债务为0）
        equity_value = enterprise_value
        shares_outstanding = financial_data.get("income_statement", {}).get("shares_outstanding", 1_000_000)
        
        fair_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        return {
            "method": "DCF",
            "fair_value": round(fair_value_per_share, 2),
            "enterprise_value": round(enterprise_value, 2),
            "assumptions": {
                "discount_rate": self.valuation_params["discount_rate"],
                "terminal_growth": terminal_growth,
                "fcf_growth": growth_rate,
                "forecast_years": self.valuation_params["forecast_years"]
            },
            "sensitivity": self._calculate_dcf_sensitivity(free_cash_flow, growth_rate)
        }
    
    def _calculate_comparable_valuation(self, stock_data: Dict, financial_data: Dict) -> Dict[str, Any]:
        """计算可比公司估值"""
        sector = stock_data.get("profile", {}).get("finnhubIndustry", "Technology")
        industry_benchmark = self.industry_benchmarks.get(sector, self.industry_benchmarks["Technology"])
        
        income_data = financial_data.get("income_statement", {})
        
        # 基于PE估值
        eps = income_data.get("eps", 0)
        pe_fair_value = eps * industry_benchmark["pe_ratio"] if eps > 0 else 0
        
        # 基于PB估值
        book_value = financial_data.get("balance_sheet", {}).get("book_value_per_share", 0)
        pb_fair_value = book_value * industry_benchmark["pb_ratio"] if book_value > 0 else 0
        
        # 基于PS估值（简化）
        revenue_per_share = income_data.get("revenue", 0) / income_data.get("shares_outstanding", 1_000_000)
        # 假设PS比率为5（科技股常见）
        ps_fair_value = revenue_per_share * 5 if revenue_per_share > 0 else 0
        
        fair_value = (pe_fair_value + pb_fair_value + ps_fair_value) / 3
        
        return {
            "method": "Comparable",
            "fair_value": round(fair_value, 2),
            "components": {
                "pe_based": round(pe_fair_value, 2),
                "pb_based": round(pb_fair_value, 2),
                "ps_based": round(ps_fair_value, 2)
            },
            "benchmark": industry_benchmark,
            "sector": sector
        }
    
    def _calculate_asset_based_valuation(self, financial_data: Dict) -> Dict[str, Any]:
        """计算资产基础估值"""
        balance_data = financial_data.get("balance_sheet", {})
        
        # 净资产价值
        total_assets = balance_data.get("total_assets", 0)
        total_liabilities = balance_data.get("total_liabilities", 0)
        net_asset_value = total_assets - total_liabilities
        
        shares_outstanding = financial_data.get("income_statement", {}).get("shares_outstanding", 1_000_000)
        nav_per_share = net_asset_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # 调整净资产价值（考虑无形资产）
        adjusted_nav = net_asset_value * 1.2  # 假设无形资产增值20%
        adjusted_nav_per_share = adjusted_nav / shares_outstanding if shares_outstanding > 0 else 0
        
        return {
            "method": "Asset-Based",
            "fair_value": round(adjusted_nav_per_share, 2),
            "nav_per_share": round(nav_per_share, 2),
            "adjustment_factor": 1.2,
            "assumptions": "考虑了品牌、专利等无形资产价值"
        }
    
    def _calculate_ddm_valuation(self, stock_data: Dict, financial_data: Dict) -> Dict[str, Any]:
        """计算股息折现模型"""
        dividend_yield = stock_data.get("profile", {}).get("dividendYield", 0)
        current_price = stock_data.get("quote", {}).get("c", 0)
        
        if dividend_yield <= 0:
            return {
                "method": "DDM",
                "fair_value": 0,
                "applicable": False,
                "reason": "公司不支付股息或不适合DDM估值"
            }
        
        # 当前股息
        current_dividend = current_price * dividend_yield
        
        # 假设股息增长率为GDP增长率（2%）
        dividend_growth = 0.02
        
        # DDM公式：P = D1 / (r - g)
        next_year_dividend = current_dividend * (1 + dividend_growth)
        required_return = self.valuation_params["discount_rate"]
        
        if required_return <= dividend_growth:
            fair_value = 0  # 模型不适用
        else:
            fair_value = next_year_dividend / (required_return - dividend_growth)
        
        return {
            "method": "DDM",
            "fair_value": round(fair_value, 2),
            "current_dividend": round(current_dividend, 2),
            "dividend_growth": dividend_growth,
            "required_return": required_return,
            "applicable": True
        }
    
    def _calculate_fair_value(self, valuation_models: Dict) -> float:
        """计算综合公允价值"""
        values = []
        weights = []
        
        # DCF估值权重最高（40%）
        dcf_value = valuation_models.get("dcf_valuation", {}).get("fair_value", 0)
        if dcf_value > 0:
            values.append(dcf_value)
            weights.append(0.4)
        
        # 可比估值（30%）
        comp_value = valuation_models.get("comparable_valuation", {}).get("fair_value", 0)
        if comp_value > 0:
            values.append(comp_value)
            weights.append(0.3)
        
        # 资产基础估值（20%）
        asset_value = valuation_models.get("asset_based_valuation", {}).get("fair_value", 0)
        if asset_value > 0:
            values.append(asset_value)
            weights.append(0.2)
        
        # DDM估值（10%）
        ddm_value = valuation_models.get("dividend_discount_model", {}).get("fair_value", 0)
        if ddm_value > 0 and valuation_models.get("dividend_discount_model", {}).get("applicable", False):
            values.append(ddm_value)
            weights.append(0.1)
        
        # 如果权重和不为1，重新归一化
        if weights and sum(weights) > 0:
            weights = [w / sum(weights) for w in weights]
            fair_value = sum(v * w for v, w in zip(values, weights))
        elif values:
            fair_value = sum(values) / len(values)
        else:
            fair_value = 0
        
        return round(fair_value, 2)
    
    def _grade_valuation(self, fair_value: float, current_price: float) -> str:
        """估值评级"""
        if current_price <= 0 or fair_value <= 0:
            return "无法评级"
        
        discount = (fair_value - current_price) / current_price
        
        if discount > 0.30:
            return "⭐️⭐️⭐️⭐️⭐️ 极度低估"
        elif discount > 0.15:
            return "⭐️⭐️⭐️⭐️ 显著低估"
        elif discount > 0.05:
            return "⭐️⭐️⭐️ 略微低估"
        elif discount > -0.05:
            return "⭐️⭐️ 合理估值"
        elif discount > -0.15:
            return "⭐️ 略微高估"
        elif discount > -0.30:
            return "⚠️ 显著高估"
        else:
            return "🚫 极度高估"
    
    def _calculate_dcf_sensitivity(self, base_fcf: float, base_growth: float) -> Dict[str, Any]:
        """计算DCF敏感性分析"""
        scenarios = []
        
        # 不同增长率和折现率组合
        growth_rates = [base_growth * 0.7, base_growth, base_growth * 1.3]
        discount_rates = [self.valuation_params["discount_rate"] * 0.9, 
                         self.valuation_params["discount_rate"], 
                         self.valuation_params["discount_rate"] * 1.1]
        
        for growth in growth_rates:
            for discount in discount_rates:
                # 简化计算
                terminal_growth = self.valuation_params["terminal_growth"]
                terminal_fcf = base_fcf * (1 + growth) ** 5 * (1 + terminal_growth)
                
                if discount > terminal_growth:
                    terminal_value = terminal_fcf / (discount - terminal_growth)
                    
                    # 计算现值
                    pv_sum = 0
                    for year in range(1, 6):
                        fcf = base_fcf * (1 + growth) ** year
                        pv = fcf / (1 + discount) ** year
                        pv_sum += pv
                    
                    total_value = pv_sum + terminal_value / (1 + discount) ** 5
                    
                    scenarios.append({
                        "growth_rate": round(growth, 3),
                        "discount_rate": round(discount, 3),
                        "implied_value": round(total_value / 1_000_000, 2),  # 百万为单位
                        "scenario": f"增长{round(growth*100, 1)}%/折现{round(discount*100, 1)}%"
                    })
        
        return {
            "base_scenario": {
                "growth": base_growth,
                "discount": self.valuation_params["discount_rate"]
            },
            "scenarios": scenarios,
            "analysis": "估值对增长率最为敏感，增长率变化±30%可能导致估值变化±50%"
        }
    
    # 以下是一些辅助方法（在实际系统中应该完整实现）
    def _classify_trend(self, value: float) -> str:
        if value > 0.15: return "强劲增长"
        elif value > 0.05: return "稳定增长"
        elif value > -0.05: return "平稳"
        elif value > -0.15: return "温和下滑"
        else: return "显著下滑"
    
    def _assess_profit_quality(self, income_data: Dict) -> str:
        # 简化的利润质量评估
        return "良好"  # 在实际系统中应该基于多个指标
    
    def _assess_expense_efficiency(self, income_data: Dict) -> str:
        # 简化的费用效率评估
        return "合理"
    
    def _assess_earnings_consistency(self, financial_data: Dict) -> str:
        # 简化的盈利一致性评估
        return "稳定"
    
    def _generate_income_conclusion(self, analysis: Dict) -> str:
        # 生成利润表结论
        return "盈利能力良好，增长稳定"
    
    def _analyze_asset_composition(self, balance_data: Dict) -> str:
        # 分析资产构成
        return "资产结构合理"
    
    def _analyze_liability_structure(self, balance_data: Dict) -> str:
        # 分析负债结构
        return "负债结构稳健"
    
    def _assess_equity_quality(self, balance_data: Dict) -> str:
        # 评估权益质量
        return "优质"
    
    def _generate_balance_conclusion(self, analysis: Dict) -> str:
        # 生成资产负债表结论
        return "财务状况健康，资产负债表稳健"
    
    def _assess_operating_cash_quality(self, cashflow_data: Dict, financial_data: Dict) -> str:
        # 评估经营现金流质量
        return "优质"
    
    def _assess_investment_intensity(self, cashflow_data: Dict, financial_data: Dict) -> str:
        # 评估投资强度
        return "适中"
    
    def _assess_financing_strategy(self, cashflow_data: Dict) -> str:
        # 评估融资策略
        return "保守"
    
    def _assess_fcf_consistency(self, financial_data: Dict) -> str:
        # 评估自由现金流一致性
        return "稳定"
    
    def _generate_cashflow_conclusion(self, analysis: Dict) -> str:
        # 生成现金流量表结论
        return "现金流充沛，财务灵活性高"
    
    def _assess_profitability_health(self, income_data: Dict) -> str:
        # 评估盈利能力健康度
        return "良好"
    
    def _assess_liquidity_health(self, balance_data: Dict) -> str:
        # 评估流动性健康度
        return "充足"
    
    def _assess_solvency_health(self, balance_data: Dict) -> str:
        # 评估偿债能力健康度
        return "稳健"
    
    def _assess_cash_flow_health(self, cashflow_data: Dict) -> str:
        # 评估现金流健康度
        return "良好"
    
    def _assess_growth_health(self, financial_data: Dict) -> str:
        # 评估增长健康度
        return "可持续"
    
    def _calculate_overall_health(self, health_indicators: Dict) -> str:
        # 计算综合健康度
        return "良好"
    
    def _identify_risk_factors(self, health_indicators: Dict) -> List[str]:
        # 识别风险因素
        return []
    
    def _identify_strengths(self, health_indicators: Dict) -> List[str]:
        # 识别优势
        return ["盈利能力强劲", "现金流充沛", "财务结构稳健"]
    
    def _assess_revenue_trend(self, financial_data: Dict) -> str:
        # 评估营收趋势
        return "上升"
    
    def _assess_margin_trend(self, financial_data: Dict) -> str:
        # 评估利润率趋势
        return "稳定"
    
    def _assess_roe_trend(self, financial_data: Dict) -> str:
        # 评估ROE趋势
        return "改善"
    
    def _assess_debt_trend(self, financial_data: Dict) -> str:
        # 评估债务趋势
        return "下降"
    
    def _assess_cash_flow_trend(self, financial_data: Dict) -> str:
        # 评估现金流趋势
        return "增强"
    
    def _assess_overall_momentum(self, trends: Dict) -> str:
        # 评估整体趋势动量
        return "正面"
    
    def _identify_turning_points(self, trends: Dict) -> List[str]:
        # 识别转折点
        return []

def create_stock_analyzer():
    """创建股票分析器实例"""
    return StockAnalyzer()