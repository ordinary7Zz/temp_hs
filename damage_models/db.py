from __future__ import annotations
import os
import sys
from contextlib import contextmanager
from typing import Iterator

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

from BusinessCode.Config import load_config

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


class Base(DeclarativeBase):
    pass


def _build_url():
    """构建 SQLAlchemy 数据库连接 URL"""
    # 优先使用环境变量，如果没有则使用从 DBHelper 提取的配置
    raw = (os.getenv("DATABASE_URL") or "").strip()
    if raw:
        return raw

    cfg = load_config()
    driver = "mysql+pymysql"
    user = cfg.get("DB_USER", "root")
    pwd = cfg.get("DB_PASS", "123456")
    host = cfg.get("DB_HOST", "127.0.0.1")
    port = int(cfg.get("DB_PORT", "3306"))
    name = cfg.get("DB_NAME", "damassessment_db")
    charset = "utf8mb4"

    return URL.create(
        drivername=driver,
        username=user,
        password=pwd,
        host=host,
        port=port,
        database=name,
        query={"charset": charset},
    )


DATABASE_URL = _build_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)


@contextmanager
def get_session() -> Iterator:
    """上下文管理器：自动开启/关闭会话。"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
