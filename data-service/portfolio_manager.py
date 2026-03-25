"""
持仓管理模块 - 管理Z的实际持仓数据
支持手动输入持仓，未来集成老虎证券API
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class PortfolioManager:
    """持仓管理器"""
    
    def __init__(self, data_path: str = None):
        """初始化持仓管理器
        
        Args:
            data_path: 持仓数据文件路径，如果为None则使用默认路径
        """
        self.data_path = data_path or "/Users/nn/WorkBuddy/Claw/data-service/portfolio_data.json"
        self.portfolio_data = self._load_portfolio_data()
        
    def _load_portfolio_data(self) -> Dict:
        """加载持仓数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果文件不存在，创建默认的持仓数据
            default_data = {
                "portfolio": {
                    "metadata": {
                        "owner": "Z",
                        "broker": "老虎证券",
                        "risk_profile": "conservative",
                        "cash_reserve_target": 0.35,
                        "last_updated": datetime.now().isoformat()
                    },
                    "holdings": {
                        "stocks": [],
                        "options": [],
                        "cash": 0.0
                    },
                    "performance": {
                        "total_value": 0.0,
                        "total_cost": 0.0,
                        "total_pnl": 0.0,
                        "total_pnl_percent": 0.0
                    }
                }
            }
            self._save_portfolio_data(default_data)
            return default_data
    
    def _save_portfolio_data(self, data: Dict) -> None:
        """保存持仓数据"""
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_stock_position(self, symbol: str, quantity: float, cost_basis: float, 
                          current_price: float = None, notes: str = "") -> Dict:
        """添加股票持仓
        
        Args:
            symbol: 股票代码
            quantity: 持仓数量
            cost_basis: 成本价（美元）
            current_price: 当前价格（可选，如果提供则计算盈亏）
            notes: 备注信息
            
        Returns:
            添加的持仓信息
        """
        position = {
            "symbol": symbol,
            "quantity": quantity,
            "cost_basis": cost_basis,
            "current_price": current_price or cost_basis,  # 默认为成本价
            "purchase_date": datetime.now().isoformat(),
            "notes": notes
        }
        
        # 计算持仓价值
        position["current_value"] = position["quantity"] * position["current_price"]
        position["cost_value"] = position["quantity"] * position["cost_basis"]
        position["pnl"] = position["current_value"] - position["cost_value"]
        position["pnl_percent"] = (position["pnl"] / position["cost_value"] * 100) if position["cost_value"] > 0 else 0
        
        # 添加到持仓数据
        self.portfolio_data["portfolio"]["holdings"]["stocks"].append(position)
        
        # 更新总持仓价值
        self._update_portfolio_value()
        
        # 保存数据
        self._save_portfolio_data(self.portfolio_data)
        
        logger.info(f"添加股票持仓: {symbol} {quantity}股 @ ${cost_basis}")
        return position
    
    def add_option_position(self, underlying: str, option_type: str, strike: float, 
                           expiration: str, quantity: int, premium: float, 
                           current_price: float = None, notes: str = "") -> Dict:
        """添加期权持仓
        
        Args:
            underlying: 标的股票代码
            option_type: 期权类型 (call/put)
            strike: 行权价
            expiration: 到期日 (YYYY-MM-DD)
            quantity: 合约数量
            premium: 权利金（每股）
            current_price: 当前权利金（可选）
            notes: 备注信息
            
        Returns:
            添加的期权持仓信息
        """
        option_position = {
            "underlying": underlying,
            "option_type": option_type,
            "strike": strike,
            "expiration": expiration,
            "quantity": quantity,
            "premium": premium,
            "current_price": current_price or premium,
            "purchase_date": datetime.now().isoformat(),
            "notes": notes
        }
        
        # 计算期权价值（每份合约100股）
        option_position["current_value"] = option_position["quantity"] * 100 * option_position["current_price"]
        option_position["cost_value"] = option_position["quantity"] * 100 * option_position["premium"]
        option_position["pnl"] = option_position["current_value"] - option_position["cost_value"]
        option_position["pnl_percent"] = (option_position["pnl"] / option_position["cost_value"] * 100) if option_position["cost_value"] > 0 else 0
        
        # 添加到持仓数据
        self.portfolio_data["portfolio"]["holdings"]["options"].append(option_position)
        
        # 更新总持仓价值
        self._update_portfolio_value()
        
        # 保存数据
        self._save_portfolio_data(self.portfolio_data)
        
        logger.info(f"添加期权持仓: {underlying} {option_type.upper()} ${strike} {expiration}")
        return option_position
    
    def set_cash_position(self, cash_amount: float) -> Dict:
        """设置现金持仓
        
        Args:
            cash_amount: 现金金额（美元）
            
        Returns:
            现金持仓信息
        """
        self.portfolio_data["portfolio"]["holdings"]["cash"] = cash_amount
        
        # 更新总持仓价值
        self._update_portfolio_value()
        
        # 保存数据
        self._save_portfolio_data(self.portfolio_data)
        
        logger.info(f"设置现金持仓: ${cash_amount}")
        return {"cash": cash_amount}
    
    def _update_portfolio_value(self) -> None:
        """更新投资组合总价值"""
        holdings = self.portfolio_data["portfolio"]["holdings"]
        
        # 计算股票总价值
        stock_value = sum(pos.get("current_value", 0) for pos in holdings["stocks"])
        
        # 计算期权总价值
        option_value = sum(pos.get("current_value", 0) for pos in holdings["options"])
        
        # 现金
        cash_value = holdings.get("cash", 0)
        
        # 总价值
        total_value = stock_value + option_value + cash_value
        
        # 计算总成本
        stock_cost = sum(pos.get("cost_value", 0) for pos in holdings["stocks"])
        option_cost = sum(pos.get("cost_value", 0) for pos in holdings["options"])
        total_cost = stock_cost + option_cost
        
        # 计算总盈亏
        total_pnl = total_value - cash_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # 更新绩效数据
        self.portfolio_data["portfolio"]["performance"] = {
            "total_value": total_value,
            "stock_value": stock_value,
            "option_value": option_value,
            "cash_value": cash_value,
            "total_cost": total_cost,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent
        }
        
        # 更新最后更新时间
        self.portfolio_data["portfolio"]["metadata"]["last_updated"] = datetime.now().isoformat()
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        self._update_portfolio_value()
        
        portfolio = self.portfolio_data["portfolio"]
        performance = portfolio["performance"]
        holdings = portfolio["holdings"]
        
        # 计算资产配置
        total_value = performance["total_value"]
        if total_value > 0:
            stock_allocation = (performance["stock_value"] / total_value) * 100
            option_allocation = (performance["option_value"] / total_value) * 100
            cash_allocation = (performance["cash_value"] / total_value) * 100
        else:
            stock_allocation = option_allocation = cash_allocation = 0
        
        # 计算行业分布
        sector_distribution = self._calculate_sector_distribution()
        
        # 计算前五大持仓
        top_holdings = self._get_top_holdings()
        
        summary = {
            "metadata": portfolio["metadata"],
            "performance": performance,
            "asset_allocation": {
                "stocks": round(stock_allocation, 1),
                "options": round(option_allocation, 1),
                "cash": round(cash_allocation, 1)
            },
            "sector_distribution": sector_distribution,
            "top_holdings": top_holdings,
            "holdings_count": {
                "stocks": len(holdings["stocks"]),
                "options": len(holdings["options"])
            },
            "risk_indicators": self._calculate_risk_indicators(),
            "last_updated": portfolio["metadata"]["last_updated"]
        }
        
        return summary
    
    def _calculate_sector_distribution(self) -> Dict[str, float]:
        """计算行业分布"""
        # 在实际系统中，这里应该根据股票代码获取行业信息
        # 现在使用简化的行业分类
        holdings = self.portfolio_data["portfolio"]["holdings"]["stocks"]
        
        # 预设的行业分类（简化）
        sector_map = {
            "NVDA": "Technology",
            "GOOGL": "Communication Services", 
            "AMZN": "Consumer Cyclical",
            "TSLA": "Consumer Cyclical",
            "AAPL": "Technology",
            "MSFT": "Technology",
            "META": "Communication Services",
            "IONQ": "Technology",
            "RKLB": "Industrials",
            "ASTS": "Communication Services",
            "COIN": "Financial Services",
            "MARA": "Financial Services",
            "CMBT": "Healthcare"
        }
        
        sector_values = {}
        total_stock_value = sum(pos.get("current_value", 0) for pos in holdings)
        
        if total_stock_value > 0:
            for pos in holdings:
                symbol = pos["symbol"]
                sector = sector_map.get(symbol, "Unknown")
                value = pos.get("current_value", 0)
                
                if sector not in sector_values:
                    sector_values[sector] = 0
                sector_values[sector] += value
            
            # 转换为百分比
            for sector in sector_values:
                sector_values[sector] = round((sector_values[sector] / total_stock_value) * 100, 1)
        
        return sector_values
    
    def _get_top_holdings(self, top_n: int = 5) -> List[Dict]:
        """获取前N大持仓"""
        all_holdings = []
        
        # 股票持仓
        for pos in self.portfolio_data["portfolio"]["holdings"]["stocks"]:
            all_holdings.append({
                "type": "stock",
                "symbol": pos["symbol"],
                "value": pos.get("current_value", 0),
                "weight": 0,  # 稍后计算
                "pnl_percent": round(pos.get("pnl_percent", 0), 1)
            })
        
        # 期权持仓
        for pos in self.portfolio_data["portfolio"]["holdings"]["options"]:
            all_holdings.append({
                "type": "option",
                "symbol": f"{pos['underlying']} {pos['option_type'].upper()} ${pos['strike']}",
                "value": pos.get("current_value", 0),
                "weight": 0,  # 稍后计算
                "pnl_percent": round(pos.get("pnl_percent", 0), 1)
            })
        
        # 按价值排序
        all_holdings.sort(key=lambda x: x["value"], reverse=True)
        
        # 计算权重
        total_value = sum(h["value"] for h in all_holdings)
        if total_value > 0:
            for holding in all_holdings:
                holding["weight"] = round((holding["value"] / total_value) * 100, 1)
        
        return all_holdings[:top_n]
    
    def _calculate_risk_indicators(self) -> Dict:
        """计算风险指标"""
        # 在实际系统中，这里应该使用更复杂的风险模型
        # 现在使用简化的风险评估
        
        holdings = self.portfolio_data["portfolio"]["holdings"]["stocks"]
        total_value = sum(pos.get("current_value", 0) for pos in holdings)
        
        if total_value <= 0:
            return {
                "concentration_risk": "低",
                "volatility_estimate": "低",
                "liquidity_score": "高",
                "diversification_score": "高"
            }
        
        # 计算集中度风险
        top_holdings = self._get_top_holdings(3)
        if top_holdings:
            top3_weight = sum(h["weight"] for h in top_holdings[:3])
            if top3_weight > 60:
                concentration = "高"
            elif top3_weight > 40:
                concentration = "中"
            else:
                concentration = "低"
        else:
            concentration = "低"
        
        # 简化的波动率估计
        tech_stocks = sum(1 for pos in holdings if pos["symbol"] in ["NVDA", "AAPL", "MSFT", "IONQ"])
        if tech_stocks >= 3:
            volatility = "中高"
        elif tech_stocks >= 1:
            volatility = "中"
        else:
            volatility = "低"
        
        # 流动性评分（基于持仓数量和市值）
        holding_count = len(holdings)
        if holding_count >= 8:
            liquidity = "高"
        elif holding_count >= 5:
            liquidity = "中"
        else:
            liquidity = "低"
        
        # 分散度评分
        sectors = self._calculate_sector_distribution()
        sector_count = len(sectors)
        if sector_count >= 4:
            diversification = "高"
        elif sector_count >= 2:
            diversification = "中"
        else:
            diversification = "低"
        
        return {
            "concentration_risk": concentration,
            "volatility_estimate": volatility,
            "liquidity_score": liquidity,
            "diversification_score": diversification
        }
    
    def export_to_claw_format(self) -> Dict:
        """导出为Claw决策系统格式"""
        summary = self.get_portfolio_summary()
        
        # 构建当前状态
        current_state = {
            "cash_ratio": summary["asset_allocation"]["cash"],
            "position_count": summary["holdings_count"]["stocks"] + summary["holdings_count"]["options"],
            "sector_allocation": summary["sector_distribution"],
            "positions": []
        }
        
        # 添加股票持仓
        for pos in self.portfolio_data["portfolio"]["holdings"]["stocks"]:
            position_value = pos.get("current_value", 0)
            total_value = summary["performance"]["total_value"]
            position_ratio = (position_value / total_value * 100) if total_value > 0 else 0
            
            current_state["positions"].append({
                "symbol": pos["symbol"],
                "type": "stock",
                "quantity": pos["quantity"],
                "cost_basis": pos["cost_basis"],
                "current_price": pos["current_price"],
                "current_value": position_value,
                "position_ratio": round(position_ratio, 1),
                "pnl_percent": round(pos.get("pnl_percent", 0), 1)
            })
        
        # 添加期权持仓
        for pos in self.portfolio_data["portfolio"]["holdings"]["options"]:
            position_value = pos.get("current_value", 0)
            total_value = summary["performance"]["total_value"]
            position_ratio = (position_value / total_value * 100) if total_value > 0 else 0
            
            current_state["positions"].append({
                "symbol": f"{pos['underlying']}_{pos['option_type']}_{pos['strike']}",
                "type": "option",
                "underlying": pos["underlying"],
                "option_type": pos["option_type"],
                "strike": pos["strike"],
                "expiration": pos["expiration"],
                "quantity": pos["quantity"],
                "premium": pos["premium"],
                "current_price": pos["current_price"],
                "current_value": position_value,
                "position_ratio": round(position_ratio, 1),
                "pnl_percent": round(pos.get("pnl_percent", 0), 1)
            })
        
        # 构建健康度评估所需数据
        portfolio_data = {
            "current_state": current_state,
            "performance": summary["performance"],
            "metadata": summary["metadata"],
            "risk_indicators": summary["risk_indicators"],
            "timestamp": summary["last_updated"]
        }
        
        return portfolio_data
    
    def clear_portfolio(self) -> None:
        """清空持仓数据"""
        self.portfolio_data = {
            "portfolio": {
                "metadata": {
                    "owner": "Z",
                    "broker": "老虎证券",
                    "risk_profile": "conservative",
                    "cash_reserve_target": 0.35,
                    "last_updated": datetime.now().isoformat()
                },
                "holdings": {
                    "stocks": [],
                    "options": [],
                    "cash": 0.0
                },
                "performance": {
                    "total_value": 0.0,
                    "total_cost": 0.0,
                    "total_pnl": 0.0,
                    "total_pnl_percent": 0.0
                }
            }
        }
        self._save_portfolio_data(self.portfolio_data)
        
        logger.info("持仓数据已清空")


def create_portfolio_manager() -> PortfolioManager:
    """创建持仓管理器实例"""
    return PortfolioManager()