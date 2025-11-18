"""
创建毁伤数据表
"""
from __future__ import annotations
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .db import engine, Base


def create_all_tables() -> None:
    """创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("毁伤数据表创建成功（如果不存在）")


if __name__ == "__main__":
    create_all_tables()
