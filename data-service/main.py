#!/usr/bin/env python3
"""
Claw Advisor 数据采集服务主程序
"""

import logging
import time
import schedule
from datetime import datetime
from data_collector import DataCollector
from config import Config

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_data_collection():
    """运行数据收集任务"""
    try:
        logger.info("=" * 60)
        logger.info(f"开始定时数据收集任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        collector = DataCollector()
        result = collector.run_collection()
        
        logger.info(f"数据收集结果: {result}")
        logger.info("定时任务完成")
        
        return result
        
    except Exception as e:
        logger.error(f"数据收集任务失败: {e}")
        return {"error": str(e)}

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Claw Advisor 数据采集服务启动")
    logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"监控股票: {', '.join(Config.get_stock_symbols())}")
    logger.info(f"数据更新间隔: {Config.DATA_UPDATE_INTERVAL_HOURS} 小时")
    logger.info("=" * 60)
    
    # 立即运行一次数据收集
    logger.info("执行首次数据收集...")
    initial_result = run_data_collection()
    logger.info(f"首次数据收集完成: {initial_result}")
    
    # 设置定时任务
    interval_hours = Config.DATA_UPDATE_INTERVAL_HOURS
    schedule.every(interval_hours).hours.do(run_data_collection)
    
    logger.info(f"定时任务已设置: 每 {interval_hours} 小时运行一次")
    
    # 保持程序运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
            
            # 每10分钟记录一次心跳
            if int(time.time()) % 600 == 0:
                logger.info(f"服务运行中... 下次任务: {schedule.next_run()}")
                
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务...")
    except Exception as e:
        logger.error(f"服务运行异常: {e}")
    finally:
        logger.info("数据采集服务已停止")

if __name__ == "__main__":
    main()