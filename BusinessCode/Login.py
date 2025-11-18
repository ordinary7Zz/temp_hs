import sys
from pathlib import Path
from typing import Optional

from loguru import logger

# 兼容脚本直接运行与包导入的路径设置
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
# from qt_material import apply_stylesheet   #皮肤控件
from UIs.Frm_Login import Ui_Frm_Login  # 导入自动生成的界面类
from BusinessCode.MainWindow import MainWindow  # 导入自动生成的界面类
from BusinessCode.XT_UserManagement import UserManagement
from DBCode.DBHelper import DBHelper
import bcrypt


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ---- 组合式 UI ----
        self.ui = Ui_Frm_Login()
        self.ui.setupUi(self)

        self.dbhelper = DBHelper()

        # 绑定信号
        self.ui.btn_Login.clicked.connect(self.check_login)
        self.ui.txt_Pwd.returnPressed.connect(self.check_login)
        self.ui.btn_Clear.clicked.connect(self.clear_input)

        self.setFixedSize(400, 280)
        self.load_bgimage()  # 加载LOGO图片

        # # 注册按钮置于登录与清空按钮之间
        # self.btn_Register = QPushButton("注册", self)
        # self.btn_Register.setFixedSize(self.btn_Login.size())
        # self.btn_Register.clicked.connect(self.open_registration_dialog)
        # self._last_registered_user: Optional[str] = None
        # self._layout_action_buttons()

    def open_registration_dialog(self) -> None:
        dialog = UserManagement(registration_mode=True)
        dialog.user_registered.connect(self.on_user_registered)
        self._last_registered_user = None
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted and self._last_registered_user:
            QMessageBox.information(
                self,
                "注册成功",
                f"用户 {self._last_registered_user} 注册成功，请使用设置的密码登录。",
            )
        dialog.deleteLater()

    def on_user_registered(self, username: str) -> None:
        self._last_registered_user = username
        self.ui.txt_UserName.setText(username)
        self.ui.txt_Pwd.clear()
        self.ui.txt_Pwd.setFocus()

    def _layout_action_buttons(self) -> None:
        """将登录/注册/清空按钮居中排列。"""
        button_width = self.ui.btn_Login.width()
        button_height = self.ui.btn_Login.height()
        button_y = self.ui.btn_Login.y()
        spacing = 12
        total_width = 3 * button_width + 2 * spacing
        start_x = max(10, int((self.width() - total_width) / 2))

        self.ui.btn_Login.setGeometry(start_x, button_y, button_width, button_height)
        # self.btn_Register.setGeometry(start_x + button_width + spacing, button_y, button_width, button_height)
        self.ui.btn_Clear.setGeometry(
            start_x + 2 * (button_width + spacing),
            button_y,
            button_width,
            button_height,
        )

    def check_login(self):
        username = self.ui.txt_UserName.text().strip()
        password = self.ui.txt_Pwd.text().strip()

        # 输入验证
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            self.ui.txt_UserName.setFocus()
        elif not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            self.ui.txt_Pwd.setFocus()
        else:
            # 查询用户信息（使用参数化查询防止SQL注入）
            query = 'SELECT TrueName,URole, UPassword, UStatus FROM User_Info  WHERE UserName = %s'
            result = self.dbhelper.execute_query(query, (username,))
            # 简单验证
            if result:
                pwd_db = result[0]['UPassword'].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), pwd_db):  # 用 sha256 生成哈希
                    if result[0]['UStatus'] == 1:  # 状态1表示启用
                        truename = result[0]['TrueName']
                        urole = "系统管理员" if str(result[0]['URole']) == "1" else "系统用户"
                        self.mainwindow = MainWindow(username, truename, urole)  # 尝试创建并显示主窗口
                        self.mainwindow.showMaximized()  # 打开主窗体并最大化
                        self.close()  # 关闭登录窗口
                    else:
                        QMessageBox.warning(self, "错误", "对不起，该用户名处于禁用状态，请联系系统管理员！")
                else:
                    QMessageBox.warning(self, "错误", "对不起，密码不正确，请重新输入！")
                    self.ui.txt_Pwd.setFocus()
            else:
                QMessageBox.warning(self, "错误", "用户名不存在，请重新输入！")
                self.ui.txt_UserName.setFocus()

    # 清空控件信息
    def clear_input(self):
        """清空输入框"""
        self.ui.txt_UserName.clear()
        self.ui.txt_Pwd.clear()
        self.ui.txt_UserName.setFocus()

    # Load the system logo image
    def load_bgimage(self):
        # Load image from disk (absolute or project-relative path)
        # Example for absolute path: D:/images/test.png
        bg_path = project_root / "UIstyles" / "images" / "bg2.png"
        pixmap = QPixmap(str(bg_path))  # load image from project assets
        if pixmap.isNull():
            # Display placeholder text if the image cannot be loaded
            self.ui.lbl_bg.setText(f"Image load failed. Check path: {bg_path}")
        else:
            # Scale pixmap to fit the label while keeping aspect ratio
            # This avoids distortion when resizing the window
            scaled_pixmap = pixmap.scaled(
                self.ui.lbl_bg.width(),
                self.ui.lbl_bg.height(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,  # 保持宽高比（PyQt6 中需指定枚举类型）
                transformMode=Qt.TransformationMode.SmoothTransformation  # 平滑缩放
            )
            self.ui.lbl_bg.setPixmap(scaled_pixmap)

            # 4. 设置标签对齐方式（居中显示）
            self.ui.lbl_bg.setAlignment(Qt.AlignmentFlag.AlignTop)


# 加载皮肤控件
def load_skin(app):
    # apply_stylesheet(app, theme="light_lightgreen.xml")
    qss_path = project_root / "UIstyles" / "QSS" / "Ubuntu.qss"
    if not qss_path.is_file():
        print(f"Warning: 未找到样式文件 {qss_path}")
        return
    with qss_path.open("r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())


if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    load_skin(app)  # 加载皮肤控件
    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
