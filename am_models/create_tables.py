from __future__ import annotations
from .db import engine, Base


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_all_tables()
    print("Tables created (if not exist).")
