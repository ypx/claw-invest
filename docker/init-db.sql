-- Claw Advisor 数据库初始化脚本
-- 创建时间：2026-03-23

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 股票基本信息表
CREATE TABLE stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(100),
    market_cap NUMERIC(20, 2),
    pe_ratio NUMERIC(10, 2),
    dividend_yield NUMERIC(6, 3),
    beta NUMERIC(6, 3),
    volatility_30d NUMERIC(6, 3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 股票价格历史表
CREATE TABLE stock_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open NUMERIC(12, 4),
    high NUMERIC(12, 4),
    low NUMERIC(12, 4),
    close NUMERIC(12, 4),
    volume BIGINT,
    adj_close NUMERIC(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, date)
);

-- 创建索引加速查询
CREATE INDEX idx_stock_prices_stock_id ON stock_prices(stock_id);
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_stock_prices_stock_id_date ON stock_prices(stock_id, date DESC);

-- 3. Mike推荐清单表
CREATE TABLE mike_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(20) NOT NULL CHECK (recommendation_type IN ('核心仓', '成长仓', '关注仓', '加密资产')),
    mike_reason TEXT,
    priority INTEGER CHECK (priority >= 1 AND priority <= 10),
    added_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 用户持仓表
CREATE TABLE user_portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    quantity NUMERIC(12, 4) NOT NULL DEFAULT 0,
    avg_cost NUMERIC(12, 4) NOT NULL,
    purchase_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    is_option BOOLEAN DEFAULT FALSE,
    option_type VARCHAR(10) CHECK (option_type IN ('call', 'put', 'none')),
    strike_price NUMERIC(12, 4),
    expiration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 保守评分表
CREATE TABLE conservative_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    score_date DATE NOT NULL,
    mike_weight NUMERIC(4, 2) NOT NULL,
    fundamental_score NUMERIC(4, 2) NOT NULL,
    technical_score NUMERIC(4, 2) NOT NULL,
    conservative_factor NUMERIC(4, 2) NOT NULL,
    final_score NUMERIC(4, 2) NOT NULL,
    recommendation VARCHAR(20) CHECK (recommendation IN ('强烈买入', '买入', '持有', '卖出', '强烈卖出')),
    sell_put_suggestion JSONB,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, score_date)
);

-- 6. 用户决策记录表
CREATE TABLE user_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
    decision_type VARCHAR(20) NOT NULL CHECK (decision_type IN ('买入正股', '卖出正股', 'sell_put', 'buy_call', '观望')),
    quantity NUMERIC(12, 4),
    price NUMERIC(12, 4),
    reasoning TEXT,
    system_score NUMERIC(4, 2),
    user_confidence INTEGER CHECK (user_confidence >= 1 AND user_confidence <= 5),
    decision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed BOOLEAN DEFAULT FALSE,
    executed_date TIMESTAMP,
    profit_loss NUMERIC(12, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 系统配置表
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 触发器：更新updated_at时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有需要更新的表创建触发器
CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_mike_recommendations_updated_at BEFORE UPDATE ON mike_recommendations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_portfolios_updated_at BEFORE UPDATE ON user_portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_configs_updated_at BEFORE UPDATE ON system_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始配置数据
INSERT INTO system_configs (config_key, config_value, description) VALUES
('conservative_factors', '{"pe_threshold_low": 20, "pe_threshold_high": 40, "beta_threshold": 1.0, "volatility_threshold": 0.3}', '保守系数计算阈值'),
('mike_weights', '{"核心仓": 1.0, "成长仓": 0.8, "关注仓": 0.6, "加密资产": 0.7}', 'Mike推荐类型权重'),
('scoring_weights', '{"fundamental": 0.6, "technical": 0.4}', '基本面和技术面评分权重'),
('recommendation_thresholds', '{"strong_buy": 80, "buy": 65, "hold": 40, "sell": 20, "strong_sell": 0}', '推荐阈值');

-- 插入Mike推荐的核心股票（示例数据）
-- 注意：实际数据将由数据采集服务填充
INSERT INTO stocks (symbol, name, sector, industry) VALUES
('NVDA', '英伟达', '科技', '半导体'),
('GOOGL', '谷歌-A', '科技', '互联网服务'),
('AMZN', '亚马逊', '科技', '电商/云计算'),
('META', 'Meta', '科技', '社交媒体'),
('TSLA', '特斯拉', '消费类', '汽车制造'),
('IONQ', 'IonQ', '科技', '量子计算'),
('AAPL', '苹果', '科技', '消费电子'),
('MSFT', '微软', '科技', '软件/云计算');

-- 插入Mike推荐清单
INSERT INTO mike_recommendations (stock_id, recommendation_type, mike_reason, priority, is_active) 
SELECT s.id, '核心仓', 'AI算力基础设施，不可替代的护城河', 1, TRUE FROM stocks s WHERE s.symbol = 'NVDA'
UNION ALL
SELECT s.id, '核心仓', 'AI+搜索+云，低估的AI巨头', 2, TRUE FROM stocks s WHERE s.symbol = 'GOOGL'
UNION ALL
SELECT s.id, '核心仓', '云计算AWS+电商，现金流稳健', 3, TRUE FROM stocks s WHERE s.symbol = 'AMZN'
UNION ALL
SELECT s.id, '成长仓', '量子霸权前夜，高风险高回报', 4, TRUE FROM stocks s WHERE s.symbol = 'IONQ'
UNION ALL
SELECT s.id, '成长仓', '广告+AI+元宇宙，被低估', 5, TRUE FROM stocks s WHERE s.symbol = 'META'
UNION ALL
SELECT s.id, '关注仓', '电动车龙头，sell put机会多', 6, TRUE FROM stocks s WHERE s.symbol = 'TSLA';

-- 创建视图：每日评分汇总
CREATE VIEW daily_scores_view AS
SELECT 
    s.symbol,
    s.name,
    mr.recommendation_type,
    cs.score_date,
    cs.final_score,
    cs.recommendation,
    cs.conservative_factor,
    cs.sell_put_suggestion
FROM conservative_scores cs
JOIN stocks s ON cs.stock_id = s.id
LEFT JOIN mike_recommendations mr ON cs.stock_id = mr.stock_id AND mr.is_active = TRUE
WHERE cs.score_date = CURRENT_DATE
ORDER BY cs.final_score DESC;

-- 创建视图：用户持仓概览
CREATE VIEW portfolio_summary_view AS
SELECT 
    s.symbol,
    s.name,
    up.quantity,
    up.avg_cost,
    sp.close AS current_price,
    (sp.close - up.avg_cost) * up.quantity AS unrealized_pnl,
    (sp.close / up.avg_cost - 1) * 100 AS pnl_percentage,
    up.is_option,
    up.option_type,
    up.strike_price,
    up.expiration_date
FROM user_portfolios up
JOIN stocks s ON up.stock_id = s.id
LEFT JOIN (
    SELECT stock_id, MAX(date) as latest_date
    FROM stock_prices 
    GROUP BY stock_id
) latest ON s.id = latest.stock_id
LEFT JOIN stock_prices sp ON s.id = sp.stock_id AND sp.date = latest.latest_date
ORDER BY unrealized_pnl DESC;