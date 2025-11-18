import sys
import os
import configparser  # 新增：用于读取配置文件
from pathlib import Path

project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录
# 2. 将项目根目录添加到Python的模块搜索路径
sys.path.append(str(project_root))
CONFIG_PATH = project_root / "config.ini"

class ConfigHelper:
    """配置文件读取工具类"""

    def __init__(self):
        self.config_path = CONFIG_PATH
        self.config = configparser.ConfigParser()
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在：{self.config_path}")
        # 读取配置文件
        self.config.read(self.config_path, encoding="utf-8")

    def get_db_config(self):
        """获取数据库配置"""
        if "Database" not in self.config.sections():
            raise KeyError("配置文件中缺少[Database]节点")

        return {
            "db_type": self.config.get("Database", "db_type", fallback="mysql"),
            "host": self.config.get("Database", "host", fallback="localhost"),
            "user": self.config.get("Database", "user", fallback="root"),
            "password": self.config.get("Database", "password", fallback=""),
            "db_name": self.config.get("Database", "db_name", fallback=""),
            "mysqldump_path": self.config.get("Database", "mysqldump_path", fallback=""),
            "mysql_path": self.config.get("Database", "mysql_path", fallback="")
        }

    def get_backup_config(self):
        """获取备份路径配置"""
        if "Backup" not in self.config.sections():
            raise KeyError("配置文件中缺少[Backup]节点")

        return {
            "auto_backup_path": self.config.get("Backup", "auto_backup_path", fallback="./auto_backups"),
            "manual_backup_path": self.config.get("Backup", "manual_backup_path", fallback="./manual_backups")
        }