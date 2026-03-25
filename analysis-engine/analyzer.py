import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import pandas as pd

from algorithm import ConservativeScoringAlgorithm
from database import db_manager

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """股票分析器"""
    
    def __init__(self):
        self.algorithm = ConservativeScoringAlgorithm()
    
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """从数据库获取股票数据"""
        session = db_manager.get_session()
        try:
            # 获取股票基本信息
            stock_result = session.execute(
                """
                SELECT id, symbol, name, sector, industry, market_cap, pe_ratio, 
                       dividend_yield, beta, volatility_30d, updated_at
                FROM stocks 
                WHERE symbol = :symbol
                """,
                {"symbol": symbol}
            ).fetchone()
            
            if not stock_result:
                logger.warning(f"未找到股票: {symbol}")
                return {}
            
            # 获取Mike推荐信息
            mike_result = session.execute(
                """
                SELECT recommendation_type, mike_reason, priority
                FROM mike_recommendations 
                WHERE stock_id = :stock_id AND is_active = TRUE
                """,
                {"stock_id": stock_result[0]}
            ).fetchone()
            
            # 获取最新价格
            price_result = session.execute(
                """
                SELECT close, date 
                FROM stock_prices 
                WHERE stock_id = :stock_id 
                ORDER BY date DESC 
                LIMIT 1
                """,
                {"stock_id": stock_result[0]}
            ).fetchone()
            
            stock_data = {
                "id": stock_result[0],
                "symbol": stock_result[1],
                "name": stock_result[2],
                "sector": stock_result[3],
                "industry": stock_result[4],
                "market_cap": float(stock_result[5]) if stock_result[5] else None,
                "pe_ratio": float(stock_result[6]) if stock_result[6] else None,
                "dividend_yield": float(stock_result[7]) if stock_result[7] else None,
                "beta": float(stock_result[8]) if stock_result[8] else None,
                "volatility_30d": float(stock_result[9]) if stock_result[9] else None,
                "updated_at": stock_result[10],
                "current_price": float(price_result[0]) if price_result else None,
                "current_price_date": price_result[1] if price_result else None
            }
            
            if mike_result:
                stock_data["mike_recommendation"] = {
                    "recommendation_type": mike_result[0],
                    "mike_reason": mike_result[1],
                    "priority": mike_result[2]
                }
            
            logger.debug(f"获取股票数据: {symbol}, 数据量: {len(stock_data)}")
            return stock_data
            
        finally:
            db_manager.close_session()
    
    def get_price_history(self, stock_id: str, days: int = 90) -> pd.DataFrame:
        """获取股票价格历史"""
        session = db_manager.get_session()
        try:
            result = session.execute(
                """
                SELECT date, open, high, low, close, volume
                FROM stock_prices 
                WHERE stock_id = :stock_id 
                ORDER BY date DESC 
                LIMIT :limit
                """,
                {"stock_id": stock_id, "limit": days}
            ).fetchall()
            
            if not result:
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = pd.DataFrame(
                result,
                columns=['date', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # 按日期升序排列
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            
            return df
            
        finally:
            db_manager.close_session()
    
    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """分析单只股票"""
        logger.info(f"开始分析股票: {symbol}")
        
        try:
            # 1. 获取股票数据
            stock_data = self.get_stock_data(symbol)
            if not stock_data:
                return {"error": f"未找到股票数据: {symbol}"}
            
            # 2. 获取价格历史
            price_history = self.get_price_history(stock_data["id"])
            
            # 3. 获取Mike推荐信息
            mike_recommendation = stock_data.get("mike_recommendation", {
                "recommendation_type": "关注仓",
                "mike_reason": "未在Mike推荐列表中",
                "priority": 10
            })
            
            # 4. 运行评分算法
            analysis_result = self.algorithm.calculate_final_score(
                mike_recommendation=mike_recommendation,
                stock_data=stock_data,
                price_history=price_history
            )
            
            # 5. 保存分析结果到数据库
            self.save_analysis_result(stock_data["id"], analysis_result)
            
            # 6. 构建完整响应
            result = {
                "symbol": symbol,
                "name": stock_data["name"],
                "current_price": stock_data.get("current_price"),
                "current_price_date": stock_data.get("current_price_date"),
                "mike_recommendation": mike_recommendation,
                "analysis": analysis_result,
                "stock_data": {
                    "pe_ratio": stock_data.get("pe_ratio"),
                    "market_cap": stock_data.get("market_cap"),
                    "beta": stock_data.get("beta"),
                    "dividend_yield": stock_data.get("dividend_yield"),
                    "sector": stock_data.get("sector"),
                    "industry": stock_data.get("industry")
                }
            }
            
            logger.info(f"股票分析完成: {symbol}, 分数={analysis_result['final_score']:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"分析股票失败 {symbol}: {e}")
            return {"error": f"分析失败: {str(e)}", "symbol": symbol}
    
    def analyze_all_stocks(self) -> List[Dict[str, Any]]:
        """分析所有股票"""
        logger.info("开始分析所有股票")
        
        # 获取所有股票代码
        session = db_manager.get_session()
        try:
            symbols_result = session.execute(
                "SELECT symbol FROM stocks ORDER BY symbol"
            ).fetchall()
            
            symbols = [row[0] for row in symbols_result]
            
        finally:
            db_manager.close_session()
        
        results = []
        for symbol in symbols:
            result = self.analyze_stock(symbol)
            if "error" not in result:
                results.append(result)
        
        # 按分数排序
        results.sort(key=lambda x: x["analysis"]["final_score"], reverse=True)
        
        logger.info(f"所有股票分析完成: {len(results)}/{len(symbols)} 成功")
        return results
    
    def save_analysis_result(self, stock_id: str, analysis_result: Dict[str, Any]) -> bool:
        """保存分析结果到数据库"""
        try:
            today = date.today()
            
            # 检查是否已有今日记录
            session = db_manager.get_session()
            try:
                existing = session.execute(
                    """
                    SELECT id FROM conservative_scores 
                    WHERE stock_id = :stock_id AND score_date = :score_date
                    """,
                    {"stock_id": stock_id, "score_date": today}
                ).fetchone()
                
                if existing:
                    # 更新现有记录
                    session.execute(
                        """
                        UPDATE conservative_scores 
                        SET mike_weight = :mike_weight,
                            fundamental_score = :fundamental_score,
                            technical_score = :technical_score,
                            conservative_factor = :conservative_factor,
                            final_score = :final_score,
                            recommendation = :recommendation,
                            sell_put_suggestion = :sell_put_suggestion,
                            reasoning = :reasoning,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                        """,
                        {
                            "id": existing[0],
                            "mike_weight": analysis_result["components"]["mike_weight"],
                            "fundamental_score": analysis_result["components"]["fundamental_score"],
                            "technical_score": analysis_result["components"]["technical_score"],
                            "conservative_factor": analysis_result["components"]["conservative_factor"],
                            "final_score": analysis_result["final_score"],
                            "recommendation": analysis_result["recommendation"],
                            "sell_put_suggestion": json.dumps(analysis_result["sell_put_suggestion"]) if analysis_result["sell_put_suggestion"] else None,
                            "reasoning": analysis_result["reasoning"]
                        }
                    )
                else:
                    # 插入新记录
                    session.execute(
                        """
                        INSERT INTO conservative_scores 
                        (stock_id, score_date, mike_weight, fundamental_score, technical_score, 
                         conservative_factor, final_score, recommendation, sell_put_suggestion, reasoning)
                        VALUES 
                        (:stock_id, :score_date, :mike_weight, :fundamental_score, :technical_score,
                         :conservative_factor, :final_score, :recommendation, :sell_put_suggestion, :reasoning)
                        """,
                        {
                            "stock_id": stock_id,
                            "score_date": today,
                            "mike_weight": analysis_result["components"]["mike_weight"],
                            "fundamental_score": analysis_result["components"]["fundamental_score"],
                            "technical_score": analysis_result["components"]["technical_score"],
                            "conservative_factor": analysis_result["components"]["conservative_factor"],
                            "final_score": analysis_result["final_score"],
                            "recommendation": analysis_result["recommendation"],
                            "sell_put_suggestion": json.dumps(analysis_result["sell_put_suggestion"]) if analysis_result["sell_put_suggestion"] else None,
                            "reasoning": analysis_result["reasoning"]
                        }
                    )
                
                session.commit()
                logger.debug(f"保存分析结果: stock_id={stock_id}, 分数={analysis_result['final_score']}")
                return True
                
            finally:
                db_manager.close_session()
                
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            return False
    
    def get_top_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取今日最高推荐股票"""
        today = date.today()
        
        session = db_manager.get_session()
        try:
            result = session.execute(
                """
                SELECT 
                    s.symbol,
                    s.name,
                    cs.final_score,
                    cs.recommendation,
                    cs.reasoning,
                    cs.sell_put_suggestion,
                    sp.close as current_price,
                    mr.recommendation_type as mike_type
                FROM conservative_scores cs
                JOIN stocks s ON cs.stock_id = s.id
                LEFT JOIN mike_recommendations mr ON cs.stock_id = mr.stock_id AND mr.is_active = TRUE
                LEFT JOIN (
                    SELECT stock_id, MAX(date) as latest_date
                    FROM stock_prices 
                    GROUP BY stock_id
                ) latest ON s.id = latest.stock_id
                LEFT JOIN stock_prices sp ON s.id = sp.stock_id AND sp.date = latest.latest_date
                WHERE cs.score_date = :score_date
                ORDER BY cs.final_score DESC
                LIMIT :limit
                """,
                {"score_date": today, "limit": limit}
            ).fetchall()
            
            recommendations = []
            for row in result:
                recommendations.append({
                    "symbol": row[0],
                    "name": row[1],
                    "final_score": float(row[2]) if row[2] else None,
                    "recommendation": row[3],
                    "reasoning": row[4],
                    "sell_put_suggestion": json.loads(row[5]) if row[5] else None,
                    "current_price": float(row[6]) if row[6] else None,
                    "mike_type": row[7]
                })
            
            return recommendations
            
        finally:
            db_manager.close_session()
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """生成仪表盘数据"""
        try:
            # 获取今日所有分析结果
            all_analysis = self.analyze_all_stocks()
            
            if not all_analysis:
                return {"error": "没有可用的分析数据"}
            
            # 统计数据
            total_stocks = len(all_analysis)
            strong_buy = sum(1 for a in all_analysis if a["analysis"]["recommendation"] == "强烈买入")
            buy = sum(1 for a in all_analysis if a["analysis"]["recommendation"] == "买入")
            hold = sum(1 for a in all_analysis if a["analysis"]["recommendation"] == "持有")
            sell = sum(1 for a in all_analysis if a["analysis"]["recommendation"] == "卖出")
            strong_sell = sum(1 for a in all_analysis if a["analysis"]["recommendation"] == "强烈卖出")
            
            # 平均分数
            avg_score = sum(a["analysis"]["final_score"] for a in all_analysis) / total_stocks
            
            # 最佳sell put机会（分数高且有sell put建议）
            sell_put_opportunities = []
            for a in all_analysis:
                if a["analysis"]["final_score"] >= 70 and a["analysis"]["sell_put_suggestion"]:
                    sell_put_opportunities.append({
                        "symbol": a["symbol"],
                        "name": a["name"],
                        "score": a["analysis"]["final_score"],
                        "current_price": a["current_price"],
                        "sell_put": a["analysis"]["sell_put_suggestion"]
                    })
            
            # 按行业分类统计
            sector_stats = {}
            for a in all_analysis:
                sector = a["stock_data"].get("sector", "未知")
                if sector not in sector_stats:
                    sector_stats[sector] = {"count": 0, "total_score": 0}
                sector_stats[sector]["count"] += 1
                sector_stats[sector]["total_score"] += a["analysis"]["final_score"]
            
            for sector in sector_stats:
                sector_stats[sector]["avg_score"] = sector_stats[sector]["total_score"] / sector_stats[sector]["count"]
            
            dashboard_data = {
                "summary": {
                    "total_stocks": total_stocks,
                    "avg_score": round(avg_score, 2),
                    "recommendation_distribution": {
                        "strong_buy": strong_buy,
                        "buy": buy,
                        "hold": hold,
                        "sell": sell,
                        "strong_sell": strong_sell
                    }
                },
                "top_recommendations": self.get_top_recommendations(10),
                "sell_put_opportunities": sell_put_opportunities[:5],  # 前5个
                "sector_analysis": sector_stats,
                "analysis_time": datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"生成仪表盘数据失败: {e}")
            return {"error": str(e)}