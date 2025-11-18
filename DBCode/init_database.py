from __future__ import annotations

import sys
from pathlib import Path
from typing import Final

import bcrypt
from sqlalchemy import text


def _project_root() -> Path:
    root = Path(__file__).resolve().parent
    return root


def _prepare_sys_path() -> Path:
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def _create_ammunition_tables() -> None:
    import am_models.orm  # noqa: F401 - ensures models are registered
    from am_models.db import Base, engine

    Base.metadata.create_all(bind=engine, checkfirst=True)


def _create_target_tables() -> None:
    import target_model.orm  # noqa: F401 - ensures models are registered
    from target_model.db import Base, engine

    Base.metadata.create_all(bind=engine, checkfirst=True)

def _create_damage_tables() -> None:
    import damage_models.orm  # noqa: F401 - ensures models are registered
    from damage_models.db import Base, engine

    Base.metadata.create_all(bind=engine, checkfirst=True)


def _ensure_user_table() -> None:
    from am_models.db import engine

    ddl: Final[str] = """
    CREATE TABLE IF NOT EXISTS User_Info (
        UID INT PRIMARY KEY AUTO_INCREMENT,
        UserName VARCHAR(100) NOT NULL,
        UPassword VARCHAR(100) NOT NULL,
        URole VARCHAR(30) NOT NULL,
        TrueName VARCHAR(100),
        Department VARCHAR(100),
        UPosition VARCHAR(100),
        Telephone VARCHAR(100),
        Address VARCHAR(200),
        UStatus INT,
        URemark TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    default_user_sql: Final[str] = """
    INSERT INTO User_Info (
        UserName, UPassword, URole, TrueName, Department, UPosition,
        Telephone, Address, UStatus, URemark
    )
    VALUES (
        :username, :password, :role, :truename, :department, :position,
        :telephone, :address, :status, :remark
    )
    """

    default_user_params = {
        "username": "admin",
        "password": bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8"),
        "role": "admin",
        "truename": "System Admin",
        "department": "System",
        "position": "Administrator",
        "telephone": "",
        "address": "",
        "status": 1,
        "remark": "Seed user",
    }

    with engine.begin() as connection:
        connection.exec_driver_sql(ddl)
        existing = connection.execute(
            text("SELECT UID FROM User_Info WHERE UserName = :username"),
            {"username": default_user_params["username"]},
        ).first()
        if existing is None:
            connection.execute(text(default_user_sql), default_user_params)


def initialize_database() -> None:
    _prepare_sys_path()
    _create_ammunition_tables()
    _create_target_tables()
    _ensure_user_table()
    _create_damage_tables()


if __name__ == "__main__":
    initialize_database()
    print("Database tables ensured. Default account: admin / 123456")
