from __future__ import annotations
import os
from contextlib import contextmanager
from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

from BusinessCode.Config import load_config

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


class Base(DeclarativeBase):
    pass


def _build_url():
    raw = (os.getenv("DATABASE_URL") or "").strip()
    if raw:
        return raw  # assume already URL-encoded

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
def session_scope() -> Iterator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
