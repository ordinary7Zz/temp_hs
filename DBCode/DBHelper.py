import mysql.connector
from loguru import logger
from mysql.connector import Error

from BusinessCode.Config import load_config
from DBCode.ConfigHelper import ConfigHelper

class DBHelper:
    def __init__(self):
        self.conn = None
        self. confighelper = ConfigHelper()
        self.db_config = self.confighelper.get_db_config()
        try:
            self.conn = mysql.connector.connect(
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                database=self.db_config["db_name"],
            )
            if self.conn.is_connected():
                print("数据库连接成功")
        except Error as e:
            print(f"数据库连接失败: {e}")

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())

            # 如果是 SELECT 查询，立即读取所有结果
            if query.strip().lower().startswith('select'):
                result = cursor.fetchall()
                cursor.close()
                return result  # 返回结果数据，而不是 cursor
            else:
                # 对于 INSERT、UPDATE、DELETE 等操作
                self.conn.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows

        except Exception as e:
            print(f"执行SQL失败: {e}")
            self.conn.rollback()
            return None

    def fetch_all(self, query, params=None):
        # 现在 execute_query 直接返回结果
        result = self.execute_query(query, params)
        return result if result is not None else []

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("数据库连接已关闭")

