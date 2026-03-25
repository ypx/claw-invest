#!/usr/bin/env python3
"""
Claw Dashboard API v3.0
- 用户注册 / 登录 / JWT 认证
- 多用户持仓数据隔离
- 管理员后台接口
- SQLite 持久化存储
"""

import json
import logging
import sqlite3
import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

import bcrypt as _bcrypt_lib
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from jose import JWTError, jwt

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("CLAW_SECRET", "claw-super-secret-key-change-in-prod-2026")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24h

# 数据库路径：优先使用环境变量，否则使用本地
data_dir = os.getenv("DATA_DIR", os.path.dirname(__file__))
DB_PATH = os.path.join(data_dir, "claw.db")

# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────
app = FastAPI(
    title="Claw 投资决策中心 API",
    description="多用户投资管理平台",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（前端）
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """首页 - 返回dashboard"""
    index_path = os.path.join(frontend_path, "claw_dashboard_enhanced.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Claw API is running"}

@app.get("/login")
async def login_page():
    """登录页"""
    login_path = os.path.join(frontend_path, "claw_login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    raise HTTPException(status_code=404, detail="Login page not found")

oauth2   = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def _pre_hash(pw: str) -> bytes:
    """sha256 后给 bcrypt，规避超长密码问题"""
    import base64, hashlib
    return base64.b64encode(hashlib.sha256(pw.encode()).digest())


# ──────────────────────────────────────────────
# 数据库
# ──────────────────────────────────────────────
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=15)   # 等锁超时 15s，防止锁死报错
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")      # 10s 等锁，单位毫秒
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            hashed_pw   TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'user',
            created_at  TEXT NOT NULL,
            last_login  TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1,
            profile     TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS holdings (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            symbol          TEXT NOT NULL,
            name            TEXT NOT NULL,
            shares          REAL NOT NULL DEFAULT 0,
            avg_cost        REAL NOT NULL DEFAULT 0,
            current_price   REAL NOT NULL DEFAULT 0,
            health_score    INTEGER DEFAULT 80,
            updated_at      TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, symbol)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          TEXT PRIMARY KEY,
            user_id     TEXT,
            action      TEXT NOT NULL,
            detail      TEXT,
            ip          TEXT,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS option_positions (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            symbol          TEXT NOT NULL,          -- 标的股票，如 TSLA
            option_type     TEXT NOT NULL DEFAULT 'put',  -- put / call
            direction       TEXT NOT NULL DEFAULT 'sell', -- sell / buy
            strike_price    REAL NOT NULL,           -- 行权价
            expiration      TEXT NOT NULL,           -- 到期日 YYYY-MM-DD
            contracts       INTEGER NOT NULL DEFAULT 1, -- 合约数（1合约=100股）
            premium         REAL NOT NULL DEFAULT 0, -- 开仓权利金（每股）
            open_price      REAL NOT NULL DEFAULT 0, -- 开仓时标的价格
            close_price     REAL,                    -- 平仓权利金（每股），NULL=未平仓
            status          TEXT NOT NULL DEFAULT 'open',  -- open / closed / expired / assigned
            note            TEXT DEFAULT '',         -- 备注
            opened_at       TEXT NOT NULL,           -- 开仓时间
            closed_at       TEXT,                    -- 平仓/到期时间
            updated_at      TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)
        # 创建默认管理员和演示用户
        _seed_default_users(db)

def _seed_default_users(db):
    # 管理员
    admin = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        now = datetime.now(timezone.utc).isoformat()
        admin_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO users(id,username,email,hashed_pw,role,created_at) VALUES(?,?,?,?,?,?)",
            (admin_id, "admin", "admin@claw.app",
             hash_pw("admin888"), "admin", now)
        )
        # 管理员默认持仓
        _seed_holdings(db, admin_id)

    # 演示用户 Z
    z_user = db.execute("SELECT id FROM users WHERE username='Z'").fetchone()
    if not z_user:
        now = datetime.now(timezone.utc).isoformat()
        z_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO users(id,username,email,hashed_pw,role,created_at,profile) VALUES(?,?,?,?,?,?,?)",
            (z_id, "Z", "z@claw.app",
             hash_pw("z888888"), "user", now,
             json.dumps({"style": "conservative", "broker": "tiger", "currency": "USD"}))
        )
        _seed_holdings(db, z_id)

DEFAULT_HOLDINGS = [
    ("MSFT","微软",      30,  386.25, 386.25, 92),
    ("TSLA","特斯拉",    25,  350.00, 383.64, 75),
    ("META","Meta",      20,  480.00, 512.00, 82),
    ("GOOGL","谷歌",     30,  280.00, 304.39, 88),
    ("NVDA","英伟达",    50,  120.00, 177.97, 85),
    ("AAPL","苹果",      35,  230.00, 252.13, 88),
    ("AMZN","亚马逊",    30,  184.00, 212.36, 90),
    ("IONQ","IonQ",     100,   12.00,  15.50, 70),
]

def _seed_holdings(db, user_id):
    now = datetime.now(timezone.utc).isoformat()
    for sym, name, shares, avg_cost, cur_price, hs in DEFAULT_HOLDINGS:
        db.execute(
            """INSERT OR IGNORE INTO holdings
               (id,user_id,symbol,name,shares,avg_cost,current_price,health_score,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (str(uuid.uuid4()), user_id, sym, name, shares, avg_cost, cur_price, hs, now)
        )

# ──────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

    @validator("username")
    @classmethod
    def username_ok(cls, v):
        if len(v) < 2 or len(v) > 20:
            raise ValueError("用户名长度 2-20 位")
        return v

    @validator("password")
    @classmethod
    def pw_ok(cls, v):
        if len(v) < 6:
            raise ValueError("密码至少 6 位")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict

class HoldingUpsert(BaseModel):
    symbol: str
    name: str
    shares: float
    avg_cost: float
    current_price: float
    health_score: int = 80

class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None

class OptionPositionCreate(BaseModel):
    symbol: str                         # 标的，如 TSLA
    option_type: str = "put"            # put / call
    direction: str = "sell"             # sell / buy
    strike_price: float                 # 行权价
    expiration: str                     # 到期日 YYYY-MM-DD
    contracts: int = 1                  # 合约数
    premium: float                      # 开仓权利金（每股）
    open_price: float = 0.0             # 开仓时标的价格
    note: str = ""                      # 备注

    @validator("option_type")
    @classmethod
    def type_ok(cls, v):
        if v not in ("put", "call"):
            raise ValueError("option_type 必须是 put 或 call")
        return v

    @validator("direction")
    @classmethod
    def dir_ok(cls, v):
        if v not in ("sell", "buy"):
            raise ValueError("direction 必须是 sell 或 buy")
        return v

class OptionPositionClose(BaseModel):
    close_price: float                  # 平仓权利金（每股）
    status: str = "closed"             # closed / expired / assigned

    @validator("status")
    @classmethod
    def status_ok(cls, v):
        if v not in ("closed", "expired", "assigned"):
            raise ValueError("status 必须是 closed/expired/assigned")
        return v

# ──────────────────────────────────────────────
# Auth Helpers
# ──────────────────────────────────────────────
def hash_pw(pw: str) -> str:
    return _bcrypt_lib.hashpw(_pre_hash(pw), _bcrypt_lib.gensalt()).decode()

def verify_pw(plain: str, hashed: str) -> bool:
    return _bcrypt_lib.checkpw(_pre_hash(plain), hashed.encode())

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    payload["exp"] = expire
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2)):
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise creds_exc
    except JWTError:
        raise creds_exc
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=? AND is_active=1", (user_id,)).fetchone()
    if not row:
        raise creds_exc
    return dict(row)

def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

def log_action(user_id: str, action: str, detail: str = "", db=None):
    """记录操作日志。可传入已有 db 连接（避免 SQLite 锁死），也可不传自动开连接。"""
    def _insert(conn):
        conn.execute(
            "INSERT INTO audit_log(id,user_id,action,detail,created_at) VALUES(?,?,?,?,?)",
            (str(uuid.uuid4()), user_id, action, detail,
             datetime.now(timezone.utc).isoformat())
        )
    if db is not None:
        _insert(db)
    else:
        with get_db() as conn:
            _insert(conn)

# ──────────────────────────────────────────────
# 数据计算
# ──────────────────────────────────────────────
MARKET_DATA = {
    "sp500": 5234.18, "sp500_change": 0.8,
    "nasdaq": 16345.27, "nasdaq_change": 1.2,
    "vix": 14.2, "vix_change": -2.1,
    "market_sentiment": "乐观",
}

RISK_ALERTS = [
    {"id":"r1","level":"high","title":"现金比例过高","description":"现金比例59.2% vs 目标35%，资金效率低","timestamp":"2h前","action":"优化现金使用，考虑sell put策略"},
    {"id":"r2","level":"high","title":"科技股集中度高","description":"科技行业占比50.7%，建议分散","timestamp":"3h前","action":"增加防御性行业配置"},
    {"id":"r3","level":"medium","title":"利率风险","description":"下周FOMC会议，关注市场反应","timestamp":"5h前","action":"保持现金，关注市场反应"},
]

OPTION_STRATEGIES = [
    {"symbol":"TSLA","type":"put","strike_price":380,"expiration":"2026-04-24","premium":3.2,"probability":68,"annualized_return":12.5,"recommendation":"高概率，适合sell put"},
    {"symbol":"NVDA","type":"put","strike_price":170,"expiration":"2026-05-08","premium":2.8,"probability":55,"annualized_return":11.2,"recommendation":"中等概率，风险可控"},
    {"symbol":"AAPL","type":"put","strike_price":245,"expiration":"2026-04-17","premium":1.5,"probability":72,"annualized_return":9.8,"recommendation":"保守策略，适合新手"},
]

NEWS = [
    {"id":"n1","title":"NVDA发布新一代AI芯片，分析师一致上调目标价","summary":"英伟达宣布下一代Blackwell Ultra架构芯片投入生产，多家机构上调目标价。","source":"路透社","timestamp":"1小时前","impact":"high","related_symbols":["NVDA","AMD"]},
    {"id":"n2","title":"美联储会议纪要：通胀放缓，年内仍有降息空间","summary":"FOMC纪要显示官员对通胀路径更有信心，市场预期年内至少两次降息。","source":"华尔街日报","timestamp":"3小时前","impact":"medium","related_symbols":["所有股票"]},
    {"id":"n3","title":"TSLA Q1交付量同比增长21%，超市场预期","summary":"特斯拉第一季度交付约47.2万辆，超出分析师预期41万辆。","source":"彭博社","timestamp":"5小时前","impact":"high","related_symbols":["TSLA","F","GM"]},
]

def calc_portfolio(holdings: list, cash_val: float = 0, target_cash_ratio: float = 35.0) -> dict:
    total_inv = sum(h["current_price"] * h["shares"] for h in holdings)
    total_cost = sum(h["avg_cost"] * h["shares"] for h in holdings)
    gain = total_inv - total_cost
    gain_pct = (gain / total_cost * 100) if total_cost > 0 else 0
    total_val = total_inv + cash_val
    cash_ratio = (cash_val / total_val * 100) if total_val > 0 else 0
    avg_hs = sum(h["health_score"] for h in holdings) / len(holdings) if holdings else 0

    enriched = []
    for h in holdings:
        cv = h["current_price"] * h["shares"]
        gl = (h["current_price"] - h["avg_cost"]) * h["shares"]
        gl_pct = ((h["current_price"] - h["avg_cost"]) / h["avg_cost"] * 100) if h["avg_cost"] > 0 else 0
        enriched.append({**h, "current_value": round(cv,2), "gain_loss": round(gl,2), "gain_loss_percent": round(gl_pct,2)})

    return {
        "portfolio_summary": {
            "total_value": round(total_val, 2),
            "cash_value": round(cash_val, 2),
            "invested_value": round(total_inv, 2),
            "total_gain_loss": round(gain, 2),
            "total_gain_loss_percent": round(gain_pct, 2),
            "cash_ratio": cash_ratio,
            "target_cash_ratio": 35.0,
            "health_score": round(avg_hs, 1),
            "positions_count": len(holdings),
            "update_time": datetime.now().isoformat(),
        },
        "portfolio_holdings": enriched,
        "portfolio_health": {
            "overall_score": round(avg_hs, 1),
            "metrics": {"diversification":92,"risk_control":85,"cash_management":45,"sector_allocation":78,"position_size":88,"volatility":76},
            "strengths": ["持仓分散度良好","风险控制措施到位","投资标的质量优秀"],
            "weaknesses": ["现金比例过高","科技股集中度过高","部分持仓估值偏高"],
            "recommendations": ["优化现金使用，考虑sell put策略","适当降低科技股仓位","增加防御性行业配置"],
        },
        "industry_distribution": {"technology":50.7,"consumer_cyclical":28.1,"communication_services":14.2,"industrials":7.0},
    }

# ──────────────────────────────────────────────
# 路由：认证
# ──────────────────────────────────────────────
@app.post("/api/auth/register", summary="注册")
async def register(body: RegisterRequest):
    with get_db() as db:
        if db.execute("SELECT id FROM users WHERE username=?", (body.username,)).fetchone():
            raise HTTPException(400, "用户名已存在")
        if db.execute("SELECT id FROM users WHERE email=?", (body.email,)).fetchone():
            raise HTTPException(400, "邮箱已注册")
        uid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            "INSERT INTO users(id,username,email,hashed_pw,role,created_at) VALUES(?,?,?,?,?,?)",
            (uid, body.username, body.email, hash_pw(body.password), "user", now)
        )
        _seed_holdings(db, uid)
        log_action(uid, "register", f"username={body.username}", db=db)
    return {"message": "注册成功", "username": body.username}

@app.post("/api/auth/login", response_model=TokenResponse, summary="登录")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE username=?", (form.username,)).fetchone()
    if not row or not verify_pw(form.password, row["hashed_pw"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if not row["is_active"]:
        raise HTTPException(403, "账号已被禁用")
    token = create_token({"sub": row["id"], "role": row["role"]},
                         timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    with get_db() as db:
        db.execute("UPDATE users SET last_login=? WHERE id=?",
                   (datetime.now(timezone.utc).isoformat(), row["id"]))
    log_action(row["id"], "login")
    return {
        "access_token": token,
        "user": {
            "id": row["id"], "username": row["username"],
            "email": row["email"], "role": row["role"],
            "profile": json.loads(row["profile"] or "{}"),
        }
    }

@app.get("/api/auth/me", summary="当前用户信息")
async def me(current_user=Depends(get_current_user)):
    u = dict(current_user)
    u.pop("hashed_pw", None)
    u["profile"] = json.loads(u.get("profile") or "{}")
    return u

# ──────────────────────────────────────────────
# 路由：仪表板数据（需登录）
# ──────────────────────────────────────────────
@app.get("/api/dashboard", summary="完整仪表板数据")
async def dashboard(current_user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM holdings WHERE user_id=?", (current_user["id"],)
        ).fetchall()
    holdings = [dict(r) for r in rows]
    profile = json.loads(current_user.get("profile") or "{}")
    cash_val = float(profile.get("cash", 0))
    target_cash_ratio = float(profile.get("target_cash_ratio", 35.0))
    portfolio = calc_portfolio(holdings, cash_val, target_cash_ratio)
    return {
        **portfolio,
        "market_status": MARKET_DATA,
        "risk_alerts": RISK_ALERTS,
        "option_strategies": OPTION_STRATEGIES,
        "news": NEWS,
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/api/portfolio/summary", summary="持仓摘要")
async def portfolio_summary(current_user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM holdings WHERE user_id=?", (current_user["id"],)).fetchall()
    profile = json.loads(current_user.get("profile") or "{}")
    cash_val = float(profile.get("cash", 0))
    target_cash_ratio = float(profile.get("target_cash_ratio", 35.0))
    return calc_portfolio([dict(r) for r in rows], cash_val, target_cash_ratio)["portfolio_summary"]

@app.get("/api/portfolio/holdings", summary="持仓列表")
async def get_holdings(current_user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute("SELECT * FROM holdings WHERE user_id=?", (current_user["id"],)).fetchall()
    holdings = [dict(r) for r in rows]
    portfolio = calc_portfolio(holdings)
    return {"holdings": portfolio["portfolio_holdings"], "count": len(holdings)}

@app.post("/api/portfolio/holdings", summary="添加/更新持仓")
async def upsert_holding(body: HoldingUpsert, current_user=Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as db:
        existing = db.execute(
            "SELECT id FROM holdings WHERE user_id=? AND symbol=?",
            (current_user["id"], body.symbol.upper())
        ).fetchone()
        if existing:
            db.execute(
                """UPDATE holdings SET name=?,shares=?,avg_cost=?,current_price=?,
                   health_score=?,updated_at=? WHERE id=?""",
                (body.name, body.shares, body.avg_cost, body.current_price,
                 body.health_score, now, existing["id"])
            )
            action = "update_holding"
        else:
            db.execute(
                """INSERT INTO holdings(id,user_id,symbol,name,shares,avg_cost,current_price,health_score,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), current_user["id"], body.symbol.upper(),
                 body.name, body.shares, body.avg_cost, body.current_price,
                 body.health_score, now)
            )
            action = "add_holding"
    log_action(current_user["id"], action, f"symbol={body.symbol}")
    return {"message": "保存成功", "symbol": body.symbol.upper()}

@app.delete("/api/portfolio/holdings/{symbol}", summary="删除持仓")
async def delete_holding(symbol: str, current_user=Depends(get_current_user)):
    with get_db() as db:
        result = db.execute(
            "DELETE FROM holdings WHERE user_id=? AND symbol=?",
            (current_user["id"], symbol.upper())
        )
    if result.rowcount == 0:
        raise HTTPException(404, "持仓不存在")
    log_action(current_user["id"], "delete_holding", f"symbol={symbol}")
    return {"message": "已删除", "symbol": symbol.upper()}

@app.get("/api/market/status", summary="市场行情")
async def market_status(current_user=Depends(get_current_user)):
    return {**MARKET_DATA, "update_time": datetime.now().isoformat()}

@app.get("/api/risk/alerts", summary="风险预警")
async def risk_alerts(current_user=Depends(get_current_user)):
    return {"alerts": RISK_ALERTS, "count": len(RISK_ALERTS)}

@app.get("/api/options/strategies", summary="期权策略")
async def option_strategies(current_user=Depends(get_current_user)):
    return {"strategies": OPTION_STRATEGIES, "count": len(OPTION_STRATEGIES)}

@app.get("/api/news", summary="资讯动态")
async def news(current_user=Depends(get_current_user)):
    return {"news": NEWS, "count": len(NEWS)}

# ──────────────────────────────────────────────
# 路由：管理员接口
# ──────────────────────────────────────────────
@app.get("/api/admin/stats", summary="[管理员] 系统统计")
async def admin_stats(admin=Depends(require_admin)):
    with get_db() as db:
        total_users   = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_users  = db.execute("SELECT COUNT(*) FROM users WHERE is_active=1").fetchone()[0]
        admin_count   = db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0]
        total_holdings = db.execute("SELECT COUNT(*) FROM holdings").fetchone()[0]
        total_logs    = db.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        recent_logins = db.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action='login' AND created_at > datetime('now','-24 hours')"
        ).fetchone()[0]
        today_regs = db.execute(
            "SELECT COUNT(*) FROM users WHERE created_at > datetime('now','start of day')"
        ).fetchone()[0]
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_count": admin_count,
        "total_holdings": total_holdings,
        "total_audit_logs": total_logs,
        "logins_last_24h": recent_logins,
        "registrations_today": today_regs,
        "db_path": DB_PATH,
        "server_time": datetime.now().isoformat(),
    }

@app.get("/api/admin/users", summary="[管理员] 用户列表")
async def admin_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(require_admin)
):
    offset = (page - 1) * limit
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        rows = db.execute(
            "SELECT id,username,email,role,is_active,created_at,last_login FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        # 每个用户的持仓数
        users = []
        for r in rows:
            hc = db.execute("SELECT COUNT(*) FROM holdings WHERE user_id=?", (r["id"],)).fetchone()[0]
            users.append({**dict(r), "holdings_count": hc})
    return {"users": users, "total": total, "page": page, "limit": limit}

@app.get("/api/admin/users/{user_id}", summary="[管理员] 用户详情")
async def admin_user_detail(user_id: str, admin=Depends(require_admin)):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if not row:
            raise HTTPException(404, "用户不存在")
        holdings = db.execute("SELECT * FROM holdings WHERE user_id=?", (user_id,)).fetchall()
        logs = db.execute(
            "SELECT * FROM audit_log WHERE user_id=? ORDER BY created_at DESC LIMIT 20", (user_id,)
        ).fetchall()
    u = dict(row)
    u.pop("hashed_pw", None)
    u["profile"] = json.loads(u.get("profile") or "{}")
    return {
        "user": u,
        "holdings": [dict(h) for h in holdings],
        "recent_logs": [dict(l) for l in logs],
    }

@app.patch("/api/admin/users/{user_id}", summary="[管理员] 修改用户")
async def admin_update_user(user_id: str, body: UpdateUserRequest, admin=Depends(require_admin)):
    if user_id == admin["id"]:
        raise HTTPException(400, "不能修改自己的状态")
    with get_db() as db:
        if body.is_active is not None:
            db.execute("UPDATE users SET is_active=? WHERE id=?", (1 if body.is_active else 0, user_id))
        if body.role is not None:
            db.execute("UPDATE users SET role=? WHERE id=?", (body.role, user_id))
    log_action(admin["id"], "admin_update_user", f"target={user_id} body={body.model_dump()}")
    return {"message": "更新成功"}

@app.delete("/api/admin/users/{user_id}", summary="[管理员] 删除用户")
async def admin_delete_user(user_id: str, admin=Depends(require_admin)):
    if user_id == admin["id"]:
        raise HTTPException(400, "不能删除自己")
    with get_db() as db:
        db.execute("DELETE FROM holdings WHERE user_id=?", (user_id,))
        result = db.execute("DELETE FROM users WHERE id=?", (user_id,))
    if result.rowcount == 0:
        raise HTTPException(404, "用户不存在")
    log_action(admin["id"], "admin_delete_user", f"target={user_id}")
    return {"message": "已删除"}

@app.get("/api/admin/logs", summary="[管理员] 操作日志")
async def admin_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    admin=Depends(require_admin)
):
    offset = (page - 1) * limit
    with get_db() as db:
        total = db.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        rows = db.execute(
            """SELECT l.*, u.username FROM audit_log l
               LEFT JOIN users u ON l.user_id=u.id
               ORDER BY l.created_at DESC LIMIT ? OFFSET ?""",
            (limit, offset)
        ).fetchall()
    return {"logs": [dict(r) for r in rows], "total": total, "page": page, "limit": limit}

@app.patch("/api/user/profile", summary="更新用户资料（现金设置等）")
async def update_profile(body: dict, current_user=Depends(get_current_user)):
    with get_db() as db:
        old_profile = json.loads(current_user.get("profile") or "{}")
        old_profile.update(body)
        db.execute("UPDATE users SET profile=? WHERE id=?",
                   (json.dumps(old_profile), current_user["id"]))
    log_action(current_user["id"], "update_profile", str(body))
    return {"message": "保存成功", "profile": old_profile}

# ──────────────────────────────────────────────
# TSLA 专项情报数据
# ──────────────────────────────────────────────
TSLA_INTEL = {
    "company": {
        "name": "Tesla, Inc.",
        "ticker": "TSLA",
        "sector": "消费科技 / 能源 / AI",
        "founded": 2003,
        "ceo": "Elon Musk",
        "description": "特斯拉是全球领先的电动汽车与清洁能源公司，业务涵盖电动汽车、储能系统、太阳能、自动驾驶软件及人形机器人。"
    },
    "moat": [
        {
            "title": "全球电动车销量第一",
            "icon": "fa-car",
            "color": "#f85149",
            "level": "极强",
            "detail": "2024 年全球交付约 180 万辆，连续多年蝉联纯电动车销量榜首。超级工厂（上海、得克萨斯、柏林）具备强大产能弹性，单车成本持续压缩。",
            "data_point": "2024 全年交付 1,789,226 辆"
        },
        {
            "title": "全球最大私有自动驾驶数据集",
            "icon": "fa-brain",
            "color": "#58a6ff",
            "level": "极强",
            "detail": "累计超过 60 亿英里真实道路数据，依托 FSD（完全自动驾驶）订阅用户实时上传影像。端到端神经网络 + 强化学习，技术迭代速度远超 Waymo、Mobileye 等竞争对手。",
            "data_point": "FSD v13 城市 Autopilot 干预率大幅下降"
        },
        {
            "title": "Supercharger 全球充电网络",
            "icon": "fa-bolt",
            "color": "#d29922",
            "level": "强",
            "detail": "全球超过 6 万个充电桩，覆盖 70 个国家，是全球最大、最可靠的电动车充电网络。正对第三方品牌开放，收取充电服务费，形成高频现金流。",
            "data_point": "6万+ 充电桩，已开放 Ford、GM 等品牌"
        },
        {
            "title": "储能业务（Megapack）",
            "icon": "fa-battery-full",
            "color": "#3fb950",
            "level": "强",
            "detail": "Megapack 大型储能系统订单爆发，2024 年储能部署量超 31.4 GWh，同比增长 114%。储能毛利率高于汽车，被视为特斯拉下一个十年增长引擎之一。",
            "data_point": "2024 储能部署 31.4 GWh，同比+114%"
        },
        {
            "title": "Robotaxi（Cybercab）无人出租",
            "icon": "fa-taxi",
            "color": "#bc8cff",
            "level": "中（兑现中）",
            "detail": "Cybercab 预计 2026 年投入量产，无方向盘/踏板设计，仅作为无人出租使用。Austin 试点已于 2025 年启动，一旦 FSD 监管放行，将创造全新收入维度（按里程收费的软件生意）。",
            "data_point": "Austin Robotaxi 试运营 2025，量产目标 2026"
        },
        {
            "title": "擎天柱机器人（Optimus）",
            "icon": "fa-robot",
            "color": "#f0883e",
            "level": "中（早期）",
            "detail": "人形机器人 Optimus 已在特斯拉工厂内部上岗执行装配任务（2025 年）。马斯克预测 2026 年对外销售，长期市值潜力超越汽车主业。全球人形机器人赛道估值重构。",
            "data_point": "工厂内部已有 Optimus 工作，2026 年对外销售"
        },
        {
            "title": "垂直整合供应链",
            "icon": "fa-industry",
            "color": "#39c5cf",
            "level": "强",
            "detail": "自研电芯（4680）、自研 FSD 芯片（D1/HW4）、自建超级工厂，极少外包核心零部件。供应链话语权强，成本控制能力出色。",
            "data_point": "4680 电芯已量产，HW4 自动驾驶芯片已全面铺装"
        }
    ],
    "business_outlook": [
        {
            "horizon": "2025",
            "title": "FSD 商业化加速",
            "desc": "FSD v13/v14 技术升级，Robotaxi Austin 试点扩大，无监督 FSD 监管推进。预计 FSD 订阅收入大幅增长，高毛利软件占比提升。",
            "sentiment": "positive",
            "tags": ["FSD", "软件收入", "自动驾驶"]
        },
        {
            "horizon": "2025–2026",
            "title": "储能 Megapack 爆发",
            "desc": "全球电网储能需求高速增长，Megapack Lathrop 工厂产能爬坡完成，订单能见度超 12 个月。储能毛利率有望超过汽车分部。",
            "sentiment": "positive",
            "tags": ["储能", "Megapack", "清洁能源"]
        },
        {
            "horizon": "2026",
            "title": "Cybercab 量产与 Optimus 发布",
            "desc": "Cybercab（低成本 Robotaxi 车型）目标 2026 年量产，起售价约 $30,000。Optimus 机器人对外销售，作为长期期权价值巨大。",
            "sentiment": "positive",
            "tags": ["Robotaxi", "Optimus", "机器人"]
        },
        {
            "horizon": "2025–2026",
            "title": "汽车价格压力持续",
            "desc": "电动车竞争加剧（比亚迪、小鹏等中国车企），TSLA 汽车毛利率承压。需靠软件收入（FSD）和储能对冲。",
            "sentiment": "neutral",
            "tags": ["毛利率", "竞争", "定价压力"]
        },
        {
            "horizon": "长期",
            "title": "AI 公司重估逻辑",
            "desc": "马斯克将特斯拉定位为「全球最大 AI 与机器人公司」而非汽车公司。若 FSD + Optimus 兑现，市值逻辑将从 PE 估值切换到类 SaaS 的 ARR 估值，天花板大幅打开。",
            "sentiment": "positive",
            "tags": ["AI重估", "长期逻辑", "SaaS化"]
        },
        {
            "horizon": "风险",
            "title": "马斯克个人风险 / 品牌风险",
            "desc": "马斯克政治立场引发部分欧美消费者抵制，欧洲销量有所下滑。DOGE 政府工作可能分散精力，管理层风险需持续关注。",
            "sentiment": "negative",
            "tags": ["品牌风险", "马斯克", "政治风险"]
        }
    ],
    "key_metrics": {
        "pe_ratio": "~100x（基于FSD预期）",
        "market_cap": "~$1.2T",
        "revenue_2024": "$97.7B",
        "gross_margin_auto": "~17%",
        "gross_margin_energy": "~27%",
        "fsd_subscribers": "700万+",
        "employees": "~140,000"
    },
    "sell_put_guide": {
        "why": "TSLA 波动率（IV）长期高于标普500，Sell Put 可收取较厚权利金。作为长期看涨 TSLA 的投资者，被行权等同于低价买入，风险可控。",
        "tips": [
            "选择 Delta 约 -0.20 到 -0.30 的行权价，胜率 70-80%",
            "到期日选 21-45 天，时间价值衰减最优",
            "财报前后 IV 飙升，是卖权利金的好时机（财报后IV crush需注意）",
            "若被行权，保持100股不慌张，继续Sell Call收取权利金（Covered Call）",
            "建议单次 Sell Put 占可用资金不超过 20%"
        ],
        "current_suggestion": "当前价格区间，$360-$380 行权价（1-2个月到期）是相对安全区域"
    },
    "last_updated": "2026-03-24"
}

@app.get("/api/tsla/intel", summary="TSLA 综合情报")
async def tsla_intel(current_user=Depends(get_current_user)):
    return TSLA_INTEL

# ──────────────────────────────────────────────
# 路由：期权持仓
# ──────────────────────────────────────────────
def _calc_option_pnl(pos: dict) -> dict:
    """计算期权持仓的盈亏"""
    contracts = pos["contracts"]
    premium_in = pos["premium"]   # 开仓权利金/股
    close_pr = pos["close_price"]
    direction = pos["direction"]  # sell / buy
    status = pos["status"]

    total_premium = premium_in * contracts * 100  # 总权利金（开仓）

    if status == "open":
        # 未平仓，显示已收权利金
        realized_pnl = 0
        unrealized_pnl = total_premium if direction == "sell" else -total_premium
        note_pnl = "持仓中"
    elif status in ("closed", "expired"):
        close_pr = close_pr or 0
        if direction == "sell":
            realized_pnl = (premium_in - close_pr) * contracts * 100
        else:
            realized_pnl = (close_pr - premium_in) * contracts * 100
        unrealized_pnl = 0
        note_pnl = "已平仓" if status == "closed" else "已到期归零"
    elif status == "assigned":
        realized_pnl = 0
        unrealized_pnl = 0
        note_pnl = "已行权（须看正股盈亏）"
    else:
        realized_pnl = unrealized_pnl = 0
        note_pnl = ""

    return {
        **pos,
        "total_premium_received": round(total_premium, 2) if direction == "sell" else round(-total_premium, 2),
        "realized_pnl": round(realized_pnl, 2),
        "unrealized_pnl": round(unrealized_pnl, 2),
        "max_loss": round(pos["strike_price"] * contracts * 100, 2) if direction == "sell" and pos["option_type"] == "put" else None,
        "pnl_note": note_pnl,
    }

@app.get("/api/options/positions", summary="获取期权持仓列表")
async def get_option_positions(
    status: Optional[str] = Query(None, description="open/closed/expired/assigned，不填返回全部"),
    current_user=Depends(get_current_user)
):
    with get_db() as db:
        if status:
            rows = db.execute(
                "SELECT * FROM option_positions WHERE user_id=? AND status=? ORDER BY opened_at DESC",
                (current_user["id"], status)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM option_positions WHERE user_id=? ORDER BY opened_at DESC",
                (current_user["id"],)
            ).fetchall()
    positions = [_calc_option_pnl(dict(r)) for r in rows]

    # 汇总统计
    open_pos = [p for p in positions if p["status"] == "open"]
    closed_pos = [p for p in positions if p["status"] in ("closed", "expired")]
    total_realized = sum(p["realized_pnl"] for p in closed_pos)
    total_premium_open = sum(p["total_premium_received"] for p in open_pos)

    return {
        "positions": positions,
        "count": len(positions),
        "summary": {
            "open_count": len(open_pos),
            "closed_count": len(closed_pos),
            "total_realized_pnl": round(total_realized, 2),
            "total_open_premium": round(total_premium_open, 2),
        }
    }

@app.post("/api/options/positions", summary="新增期权持仓（开仓）")
async def add_option_position(body: OptionPositionCreate, current_user=Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    pos_id = str(uuid.uuid4())
    with get_db() as db:
        db.execute(
            """INSERT INTO option_positions
               (id,user_id,symbol,option_type,direction,strike_price,expiration,
                contracts,premium,open_price,status,note,opened_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (pos_id, current_user["id"], body.symbol.upper(),
             body.option_type, body.direction, body.strike_price, body.expiration,
             body.contracts, body.premium, body.open_price,
             "open", body.note, now, now)
        )
    log_action(current_user["id"], "add_option", f"{body.direction} {body.option_type} {body.symbol} K={body.strike_price} exp={body.expiration}")
    return {"message": "开仓记录已保存", "id": pos_id}

@app.patch("/api/options/positions/{pos_id}/close", summary="平仓/到期/行权")
async def close_option_position(pos_id: str, body: OptionPositionClose, current_user=Depends(get_current_user)):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM option_positions WHERE id=? AND user_id=?",
            (pos_id, current_user["id"])
        ).fetchone()
        if not row:
            raise HTTPException(404, "期权持仓不存在")
        if dict(row)["status"] != "open":
            raise HTTPException(400, "该持仓已平仓或到期，无法重复操作")
        db.execute(
            "UPDATE option_positions SET close_price=?,status=?,closed_at=?,updated_at=? WHERE id=?",
            (body.close_price, body.status, now, now, pos_id)
        )
    log_action(current_user["id"], "close_option", f"id={pos_id} status={body.status} close_price={body.close_price}")
    return {"message": f"已标记为{body.status}", "id": pos_id}

@app.delete("/api/options/positions/{pos_id}", summary="删除期权记录")
async def delete_option_position(pos_id: str, current_user=Depends(get_current_user)):
    with get_db() as db:
        result = db.execute(
            "DELETE FROM option_positions WHERE id=? AND user_id=?",
            (pos_id, current_user["id"])
        )
    if result.rowcount == 0:
        raise HTTPException(404, "期权持仓不存在")
    log_action(current_user["id"], "delete_option", f"id={pos_id}")
    return {"message": "已删除"}

@app.get("/api/options/stats", summary="期权收益统计")
async def option_stats(current_user=Depends(get_current_user)):
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM option_positions WHERE user_id=? ORDER BY opened_at DESC",
            (current_user["id"],)
        ).fetchall()
    positions = [_calc_option_pnl(dict(r)) for r in rows]

    # 按月统计已实现盈亏
    monthly = {}
    for p in positions:
        if p["status"] in ("closed", "expired") and p.get("closed_at"):
            month = p["closed_at"][:7]  # YYYY-MM
            monthly[month] = monthly.get(month, 0) + p["realized_pnl"]

    # 按标的统计
    by_symbol = {}
    for p in positions:
        sym = p["symbol"]
        if sym not in by_symbol:
            by_symbol[sym] = {"count": 0, "realized_pnl": 0, "open_count": 0}
        by_symbol[sym]["count"] += 1
        by_symbol[sym]["realized_pnl"] += p["realized_pnl"]
        if p["status"] == "open":
            by_symbol[sym]["open_count"] += 1

    total_realized = sum(p["realized_pnl"] for p in positions if p["status"] in ("closed","expired"))
    total_trades = len([p for p in positions if p["status"] != "open"])
    win_trades = len([p for p in positions if p["status"] in ("closed","expired") and p["realized_pnl"] > 0])

    return {
        "total_realized_pnl": round(total_realized, 2),
        "total_trades": total_trades,
        "win_rate": round(win_trades / total_trades * 100, 1) if total_trades > 0 else 0,
        "monthly_pnl": [{"month": k, "pnl": round(v, 2)} for k, v in sorted(monthly.items())],
        "by_symbol": [{"symbol": k, **v, "realized_pnl": round(v["realized_pnl"], 2)} for k, v in by_symbol.items()],
    }



# ──────────────────────────────────────────────
# 静态页面路由
# ──────────────────────────────────────────────
BASE = os.path.dirname(__file__)

def _serve_html(filename: str) -> HTMLResponse:
    path = os.path.join(BASE, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(404, f"{filename} 不存在")

@app.get("/", include_in_schema=False)
async def root_redirect():
    return HTMLResponse('<script>location.href="/login"</script>')

@app.get("/login", include_in_schema=False)
async def serve_login():
    return _serve_html("claw_login.html")

@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    return _serve_html("claw_dashboard_enhanced.html")

@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return _serve_html("claw_admin.html")

# ──────────────────────────────────────────────
# 静态文件服务
# ──────────────────────────────────────────────
@app.get("/styles/{file_path:path}", include_in_schema=False)
async def serve_styles(file_path: str):
    """服务CSS样式文件"""
    styles_dir = os.path.join(BASE, "styles")
    full_path = os.path.join(styles_dir, file_path)
    # 安全检查：确保路径在styles目录内
    real_full_path = os.path.realpath(full_path)
    real_styles_dir = os.path.realpath(styles_dir)
    if not real_full_path.startswith(real_styles_dir):
        raise HTTPException(403, "Access denied")
    if not os.path.exists(full_path):
        raise HTTPException(404, f"Style file not found: {file_path}")
    return FileResponse(full_path)

# ──────────────────────────────────────────────
# 启动
# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    logger.info(f"数据库: {DB_PATH}")
    logger.info("默认账号: admin / admin888  |  Z / z888888")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
