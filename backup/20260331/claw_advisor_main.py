#!/usr/bin/env python3
"""
Claw Advisor 主程序 - 完整的投资决策系统
整合：数据采集 + 决策引擎 + 界面展示
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
from claw_decision_engine import ClawDecisionEngine

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ClawAdvisor:
    """Claw Advisor 系统主类"""
    
    def __init__(self):
        logger.info("初始化 Claw Advisor 系统...")
        
        # 初始化客户端
        self.finnhub_client = create_finnhub_client()
        self.news_client = create_news_client()
        self.decision_engine = ClawDecisionEngine()
        
        # 缓存数据
        self.stocks_data = {}
        self.market_data = {}
        self.recommendations = None
        
        logger.info("Claw Advisor 系统初始化完成")
    
    def fetch_all_data(self):
        """获取所有必要数据"""
        logger.info("开始获取股票数据...")
        
        # 获取主要股票数据
        for symbol in PRIMARY_STOCKS:
            logger.info(f"获取 {symbol} 数据...")
            try:
                stock_data = self._fetch_stock_data(symbol)
                if stock_data:
                    self.stocks_data[symbol] = stock_data
                    logger.info(f"  {symbol}: 价格 ${stock_data.get('quote', {}).get('c', 0):.2f}")
            except Exception as e:
                logger.error(f"获取 {symbol} 数据失败: {e}")
        
        # 获取市场数据
        logger.info("获取市场数据...")
        self.market_data = self._fetch_market_data()
        
        logger.info(f"数据获取完成，共获取 {len(self.stocks_data)} 只股票数据")
    
    def _fetch_stock_data(self, symbol: str) -> dict:
        """获取单只股票的完整数据"""
        data = {"symbol": symbol}
        
        # 1. 实时报价
        quote = self.finnhub_client.get_quote(symbol)
        if quote:
            data["quote"] = quote
        
        # 2. 公司信息
        profile = self.finnhub_client.get_stock_profile(symbol)
        if profile:
            data["profile"] = profile
        
        # 3. 财务指标
        metrics = self.finnhub_client.get_metric(symbol)
        if metrics and metrics.get("metric"):
            data["metrics"] = metrics["metric"]
        
        # 4. 分析师推荐
        recommendations = self.finnhub_client.get_recommendation_trends(symbol)
        if recommendations:
            data["recommendations"] = recommendations
        
        # 5. 新闻情感
        news_articles = self.news_client.get_stock_news(symbol)
        if news_articles:
            sentiment = self.news_client.analyze_sentiment(news_articles)
            data["sentiment"] = sentiment
            data["recent_news"] = news_articles[:3]  # 只保留最近3条
        
        return data
    
    def _fetch_market_data(self) -> dict:
        """获取市场整体数据"""
        market_data = {}
        
        # 获取标普500作为市场基准
        sp500_quote = self.finnhub_client.get_quote("^GSPC")
        if sp500_quote:
            market_data["sp500"] = sp500_quote
        
        # 获取恐慌指数VIX
        vix_quote = self.finnhub_client.get_quote("^VIX")
        if vix_quote:
            market_data["vix"] = vix_quote
        
        # 获取市场新闻
        market_news = self.news_client.get_top_headlines(category="business")
        if market_news:
            market_data["headlines"] = market_news[:5]  # 只保留5条头条
        
        return market_data
    
    def generate_recommendations(self):
        """生成投资建议"""
        logger.info("生成投资建议...")
        
        if not self.stocks_data:
            logger.warning("没有股票数据，无法生成建议")
            return
        
        self.recommendations = self.decision_engine.generate_daily_recommendations(
            self.stocks_data, self.market_data
        )
        
        logger.info(f"生成了 {len(self.recommendations.get('top_buy_recommendations', []))} 个买入建议")
        logger.info(f"生成了 {len(self.recommendations.get('top_sell_put_opportunities', []))} 个sell put机会")
    
    def generate_html_report(self, output_path: str = None):
        """生成HTML报告"""
        if not self.recommendations:
            logger.warning("没有推荐数据，无法生成报告")
            return
        
        if not output_path:
            output_path = f"claw_advisor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        logger.info(f"生成HTML报告: {output_path}")
        
        html_content = self._create_html_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _create_html_content(self) -> str:
        """创建HTML内容"""
        date_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        # 获取推荐数据
        top_buys = self.recommendations.get("top_buy_recommendations", [])
        sell_puts = self.recommendations.get("top_sell_put_opportunities", [])
        portfolio_advice = self.recommendations.get("portfolio_advice", [])
        risk_warnings = self.recommendations.get("risk_warnings", [])
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claw Advisor - 投资决策系统</title>
    <style>
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
            max-width: 1200px;
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
        
        .card-title h2 {{
            color: #2c3e50;
            font-size: 1.5rem;
            margin-left: 10px;
        }}
        
        .icon {{
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }}
        
        .icon.buy {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .icon.sell-put {{
            background: #e3f2fd;
            color: #1565c0;
        }}
        
        .icon.portfolio {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}
        
        .icon.risk {{
            background: #ffebee;
            color: #c62828;
        }}
        
        .recommendation-item {{
            background: #f8f9fa;
            border-radius: 10px;
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
            font-size: 1.3rem;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .stock-price {{
            font-size: 1.2rem;
            color: #27ae60;
            font-weight: bold;
        }}
        
        .score-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-left: 10px;
        }}
        
        .score-high {{
            background: #d4edda;
            color: #155724;
        }}
        
        .score-medium {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .score-low {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .operation-details {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            border: 1px solid #e0e0e0;
        }}
        
        .operation-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .type-buy {{
            background: #d4edda;
            color: #155724;
        }}
        
        .type-sell-put {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .reasons {{
            margin-top: 10px;
        }}
        
        .reason-tag {{
            display: inline-block;
            background: #e3f2fd;
            color: #1565c0;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85rem;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        
        .advice-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        
        .advice-item:before {{
            content: "💡";
            margin-right: 10px;
            font-size: 1.2rem;
        }}
        
        .warning-item {{
            background: #fff3cd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            border-left: 4px solid #ffc107;
        }}
        
        .warning-item:before {{
            content: "⚠️";
            margin-right: 10px;
            font-size: 1.2rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9rem;
        }}
        
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦅 Claw Advisor</h1>
            <div class="subtitle">基于我的投资经验 + 你的保守偏好</div>
            <div class="date">{date_str}</div>
        </div>
        
        <div class="grid">
            <!-- 今日最佳操作 -->
            <div class="card">
                <div class="card-title">
                    <div class="icon buy">🔥</div>
                    <h2>今日最佳操作</h2>
                </div>
                """
        
        # 添加买入建议
        if top_buys:
            for i, stock in enumerate(top_buys, 1):
                symbol = stock.get("symbol", "")
                name = stock.get("name", "")
                price = stock.get("current_price", 0)
                score = stock.get("score", {}).get("total", 0)
                rec = stock.get("recommendation", {})
                operation = rec.get("operation", {})
                
                # 确定分数等级
                score_class = "score-high" if score >= 80 else "score-medium" if score >= 60 else "score-low"
                
                # 确定操作类型
                op_type_class = "type-buy" if operation.get("type") == "buy_stock" else "type-sell-put"
                op_type_text = "买入正股" if operation.get("type") == "buy_stock" else "卖出看跌期权"
                
                html += f"""
                <div class="recommendation-item buy">
                    <div class="stock-header">
                        <div>
                            <span class="stock-symbol">{symbol}</span>
                            <span class="stock-price">${price:.2f}</span>
                            <span class="score-badge {score_class}">{score:.1f}分</span>
                        </div>
                    </div>
                    <div>{name}</div>
                    
                    <div class="operation-details">
                        <span class="operation-type {op_type_class}">{op_type_text}</span>
                        """
                
                if operation.get("type") == "buy_stock":
                    html += f"""
                        <div><strong>建议价格:</strong> ${operation.get('suggested_price', price):.2f}</div>
                        <div><strong>仓位建议:</strong> {operation.get('position_size', '2-5%')}</div>
                    """
                elif operation.get("type") == "sell_put":
                    html += f"""
                        <div><strong>行权价:</strong> ${operation.get('strike_price', 0):.2f}</div>
                        <div><strong>权利金预估:</strong> ${operation.get('premium_estimate', 0):.2f}</div>
                        <div><strong>年化收益:</strong> {operation.get('annualized_return', '0%')}</div>
                        <div><strong>时间:</strong> {operation.get('timeframe', '30-45天')}</div>
                    """
                
                html += f"""
                        <div class="reasons">
                            {" ".join([f'<span class="reason-tag">{reason}</span>' for reason in rec.get('reasons', [])])}
                        </div>
                    </div>
                </div>
                """
        else:
            html += """
                <div class="recommendation-item">
                    <div style="text-align: center; padding: 30px; color: #7f8c8d;">
                        📊 今日无强烈买入建议，建议保持现金观望
                    </div>
                </div>
            """
        
        html += """
            </div>
            
            <!-- 投资组合建议 -->
            <div class="card">
                <div class="card-title">
                    <div class="icon portfolio">📊</div>
                    <h2>投资组合建议</h2>
                </div>
        """
        
        # 添加投资组合建议
        if portfolio_advice:
            for advice in portfolio_advice:
                html += f"""
                <div class="advice-item">
                    {advice}
                </div>
                """
        else:
            html += """
                <div style="text-align: center; padding: 30px; color: #7f8c8d;">
                    💼 暂无特别组合调整建议
                </div>
            """
        
        html += """
            </div>
        </div>
        
        <div class="grid">
            <!-- 最佳sell put机会 -->
            <div class="card">
                <div class="card-title">
                    <div class="icon sell-put">💰</div>
                    <h2>最佳期权机会</h2>
                </div>
        """
        
        # 添加sell put机会
        if sell_puts:
            for stock in sell_puts:
                symbol = stock.get("symbol", "")
                name = stock.get("name", "")
                price = stock.get("current_price", 0)
                score = stock.get("score", {}).get("total", 0)
                rec = stock.get("recommendation", {})
                operation = rec.get("operation", {})
                
                # 检查是否是sell put建议
                if operation.get("type") == "sell_put":
                    html += f"""
                    <div class="recommendation-item sell-put">
                        <div class="stock-header">
                            <div>
                                <span class="stock-symbol">{symbol}</span>
                                <span class="stock-price">${price:.2f}</span>
                            </div>
                        </div>
                        <div>{name}</div>
                        
                        <div class="operation-details">
                            <span class="operation-type type-sell-put">卖出看跌期权</span>
                            <div><strong>当前价:</strong> ${price:.2f}</div>
                            <div><strong>建议行权价:</strong> ${operation.get('strike_price', 0):.2f}</div>
                            <div><strong>权利金预估:</strong> ${operation.get('premium_estimate', 0):.2f}</div>
                            <div><strong>年化收益:</strong> {operation.get('annualized_return', '0%')}</div>
                            <div><strong>理由:</strong> {operation.get('reason', '')}</div>
                        </div>
                    </div>
                    """
        else:
            html += """
                <div class="recommendation-item">
                    <div style="text-align: center; padding: 30px; color: #7f8c8d;">
                        📈 今日无特别期权机会，建议关注正股投资
                    </div>
                </div>
            """
        
        html += """
            </div>
            
            <!-- 风险提示 -->
            <div class="card">
                <div class="card-title">
                    <div class="icon risk">⚠️</div>
                    <h2>风险提示</h2>
                </div>
        """
        
        # 添加风险提示
        if risk_warnings:
            for warning in risk_warnings:
                html += f"""
                <div class="warning-item">
                    {warning}
                </div>
                """
        else:
            html += """
                <div style="text-align: center; padding: 30px; color: #7f8c8d;">
                    ✅ 当前市场风险可控
                </div>
            """
        
        html += """
            </div>
        </div>
        
        <div class="footer">
            <p>🦅 Claw Advisor - 基于我的投资经验构建的决策系统</p>
            <p>⚠️ 免责声明: 本系统提供的建议仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
            <p>📅 数据更新时间: {date_str} | 🔄 建议每日查看更新</p>
        </div>
    </div>
    
    <script>
        // 简单的页面交互
        document.addEventListener('DOMContentLoaded', function() {{
            // 为所有推荐项添加点击效果
            const recommendations = document.querySelectorAll('.recommendation-item');
            recommendations.forEach(item => {{
                item.addEventListener('click', function() {{
                    this.style.transform = 'scale(0.98)';
                    setTimeout(() => {{
                        this.style.transform = '';
                    }}, 150);
                }});
            }});
            
            // 自动更新时间
            function updateTime() {{
                const now = new Date();
                const timeStr = now.toLocaleString('zh-CN', {{ 
                    year: 'numeric', 
                    month: '2-digit', 
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                }});
                document.querySelector('.date').textContent = timeStr;
            }}
            
            // 每分钟更新一次时间
            setInterval(updateTime, 60000);
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def run(self):
        """运行完整流程"""
        try:
            # 1. 获取数据
            self.fetch_all_data()
            
            # 2. 生成建议
            self.generate_recommendations()
            
            # 3. 生成报告
            report_path = self.generate_html_report("claw_advisor_latest.html")
            
            if report_path:
                logger.info(f"✅ 报告已生成: {report_path}")
                return {
                    "success": True,
                    "report_path": report_path,
                    "recommendations": self.recommendations,
                    "stocks_analyzed": len(self.stocks_data)
                }
            else:
                return {"success": False, "error": "报告生成失败"}
                
        except Exception as e:
            logger.error(f"运行失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

def main():
    """主函数"""
    print("=" * 60)
    print("🦅 Claw Advisor 投资决策系统")
    print("=" * 60)
    
    advisor = ClawAdvisor()
    result = advisor.run()
    
    if result["success"]:
        print("\n✅ 运行成功！")
        print(f"📊 分析了 {result['stocks_analyzed']} 只股票")
        print(f"📄 报告已保存: {result['report_path']}")
        
        # 显示简要推荐
        recs = result.get("recommendations", {})
        if recs.get("top_buy_recommendations"):
            print("\n🔥 今日最佳操作:")
            for stock in recs["top_buy_recommendations"][:3]:
                symbol = stock.get("symbol", "")
                price = stock.get("current_price", 0)
                score = stock.get("score", {}).get("total", 0)
                action = stock.get("recommendation", {}).get("action", "")
                print(f"   {symbol}: ${price:.2f} | 评分{score:.1f} | 建议{action}")
    else:
        print(f"\n❌ 运行失败: {result.get('error')}")

if __name__ == "__main__":
    main()