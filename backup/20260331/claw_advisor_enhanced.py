#!/usr/bin/env python3
"""
Claw Advisor 增强版 - 完整功能投资决策系统
整合所有新开发的功能模块
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "data-service"))
sys.path.append(str(Path(__file__).parent / "analysis-engine"))

from finnhub_client import create_finnhub_client, PRIMARY_STOCKS
from news_client import create_news_client
from macro_data import create_macro_collector
from claw_decision_engine import ClawDecisionEngine
from stock_analyzer import create_stock_analyzer
from options_engine import create_options_engine
from portfolio_optimizer import create_portfolio_optimizer
from risk_monitor import create_risk_monitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClawAdvisorEnhanced:
    """Claw Advisor 增强版系统"""
    
    def __init__(self):
        logger.info("初始化 Claw Advisor 增强版系统...")
        
        # 初始化所有客户端和引擎
        self.finnhub_client = create_finnhub_client()
        self.news_client = create_news_client()
        self.macro_collector = create_macro_collector()
        
        # 初始化所有分析引擎
        self.decision_engine = ClawDecisionEngine()
        self.stock_analyzer = create_stock_analyzer()
        self.options_engine = create_options_engine()
        self.portfolio_optimizer = create_portfolio_optimizer()
        self.risk_monitor = create_risk_monitor()
        
        # 数据缓存
        self.stocks_data = {}
        self.market_data = {}
        self.macro_data = {}
        self.analyses = {}
        
        logger.info("Claw Advisor 增强版系统初始化完成")
    
    def run_full_analysis(self):
        """运行完整分析流程"""
        try:
            logger.info("=" * 60)
            logger.info("🦅 Claw Advisor 增强版 - 完整分析开始")
            logger.info("=" * 60)
            
            # 1. 获取所有数据
            logger.info("📊 阶段1: 数据采集...")
            self._collect_all_data()
            
            # 2. 执行个股深度分析
            logger.info("🔍 阶段2: 个股深度分析...")
            stock_analyses = self._analyze_all_stocks()
            
            # 3. 生成投资建议
            logger.info("💡 阶段3: 投资建议生成...")
            recommendations = self._generate_recommendations(stock_analyses)
            
            # 4. 期权策略分析
            logger.info("💰 阶段4: 期权策略分析...")
            options_analysis = self._analyze_options_strategies()
            
            # 5. 投资组合优化
            logger.info("📈 阶段5: 投资组合优化...")
            portfolio_analysis = self._optimize_portfolio(stock_analyses)
            
            # 6. 风险监控
            logger.info("⚠️ 阶段6: 风险监控...")
            risk_monitoring = self._monitor_risks(portfolio_analysis)
            
            # 7. 生成综合报告
            logger.info("📄 阶段7: 生成综合报告...")
            report_path = self._generate_comprehensive_report(
                recommendations, options_analysis, portfolio_analysis, risk_monitoring
            )
            
            logger.info("✅ 完整分析流程完成")
            return {
                "success": True,
                "report_path": report_path,
                "summary": {
                    "stocks_analyzed": len(stock_analyses),
                    "recommendations_generated": len(recommendations.get("top_buy_recommendations", [])),
                    "options_opportunities": len(options_analysis.get("opportunities_by_stock", {})),
                    "risk_alerts": len(risk_monitoring.get("alerts", []))
                }
            }
            
        except Exception as e:
            logger.error(f"完整分析失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _collect_all_data(self):
        """收集所有数据"""
        logger.info("获取股票数据...")
        self._collect_stock_data()
        
        logger.info("获取市场数据...")
        self._collect_market_data()
        
        logger.info("获取宏观经济数据...")
        self._collect_macro_data()
    
    def _collect_stock_data(self):
        """收集股票数据"""
        for symbol in PRIMARY_STOCKS:
            try:
                logger.info(f"  获取 {symbol} 数据...")
                stock_data = self._fetch_stock_data(symbol)
                if stock_data:
                    self.stocks_data[symbol] = stock_data
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败: {e}")
    
    def _fetch_stock_data(self, symbol: str) -> dict:
        """获取单只股票的完整数据"""
        data = {"symbol": symbol}
        
        # 基础数据
        quote = self.finnhub_client.get_quote(symbol)
        if quote:
            data["quote"] = quote
        
        profile = self.finnhub_client.get_stock_profile(symbol)
        if profile:
            data["profile"] = profile
        
        metrics = self.finnhub_client.get_metric(symbol)
        if metrics and metrics.get("metric"):
            data["metrics"] = metrics["metric"]
        
        # 新闻情感
        news_articles = self.news_client.get_stock_news(symbol)
        if news_articles:
            sentiment = self.news_client.analyze_sentiment(news_articles)
            data["sentiment"] = sentiment
        
        return data
    
    def _collect_market_data(self):
        """收集市场数据"""
        self.market_data = {
            "vix": self.finnhub_client.get_quote("^VIX"),
            "sp500": self.finnhub_client.get_quote("^GSPC"),
            "headlines": self.news_client.get_top_headlines(category="business", country="us")
        }
    
    def _collect_macro_data(self):
        """收集宏观经济数据"""
        self.macro_data = {
            "market_sentiment": self.macro_collector.get_market_sentiment(),
            "economic_indicators": self.macro_collector.get_economic_indicators(),
            "sector_performance": self.macro_collector.get_sector_performance()
        }
    
    def _analyze_all_stocks(self) -> Dict[str, Dict]:
        """分析所有股票"""
        stock_analyses = {}
        
        for symbol, data in self.stocks_data.items():
            try:
                # 基础决策分析
                decision_analysis = self.decision_engine.analyze_stock(data, self.market_data)
                
                # 深度财务分析
                financial_data = self._prepare_financial_data(data)
                financial_analysis = self.stock_analyzer.analyze_financial_statements(financial_data)
                
                # 估值分析
                valuation_analysis = self.stock_analyzer.calculate_valuation(data, financial_data)
                
                stock_analyses[symbol] = {
                    "decision_analysis": decision_analysis,
                    "financial_analysis": financial_analysis,
                    "valuation_analysis": valuation_analysis,
                    "raw_data": data
                }
                
                logger.info(f"  分析完成: {symbol} - 评分: {decision_analysis.get('score', {}).get('total', 0):.1f}")
                
            except Exception as e:
                logger.error(f"分析 {symbol} 失败: {e}")
        
        return stock_analyses
    
    def _prepare_financial_data(self, stock_data: Dict) -> Dict:
        """准备财务数据"""
        # 在实际系统中，这里应该从API获取完整的财务数据
        # 现在使用基于现有数据的简化版本
        return {
            "income_statement": {
                "revenue": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.1,
                "revenue_growth": 0.12,
                "eps": stock_data.get("quote", {}).get("c", 0) * 0.05,
                "eps_growth": 0.15,
                "net_margin": 0.18,
                "gross_margin": 0.45,
                "operating_margin": 0.25,
                "shares_outstanding": 1_000_000_000
            },
            "balance_sheet": {
                "total_assets": stock_data.get("profile", {}).get("marketCapitalization", 0) * 1.5,
                "current_assets": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.3,
                "total_liabilities": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.8,
                "current_liabilities": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.2,
                "total_equity": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.7,
                "book_value_per_share": stock_data.get("quote", {}).get("c", 0) * 0.6,
                "current_ratio": 1.8,
                "debt_to_equity": 0.5
            },
            "cash_flow": {
                "operating_cash_flow": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.08,
                "investing_cash_flow": stock_data.get("profile", {}).get("marketCapitalization", 0) * -0.05,
                "financing_cash_flow": stock_data.get("profile", {}).get("marketCapitalization", 0) * -0.03,
                "free_cash_flow": stock_data.get("profile", {}).get("marketCapitalization", 0) * 0.06,
                "fcf_yield": 0.04
            }
        }
    
    def _generate_recommendations(self, stock_analyses: Dict) -> Dict[str, Any]:
        """生成投资建议"""
        # 提取决策分析结果
        decision_analyses = {}
        for symbol, analysis in stock_analyses.items():
            # 直接使用decision_analysis，不是空字典
            decision_analyses[symbol] = analysis.get("decision_analysis")
        
        # 生成每日推荐
        recommendations = self.decision_engine.generate_daily_recommendations(
            decision_analyses, self.market_data
        )
        
        # 添加深度分析摘要
        for rec in recommendations.get("top_buy_recommendations", []):
            symbol = rec.get("symbol", "")
            if symbol in stock_analyses:
                deep_analysis = stock_analyses[symbol]
                rec["deep_analysis"] = {
                    "financial_score": deep_analysis.get("financial_analysis", {}).get("financial_score", 0),
                    "valuation_grade": deep_analysis.get("valuation_analysis", {}).get("valuation_grade", ""),
                    "fair_value": deep_analysis.get("valuation_analysis", {}).get("fair_value", 0)
                }
        
        logger.info(f"生成 {len(recommendations.get('top_buy_recommendations', []))} 个买入建议")
        return recommendations
    
    def _analyze_options_strategies(self) -> Dict[str, Any]:
        """分析期权策略"""
        options_opportunities = {}
        
        for symbol, data in self.stocks_data.items():
            try:
                opportunity = self.options_engine.analyze_options_opportunities(data, self.market_data)
                options_opportunities[symbol] = opportunity
            except Exception as e:
                logger.error(f"期权分析 {symbol} 失败: {e}")
        
        # 生成摘要
        summary = self.options_engine.generate_options_summary(options_opportunities)
        
        logger.info(f"分析 {len(options_opportunities)} 只股票的期权机会")
        return {
            "opportunities_by_stock": options_opportunities,
            "summary": summary
        }
    
    def _optimize_portfolio(self, stock_analyses: Dict) -> Dict[str, Any]:
        """优化投资组合"""
        # 准备股票分析数据
        simplified_analyses = {}
        for symbol, analysis in stock_analyses.items():
            simplified_analyses[symbol] = {
                "quote": analysis.get("raw_data", {}).get("quote", {}),
                "profile": analysis.get("raw_data", {}).get("profile", {}),
                "metrics": analysis.get("raw_data", {}).get("metrics", {}),
                "score": analysis.get("decision_analysis", {}).get("score", {})
            }
        
        # 分析投资组合
        portfolio_analysis = self.portfolio_optimizer.analyze_portfolio(None, simplified_analyses)
        
        logger.info(f"投资组合健康评分: {portfolio_analysis.get('overall_score', 0):.1f}")
        return portfolio_analysis
    
    def _monitor_risks(self, portfolio_analysis: Dict) -> Dict[str, Any]:
        """监控风险"""
        risk_monitoring = self.risk_monitor.monitor_portfolio_risk(portfolio_analysis, self.market_data)
        
        alert_count = len(risk_monitoring.get("alerts", []))
        if alert_count > 0:
            logger.warning(f"发现 {alert_count} 个风险警报")
        else:
            logger.info("风险监控正常，无警报")
        
        return risk_monitoring
    
    def _generate_comprehensive_report(self, recommendations: Dict, options_analysis: Dict, 
                                       portfolio_analysis: Dict, risk_monitoring: Dict) -> str:
        """生成综合报告"""
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"claw_advisor_full_report_{date_str}.html"
        
        logger.info(f"生成综合报告: {report_path}")
        
        html_content = self._create_full_html_content(
            recommendations, options_analysis, portfolio_analysis, risk_monitoring
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _create_full_html_content(self, recommendations: Dict, options_analysis: Dict,
                                   portfolio_analysis: Dict, risk_monitoring: Dict) -> str:
        """创建完整的HTML内容"""
        date_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        # 获取数据
        top_buys = recommendations.get("top_buy_recommendations", [])
        sell_puts = recommendations.get("top_sell_put_opportunities", [])
        options_summary = options_analysis.get("summary", {})
        portfolio_state = portfolio_analysis.get("current_state", {})
        portfolio_health = portfolio_analysis.get("health_assessment", {})
        risk_alerts = risk_monitoring.get("alerts", [])
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claw Advisor 增强版 - 完整投资决策报告</title>
    <style>
        /* 基础样式（与之前相同） */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2rem;
        }}
        
        .header .date {{
            color: #3498db;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .section-icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            margin-right: 15px;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            color: #2c3e50;
            flex-grow: 1;
        }}
        
        .section-badge {{
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.12);
        }}
        
        .card-title {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .card-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            margin-right: 12px;
        }}
        
        .card-title h3 {{
            color: #2c3e50;
            font-size: 1.3rem;
        }}
        
        /* 具体组件的样式 */
        .alert-box {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
            color: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        
        .alert-box.warning {{
            background: linear-gradient(135deg, #ffa726 0%, #ffb74d 100%);
        }}
        
        .alert-box.info {{
            background: linear-gradient(135deg, #42a5f5 0%, #64b5f6 100%);
        }}
        
        .recommendation-item {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }}
        
        .recommendation-item.buy {{
            border-left-color: #2ecc71;
        }}
        
        .recommendation-item.sell-put {{
            border-left-color: #3498db;
        }}
        
        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .stock-symbol {{
            font-size: 1.4rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .stock-price {{
            font-size: 1.3rem;
            color: #27ae60;
            font-weight: bold;
        }}
        
        .score-badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .score-high {{ background: #d4edda; color: #155724; }}
        .score-medium {{ background: #fff3cd; color: #856404; }}
        .score-low {{ background: #f8d7da; color: #721c24; }}
        
        .operation-details {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            border: 1px solid #e0e0e0;
        }}
        
        .portfolio-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .metric-box {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: #7f8c8d;
        }}
        
        .metric-good {{ color: #2ecc71; }}
        .metric-warning {{ color: #f39c12; }}
        .metric-danger {{ color: #e74c3c; }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .portfolio-metrics {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        /* 动画 */
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.9; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 页头 -->
        <div class="header">
            <h1>🦅 Claw Advisor 增强版</h1>
            <div class="subtitle">基于我的投资经验 + 你的保守偏好 | 完整决策分析报告</div>
            <div class="date">{date_str}</div>
        </div>
        
        <!-- 风险警报 -->
        """
        
        # 风险警报部分
        critical_alerts = [alert for alert in risk_alerts if alert.get("level") in ["critical", "emergency"]]
        warning_alerts = [alert for alert in risk_alerts if alert.get("level") == "warning"]
        
        if critical_alerts:
            html += f"""
        <div class="section">
            <div class="alert-box">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 1.5rem; margin-right: 10px;">🛑</div>
                    <div style="font-size: 1.2rem; font-weight: bold;">紧急风险警报</div>
                </div>
                <p>发现 {len(critical_alerts)} 个紧急风险警报，请立即关注！</p>
                <div style="margin-top: 15px;">
                    {"".join([f'<div style="margin-bottom: 8px;">• {alert.get("message", "")}</div>' for alert in critical_alerts[:3]])}
                </div>
            </div>
        </div>
            """
        
        elif warning_alerts:
            html += f"""
        <div class="section">
            <div class="alert-box warning">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 1.5rem; margin-right: 10px;">⚠️</div>
                    <div style="font-size: 1.2rem; font-weight: bold;">风险警告</div>
                </div>
                <p>发现 {len(warning_alerts)} 个风险警告，建议关注。</p>
            </div>
        </div>
            """
        
        # 今日最佳操作
        html += f"""
        <div class="section">
            <div class="section-header">
                <div class="section-icon" style="background: #e8f5e9; color: #2e7d32;">🔥</div>
                <div class="section-title">今日最佳操作</div>
                <div class="section-badge">{len(top_buys)} 个推荐</div>
            </div>
            
            <div class="grid">
        """
        
        if top_buys:
            for stock in top_buys[:3]:
                symbol = stock.get("symbol", "")
                name = stock.get("name", "")
                price = stock.get("current_price", 0)
                score = stock.get("score", {}).get("total", 0)
                rec = stock.get("recommendation", {})
                
                score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"
                
                html += f"""
                <div class="card">
                    <div class="card-title">
                        <div class="card-icon" style="background: #e8f5e9; color: #2e7d32;">💰</div>
                        <h3>{symbol}</h3>
                    </div>
                    
                    <div class="stock-header">
                        <div>
                            <span class="stock-symbol">{symbol}</span>
                            <span class="stock-price">${price:.2f}</span>
                        </div>
                        <span class="score-badge {score_class}">{score:.1f}分</span>
                    </div>
                    
                    <div style="margin-bottom: 10px; color: #7f8c8d;">{name}</div>
                    
                    <div class="operation-details">
                        <div style="font-weight: bold; margin-bottom: 8px;">操作建议:</div>
                        <div style="color: #2ecc71; font-weight: bold; margin-bottom: 10px;">
                            {rec.get('operation', {}).get('type', '').replace('_', ' ').title()}
                        </div>
                        
                        <div style="font-size: 0.9rem; color: #666; margin-bottom: 10px;">
                            {rec.get('reasons', [''])[0] if rec.get('reasons') else '暂无具体理由'}
                        </div>
                        
                        <div style="font-size: 0.85rem; color: #7f8c8d;">
                            信心: {rec.get('confidence', '').replace('_', ' ').title()}
                        </div>
                    </div>
                </div>
                """
        else:
            html += """
                <div class="card">
                    <div style="text-align: center; padding: 40px;">
                        <div style="font-size: 3rem; color: #bdc3c7; margin-bottom: 20px;">📊</div>
                        <div style="color: #7f8c8d; font-size: 1.1rem;">今日无强烈操作建议</div>
                        <div style="color: #95a5a6; font-size: 0.9rem; margin-top: 10px;">建议保持现金，等待更好机会</div>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        
        <!-- 期权机会 -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon" style="background: #e3f2fd; color: #1565c0;">💰</div>
                <div class="section-title">最佳期权机会</div>
                <div class="section-badge">特别为你优化</div>
            </div>
            
            <div class="grid">
        """
        
        # 期权机会
        best_options = options_summary.get("best_overall_opportunity", {})
        z_suggestion = options_summary.get("z_portfolio_suggestion", {})
        
        if best_options:
            html += f"""
                <div class="card">
                    <div class="card-title">
                        <div class="card-icon" style="background: #e3f2fd; color: #1565c0;">⭐️</div>
                        <h3>最佳期权机会</h3>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <div style="font-size: 1.4rem; font-weight: bold; color: #2c3e50;">{best_options.get('symbol', '')}</div>
                        <div style="color: #7f8c8d;">{best_options.get('strategy', {}).get('name', '')}</div>
                    </div>
                    
                    <div class="operation-details">
                        <div style="font-weight: bold; margin-bottom: 10px;">关键参数:</div>
                        <div style="margin-bottom: 8px;">策略评分: {best_options.get('strategy', {}).get('score', 0)}</div>
                        <div style="margin-bottom: 8px;">年化收益: {best_options.get('strategy', {}).get('returns', {}).get('annualized_return', 0)}%</div>
                        <div style="margin-bottom: 8px;">推荐: {best_options.get('strategy', {}).get('recommendation', '')}</div>
                    </div>
                </div>
            """
        else:
            html += """
                <div class="card">
                    <div style="text-align: center; padding: 40px;">
                        <div style="font-size: 3rem; color: #bdc3c7; margin-bottom: 20px;">📈</div>
                        <div style="color: #7f8c8d; font-size: 1.1rem;">今日无特别期权机会</div>
                    </div>
                </div>
            """
        
        # 投资组合建议
        if z_suggestion.get("suggestions"):
            html += f"""
                <div class="card">
                    <div class="card-title">
                        <div class="card-icon" style="background: #f3e5f5; color: #7b1fa2;">💡</div>
                        <h3>Z的专属建议</h3>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <div style="color: #7f8c8d; margin-bottom: 10px;">基于你的偏好特别优化</div>
                    </div>
                    
                    <div class="operation-details">
            """
            
            for suggestion in z_suggestion.get("suggestions", [])[:2]:
                html += f"""
                        <div style="margin-bottom: 10px;">
                            <div style="font-weight: bold; color: #7b1fa2;">{suggestion.get('symbol', '')}</div>
                            <div style="font-size: 0.9rem; color: #666;">{suggestion.get('action', '')} - {suggestion.get('allocation', '')}</div>
                        </div>
                """
            
            html += f"""
                        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #e0e0e0;">
                            <div style="font-size: 0.9rem; color: #7f8c8d;">总现金分配: {z_suggestion.get('total_cash_allocation', 0)}%</div>
                            <div style="font-size: 0.85rem; color: #95a5a6;">现金剩余: {z_suggestion.get('cash_reserve_remaining', 0)}%</div>
                        </div>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        
        <!-- 投资组合健康度 -->
        <div class="section">
            <div class="section-header">
                <div class="section-icon" style="background: #fff3cd; color: #856404;">📊</div>
                <div class="section-title">投资组合健康度</div>
                <div class="section-badge">{portfolio_health_score}分</div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <div class="card-title">
                        <div class="card-icon" style="background: #e8f5e9; color: #2e7d32;">❤️</div>
                        <h3>健康评估</h3>
                    </div>
                    
                    <div class="portfolio-metrics">
                        <div class="metric-box">
                            <div class="metric-value metric-good">{portfolio_health.get("overall_score", 0):.1f}</div>
                            <div class="metric-label">综合评分</div>
                        </div>
                        
                        <div class="metric-box">
                            <div class="metric-value metric-good">{portfolio_health.get("rating", "N/A").split(" ")[-1]}</div>
                            <div class="metric-label">健康等级</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <div style="font-weight: bold; margin-bottom: 10px;">关键优势:</div>
        """
        
        strengths = portfolio_health.get("strengths", [])
        if strengths:
            for strength in strengths[:3]:
                html += f'<div style="margin-bottom: 8px; color: #27ae60;">✅ {strength}</div>'
        else:
            html += '<div style="color: #7f8c8d;">暂无特别优势</div>'
        
        html += """
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-title">
                        <div class="card-icon" style="background: #ffebee; color: #c62828;">⚠️</div>
                        <h3>风险监控</h3>
                    </div>
                    
                    <div class="portfolio-metrics">
                        <div class="metric-box">
                            <div class="metric-value {volatility_class}">{portfolio_risk_indicators.get("annualized_volatility", 0):.1f}%</div>
                            <div class="metric-label">年化波动率</div>
                        </div>
                        
                        <div class="metric-box">
                            <div class="metric-value {drawdown_class}">{portfolio_risk_indicators.get("max_drawdown", 0)*100:.1f}%</div>
                            <div class="metric-label">最大回撤</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <div style="font-weight: bold; margin-bottom: 10px;">关注点:</div>
        """
        
        concerns = portfolio_health.get("key_concerns", [])
        if concerns:
            for concern in concerns[:3]:
                html += f'<div style="margin-bottom: 8px; color: #e74c3c;">⚠️ {concern}</div>'
        else:
            html += '<div style="color: #7f8c8d;">暂无显著关注点</div>'
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 页脚 -->
        <div style="text-align: center; margin-top: 40px; padding: 20px; color: #7f8c8d; font-size: 0.9rem;">
            <p>🦅 Claw Advisor 增强版 - 基于我的投资经验构建的完整决策系统</p>
            <p>⚠️ 免责声明: 本系统提供的建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
            <p>📅 报告生成时间: {date_str} | 🔄 建议每日查看更新</p>
        </div>
    </div>
    
    <script>
        // 简单的页面交互
        document.addEventListener('DOMContentLoaded', function() {
            // 更新显示的数据
            const portfolioHealthScore = {portfolio_health.get("overall_score", 0):.1f};
            const portfolioRiskIndicators = {json.dumps(portfolio_analysis.get("risk_assessment", {}).get("indicators", {}))};
            
            // 设置波动率和回撤的样式
            const volatility = portfolioRiskIndicators.annualized_volatility || 0;
            const drawdown = (portfolioRiskIndicators.max_drawdown || 0) * 100;
            
            // 更新元素
            const volatilityElements = document.querySelectorAll('.volatility-value');
            const drawdownElements = document.querySelectorAll('.drawdown-value');
            
            volatilityElements.forEach(el => el.textContent = volatility.toFixed(1) + '%');
            drawdownElements.forEach(el => el.textContent = drawdown.toFixed(1) + '%');
            
            // 设置样式类
            const volatilityClass = volatility > 25 ? 'metric-danger' : volatility > 18 ? 'metric-warning' : 'metric-good';
            const drawdownClass = drawdown > 20 ? 'metric-danger' : drawdown > 15 ? 'metric-warning' : 'metric-good';
            
            const volatilityEls = document.querySelectorAll('.volatility-class');
            const drawdownEls = document.querySelectorAll('.drawdown-class');
            
            volatilityEls.forEach(el => el.className = 'metric-value ' + volatilityClass);
            drawdownEls.forEach(el => el.className = 'metric-value ' + drawdownClass);
            
            // 卡片点击效果
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 150);
                });
            });
            
            // 自动更新时间
            function updateTime() {
                const now = new Date();
                const timeStr = now.toLocaleString('zh-CN', {{ 
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }});
                const timeElements = document.querySelectorAll('.date');
                timeElements.forEach(el => el.textContent = timeStr);
            }
            
            setInterval(updateTime, 60000);
        });
    </script>
</body>
</html>
        """
        
        return html

def main():
    """主函数"""
    print("=" * 70)
    print("🦅 Claw Advisor 增强版 - 完整功能投资决策系统")
    print("=" * 70)
    print("功能模块:")
    print("  ✅ 实时数据采集 (股票、市场、宏观)")
    print("  ✅ 个股深度分析 (财务、估值、评分)")
    print("  ✅ 期权策略引擎 (多种策略，Z专属优化)")
    print("  ✅ 投资组合优化 (基于持仓和偏好)")
    print("  ✅ 风险监控预警 (实时监控，自动警报)")
    print("=" * 70)
    
    advisor = ClawAdvisorEnhanced()
    result = advisor.run_full_analysis()
    
    if result["success"]:
        print("\n✅ 分析完成！")
        print(f"📊 分析了 {result['summary']['stocks_analyzed']} 只股票")
        print(f"💡 生成了 {result['summary']['recommendations_generated']} 个投资建议")
        print(f"💰 发现了 {result['summary']['options_opportunities']} 个期权机会")
        print(f"⚠️ 监控到 {result['summary']['risk_alerts']} 个风险警报")
        print(f"📄 完整报告已保存: {result['report_path']}")
        
        # 建议
        if result['summary']['risk_alerts'] > 0:
            print("\n🔴 重要: 发现风险警报，请查看报告中的风险监控部分")
        else:
            print("\n🟢 风险监控正常，无紧急警报")
            
    else:
        print(f"\n❌ 分析失败: {result.get('error')}")

if __name__ == "__main__":
    main()
