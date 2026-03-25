#!/usr/bin/env python3
"""
Claw Dashboard 测试脚本
测试API接口和前端功能
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoints():
    """测试所有API端点"""
    base_url = "http://localhost:8000"
    
    print("🧪 开始测试 Claw Dashboard API...")
    print("=" * 50)
    
    tests = [
        ("根目录", "/", None),
        ("投资组合摘要", "/api/portfolio/summary", {
            "total_value": float,
            "health_score": float,
            "cash_ratio": float
        }),
        ("持仓详情", "/api/portfolio/holdings", {
            "count": int,
            "holdings": list
        }),
        ("市场状态", "/api/market/status", {
            "sp500": float,
            "vix": float,
            "market_sentiment": str
        }),
        ("风险警报", "/api/risk/alerts", {
            "count": int,
            "alerts": list
        }),
        ("期权策略", "/api/options/strategies", {
            "count": int,
            "strategies": list
        }),
        ("完整仪表板数据", "/api/dashboard", {
            "portfolio_summary": dict,
            "market_status": dict,
            "risk_alerts": dict
        })
    ]
    
    all_passed = True
    
    for test_name, endpoint, expected_structure in tests:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if expected_structure is None:
                    print(f"✅ {test_name}: 200 OK")
                    if "endpoints" in data:
                        print(f"   可用端点: {len(data['endpoints'])}个")
                else:
                    # 检查数据结构
                    validation_passed = True
                    validation_details = []
                    
                    for key, expected_type in expected_structure.items():
                        if key not in data:
                            validation_passed = False
                            validation_details.append(f"缺少字段: {key}")
                        elif not isinstance(data[key], expected_type):
                            validation_passed = False
                            actual_type = type(data[key]).__name__
                            validation_details.append(f"{key}类型错误: 期望{expected_type.__name__}, 实际{actual_type}")
                    
                    if validation_passed:
                        print(f"✅ {test_name}: 200 OK, 数据结构正确")
                        
                        # 显示一些关键数据
                        if endpoint == "/api/portfolio/summary":
                            print(f"   总资产: ${data['total_value']:,.2f}")
                            print(f"   健康评分: {data['health_score']}/100")
                            print(f"   现金比例: {data['cash_ratio']}%")
                        elif endpoint == "/api/portfolio/holdings":
                            print(f"   持仓数量: {data['count']}")
                        elif endpoint == "/api/market/status":
                            print(f"   标普500: {data['sp500']}")
                            print(f"   VIX指数: {data['vix']}")
                            print(f"   市场情绪: {data['market_sentiment']}")
                    else:
                        print(f"❌ {test_name}: 数据结构错误")
                        for detail in validation_details:
                            print(f"   {detail}")
                        all_passed = False
            else:
                print(f"❌ {test_name}: HTTP {response.status_code}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test_name}: 连接失败 - 请确保API服务器正在运行")
            print(f"   运行命令: python claw_dashboard_api.py")
            all_passed = False
        except requests.exceptions.Timeout:
            print(f"❌ {test_name}: 请求超时")
            all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: 未知错误 - {e}")
            all_passed = False
    
    print("=" * 50)
    
    return all_passed

def test_frontend():
    """测试前端HTML文件"""
    print("\n🌐 测试前端HTML文件...")
    print("=" * 50)
    
    html_path = "/Users/nn/WorkBuddy/Claw/frontend/claw_dashboard_enhanced.html"
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 检查关键元素
        checks = [
            ("HTML结构", "<!DOCTYPE html>"),
            ("标题", "Claw投资决策中心"),
            ("主容器", '<div id="app">'),
            ("图表", '<canvas id="portfolioChart">'),
            ("导航菜单", '<nav class="flex-1 px-4 space-y-1">'),
            ("统计卡片", "总资产"),
            ("JavaScript", "<script>"),
            ("样式表", "<style>")
        ]
        
        all_passed = True
        
        for check_name, required_content in checks:
            if required_content in html_content:
                print(f"✅ {check_name}: 存在")
            else:
                print(f"❌ {check_name}: 缺失")
                all_passed = False
        
        # 统计HTML文件信息
        lines = html_content.count('\n')
        characters = len(html_content)
        
        print(f"\n📊 HTML文件统计:")
        print(f"   行数: {lines}")
        print(f"   字符数: {characters:,}")
        print(f"   文件大小: {characters / 1024:.2f} KB")
        
        return all_passed
        
    except FileNotFoundError:
        print(f"❌ HTML文件不存在: {html_path}")
        return False
    except Exception as e:
        print(f"❌ 读取HTML文件失败: {e}")
        return False

def test_integration():
    """测试前后端集成"""
    print("\n🔗 测试前后端集成...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # 测试仪表板页面
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        
        if response.status_code == 200:
            print("✅ 仪表板页面: 200 OK")
            
            # 检查页面内容
            content = response.text
            if "Claw投资决策中心" in content and "投资组合健康度" in content:
                print("✅ 页面内容: 包含关键元素")
                
                # 检查API数据集成
                api_response = requests.get(f"{base_url}/api/dashboard", timeout=5)
                if api_response.status_code == 200:
                    api_data = api_response.json()
                    
                    print(f"✅ API数据集成: 成功")
                    print(f"   投资组合摘要: ${api_data['portfolio_summary']['total_value']:,.2f}")
                    print(f"   市场状态: {api_data['market_status']['market_sentiment']}")
                    print(f"   风险警报: {len(api_data['risk_alerts']['alerts'])}个")
                    
                    return True
                else:
                    print(f"❌ API数据集成失败: HTTP {api_response.status_code}")
                    return False
            else:
                print("❌ 页面内容: 缺少关键元素")
                return False
        else:
            print(f"❌ 仪表板页面失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确保API服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

def generate_test_report():
    """生成测试报告"""
    print("\n📋 生成测试报告...")
    print("=" * 50)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {
            "total_tests": 3,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0
        }
    }
    
    # 运行测试
    api_result = test_api_endpoints()
    frontend_result = test_frontend()
    integration_result = test_integration()
    
    # 收集结果
    report["tests"]["api_endpoints"] = {
        "name": "API接口测试",
        "passed": api_result,
        "timestamp": datetime.now().isoformat()
    }
    
    report["tests"]["frontend"] = {
        "name": "前端HTML测试",
        "passed": frontend_result,
        "timestamp": datetime.now().isoformat()
    }
    
    report["tests"]["integration"] = {
        "name": "前后端集成测试",
        "passed": integration_result,
        "timestamp": datetime.now().isoformat()
    }
    
    # 计算统计
    passed_count = sum(1 for test in report["tests"].values() if test["passed"])
    
    report["summary"]["passed_tests"] = passed_count
    report["summary"]["failed_tests"] = len(report["tests"]) - passed_count
    report["summary"]["success_rate"] = passed_count / len(report["tests"])
    
    # 输出报告
    print(f"\n📊 测试总结:")
    print(f"   总测试数: {report['summary']['total_tests']}")
    print(f"   通过数: {report['summary']['passed_tests']}")
    print(f"   失败数: {report['summary']['failed_tests']}")
    print(f"   成功率: {report['summary']['success_rate']:.1%}")
    
    if report["summary"]["success_rate"] == 1.0:
        print("\n🎉 所有测试通过！Claw Dashboard 运行正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能。")
    
    # 保存报告
    report_path = "/Users/nn/WorkBuddy/Claw/frontend/test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 测试报告已保存: {report_path}")
    
    return report["summary"]["success_rate"] == 1.0

def main():
    """主函数"""
    print("=" * 60)
    print("        Claw Dashboard 测试套件")
    print("=" * 60)
    
    try:
        # 检查API服务器是否运行
        print("🔍 检查API服务器状态...")
        requests.get("http://localhost:8000", timeout=2)
        print("✅ API服务器正在运行")
        
        # 运行测试
        all_passed = generate_test_report()
        
        if all_passed:
            print("\n🚀 测试完成！系统可以投入使用。")
            print("\n💡 提示:")
            print("   1. 访问仪表板: http://localhost:8000/dashboard")
            print("   2. 查看API文档: http://localhost:8000/docs")
            print("   3. 手动测试前端功能:")
            print("      - 点击刷新数据按钮")
            print("      - 切换暗色模式")
            print("      - 查看不同导航页面")
            
            return 0
        else:
            print("\n⚠️ 测试失败！请修复问题后重试。")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("\n❌ API服务器未运行！")
        print("请先启动API服务器:")
        print("   1. cd /Users/nn/WorkBuddy/Claw/frontend")
        print("   2. python claw_dashboard_api.py")
        print("或使用启动脚本:")
        print("   python start_dashboard.py")
        return 1
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())