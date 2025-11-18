import sys
from pathlib import Path
from loguru import logger

# Ensure project root is on sys.path when running directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QDialog, QAbstractItemView, QTableWidgetItem, QMessageBox, QHeaderView
from UIs.Frm_UserManagement import Ui_Frm_UserManagement  # 导入自动生成的界面类
from DBCode.DBHelper import DBHelper
import bcrypt
import datetime


class UserManagement(QDialog):
    """User management dialog used for admin maintenance and registration."""

    user_registered = pyqtSignal(str)

    def __init__(self, registration_mode: bool = False):
        super().__init__()
        self.registration_mode = registration_mode

        # 组合式：持有 Ui 实例，并在其中构建界面
        self.ui = Ui_Frm_UserManagement()
        self.ui.setupUi(self)

        self.db = DBHelper()
        self.ischeckusername = False  # track username availability check
        self.current_user_id = None
        self.init_ui()
        self.load_user_data()
        self.setFixedSize(840, 630)

    def init_ui(self) -> None:
        """Initialise combo boxes, signals and table defaults."""
        self.ui.txt_UStatus.clear()
        self.ui.txt_UStatus.addItems(["启用", "禁用"])
        self.ui.txt_UStatus.setCurrentIndex(0)  # 默认选中第一个选项

        # 初始化用户角色
        self.ui.txt_URole.clear()
        self.ui.txt_URole.addItems(["系统用户", "系统管理员"])
        self.ui.txt_URole.setCurrentIndex(0)

        self.ui.btn_Save.clicked.connect(self.save_user)
        self.ui.btn_Check.clicked.connect(self.check_username)
        self.ui.btn_Clear.clicked.connect(self.clear_input)
        self.ui.btn_Delete.clicked.connect(self.delete_user)
        self.ui.btn_ResetPwd.clicked.connect(self.resetpwd)
        self.ui.tv_UserInfo.clicked.connect(self.select_user)

        self.ui.tv_UserInfo.setColumnCount(9)
        self.ui.tv_UserInfo.setHorizontalHeaderLabels([
            "用户ID",
            "用户名",
            "真实姓名",
            "用户角色",
            "单位部门",
            "联系电话",
            "用户状态",
            "创建时间",
            "更新时间",
        ])
        header = self.ui.tv_UserInfo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tv_UserInfo.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tv_UserInfo.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def load_user_data(self) -> None:

        self.ui.tv_UserInfo.setRowCount(0)
        users = self.db.fetch_all("SELECT * FROM User_Info")
        for row, user in enumerate(users):
            self.ui.tv_UserInfo.insertRow(row)
            self.ui.tv_UserInfo.setItem(row, 0, QTableWidgetItem(str(user.get("UID", ""))))  # 用户名
            self.ui.tv_UserInfo.setItem(row, 1, QTableWidgetItem(str(user.get("UserName", ""))))  # 用户名
            self.ui.tv_UserInfo.setItem(row, 2, QTableWidgetItem(user.get("TrueName", "")))  # 真实姓名
            self.ui.tv_UserInfo.setItem(row, 3, QTableWidgetItem(
                "系统用户" if str(user.get("URole", "")) == "0" else "系统管理员"))
            self.ui.tv_UserInfo.setItem(row, 4, QTableWidgetItem(user.get("Department", "")))  # 单位部门
            self.ui.tv_UserInfo.setItem(row, 5, QTableWidgetItem(user.get("Telephone", "")))  # 联系电话
            self.ui.tv_UserInfo.setItem(row, 6, QTableWidgetItem(
                "启用" if str(user.get("UStatus", "")) == "1" else "禁用"))  # 用户状态
            self.ui.tv_UserInfo.setItem(row, 7, QTableWidgetItem(str(user.get("CreatedTime", ""))))  # 创建时间
            self.ui.tv_UserInfo.setItem(row, 8, QTableWidgetItem(str(user.get("UpdatedTime", ""))))  # 更新时间
            logger.info(str(user.get("UID", "")))
        self.setup_table_view()

    # 检测用户名是否已经存在
    def check_username(self):
        username = self.ui.txt_UserName.text().strip()
        if not username:
            self.ui.lab_Note.text = "请输入用户名后再检测！"
            self.ui.lab_Note.setStyleSheet("color: red;")
            return

        try:
            result = None
            # 查询条件：用户名相同，且排除当前修改的用户（如果是修改操作）
            if self.current_user_id:
                sql = "SELECT UID FROM User_Info WHERE username = %s AND UID != %s"
                result = self.db.fetch_all(sql, (username, self.current_user_id))
            else:
                sql = "SELECT UID FROM User_Info WHERE username = %s"
                result = self.db.fetch_all(sql, (username,))

            if result:
                self.ui.lab_Note.setText("该用户名已存在，请更换！")
                self.ui.lab_Note.setStyleSheet("color: red;")
            else:
                self.ui.lab_Note.setText("用户名可用！")
                self.ui.lab_Note.setStyleSheet("color: green;")
                self.ui.ischeckusername = True
        except Exception as e:
            self.ui.lab_Note.setText(f"检测失败：{str(e)}")

    def validate_required(self) -> bool:
        # 定义必填字段（控件变量 -> 字段名称）
        required = {
            self.ui.txt_TrueName: "真实姓名",
            self.ui.txt_Department: "单位部门",
            self.ui.txt_UserName: "用户名",
            self.ui.txt_Telephone: "联系电话",
            self.ui.txt_UPassword: "密码"
        }
        for var, field_name in required.items():
            if not var.text().strip():
                self.ui.lab_Note.setText(f"{field_name}为必填项，请填写完整！")
                self.ui.lab_Note.setStyleSheet("color: red;")
                return False
        return True

    def setup_table_view(self) -> None:
        """Tune table appearance for better readability."""
        self.ui.tv_UserInfo.resizeColumnsToContents()
        header = self.ui.tv_UserInfo.horizontalHeader()
        header.setStretchLastSection(True)
        self.ui.tv_UserInfo.setAlternatingRowColors(True)
        self.ui.tv_UserInfo.setShowGrid(True)
        self.ui.tv_UserInfo.setStyleSheet(
            "QTableView {gridline-color: #d0d0d0; alternate-background-color: #f8f8f8;}"
        )

    def save_user(self) -> None:
        """Handle create or update operations for a user."""
        if not self.validate_required():
            return

        username = self.ui.txt_UserName.text().strip()
        if not username:
            QMessageBox.warning(self, "Validation", "Username is required.")
            self.ui.txt_UserName.setFocus()
            self.ischeckusername = False
            return

        # 如果是添加用户，则要检测用户名
        if not self.current_user_id:
            if not self.ischeckusername:  # 如果还没检测，就要检测
                if not self.check_username():
                    return

        true_name = self.ui.txt_TrueName.text().strip()
        department = self.ui.txt_Department.text().strip()
        position = self.ui.txt_UPosition.text().strip()
        password = self.ui.txt_UPassword.text().strip()
        user_role = self.ui.txt_URole.currentIndex()
        telephone = self.ui.txt_Telephone.text().strip()
        address = self.ui.txt_Address.text().strip()
        user_status = 1 if self.ui.txt_UStatus.currentIndex() == 0 else 0  # 用户状态(1表示启用, 0表示禁用)
        remark = self.ui.txt_URemark.text().strip()

        try:
            if self.current_user_id:
                query = """
                        UPDATE User_Info
                        SET TrueName   = %s,
                            Department = %s,
                            UPosition  = %s,
                            UserName   = %s,
                            URole      = %s,
                            Telephone  = %s,
                            Address    = %s,
                            UStatus    = %s,
                            URemark    = %s,
                            UpdatedTime=%s
                        WHERE UID = %s \
                        """
                params = (true_name, department, position, username, user_role, telephone, address, user_status, remark,
                          datetime.datetime.now(), self.current_user_id)
                logger.debug(f"params: {params}")
                self.db.execute_query(query, params)
                QMessageBox.information(self, "操作成功", "用户信息修改成功！")
                self.clear_input()
            else:
                hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                query = """
                        INSERT INTO User_Info (TrueName, Department, UPosition, UserName,
                                               UPassword, URole, Telephone, Address, UStatus, URemark, CreatedTime)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                params = (true_name, department, position, username, hashed_password, user_role, telephone, address,
                          user_status, remark, datetime.datetime.now())
                self.db.execute_query(query, params)
                QMessageBox.information(self, "操作成功", "用户信息添加成功！")
                self.clear_input()
        except Exception as exc:
            QMessageBox.critical(self, "出错提示", f"用户信息保存失败: {exc}")
            return

        self.load_user_data()

    def select_user(self, index) -> None:
        uid_item = self.ui.tv_UserInfo.item(index.row(), 0)
        if uid_item is None:
            return
        logger.info(uid_item.text())
        uid = int(uid_item.text())
        user_records = self.db.fetch_all("SELECT * FROM User_Info WHERE UID = %s", (uid,))
        if not user_records:
            return
        user = user_records[0]
        self.current_user_id = uid
        self.ui.txt_UserName.setText(user.get("UserName", ""))
        self.ui.txt_TrueName.setText(user.get("TrueName", ""))
        self.ui.txt_Department.setText(user.get("Department", ""))
        self.ui.txt_UPosition.setText(user.get("UPosition", ""))
        self.ui.txt_UPassword.setText("密码不可在此修改")
        self.ui.txt_UserName.setReadOnly(True)
        self.ui.btn_Check.setDisabled(True)
        try:
            self.ui.txt_URole.setCurrentIndex(int(user.get("URole", 0)))
        except Exception:
            self.ui.txt_URole.setCurrentIndex(1)
        self.ui.txt_Telephone.setText(user.get("Telephone", ""))
        self.ui.txt_Address.setText(user.get("Address", ""))
        try:
            i = 0 if int(user.get("UStatus", 0)) == 1 else 1  # 状态0表示禁用, 1表示启用
            self.ui.txt_UStatus.setCurrentIndex(i)
        except Exception:
            self.ui.txt_UStatus.setCurrentIndex(0)
        self.ui.txt_URemark.setText(user.get("URemark", ""))
        self.ui.lbl_status.setText("修改用户信息")
        self.ui.lab_Note.clear()
        self.ischeckusername = False

    def delete_user(self) -> None:
        selection = self.ui.tv_UserInfo.selectedItems()
        if not selection:
            QMessageBox.warning(self, "操作提示", "请先选中要删除的用户！")
            return

        reply = QMessageBox.question(self, "确认删除", "确定要删除选中的用户吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        else:
            uid_item = self.ui.tv_UserInfo.item(self.ui.tv_UserInfo.currentRow(), 0)
            if uid_item is None:
                return
            uid = int(uid_item.text())
            self.db.execute_query("DELETE FROM User_Info WHERE UID = %s", (uid,))
            self.load_user_data()
            QMessageBox.information(self, "操作成功", "用户删除成功！")
            self.clear_input()

    def resetpwd(self) -> None:
        selection = self.ui.tv_UserInfo.selectedItems()
        if not selection:
            QMessageBox.warning(self, "操作提示", "请先选中要重置密码的用户！")
            return

        reply = QMessageBox.question(self, "确认删除", "确定要将选中用户的密码重置为 123456 吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        else:
            uid_item = self.ui.tv_UserInfo.item(self.ui.tv_UserInfo.currentRow(), 0)
            if uid_item is None:
                return
            uid = int(uid_item.text())
            password = "123456"
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            self.db.execute_query("Update User_Info set UPassword=%s WHERE UID = %s", (hashed_password, uid))
            QMessageBox.information(self, "操作成功", "该用户的密码已经重置为 123456")
            self.clear_input()

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    """清空输入框"""

    def clear_input(self) -> None:
        self.ui.txt_TrueName.clear()
        self.ui.txt_Department.clear()
        self.ui.txt_UserName.clear()
        self.ui.txt_UPosition.clear()
        self.ui.txt_Telephone.clear()
        self.ui.txt_Address.clear()
        self.ui.txt_URole.setCurrentIndex(0)
        self.ui.txt_UStatus.setCurrentIndex(0)
        self.ui.txt_UPassword.clear()
        self.ui.txt_URemark.clear()
        self.ui.txt_TrueName.setFocus()
        self.ui.lbl_status.setText("新增用户信息")
        self.ui.lab_Note.clear()
        self.ischeckusername = False
        self.current_user_id = None
        self.ui.txt_UserName.setReadOnly(False)
        self.ui.btn_Check.setEnabled(True)
