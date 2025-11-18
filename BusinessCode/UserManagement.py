import sys
from pathlib import Path

from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QApplication, QMainWindow, QAbstractItemView, QTableWidgetItem, QMessageBox, QHeaderView
from UIs.Frm_UserManagement import Ui_Frm_UserManagement  # 导入自动生成的界面类
from DBCode.DBHelper import DBHelper
import bcrypt

# 1. 获取项目根目录的绝对路径，通过"./"回到项目根目录
project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录

# 2. 将项目根目录添加到Python的模块搜索路径
sys.path.append(str(project_root))


class UserManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Frm_UserManagement()
        self.ui.setupUi(self)

        self.db = DBHelper()
        self.ischeckusername = False  # 是否已确认用户名可用
        self.current_user_id = None
        self.initial_data = {}

        self.init_ui()
        self.load_user_data()

    # ------------------------------ UI 初始化 ------------------------------
    def init_ui(self):
        # 用户状态
        self.ui.txt_UStatus.addItems(["启用", "禁用"])
        self.ui.txt_UStatus.setCurrentIndex(0)

        # 用户角色
        self.ui.txt_URole.addItems(["系统用户", "系统管理员"])
        self.ui.txt_URole.setCurrentIndex(0)

        # 信号连接
        self.ui.btn_Save.clicked.connect(self.save_user)
        self.ui.btn_Check.clicked.connect(self.check_username)
        self.ui.tv_UserInfo.clicked.connect(self.select_user)

        # 表格头与选择行为
        self.ui.tv_UserInfo.setColumnCount(8)
        self.ui.tv_UserInfo.setHorizontalHeaderLabels(
            ["用户ID", "真实姓名", "用户名", "用户角色", "联系电话", "单位部门", "职务职位", "用户状态"]
        )
        header = self.ui.tv_UserInfo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tv_UserInfo.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tv_UserInfo.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    # ------------------------------ 加载列表 ------------------------------
    def load_user_data(self):
        self.ui.tv_UserInfo.setRowCount(0)
        users = self.db.fetch_all("SELECT * FROM User_Info")
        for row, user in enumerate(users):
            self.ui.tv_UserInfo.insertRow(row)
            self.ui.tv_UserInfo.setItem(row, 0, QTableWidgetItem(str(user.get("UID", ""))))
            self.ui.tv_UserInfo.setItem(row, 1, QTableWidgetItem(user.get("TrueName", "")))
            self.ui.tv_UserInfo.setItem(row, 2, QTableWidgetItem(user.get("UserName", "")))
            role_text = "系统用户" if int(user.get("URole", 0)) == 0 else "系统管理员"
            self.ui.tv_UserInfo.setItem(row, 3, QTableWidgetItem(role_text))
            self.ui.tv_UserInfo.setItem(row, 4, QTableWidgetItem(user.get("Telephone", "")))
            self.ui.tv_UserInfo.setItem(row, 5, QTableWidgetItem(user.get("Department", "")))
            self.ui.tv_UserInfo.setItem(row, 6, QTableWidgetItem(user.get("UPosition", "")))
            status_text = "启用" if int(user.get("UStatus", 0)) == 0 else "禁用"
            self.ui.tv_UserInfo.setItem(row, 7, QTableWidgetItem(status_text))

            # 表格样式与行为
            self.setup_table_view()

    def setup_table_view(self):
        tv = self.ui.tv_UserInfo
        tv.resizeColumnsToContents()
        tv.setAlternatingRowColors(True)
        tv.setShowGrid(True)
        tv.setStyleSheet("""
            QTableView {
                gridline-color: #d0d0d0;
                alternate-background-color: #f8f8f8;
            }
            QTableView::item { padding: 5px; }
        """)

    # ------------------------------ 校验 ------------------------------
    def validate_required(self):
        required = {
            self.ui.txt_TrueName: "真实姓名",
            self.ui.txt_Department: "单位部门",
            self.ui.txt_UserName: "用户名",
            self.ui.txt_Telephone: "联系电话",
            self.ui.txt_UPassword: "密码",
        }
        for w, name in required.items():
            if not w.text().strip():
                self.ui.lab_Note.setText(f"{name}为必填项，请填写完整！")
                self.ui.lab_Note.setStyleSheet("color: red;")
                return False
        return True

    # ------------------------------ 用户名重名检测 ------------------------------
    def check_username(self):
        username = self.ui.txt_UserName.text().strip()
        if not username:
            self.ui.lab_Note.setText("请输入用户名后再检测！")
            self.ui.lab_Note.setStyleSheet("color: red;")
            return

        try:
            if self.current_user_id:
                sql = "SELECT UID FROM User_Info WHERE UserName = %s AND UID != %s"
                result = self.db.fetch_all(sql, (username, self.current_user_id))
            else:
                sql = "SELECT UID FROM User_Info WHERE UserName = %s"
                result = self.db.fetch_all(sql, (username,))

            if result:
                self.ui.lab_Note.setText("该用户名已存在，请更换！")
                self.ui.lab_Note.setStyleSheet("color: red;")
                self.ischeckusername = False
            else:
                self.ui.lab_Note.setText("用户名可用！")
                self.ui.lab_Note.setStyleSheet("color: green;")
                self.ischeckusername = True
        except Exception as e:
            self.ui.lab_Note.setText(f"检测失败：{e}")

    # ------------------------------ 保存/新增/修改 ------------------------------
    def save_user(self):
        if not self.validate_required():
            return
        if not self.ischeckusername:
            self.ui.lab_Note.setText("请先确认用户名是否可用")
            self.ui.lab_Note.setStyleSheet("color: red;")
            return

        true_name = self.ui.txt_TrueName.text().strip()
        department = self.ui.txt_Department.text().strip()
        position = self.ui.txt_UPosition.text().strip()
        username = self.ui.txt_UserName.text().strip()
        password = self.ui.txt_UPassword.text().strip()
        user_role = self.ui.txt_URole.currentIndex()
        telephone = self.ui.txt_Telephone.text().strip()
        address = self.ui.txt_Address.text().strip()
        user_status = self.ui.txt_UStatus.currentIndex()
        remark = self.ui.txt_URemark.text().strip()

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        if self.current_user_id:
            query = """
                    UPDATE User_Info
                    SET TrueName=%s,
                        Department=%s,
                        UPosition=%s,
                        UserName=%s,
                        UPassword=%s,
                        URole=%s,
                        Telephone=%s,
                        Address=%s,
                        UStatus=%s,
                        URemark=%s
                    WHERE UID = %s \
                    """
            params = (
                true_name, department, position, username,
                hashed_password, user_role, telephone, address,
                user_status, remark, self.current_user_id
            )
            self.db.execute_query(query, params)
            QMessageBox.information(self, "操作成功", "用户信息修改成功！")
        else:
            try:
                query = """
                        INSERT INTO User_Info
                        (TrueName, Department, UPosition, UserName,
                         UPassword, URole, Telephone, Address, UStatus, URemark)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                        """
                params = (
                    true_name, department, position, username,
                    hashed_password, user_role, telephone, address,
                    user_status, remark
                )
                self.db.execute_query(query, params)
                QMessageBox.information(self, "操作成功", "用户信息添加成功！")
                self.clear_input()
            except Exception as e:
                print(f"用户信息添加失败: {e}")
                return

        self.load_user_data()

    # ------------------------------ 选择行回填 ------------------------------
    def select_user(self, index: QModelIndex):
        uid = int(self.ui.tv_UserInfo.item(index.row(), 0).text())
        user = self.db.fetch_all("SELECT * FROM User_Info WHERE UID = %s", (uid,))[0]

        self.current_user_id = uid
        self.ui.txt_TrueName.setText(user.get("TrueName", ""))
        self.ui.txt_Department.setText(user.get("Department", ""))
        self.ui.txt_UPosition.setText(user.get("UPosition", ""))
        self.ui.txt_UserName.setText(user.get("UserName", ""))
        self.ui.txt_UPassword.setText("密码不可在此修改")
        self.ui.txt_URole.setCurrentIndex(int(user.get("URole", 0)))
        self.ui.txt_Telephone.setText(user.get("Telephone", ""))
        self.ui.txt_Address.setText(user.get("Address", ""))
        self.ui.txt_UStatus.setCurrentIndex(int(user.get("UStatus", 0)))
        self.ui.txt_URemark.setText(user.get("URemark", ""))
        self.ui.lbl_status.setText("当前状态：修改用户")

    # ------------------------------ 删除用户 ------------------------------
    def delete_user(self):
        tv = self.ui.tv_UserInfo
        if not tv.selectedItems():
            QMessageBox.warning(self, "操作提示", "请先选中要删除的用户！")
            return

        reply = QMessageBox.question(
            self, "确认删除", "确定要删除选中的用户吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            uid = int(tv.item(tv.currentRow(), 0).text())
            self.db.execute_query("DELETE FROM User_Info WHERE UID = %s", (uid,))
            self.load_user_data()
            QMessageBox.information(self, "操作成功", "用户删除成功！")
            self.reset_form()

    # ------------------------------ 复位表单 ------------------------------
    def reset_form(self):
        self.ui.txt_TrueName.clear()
        self.ui.txt_Department.clear()
        self.ui.txt_UPosition.clear()
        self.ui.txt_UserName.clear()
        self.ui.txt_UPassword.clear()
        self.ui.txt_URole.setCurrentIndex(0)
        self.ui.txt_Telephone.clear()
        self.ui.txt_Address.clear()
        self.ui.txt_UStatus.setCurrentIndex(0)
        self.ui.txt_URemark.clear()
        self.current_user_id = None
        self.ui.lbl_status.setText("当前状态：新增用户")
        self.initial_data = {}
        self.ischeckusername = False
        self.ui.lab_Note.clear()

    # ------------------------------ 关闭 ------------------------------
    def closeEvent(self, event):
        self.db.close()
        event.accept()

    # ------------------------------ 清空 ------------------------------
    def clear_input(self):
        self.ui.txt_TrueName.clear()
        self.ui.txt_Department.clear()
        self.ui.txt_UserName.clear()
        self.ui.txt_UPosition.clear()
        self.ui.txt_Telephone.clear()
        self.ui.txt_Address.clear()
        self.ui.txt_URole.setCurrentIndex(0)
        self.ui.txt_UStatus.setCurrentIndex(0)
        self.ui.txt_URemark.clear()
        self.ui.txt_TrueName.setFocus()
        self.ui.lbl_status.setText("当前状态：新增用户")


if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = UserManagement()
    window.show()
    sys.exit(app.exec())
