#!/usr/bin/env python3
"""
Claw Holdings Analyzer - 专门分析Z的实际持仓
基于PortfolioAnalyzer，生成详细的持仓分析报告
"""

import logging
import json
from datetime import datetime
import sys
import os
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 使用相对导入
from analysis_engine.portfolio_analyzer import create_portfolio_analyzer
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/nn/WorkBuddy/Claw/logs/holdings_analysis.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_default_holdings() -> None:
    """设置Z的默认持仓数据（模拟实际持仓）
    
    在实际使用中，你应该输入自己的真实持仓数据
    这里使用模拟数据展示分析功能
    """
    from data_service.portfolio_manager import PortfolioManager
    
    portfolio_manager = PortfolioManager()
    
    # 清空现有持仓（如果已有）
    portfolio_manager.clear_portfolio()
    
    # 设置现金持仓（假设有100,000美元现金）
    portfolio_manager.set_cash_position(100000.0)
    
    # 添加股票持仓（假设Z的实际持仓）
    # 基于记忆中的信息：Z长期持有AI/科技/太空正股，常做特斯拉sell put
    
    # 1. 核心科技股
    portfolio_manager.add_stock_position(
        symbol="NVDA",
        quantity=50,
        cost_basis=120.0,
        current_price=177.97,
        notes="AI算力基础设施，长期持有"
    )
    
    portfolio_manager.add_stock_position(
        symbol="GOOGL",
        quantity=30,
        cost_basis=280.0,
        current_price=304.39,
        notes="AI+搜索+云，低估的AI巨头"
    )
    
    portfolio_manager.add_stock_position(
        symbol="AMZN",
        quantity=40,
        cost_basis=180.0,
        current_price=212.36,
        notes="AWS云计算+电商，现金流稳健"
    )
    
    # 2. Z熟悉且偏好的股票
    portfolio_manager.add_stock_position(
        symbol="TSLA",
        quantity=25,
        cost_basis=350.0,
        current_price=383.64,
        notes="长期关注，常做sell put"
    )
    
    portfolio_manager.add_stock_position(
        symbol="AAPL",
        quantity=35,
        cost_basis=230.0,
        current_price=252.13,
        notes="核心持仓，定期买入"
    )
    
    portfolio_manager.add_stock_position(
        symbol="MSFT",
        quantity=30,
        cost_basis=360.0,
        current_price=386.25,
        notes="企业软件+AI，稳定增长"
    )
    
    # 3. 成长型股票（基于Z对前沿技术的兴趣）
    portfolio_manager.add_stock_position(
        symbol="IONQ",
        quantity=100,
        cost_basis=20.0,
        current_price=33.07,
        notes="量子计算，高风险高回报"
    )
    
    portfolio_manager.add_stock_position(
        symbol="RKLB",
        quantity=200,
        cost_basis=15.0,
        current_price=22.50,
        notes="太空发射，新兴领域"
    )
    
    # 4. 期权持仓（模拟Z的sell put操作）
    # 假设Z卖出特斯拉put期权
    portfolio_manager.add_option_position(
        underlying="TSLA",
        option_type="put",
        strike=350.0,
        expiration="2026-06-30",
        quantity=2,
        premium=15.0,
        current_price=10.5,
        notes="sell put策略，目标价位$350"
    )
    
    # 假设Z卖出英伟达put期权
    portfolio_manager.add_option_position(
        underlying="NVDA",
        option_type="put",
        strike=160.0,
        expiration="2026-05-31",
        quantity=3,
        premium=12.0,
        current_price=8.5,
        notes="sell put策略，目标价位$160"
    )
    
    logger.info("默认持仓数据已设置完成")
    print("✅ 模拟持仓数据已创建，基于Z的实际投资偏好：")
    print("   - AI/科技股：NVDA, GOOGL, AMZN, MSFT")
    print("   - 熟悉股票：TSLA, AAPL")
    print("   - 成长领域：IONQ（量子计算）, RKLB（太空）")
    print("   - sell put策略：TSLA和NVDA的看跌期权")
    print("   - 现金：$100,000（35%目标比例）")

def input_real_holdings() -> None:
    """输入Z的真实持仓数据"""
    from data_service.portfolio_manager import PortfolioManager
    
    portfolio_manager = PortfolioManager()
    portfolio_manager.clear_portfolio()
    
    print("\n📊 请输入你的真实持仓数据（按Enter跳过或输入'q'退出）")
    
    # 输入现金持仓
    while True:
        cash_input = input("\n💰 请输入现金持仓金额（美元）: ")
        if cash_input.lower() == 'q':
            return
        elif cash_input == '':
            cash_amount = 0
            break
        else:
            try:
                cash_amount = float(cash_input)
                if cash_amount < 0:
                    print("⚠️  现金金额不能为负数")
                else:
                    break
            except ValueError:
                print("⚠️  请输入有效的数字")
    
    portfolio_manager.set_cash_position(cash_amount)
    print(f"✅ 现金持仓: ${cash_amount:,.2f}")
    
    # 输入股票持仓
    print("\n📈 请输入股票持仓（输入完成后按Enter继续）")
    stock_count = 0
    
    while True:
        print(f"\n股票 #{stock_count + 1} (输入'q'完成输入)")
        symbol = input("  股票代码 (如 NVDA, TSLA): ").upper()
        
        if symbol == '' or symbol == 'Q':
            if stock_count == 0:
                print("⚠️  至少需要输入一只股票")
                continue
            else:
                print(f"✅ 共输入{stock_count}只股票")
                break
        
        try:
            quantity = float(input("  持仓数量: "))
            cost_basis = float(input("  成本价 ($): "))
            current_price_input = input("  当前价格 ($, 按Enter跳过): ")
            notes = input("  备注 (按Enter跳过): ")
            
            if not current_price_input:
                current_price = cost_basis
            else:
                current_price = float(current_price_input)
            
            portfolio_manager.add_stock_position(
                symbol=symbol,
                quantity=quantity,
                cost_basis=cost_basis,
                current_price=current_price,
                notes=notes
            )
            
            stock_count += 1
            print(f"✅ 已添加: {symbol}")
            
        except ValueError:
            print("⚠️  请输入有效的数字")
        except Exception as e:
            print(f"⚠️  错误: {e}")
    
    # 输入期权持仓（可选）
    print("\n📊 输入期权持仓 (可选，按Enter跳过)")
    option_input = input("是否输入期权持仓? (y/n): ")
    
    if option_input.lower() == 'y':
        option_count = 0
        
        while True:
            print(f"\n期权 #{option_count + 1} (输入'q'完成输入)")
            underlying = input("  标的股票代码: ").upper()
            
            if underlying == '' or underlying == 'Q':
                if option_count > 0:
                    print(f"✅ 共输入{option_count}个期权合约")
                break
            
            try:
                option_type = input("  期权类型 (call/put): ").lower()
                strike = float(input("  行权价 ($): "))
                expiration = input("  到期日 (YYYY-MM-DD): ")
                quantity = int(input("  合约数量: "))
                premium = float(input("  权利金 ($/股): "))
                current_price_input = input("  当前权利金 ($/股, 按Enter跳过): ")
                notes = input("  备注 (按Enter跳过): ")
                
                if not current_price_input:
                    current_price = premium
                else:
                    current_price = float(current_price_input)
                
                portfolio_manager.add_option_position(
                    underlying=underlying,
                    option_type=option_type,
                    strike=strike,
                    expiration=expiration,
                    quantity=quantity,
                    premium=premium,
                    current_price=current_price,
                    notes=notes
                )
                
                option_count += 1
                print(f"✅ 已添加: {underlying} {option_type.upper()}")
                
            except ValueError:
                print("⚠️  请输入有效的数字")
            except Exception as e:
                print(f"⚠️  错误: {e}")

def analyze_portfolio() -> None:
    """分析投资组合"""
    logger.info("开始投资组合分析...")
    
    try:
        # 创建分析器
        portfolio_analyzer = create_portfolio_analyzer()
        
        # 进行分析
        analysis_report = portfolio_analyzer.analyze_portfolio()
        
        # 保存分析结果
        save_analysis_results(analysis_report)
        
        # 显示关键信息
        display_analysis_summary(analysis_report)
        
        logger.info("投资组合分析完成")
        
    except Exception as e:
        logger.error(f"分析失败: {e}")
        print(f"❌ 分析失败: {e}")

def save_analysis_results(analysis_report: Dict[str, Any]) -> None:
    """保存分析结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/Users/nn/WorkBuddy/Claw/reports/holdings_analysis_{timestamp}.json"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 保存JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✅ 分析结果已保存: {filename}")

def display_analysis_summary(analysis_report: Dict[str, Any]) -> None:
    """显示分析摘要"""
    print("\n" + "="*60)
    print("📊 Z的投资组合分析报告")
    print("="*60)
    
    metadata = analysis_report.get("metadata", {})
    portfolio_summary = analysis_report.get("portfolio_summary", {})
    health_analysis = analysis_report.get("health_analysis", {})
    
    # 基本信息
    print(f"\n📈 基本信息")
    print(f"  分析日期: {metadata.get('analysis_date', 'N/A')}")
    print(f"  投资风格: {metadata.get('risk_profile', 'conservative')}")
    
    # 投资组合价值
    performance = portfolio_summary.get("performance", {})
    print(f"\n💰 投资组合价值")
    print(f"  总价值: ${performance.get('total_value', 0):,.2f}")
    print(f"  股票价值: ${performance.get('stock_value', 0):,.2f}")
    print(f"  期权价值: ${performance.get('option_value', 0):,.2f}")
    print(f"  现金价值: ${performance.get('cash_value', 0):,.2f}")
    
    # 资产配置
    asset_allocation = portfolio_summary.get("asset_allocation", {})
    print(f"\n⚖️  资产配置")
    print(f"  股票占比: {asset_allocation.get('stocks', 0):.1f}%")
    print(f"  期权占比: {asset_allocation.get('options', 0):.1f}%")
    print(f"  现金占比: {asset_allocation.get('cash', 0):.1f}%")
    
    # 健康度评分
    health_score = health_analysis.get("overall_health_score", 0)
    print(f"\n❤️  投资组合健康度")
    print(f"  综合健康评分: {health_score}/100")
    
    if health_score >= 80:
        print(f"  状态: 🟢 优秀 - 投资组合状态良好")
    elif health_score >= 70:
        print(f"  状态: 🟡 良好 - 可考虑小幅优化")
    elif health_score >= 60:
        print(f"  状态: 🟠 一般 - 需要适当调整")
    else:
        print(f"  状态: 🔴 需要关注 - 建议立即调整")
    
    # 现金管理分析
    cash_analysis = health_analysis.get("cash_analysis", {})
    print(f"\n💵 现金管理分析")
    print(f"  当前现金比例: {cash_analysis.get('current_ratio', 0):.1f}%")
    print(f"  目标现金比例: {cash_analysis.get('target_ratio', 0):.1f}%")
    print(f"  偏差: {cash_analysis.get('deviation', 0):.1f}%")
    
    deviation = abs(cash_analysis.get('deviation', 0))
    if deviation <= 5:
        print(f"  🟢 现金比例良好")
    elif deviation <= 10:
        print(f"  🟡 现金比例可调整")
    else:
        print(f"  🔴 现金比例需要调整")
    
    # 行业分布

    sector_analysis = health_analysis.get("sector_analysis", {})
    sector_distribution = sector_analysis.get("sector_distribution", {})
    
    print(f"\n🏭 行业分布")
    if sector_distribution:
        for sector, allocation in sorted(sector_distribution.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sector}: {allocation:.1f}%")
    else:
        print("  无股票持仓")
    
    # 风险分析
    
    risk_analysis = analysis_report.get("risk_analysis", {})
    risk_metrics = risk_analysis.get("risk_metrics", {})
    
    print(f"\n⚠️  风险指标")
    indicators = risk_metrics.get("indicators", {})
    print(f"  年化波动率: {indicators.get('annualized_volatility', 0):.1f}%")
    print(f"  95% VaR (日): {indicators.get('var_95_daily', 0):.2f}%")
    print(f"  最大回撤: {indicators.get('max_drawdown', 0):.1f}%")
    print(f"  Beta: {indicators.get('beta_to_market', 0):.2f}")
    
    # 个性化建议
    
    recommendations = analysis_report.get("personalized_recommendations", {})
    
    print(f"\n🎯 个性化投资建议")
    print(f"\n💵 现金管理建议:")
    for rec in recommendations.get("cash_management", []):
        print(f"  • {rec}")
    
    print(f"\n📊 分散度建议:")
    for rec in recommendations.get("diversification", []):
        print(f"  • {rec}")
    
    print(f"\n🛡️  风险管理建议:")
    for rec in recommendations.get("risk_management", []):
        print(f"  • {rec}")
    
    print(f"\n🎪 投资机会建议:")
    for rec in recommendations.get("opportunities", []):
        print(f"  • {rec}")
    
    print(f"\n🎯 具体行动项:")
    action_items = recommendations.get("action_items", [])
    for i, item in enumerate(action_items, 1):
        print(f"  {i}. [{item.get('priority', '低')}优先级] {item.get('action', '')}")
        print(f"     目标: {item.get('target', '')}")
        print(f"     时间: {item.get('timeline', '')}")
    
    print("\n" + "="*60)
    print("📋 分析完成 - 基于你的实际持仓和保守投资偏好")
    print("="*60)

def main() -> None:
    """主函数"""
    print("\n" + "🦅"*15)
    print("   Claw Holdings Analyzer")
    print("🦅"*15)
    print("   专门分析Z的实际投资持仓")
    print("   " + "-"*35)
    
    # 检查是否已经有持仓数据
    try:
        from data_service.portfolio_manager import PortfolioManager
        portfolio_manager = PortfolioManager()
        portfolio_summary = portfolio_manager.get_portfolio_summary()
        
        print(f"\n📊 当前持仓概况:")
        performance = portfolio_summary.get("performance", {})
        print(f"  总价值: ${performance.get('total_value', 0):,.2f}")
        print(f"  现金: ${performance.get('cash_value', 0):,.2f}")
        print(f"  股票数量: {portfolio_summary.get('holdings_count', {}).get('stocks', 0)}")
        
        choice = input(f"\n🔄 是否重新设置持仓数据? (y/n): ")
        
        if choice.lower() == 'y':
            print("\n请选择:")
            print("  1. 使用模拟持仓数据（演示用）")
            print("  2. 输入真实持仓数据")
            option = input("请选择 (1/2): ")
            
            if option == '1':
                setup_default_holdings()
            elif option == '2':
                input_real_holdings()
            else:
                print("⚠️  无效选择，使用现有持仓数据")
        else:
            print("✅ 使用现有持仓数据进行分析")
    
    except Exception as e:
        print(f"⚠️  无法读取现有持仓数据: {e}")
        print("正在使用模拟持仓数据...")
        setup_default_holdings()
    
    # 进行分析
    print("\n🔍 正在进行持仓分析...")
    analyze_portfolio()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  分析已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)