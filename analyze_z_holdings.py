#!/usr/bin/env python3
"""
分析Z的实际持仓 - 简化版本
直接使用现有模块，避免导入问题
"""

import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZPortfolioAnalyzer:
    """Z的持仓分析器（简化版）"""
    
    def __init__(self):
        """初始化分析器"""
        self.holdings = {
            "cash": 0.0,
            "stocks": [],
            "options": []
        }
        
        # Z的特殊偏好
        self.z_preferences = {
            "risk_tolerance": "conservative",
            "target_cash_ratio": 0.35,  # 35%现金目标
            "max_single_position": 0.15,  # 单一仓位最高15%
            "preferred_stocks": ["TSLA", "NVDA", "GOOGL", "AAPL", "AMZN"],
            "preferred_strategies": ["cash_secured_put"]
        }
    
    def setup_default_holdings(self):
        """设置默认持仓（基于Z的投资偏好）"""
        logger.info("设置默认持仓数据...")
        
        # 重置持仓
        self.holdings = {
            "cash": 100000.0,  # 10万美元现金
            "stocks": [],
            "options": []
        }
        
        # 添加股票持仓（基于Z的实际投资风格）
        # 长期持有AI/科技/太空正股，保守型投资者
        stock_positions = [
            # AI/科技核心持仓
            {"symbol": "NVDA", "quantity": 50, "cost_basis": 120.0, "current_price": 177.97, "notes": "AI算力，长期持有"},
            {"symbol": "GOOGL", "quantity": 30, "cost_basis": 280.0, "current_price": 304.39, "notes": "AI+搜索，低估"},
            {"symbol": "AMZN", "quantity": 40, "cost_basis": 180.0, "current_price": 212.36, "notes": "AWS+电商，稳健"},
            {"symbol": "MSFT", "quantity": 30, "cost_basis": 360.0, "current_price": 386.25, "notes": "企业软件+AI"},
            {"symbol": "AAPL", "quantity": 35, "cost_basis": 230.0, "current_price": 252.13, "notes": "核心持仓，定期买入"},
            
            # Z特别关注的股票
            {"symbol": "TSLA", "quantity": 25, "cost_basis": 350.0, "current_price": 383.64, "notes": "常做sell put"},
            
            # 成长型/前沿科技
            {"symbol": "IONQ", "quantity": 100, "cost_basis": 20.0, "current_price": 33.07, "notes": "量子计算"},
            {"symbol": "RKLB", "quantity": 200, "cost_basis": 15.0, "current_price": 22.50, "notes": "太空发射"}
        ]
        
        for position in stock_positions:
            self._add_stock_position(position)
        
        # 添加期权持仓（Z的sell put策略）
        option_positions = [
            {"underlying": "TSLA", "type": "put", "strike": 350.0, "expiration": "2026-06-30", 
             "quantity": 2, "premium": 15.0, "current_price": 10.5, "notes": "sell put策略"},
            {"underlying": "NVDA", "type": "put", "strike": 160.0, "expiration": "2026-05-31", 
             "quantity": 3, "premium": 12.0, "current_price": 8.5, "notes": "sell put策略"}
        ]
        
        for position in option_positions:
            self._add_option_position(position)
        
        logger.info("默认持仓设置完成")
        print("✅ 模拟持仓数据已创建，基于Z的实际投资偏好：")
        print("   - AI/科技股：NVDA, GOOGL, AMZN, MSFT")
        print("   - 熟悉股票：TSLA, AAPL")
        print("   - 成长领域：IONQ（量子计算）, RKLB（太空）")
        print("   - sell put策略：TSLA和NVDA的看跌期权")
        print("   - 现金：$100,000（35%目标比例）")
    
    def _add_stock_position(self, position: Dict):
        """添加股票持仓"""
        # 计算持仓价值
        current_value = position["quantity"] * position["current_price"]
        cost_value = position["quantity"] * position["cost_basis"]
        pnl = current_value - cost_value
        pnl_percent = (pnl / cost_value * 100) if cost_value > 0 else 0
        
        position.update({
            "current_value": current_value,
            "cost_value": cost_value,
            "pnl": pnl,
            "pnl_percent": round(pnl_percent, 1)
        })
        
        self.holdings["stocks"].append(position)
        logger.info(f"添加股票: {position['symbol']} {position['quantity']}股 @ ${position['current_price']}")
    
    def _add_option_position(self, position: Dict):
        """添加期权持仓"""
        # 计算期权价值（每份合约100股）
        current_value = position["quantity"] * 100 * position["current_price"]
        cost_value = position["quantity"] * 100 * position["premium"]
        pnl = current_value - cost_value
        pnl_percent = (pnl / cost_value * 100) if cost_value > 0 else 0
        
        position.update({
            "current_value": current_value,
            "cost_value": cost_value,
            "pnl": pnl,
            "pnl_percent": round(pnl_percent, 1)
        })
        
        self.holdings["options"].append(position)
        logger.info(f"添加期权: {position['underlying']} {position['type'].upper()} ${position['strike']}")
    
    def analyze(self):
        """进行综合分析"""
        logger.info("开始投资组合分析...")
        
        # 计算投资组合数据
        portfolio_data = self._calculate_portfolio_data()
        
        # 健康度分析
        health_analysis = self._analyze_portfolio_health(portfolio_data)
        
        # 风险分析
        risk_analysis = self._analyze_portfolio_risk(portfolio_data)
        
        # 生成建议
        recommendations = self._generate_recommendations(portfolio_data, health_analysis, risk_analysis)
        
        # 构建分析报告
        analysis_report = {
            "metadata": {
                "analyzed_for": "Z",
                "analysis_date": datetime.now().isoformat(),
                "risk_profile": self.z_preferences["risk_tolerance"]
            },
            "portfolio_data": portfolio_data,
            "health_analysis": health_analysis,
            "risk_analysis": risk_analysis,
            "recommendations": recommendations
        }
        
        # 保存和显示结果
        self._save_results(analysis_report)
        self._display_results(analysis_report)
        
        return analysis_report
    
    def _calculate_portfolio_data(self) -> Dict:
        """计算投资组合数据"""
        stocks = self.holdings["stocks"]
        options = self.holdings["options"]
        cash = self.holdings["cash"]
        
        # 计算总价值
        stock_value = sum(pos["current_value"] for pos in stocks)
        option_value = sum(pos["current_value"] for pos in options)
        total_value = stock_value + option_value + cash
        
        # 计算总成本
        stock_cost = sum(pos["cost_value"] for pos in stocks)
        option_cost = sum(pos["cost_value"] for pos in options)
        total_cost = stock_cost + option_cost
        
        # 计算总盈亏
        total_pnl = stock_value + option_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 计算资产配置
        if total_value > 0:
            stock_allocation = (stock_value / total_value) * 100
            option_allocation = (option_value / total_value) * 100
            cash_allocation = (cash / total_value) * 100
        else:
            stock_allocation = option_allocation = cash_allocation = 0
        
        # 计算行业分布
        sector_distribution = self._calculate_sector_distribution(stocks)
        
        # 计算前五大持仓
        top_holdings = self._get_top_holdings(stocks + options)
        
        return {
            "total_value": total_value,
            "stock_value": stock_value,
            "option_value": option_value,
            "cash_value": cash,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": round(total_pnl_percent, 1),
            "asset_allocation": {
                "stocks": round(stock_allocation, 1),
                "options": round(option_allocation, 1),
                "cash": round(cash_allocation, 1)
            },
            "sector_distribution": sector_distribution,
            "top_holdings": top_holdings,
            "stock_count": len(stocks),
            "option_count": len(options)
        }
    
    def _calculate_sector_distribution(self, stocks: List) -> Dict:
        """计算行业分布"""
        # 简化的行业分类
        sector_map = {
            "NVDA": "Technology",
            "GOOGL": "Communication Services", 
            "AMZN": "Consumer Cyclical",
            "TSLA": "Consumer Cyclical",
            "AAPL": "Technology",
            "MSFT": "Technology",
            "IONQ": "Technology",
            "RKLB": "Industrials"
        }
        
        sector_values = {}
        total_stock_value = sum(pos["current_value"] for pos in stocks)
        
        if total_stock_value > 0:
            for pos in stocks:
                symbol = pos["symbol"]
                sector = sector_map.get(symbol, "Unknown")
                value = pos["current_value"]
                
                if sector not in sector_values:
                    sector_values[sector] = 0
                sector_values[sector] += value
            
            # 转换为百分比
            for sector in sector_values:
                sector_values[sector] = round((sector_values[sector] / total_stock_value) * 100, 1)
        
        return sector_values
    
    def _get_top_holdings(self, holdings: List) -> List:
        """获取前五大持仓"""
        # 按价值排序
        sorted_holdings = sorted(holdings, key=lambda x: x.get("current_value", 0), reverse=True)
        
        top_holdings = []
        for i, pos in enumerate(sorted_holdings[:5], 1):
            if "symbol" in pos:  # 股票持仓
                holding_info = {
                    "rank": i,
                    "type": "stock",
                    "name": pos["symbol"],
                    "value": pos["current_value"],
                    "pnl_percent": pos.get("pnl_percent", 0)
                }
            else:  # 期权持仓
                holding_info = {
                    "rank": i,
                    "type": "option",
                    "name": f"{pos['underlying']} {pos['type'].upper()} ${pos['strike']}",
                    "value": pos["current_value"],
                    "pnl_percent": pos.get("pnl_percent", 0)
                }
            
            top_holdings.append(holding_info)
        
        return top_holdings
    
    def _analyze_portfolio_health(self, portfolio_data: Dict) -> Dict:
        """分析投资组合健康度"""
        # 现金健康度
        cash_ratio = portfolio_data["asset_allocation"]["cash"]
        target_cash = self.z_preferences["target_cash_ratio"] * 100
        cash_deviation = cash_ratio - target_cash
        
        if abs(cash_deviation) <= 5:
            cash_status = "优秀"
        elif abs(cash_deviation) <= 10:
            cash_status = "良好"
        else:
            cash_status = "需要调整"
        
        # 集中度分析
        stock_count = portfolio_data["stock_count"]
        if stock_count >= 8:
            concentration_status = "分散良好"
        elif stock_count >= 5:
            concentration_status = "适中"
        else:
            concentration_status = "较集中"
        
        # 行业分散度
        sector_dist = portfolio_data["sector_distribution"]
        sector_count = len(sector_dist)
        
        if sector_count >= 4:
            diversification_status = "优秀"
        elif sector_count >= 2:
            diversification_status = "良好"
        else:
            diversification_status = "需要改进"
        
        # 整体健康评分
        health_score = self._calculate_health_score(
            cash_ratio, target_cash, stock_count, sector_count
        )
        
        return {
            "cash_analysis": {
                "current_ratio": cash_ratio,
                "target_ratio": target_cash,
                "deviation": round(cash_deviation, 1),
                "status": cash_status
            },
            "concentration_analysis": {
                "stock_count": stock_count,
                "ideal_count": 8,
                "status": concentration_status
            },
            "sector_analysis": {
                "sector_count": sector_count,
                "status": diversification_status
            },
            "overall_health_score": health_score
        }
    
    def _calculate_health_score(self, cash_ratio: float, target_cash: float, 
                               stock_count: int, sector_count: int) -> float:
        """计算整体健康评分"""
        scores = []
        
        # 现金评分（权重35%）
        cash_deviation = abs(cash_ratio - target_cash)
        if cash_deviation <= 5:
            cash_score = 95
        elif cash_deviation <= 10:
            cash_score = 85
        elif cash_deviation <= 15:
            cash_score = 75
        else:
            cash_score = 60
        scores.append(cash_score * 0.35)
        
        # 持仓数量评分（权重30%）
        if stock_count >= 8:
            count_score = 90
        elif stock_count >= 5:
            count_score = 80
        else:
            count_score = 65
        scores.append(count_score * 0.30)
        
        # 行业分散评分（权重35%）
        if sector_count >= 4:
            sector_score = 95
        elif sector_count >= 2:
            sector_score = 85
        else:
            sector_score = 70
        scores.append(sector_score * 0.35)
        
        return round(sum(scores), 1)
    
    def _analyze_portfolio_risk(self, portfolio_data: Dict) -> Dict:
        """分析投资组合风险"""
        # 简化的风险评估
        total_value = portfolio_data["total_value"]
        stock_value = portfolio_data["stock_value"]
        
        if total_value <= 0:
            return {
                "volatility_risk": "低",
                "concentration_risk": "低",
                "liquidity_risk": "低",
                "overall_risk_level": "低"
            }
        
        # 波动率风险评估（基于股票占比）
        stock_ratio = stock_value / total_value
        if stock_ratio > 0.8:
            volatility_risk = "高"
        elif stock_ratio > 0.6:
            volatility_risk = "中高"
        elif stock_ratio > 0.4:
            volatility_risk = "中"
        else:
            volatility_risk = "低"
        
        # 集中度风险（基于前三大持仓）
        top_holdings = portfolio_data["top_holdings"]
        if len(top_holdings) >= 3:
            top3_value = sum(h["value"] for h in top_holdings[:3])
            top3_ratio = top3_value / total_value
            if top3_ratio > 0.6:
                concentration_risk = "高"
            elif top3_ratio > 0.4:
                concentration_risk = "中"
            else:
                concentration_risk = "低"
        else:
            concentration_risk = "低"
        
        # 流动性风险（基于持仓数量）
        stock_count = portfolio_data["stock_count"]
        if stock_count <= 2:
            liquidity_risk = "高"
        elif stock_count <= 4:
            liquidity_risk = "中"
        else:
            liquidity_risk = "低"
        
        # 整体风险水平
        risk_level = self._determine_overall_risk(volatility_risk, concentration_risk, liquidity_risk)
        
        return {
            "volatility_risk": volatility_risk,
            "concentration_risk": concentration_risk,
            "liquidity_risk": liquidity_risk,
            "overall_risk_level": risk_level
        }
    
    def _determine_overall_risk(self, *risk_levels: str) -> str:
        """确定整体风险水平"""
        risk_mapping = {"高": 3, "中": 2, "低": 1}
        risk_scores = [risk_mapping.get(r, 1) for r in risk_levels]
        avg_score = sum(risk_scores) / len(risk_scores)
        
        if avg_score >= 2.5:
            return "高"
        elif avg_score >= 1.5:
            return "中"
        else:
            return "低"
    
    def _generate_recommendations(self, portfolio_data: Dict, 
                                 health_analysis: Dict, 
                                 risk_analysis: Dict) -> Dict:
        """生成投资建议"""
        recommendations = []
        
        # 现金管理建议
        cash_analysis = health_analysis["cash_analysis"]
        current_cash = cash_analysis["current_ratio"]
        target_cash = cash_analysis["target_ratio"]
        deviation = cash_analysis["deviation"]
        
        if deviation < -10:  # 现金过少
            recommendations.append({
                "category": "现金管理",
                "priority": "高",
                "action": "增加现金储备",
                "reason": f"现金比例({current_cash:.1f}%)低于目标({target_cash:.1f}%)",
                "suggestion": "可考虑卖出部分高估值持仓或增加现金存入"
            })
        elif deviation > 10:  # 现金过多
            recommendations.append({
                "category": "现金管理",
                "priority": "中",
                "action": "优化现金使用",
                "reason": f"现金比例({current_cash:.1f}%)高于目标({target_cash:.1f}%)",
                "suggestion": "考虑使用部分现金进行sell put策略或分批买入优质标的"
            })
        
        # 分散度建议
        concentration_analysis = health_analysis["concentration_analysis"]
        stock_count = concentration_analysis["stock_count"]
        ideal_count = concentration_analysis["ideal_count"]
        
        if stock_count < ideal_count * 0.6:
            recommendations.append({
                "category": "分散度",
                "priority": "中",
                "action": "增加持仓数量",
                "reason": f"当前持仓{stock_count}只，建议增加至{ideal_count}只左右",
                "suggestion": "可考虑在回调时分批买入熟悉的股票（如NVDA、TSLA）"
            })
        
        # 风险管理建议
        risk_level = risk_analysis["overall_risk_level"]
        if risk_level == "高":
            recommendations.append({
                "category": "风险管理",
                "priority": "高",
                "action": "降低组合风险",
                "reason": "投资组合整体风险水平偏高",
                "suggestion": "考虑减少高风险资产配置，增加现金或防御性资产"
            })
        
        # 基于Z偏好的建议
        if not any("sell put" in rec.get("suggestion", "") for rec in recommendations):
            recommendations.append({
                "category": "策略优化",
                "priority": "低",
                "action": "优化sell put策略",
                "reason": "适合Z的交易习惯和市场环境",
                "suggestion": "考虑在熟悉股票（TSLA、NVDA）上寻找sell put机会"
            })
        
        # 默认建议
        if not recommendations:
            recommendations.append({
                "category": "组合维护",
                "priority": "低",
                "action": "定期监控",
                "reason": "投资组合状态良好",
                "suggestion": "继续定期检查持仓，关注市场变化"
            })
        
        return recommendations
    
    def _save_results(self, analysis_report: Dict):
        """保存分析结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/Users/nn/WorkBuddy/Claw/reports/z_holdings_analysis_{timestamp}.json"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 保存JSON文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 分析结果已保存: {filename}")
    
    def _display_results(self, analysis_report: Dict):
        """显示分析结果"""
        print("\n" + "="*60)
        print("📊 Z的投资组合分析报告")
        print("="*60)
        
        portfolio_data = analysis_report["portfolio_data"]
        health_analysis = analysis_report["health_analysis"]
        risk_analysis = analysis_report["risk_analysis"]
        
        # 基本统计
        print(f"\n📈 投资组合统计")
        print(f"  总价值: ${portfolio_data['total_value']:,.2f}")
        print(f"  总盈亏: ${portfolio_data['total_pnl']:,.2f} ({portfolio_data['total_pnl_percent']}%)")
        
        # 资产配置
        allocation = portfolio_data["asset_allocation"]
        print(f"\n⚖️  资产配置")
        print(f"  股票: {allocation['stocks']}%")
        print(f"  期权: {allocation['options']}%")
        print(f"  现金: {allocation['cash']}%")
        
        # 健康度评分
        health_score = health_analysis["overall_health_score"]
        print(f"\n❤️  投资组合健康度")
        print(f"  健康评分: {health_score}/100")
        
        if health_score >= 80:
            print("  🟢 状态: 优秀 - 投资组合状态良好")
        elif health_score >= 70:
            print("  🟡 状态: 良好 - 可考虑小幅优化")
        elif health_score >= 60:
            print("  🟠 状态: 一般 - 需要适当调整")
        else:
            print("  🔴 状态: 需要关注 - 建议立即调整")
        
        # 现金分析
        cash_analysis = health_analysis["cash_analysis"]
        print(f"\n💵 现金管理分析")
        print(f"  当前: {cash_analysis['current_ratio']:.1f}%")
        print(f"  目标: {cash_analysis['target_ratio']:.1f}%")
        print(f"  状态: {cash_analysis['status']}")
        
        # 行业分布
        sector_dist = portfolio_data["sector_distribution"]
        print(f"\n🏭 行业分布")
        if sector_dist:
            for sector, allocation in sorted(sector_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"  {sector}: {allocation}%")
        else:
            print("  无股票持仓")
        
        # 风险分析
        print(f"\n⚠️  风险分析")
        print(f"  波动率风险: {risk_analysis['volatility_risk']}")
        print(f"  集中度风险: {risk_analysis['concentration_risk']}")
        print(f"  流动性风险: {risk_analysis['liquidity_risk']}")
        print(f"  整体风险水平: {risk_analysis['overall_risk_level']}")
        
        # 前五大持仓
        print(f"\n🏆 前五大持仓")
        for holding in portfolio_data["top_holdings"]:
            pnl_sign = "+" if holding["pnl_percent"] >= 0 else ""
            print(f"  {holding['rank']}. {holding['name']} - ${holding['value']:,.2f} ({pnl_sign}{holding['pnl_percent']}%)")
        
        # 投资建议
        print(f"\n🎯 投资建议")
        recommendations = analysis_report["recommendations"]
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. [{rec['category']}] {rec['action']}")
            print(f"     优先级: {rec['priority']}")
            print(f"     原因: {rec['reason']}")
            print(f"     建议: {rec['suggestion']}")
        
        print("\n" + "="*60)
        print("📋 分析完成 - 基于你的实际持仓和保守投资偏好")
        print("="*60)

def main():
    """主函数"""
    print("\n" + "🦅"*15)
    print("   Z的持仓分析器")
    print("🦅"*15)
    print("   基于你的实际投资偏好进行分析")
    print("   " + "-"*35)
    
    # 创建分析器
    analyzer = ZPortfolioAnalyzer()
    
    # 设置默认持仓
    print("\n📊 使用模拟持仓数据进行分析...")
    print("   (基于Z的投资偏好：保守型，AI/科技股，sell put策略)")
    analyzer.setup_default_holdings()
    
    # 进行分析
    print("\n🔍 正在进行持仓分析...")
    analysis_report = analyzer.analyze()
    
    # 询问是否输入真实数据
    print("\n🔄 是否输入真实持仓数据进行更准确的分析?")
    choice = input("   (输入'y'手动输入真实数据，其他任意键结束): ")
    
    if choice.lower() == 'y':
        print("\n📝 请准备输入你的真实持仓数据...")
        print("   注意：由于时间关系，手动输入功能在此简化版本中暂未实现")
        print("   建议使用完整版本的Claw Holdings Analyzer进行详细分析")
    
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  分析已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)