def _generate_dynamic_strategies(profile: dict, prices: dict, vix: float) -> list:
    """根据用户画像和实时数据生成动态期权策略
    
    策略逻辑：
    1. 基于实时股价计算合理的OTM行权价
    2. 根据用户风险偏好调整OTM距离和到期日
    3. 使用固定算法（非随机）确保结果可复现且合理
    """
    strategies = []
    
    # 风险等级映射
    risk_level = profile.get("risk_tolerance", "中等")
    capital = profile.get("capital_scale", "中等")
    experience = profile.get("experience_level", "中级")
    
    # 根据风险等级确定Delta和OTM距离（使用固定值而非随机）
    if risk_level == "保守":
        delta_target = 0.15
        otm_pct_base = 0.15  # 15% OTM
        dte_target = 45  # 45天到期
    elif risk_level == "激进":
        delta_target = 0.35
        otm_pct_base = 0.05  # 5% OTM
        dte_target = 21  # 21天到期
    else:  # 中等/平衡
        delta_target = 0.25
        otm_pct_base = 0.10  # 10% OTM
        dte_target = 30  # 30天到期
    
    # 根据VIX调整策略
    vix_adj = 1.0
    if vix < 15:  # 低波动
        vix_adj = 0.8
        vix_comment = "VIX低，权利金较少，建议等待"
    elif vix > 30:  # 高波动
        vix_adj = 1.3
        vix_comment = "VIX高，权利金丰厚，适合操作"
    else:
        vix_comment = "VIX适中，正常操作"
    
    # 选择标的：优先选择高流动性的大盘股
    candidates = []
    for sym, data in prices.items():
        price = data.get("price", 0)
        if price <= 0:
            continue
        change_pct = data.get("change_percent", 0)
        # 计算IV估算
        iv_estimate = max(0.25, min(0.80, (vix / 100) * (1 + abs(change_pct) / 100)))
        candidates.append({
            "symbol": sym,
            "price": price,
            "change_pct": change_pct,
            "iv": iv_estimate
        })
    
    # 按股价排序（优先推荐高价股，通常流动性更好）
    candidates.sort(key=lambda x: x["price"], reverse=True)
    
    # 生成3个策略，使用不同参数组合
    strategy_configs = [
        {"name": "主推策略", "otm_mult": 1.0, "dte_mult": 1.0},   # 标准参数
        {"name": "进取策略", "otm_mult": 0.6, "dte_mult": 0.7},   # 更激进的参数
        {"name": "保守策略", "otm_mult": 1.5, "dte_mult": 1.3},   # 更保守的参数
    ]
    
    for i, stock in enumerate(candidates[:3]):
        sym = stock["symbol"]
        price = stock["price"]
        iv = stock["iv"]
        
        config = strategy_configs[i]
        
        # 确定策略类型：主推Sell Put，根据经验可能推荐Covered Call
        if i == 0:
            strategy_type = "sell_put"
            strategy_name = "Sell Put"
        elif i == 1 and experience in ["高级", "资深"]:
            strategy_type = "covered_call"
            strategy_name = "Covered Call"
        else:
            strategy_type = "sell_put"
            strategy_name = "Sell Put"
        
        # 计算OTM百分比（基于配置调整）
        otm_pct = min(0.25, max(0.03, otm_pct_base * config["otm_mult"]))
        
        # 计算行权价：Sell Put用低于现价的行权价，Covered Call用高于现价的行权价
        if strategy_type == "sell_put":
            strike = price * (1 - otm_pct)
        else:  # covered_call
            strike = price * (1 + otm_pct)
        
        # 标准化行权价（根据股票价格选择合适的精度）
        if strike >= 200:
            strike = round(strike / 5) * 5  # 5美元精度
        elif strike >= 50:
            strike = round(strike / 2.5) * 2.5  # 2.5美元精度
        else:
            strike = round(strike, 1)
        
        # 计算到期日（基于配置调整）
        dte = int(min(60, max(14, dte_target * config["dte_mult"])))
        exp_date = (datetime.now() + timedelta(days=dte)).strftime("%Y-%m-%d")
        
        # 计算权利金（简化Black-Scholes近似）
        # Premium ≈ S * IV * sqrt(DTE/365) * Delta
        time_factor = math.sqrt(dte / 365)
        premium = price * iv * time_factor * delta_target * vix_adj
        
        # 标准化权利金（根据股价调整合理范围）
        max_premium = price * 0.10  # 最大不超过股价的10%
        premium = min(premium, max_premium)
        premium = max(0.1, premium)  # 最小0.1
        
        # 根据行权价精度调整权利金精度
        if price >= 200:
            premium = round(premium, 2)
        else:
            premium = round(premium, 2)
        
        # 计算年化收益
        if strike > 0 and premium > 0:
            annualized = (premium / strike) * (365 / dte) * 100
            annualized = min(annualized, 100)  # 限制最大100%
        else:
            annualized = 0
        
        # 计算盈利概率（基于Delta）
        probability = min(95, max(30, round((1 - delta_target) * 100)))
        
        # 生成推荐语
        distance_desc = f"{round(otm_pct * 100, 1)}%"
        if strategy_type == "sell_put":
            if otm_pct >= 0.15:
                rec = f"深度价外({distance_desc})，胜率{probability}%，{vix_comment}"
            elif otm_pct >= 0.08:
                rec = f"中度价外({distance_desc})，平衡收益风险，{vix_comment}"
            else:
                rec = f"轻度价外({distance_desc})，权利金收益{round(annualized, 1)}%年化，{vix_comment}"
        else:  # covered_call
            rec = f"持有正股可额外收益{round(annualized, 1)}%年化，行权价距现价+{distance_desc}"
        
        strategies.append({
            "symbol": sym,
            "type": strategy_type,
            "strategy_name": strategy_name,
            "strike_price": strike,
            "current_price": round(price, 2),
            "expiration": exp_date,
            "dte": dte,
            "premium": premium,
            "probability": probability,
            "annualized_return": round(annualized, 1),
            "implied_volatility": round(iv * 100, 1),
            "vix": round(vix, 2),
            "recommendation": rec,
            "risk_level": risk_level,
            "distance_pct": round(otm_pct * 100, 1),
            "config_name": config["name"]
        })
    
    return strategies
