import sys
from pathlib import Path
from UIs.Frm_DataRestore import Ui_Frm_DataRestore  # 导入自动生成的界面类
from PyQt6.QtWidgets import (QApplication, QDialog, QMessageBox, QMainWindow, QGroupBox, QRadioButton,
                             QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QWidget, QTableWidget, QTableWidgetItem, QFileDialog, QButtonGroup)
import sys
import shutil
import os
import os
import subprocess
import datetime
from typing import Tuple, List, Dict
# 导入现有数据库连接工具（假设DBHelper提供数据库配置获取功能）
from DBCode.DBHelper import DBHelper  # 假设该类包含数据库连接配置
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
import uuid
from PyQt6.QtGui import QStandardItemModel, QStandardItem

# 1. 获取项目根目录的绝对路径（根据实际结构调整）
# 这里假设main.py的父目录（folder_a）与项目根目录（project）的关系是：project/folder_a/main.py
# 因此通过"./"回到项目根目录
project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录

# 2. 将项目根目录添加到Python的模块搜索路径
sys.path.append(str(project_root))

class DataRestore(QDialog, Ui_Frm_DataRestore):
    def __init__(self, username):
        super().__init__()
        self.setupUi(self)
        self.username = username
#        self.backup_config["manual_backup_path"]="D:\\"
        self.backup_records: List[Dict[str, str]] = []  # 备份记录
        self.db_helper = DBHelper()  # 实例化现有数据库连接工具

        self.group1 = QButtonGroup(self)  # 父对象设为窗口，自动管理生命周期
        self.group1.addButton(self.rb_AutoBackup, id=1)  # id可选，用于标识选中的按钮
        self.group1.addButton(self.rb_ManualBackup, id=2)
        self.rb_AutoBackup.setChecked(True)  #设置自动备份默认选中
        self.rb_AutoBackup.setChecked(True)
        self.txt_ResotrePath.setReadOnly(True)
        self.txt_BackupPath.setReadOnly(True)

        #self._load_backup_records()  # 加载历史记录
        self.btn_SelectPath.clicked.connect(self.select_backup_path)
        # 定时备份计时器
        #self.auto_timer = QTimer(self)
        #self.auto_timer.timeout.connect(self._auto_backup_task)
        # 2. 初始化倒计时定时器（每秒触发一次）
        self.rb_AutoBackup.setChecked(True)
        self.rb_weekly.setChecked(True)
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.update_remaining_time)  # 绑定刷新函数
        self.next_backup_time = None  # 存储下一次备份的时间
        self.auto_cycle_sec = 0  # 存储自动备份周期的总秒数（如每周=604800秒）

        # ---------- 关联信号与槽 ----------
        self.rb_AutoBackup.toggled.connect(self._setup_auto_backup)
        self.rb_weekly.toggled.connect(self._setup_auto_backup)
        self.rb_monthly.toggled.connect(self._setup_auto_backup)
        self.rb_quarterly.toggled.connect(self._setup_auto_backup)
        self.rb_yearly.toggled.connect(self._setup_auto_backup)
        self.btn_Backup.clicked.connect(self._do_manual_backup)
        self.tv_BackupList.clicked.connect(self._on_backup_selected)
        self.btn_Restore.clicked.connect(self._do_restore)

        # 初始化TableView模型
        self.load_backup_data()

        # 检查自动备份是否默认勾选，若勾选则启动倒计时
        if self.rb_AutoBackup.isChecked():
            self._setup_auto_backup()  # 主动触发启动逻辑

        # 需要备份和恢复的表
        self.TARGET_TABLES = [
            "Ammunition_Info",
            "Runway_Info",
            "Shelter_Info",
            "UCC_Info",
            "DamageScene_Info",
            "DamageParameter_Info",
            "Assessment_Result",
            "Assessment_Report"
            #"DataBackup_Records",
            #"DataRestore_Records",
            #"User_Info"
        ]



    def load_backup_data(self) -> None:
        # 1. 给QTableWidget设置列数（和表头数量一致）
        self.tv_BackupList.setColumnCount(9)  # 对应8个列

        # 2. 设置水平表头（显示列名称）
        self.tv_BackupList.setHorizontalHeaderLabels([
            "备份ID", "备份类型", "备份周期", "备份路径",
            "备份文件名", "版本号", "状态", "备份时间", "备注信息"
        ])
        # 4. 清空原有数据（避免重复加载）
        self.tv_BackupList.setRowCount(0)
        datalist = self.db_helper.fetch_all("SELECT * FROM DataBackup_Records ORDER BY BackupTime DESC")
        for row, data in enumerate(datalist):
            self.tv_BackupList.insertRow(row)
            self.tv_BackupList.setItem(row, 0, QTableWidgetItem(str(data.get("BackupID", ""))))
            backtype = "自动定期备份" if  data.get("BackType", "")  ==1 else "手动立即备份"
            self.tv_BackupList.setItem(row, 1, QTableWidgetItem(backtype))
            self.tv_BackupList.setItem(row, 2, QTableWidgetItem(data.get("BackupCycle", "")))
            self.tv_BackupList.setItem(row, 3, QTableWidgetItem(data.get("BackupPath", "")))
            self.tv_BackupList.setItem(row, 4, QTableWidgetItem(data.get("BackupFile", "")))
            self.tv_BackupList.setItem(row, 5, QTableWidgetItem(data.get("VersionNo", "")))
            self.tv_BackupList.setItem(row, 6, QTableWidgetItem(data.get("BackupStatus", "")))
            self.tv_BackupList.setItem(row, 7, QTableWidgetItem(str(data.get("BackupTime", ""))))
            self.tv_BackupList.setItem(row, 8, QTableWidgetItem(data.get("Remark", "")))

        # 6. 自动调整列宽（让内容完整显示）
        self.tv_BackupList.resizeColumnsToContents()
        self.setup_table_view()

    def setup_table_view(self) -> None:
        """Tune table appearance for better readability."""
        self.tv_BackupList.resizeColumnsToContents()
        header = self.tv_BackupList.horizontalHeader()
        header.setStretchLastSection(True)
        self.tv_BackupList.setAlternatingRowColors(True)
        self.tv_BackupList.setShowGrid(True)
        self.tv_BackupList.setStyleSheet(
            "QTableView {gridline-color: #d0d0d0; alternate-background-color: #f8f8f8;}"
        )

    # 选择备份路径功能
    def select_backup_path(self):
        """选择备份目录并填充到输入框"""
        # 打开目录选择对话框
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "选择备份路径",
            # 默认路径：当前输入框内容或配置的手动备份路径
            self.txt_BackupPath.text().strip(),
            QFileDialog.Option.ShowDirsOnly  # 仅显示目录
        )
        if selected_path:  # 用户选择了路径
            self.txt_BackupPath.setText(selected_path)

    #设置自动定期备份
    def _setup_auto_backup(self):
        """设置自动备份定时任务"""
        is_rb_AutoBackup_checked = self.rb_AutoBackup.isChecked()
        if not is_rb_AutoBackup_checked:
            # 关闭自动备份时，停止倒计时并清空显示
            self.auto_timer.stop()
            self.lbl_remaintime.clear()
            self.next_backup_time = None
            return

        # 获取选中的周期
        cycle_map = {
            #self.rb_weekly: ("每周", 60 * 60 * 24 * 7),
            self.rb_weekly: ("每周", 30),
            self.rb_monthly: ("每月", 60 * 60 * 24 * 30),
            self.rb_quarterly: ("每季度", 60 * 60 * 24 * 90),
            self.rb_yearly: ("每年", 60 * 60 * 24 * 365)
        }

        # 获取用户选择的周期
        selected_cycle = None
        for rb, (name, sec) in cycle_map.items():
            if rb.isChecked():
                selected_cycle = (name, sec)
                break

        if not selected_cycle:
            QMessageBox.warning(self, "提示", "请选择自动备份周期")
            self.rb_AutoBackup.setChecked(False)
            return

        # 记录周期名称和总秒数
        self.auto_cycle_name, self.auto_cycle_sec = selected_cycle

        # 计算下一次备份时间：当前时间 + 周期秒数
        self.next_backup_time = datetime.datetime.now() + datetime.timedelta(seconds=self.auto_cycle_sec)

        # 启动自动备份定时器和倒计时定时器
        #self.auto_timer.setInterval(self.auto_cycle_sec * 1000)
        #self.auto_timer.start()
        self.auto_timer.start(1000)  # 每秒刷新一次

    # 自动定期备份
    def _auto_backup_task(self):
        """自动备份任务（定时器触发）"""
        backup_path = self.txt_BackupPath.text().strip()
        backup_file = f"auto_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.sql"
        version = f"V{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        try:
            # 执行备份
            self.backup_db(backup_path, backup_file)
            # 插入记录（BackupType=1=自动）
            self.insert_backup_record(
                backup_type=1,
                cycle=self.auto_cycle_name,
                path=backup_path,
                file=backup_file,
                version=version,
                status="成功",
                operator=self.username
            )
            # 刷新TableView
            self.load_backup_data()
            self.lbl_Note.setText("自动备份完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动备份失败: {str(e)}")


    def _do_manual_backup(self):
        """执行手动备份"""
        if not self.rb_ManualBackup.isChecked():
            QMessageBox.warning(self, "提示", "请选择“手动立即备份”")
            return
        self.lbl_Note.setText("正在执行数据恢复操作...")
        backup_path = self.txt_BackupPath.text().strip()
        if not backup_path:
            QMessageBox.warning(self, "提示", "请输入备份路径")
            return

        # 生成文件名与版本号
        backup_file = f"manual_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.sql"
        version = f"V{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"

        try:
            # 执行备份
            self.backup_db(backup_path, backup_file)
            # 插入记录（BackupType=2=手动）
            self.insert_backup_record(
                backup_type=2,
                cycle="",
                path=backup_path,
                file=backup_file,
                version=version,
                status="成功",
                operator=self.username
            )
            # 刷新TableView
            self.load_backup_data()
            self.lbl_Note.setText("手动备份完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"手动备份失败: {str(e)}")


    def _on_backup_selected(self, index):
        """选中备份记录时，填充恢复路径"""
        if not index.isValid():
            return
        path = self.tv_BackupList.item(index.row(), 3).text()
        file = self.tv_BackupList.item(index.row(), 4).text()
        print(path)
        self.txt_ResotrePath.setText(os.path.join(path, file))


    def _do_restore(self):
        """执行数据恢复"""
        # 获取选中的备份记录
        index  = self.tv_BackupList.selectedIndexes()
        if not index:
            QMessageBox.warning(self, "提示", "请选择要恢复的备份记录")
            return
        row = index[0].row()
        backup_id =self.tv_BackupList.item(row, 0).text()
        backup_path = self.tv_BackupList.item(row, 3).text()
        backup_file = self.tv_BackupList.item(row, 4).text()
        version = self.tv_BackupList.item(row, 5).text()

        # 二次确认
        if QMessageBox.question(self, "确认", "恢复会覆盖当前数据，是否继续？",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return

        try:
            # 执行恢复
            self.restore_db(backup_path, backup_file)
            # 插入恢复记录（状态1=成功）
            self.insert_restore_record(
                backup_id=backup_id,
                path=backup_path,
                file=backup_file,
                version=version,
                status=1,
                operator=self.username
            )
            self.lbl_Note.setText("恢复成功")
        except Exception as e:
            # 插入恢复失败记录（状态0=失败）
            self.insert_restore_record(
                backup_id=backup_id,
                path=backup_path,
                file=backup_file,
                version=version,
                status=0,
                operator=self.username,
                remark=str(e)
            )
            QMessageBox.critical(self, "错误", f"恢复失败: {str(e)}")


    def closeEvent(self, event):
        """窗口关闭时释放资源"""
        self.db_helper.close()
        self.auto_timer.stop()
        event.accept()

    def backup_db(self, backup_path, backup_file):
        """执行数据库备份（MySQL用mysqldump，SQLite用文件复制）"""
        try:
            full_path = os.path.join(backup_path, backup_file)
            os.makedirs(backup_path, exist_ok=True)
            self.mysqldump_path = self.db_helper.db_config["mysqldump_path"]
            # 拼接表名（带空格）
            table_list = " ".join(self.TARGET_TABLES)
            cmd = f'"{self.mysqldump_path}" -u{self.db_helper.db_config["user"]} -p{self.db_helper.db_config["password"]} -h{self.db_helper.db_config["host"]} {self.db_helper.db_config["db_name"]} {table_list}  --skip-add-drop-table  > {full_path}'
            print(f"生成的命令：{cmd}")
            result  = subprocess.run(cmd, shell=True, check=True)
            if result.returncode != 0:
                print(f"mysqldump错误输出: {result.stderr}")  # 控制台打印
            return full_path
        except Exception as e:
            raise Exception(f"备份失败: {str(e)}")

    def insert_backup_record(self, backup_type, cycle, path, file, version, status, operator, remark=""):
        """插入备份记录到DataBackup_Records"""
        try:
            sqlstr = """
                INSERT INTO DataBackup_Records 
                (BackupType, BackupCycle, BackupPath, BackupFile, VersionNo, BackupStatus, BackupTime, Operator, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (backup_type, cycle, path, file, version, status,
                datetime.datetime.now(), operator, remark)
            self.db_helper.execute_query(sqlstr, params)
        except Exception as e:
            raise Exception(f"备份记录插入失败: {str(e)}")

    def restore_db(self, backup_path, backup_file):
        """执行数据库恢复"""
        try:
            full_path = os.path.join(backup_path, backup_file)
            if not os.path.exists(full_path):
                raise FileNotFoundError("备份文件不存在")

            # ===== 1. 删除表 =====
            for table in self.TARGET_TABLES:
                try:
                    self.lbl_Note.setText( f"正在删除原始数据表: {table} ...")
                    self.db_helper.execute_query(f"DROP TABLE IF EXISTS `{table}`;")
                except Exception as e:
                    self.lbl_Note.setText(f"原始数据表删除失败: {str(e)}")

            self.mysql_path = self.db_helper.db_config["mysql_path"]
            cmd = f'"{self.mysql_path}" -u{self.db_helper.db_config["user"]} -p{self.db_helper.db_config["password"]} -h{self.db_helper.db_config["host"]} {self.db_helper.db_config["db_name"]} < "{full_path}"'
            subprocess.run(cmd, shell=True, check=True)
            return full_path
        except Exception as e:
            raise Exception(f"恢复失败: {str(e)}")

    def insert_restore_record(self, backup_id, path, file, version, status, operator, remark=""):
        """插入恢复记录到DataRestore_Records"""
        try:
            sqlstr = """
                INSERT INTO DataRestore_Records 
                (BackupID, RestorePath, RestoreFile, VersionNo, RestoreStatus, RestoreTime, Operator, Remark)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (backup_id, path, file, version, status, datetime.datetime.now(), operator, remark)
            self.db_helper.execute_query(sqlstr, params)
        except Exception as e:
            raise Exception(f"恢复记录插入失败: {str(e)}")

    def update_remaining_time(self):
        if self.next_backup_time is None or self.auto_cycle_sec == 0:
            self.lbl_remaintime.setText("0")
            return

        # 计算当前时间与下一次备份的时间差
        now = datetime.datetime.now()
        time_delta = self.next_backup_time - now
        remaining_sec = int(time_delta.total_seconds())  # 转换为总秒数

        # 若剩余时间≤0，说明到了备份时间
        if remaining_sec <= 0:
            # 触发自动备份任务
            self._auto_backup_task()
            # 重新计算下一次备份时间
            self.next_backup_time = datetime.datetime.now() + datetime.timedelta(seconds=self.auto_cycle_sec)
            remaining_sec = self.auto_cycle_sec  # 重置为周期总秒数

        # 更新到界面显示
        self.lbl_remaintime.setText(str(remaining_sec))

if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = DataRestore()
    window.show()
    sys.exit(app.exec())