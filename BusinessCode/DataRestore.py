import sys
from pathlib import Path
from UIs.Frm_DataRestore import Ui_Frm_DataRestore  # 导入自动生成的界面类
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGroupBox, QRadioButton,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QTableWidget, QTableWidgetItem, QFileDialog)
import sys
import shutil
import os
from datetime import datetime
#from DBCode.DBHelper import DBHelper
import os
import subprocess
import datetime
from typing import Tuple, List, Dict
# 导入现有数据库连接工具（假设DBHelper提供数据库配置获取功能）
from DBCode.DBHelper import DBHelper  # 假设该类包含数据库连接配置


# 1. 获取项目根目录的绝对路径（根据实际结构调整）
# 这里假设main.py的父目录（folder_a）与项目根目录（project）的关系是：project/folder_a/main.py
# 因此通过"./"回到项目根目录
project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录

# 2. 将项目根目录添加到Python的模块搜索路径
sys.path.append(str(project_root))

class DataRestore(QMainWindow, Ui_Frm_DataRestore):
    def __init__(self):
        self.backup_records: List[Dict[str, str]] = []  # 备份记录
        self.db_helper = DBHelper()  # 实例化现有数据库连接工具
        self._load_backup_records()  # 加载历史记录

    def _get_db_config(self) -> Dict[str, str]:
        """从DBHelper获取数据库配置（适配现有连接逻辑）"""
        # 假设DBHelper提供以下方法获取配置，根据实际情况调整
        return {
            "host": self.db_helper.get_host(),
            "user": self.db_helper.get_user(),
            "password": self.db_helper.get_password(),
            "db_name": "AD_DB",  # 固定备份AD_DB数据库
            "charset": self.db_helper.get_charset() or "utf8mb4"
        }

    def validate_connection(self) -> Tuple[bool, str]:
        """通过DBHelper验证数据库连接（复用现有连接逻辑）"""
        try:
            # 假设DBHelper有测试连接的方法
            if self.db_helper.test_connection():
                return True, "数据库连接正常"
            else:
                return False, "数据库连接失败，请检查配置"
        except Exception as e:
            return False, f"连接验证异常：{str(e)}"

    def check_backup_env(self) -> Tuple[bool, str]:
        """检查备份所需环境（mysqldump工具）"""
        try:
            # 检查mysqldump是否可用
            subprocess.run(
                ["mysqldump", "--version"],
                capture_output=True,
                check=True,
                text=True
            )
            return True, "备份环境正常"
        except FileNotFoundError:
            return False, "未找到mysqldump工具，请配置MySQL环境变量"
        except Exception as e:
            return False, f"环境检查失败：{str(e)}"

    def backup_database(self, backup_path: str, is_auto: bool = False) -> Tuple[bool, str, Dict[str, str] | None]:
        """
        备份AD_DB数据库（使用DBHelper的配置）
        :param backup_path: 备份文件存储路径
        :param is_auto: 是否为自动备份
        """
        # 1. 验证前置条件
        conn_ok, conn_msg = self.validate_connection()
        if not conn_ok:
            return False, conn_msg, None

        env_ok, env_msg = self.check_backup_env()
        if not env_ok:
            return False, env_msg, None

        # 2. 准备配置和路径
        db_config = self._get_db_config()
        os.makedirs(backup_path, exist_ok=True)  # 确保目录存在

        # 3. 生成备份文件名（带时间戳）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_path, f"AD_DB_{timestamp}.sql")

        # 4. 构建mysqldump命令（使用DBHelper中的配置）
        cmd = [
            "mysqldump",
            f"--host={db_config['host']}",
            f"--user={db_config['user']}",
            f"--password={db_config['password']}",
            db_config["db_name"],
            f"--result-file={backup_file}",
            f"--default-character-set={db_config['charset']}"
        ]

        # 5. 执行备份
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                # 记录备份信息
                backup_record = {
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "自动备份" if is_auto else "手动备份",
                    "path": backup_file,
                    "size": f"{os.path.getsize(backup_file) // 1024}KB"
                }
                self.backup_records.insert(0, backup_record)
                self._save_backup_records()  # 持久化记录
                return True, f"备份成功：{backup_file}", backup_record
            else:
                error_msg = result.stderr.split("\n")[0] if result.stderr else "未知错误"
                return False, f"备份失败：{error_msg}", None

        except subprocess.TimeoutExpired:
            return False, "备份超时（超过5分钟）", None
        except Exception as e:
            return False, f"备份异常：{str(e)}", None

    def restore_database(self, backup_file: str) -> Tuple[bool, str]:
        """
        从备份文件恢复AD_DB数据库（使用DBHelper的配置）
        :param backup_file: 备份文件路径
        """
        # 1. 验证前置条件
        if not os.path.exists(backup_file):
            return False, f"备份文件不存在：{backup_file}"

        conn_ok, conn_msg = self.validate_connection()
        if not conn_ok:
            return False, conn_msg

        env_ok, env_msg = self.check_backup_env()
        if not env_ok:
            return False, env_msg

        # 2. 获取数据库配置
        db_config = self._get_db_config()

        # 3. 先创建数据库（如果不存在）
        try:
            # 使用DBHelper执行SQL（复用现有连接）
            create_sql = f"CREATE DATABASE IF NOT EXISTS `{db_config['db_name']}` CHARACTER SET {db_config['charset']};"
            self.db_helper.execute_sql(create_sql)  # 假设DBHelper有执行SQL的方法
        except Exception as e:
            return False, f"创建数据库失败：{str(e)}"

        # 4. 执行恢复命令（mysql客户端导入）
        cmd = [
            "mysql",
            f"--host={db_config['host']}",
            f"--user={db_config['user']}",
            f"--password={db_config['password']}",
            db_config["db_name"],
            f"--default-character-set={db_config['charset']}"
        ]

        try:
            with open(backup_file, 'r', encoding=db_config['charset']) as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

            if result.returncode == 0:
                return True, "数据恢复成功"
            else:
                error_msg = result.stderr.split("\n")[0] if result.stderr else "未知错误"
                return False, f"恢复失败：{error_msg}"

        except subprocess.TimeoutExpired:
            return False, "恢复超时（超过5分钟）"
        except Exception as e:
            return False, f"恢复异常：{str(e)}"

    def get_all_backups(self) -> List[Dict[str, str]]:
        """获取所有备份记录"""
        return self.backup_records

    def delete_backup(self, backup_path: str) -> Tuple[bool, str]:
        """删除备份文件及记录"""
        try:
            # 删除文件
            if os.path.exists(backup_path):
                os.remove(backup_path)
            # 删除记录
            self.backup_records = [r for r in self.backup_records if r["path"] != backup_path]
            self._save_backup_records()  # 更新持久化记录
            return True, "备份已删除"
        except Exception as e:
            return False, f"删除失败：{str(e)}"

    def _load_backup_records(self) -> None:
        """从文件加载备份记录（实际可根据需求实现）"""
        # 示例：从JSON文件加载，实际可替换为数据库存储
        record_file = os.path.join(os.getcwd(), "backup_records.json")
        if os.path.exists(record_file):
            import json
            with open(record_file, 'r', encoding='utf-8') as f:
                self.backup_records = json.load(f)

    def _save_backup_records(self) -> None:
        """持久化备份记录（实际可根据需求实现）"""
        record_file = os.path.join(os.getcwd(), "backup_records.json")
        import json
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(self.backup_records, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = DataRestore()
    window.show()
    sys.exit(app.exec())