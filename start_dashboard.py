#!/usr/bin/env python3
"""
Claw Dashboard 启动脚本
一键启动API服务器并打开浏览器
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查并安装依赖"""
    print("🔍 检查依赖...")
    
    requirements_path = Path(__file__).parent / "requirements.txt"
    
    # 创建虚拟环境（如果不存在）
    venv_path = Path(__file__).parent / ".venv"
    if not venv_path.exists():
        print("📦 创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
    
    # 激活虚拟环境并安装依赖
    if os.name == "nt":  # Windows
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:  # macOS/Linux
        pip_path = venv_path / "bin" / "pip"
    
    print("📥 安装依赖...")
    subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], check=True)
    
    return venv_path

def start_api_server(venv_path):
    """启动API服务器"""
    print("🚀 启动API服务器...")
    
    if os.name == "nt":  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # macOS/Linux
        python_path = venv_path / "bin" / "python"
    
    # 启动API服务器
    api_script = Path(__file__).parent / "claw_dashboard_api.py"
    process = subprocess.Popen(
        [str(python_path), str(api_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    return process

def open_browser():
    """打开浏览器"""
    print("🌐 打开浏览器...")
    
    dashboard_url = "http://localhost:8000/dashboard"
    webbrowser.open(dashboard_url)
    
    print(f"✅ 仪表板已启动: {dashboard_url}")
    print("📊 请访问上面的URL查看实时投资仪表板")

def main():
    """主函数"""
    print("=" * 50)
    print("      Claw投资决策中心 - 仪表板启动器")
    print("=" * 50)
    
    try:
        # 检查依赖
        venv_path = check_dependencies()
        
        # 启动API服务器
        api_process = start_api_server(venv_path)
        
        # 打开浏览器
        open_browser()
        
        print("\n📝 控制台信息:")
        print("-" * 40)
        print("API服务器运行在: http://localhost:8000")
        print("仪表板页面: http://localhost:8000/dashboard")
        print("API文档: http://localhost:8000/docs")
        print("\n🛑 按 Ctrl+C 停止服务器")
        
        # 等待进程结束
        try:
            stdout, stderr = api_process.communicate(timeout=3600)  # 1小时超时
            if stdout:
                print("标准输出:", stdout)
            if stderr:
                print("错误输出:", stderr)
        except subprocess.TimeoutExpired:
            print("⏰ 服务器运行超时")
            api_process.kill()
            
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断，停止服务器...")
        if 'api_process' in locals():
            api_process.kill()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())