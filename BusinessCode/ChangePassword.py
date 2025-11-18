import sys
from pathlib import Path
from typing import Optional

# 兼容脚本直接运行与包导入的路径设置
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox, QPushButton
from UIs.Frm_ChangePassword import Ui_Frm_ChangePassword  # 导入自动生成的界面类
from DBCode.DBHelper import DBHelper
import bcrypt


class ChangePasswordWindow(QDialog, Ui_Frm_ChangePassword):
    def __init__(self, username):
        super().__init__()
        # 初始化界面（调用Ui_MainWindow的setupUi方法）
        self.setupUi(self)
        self.dbhelper = DBHelper()
        self.username = username
        self.txt_UserName.setText(self.username)
        # 绑定登录按钮点击事件
        self.btn_Save.clicked.connect(self.change_password)
        self.btn_Clear.clicked.connect(self.clear_input)
        self.setFixedSize(400, 280)



    def change_password(self):
        # 获取输入的用户名和密码（实际项目中应对接数据库验证）
        username = self.txt_UserName.text().strip()
        oldpwd = self.txt_OldPwd.text().strip()
        newpwd1 = self.txt_NewPwd1.text().strip()
        newpwd2 = self.txt_NewPwd2.text().strip()

        # 输入验证
        if not username:
            QMessageBox.warning(self, "错误提示", "用户名为空，请重新返回窗体")
            self.txt_UserName.setFocus()
        elif not oldpwd:
            QMessageBox.warning(self, "输入错误", "请输入当前密码")
            self.txt_OldPwd.setFocus()
        elif not newpwd1:
            QMessageBox.warning(self, "输入错误", "请输入新密码")
            self.txt_NewPwd1.setFocus()
        elif not newpwd2:
            QMessageBox.warning(self, "输入错误", "请输入确认密码")
            self.txt_NewPwd2.setFocus()
        elif newpwd1 != newpwd2:
            QMessageBox.warning(self, "输入错误", "新密码和确认密码不一致，请重新输入")
            self.txt_NewPwd2.setFocus()
        else:
            # 3. 验证当前密码是否正确
            result = self.dbhelper.execute_query("SELECT UPassword FROM user_info WHERE username=%s", (self.username,))
            if not result:
                QMessageBox.warning(self, "错误", "用户不存在")
                return
            else:
                pwd_db =  result[0]['UPassword'].encode('utf-8')
                if bcrypt.checkpw(oldpwd.encode('utf-8'), pwd_db):  # 用 sha256 生成哈希
                    # 4. 更新新密码
                    hashed_password = bcrypt.hashpw(newpwd1.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    self.dbhelper.execute_query("UPDATE user_info SET UPassword=%s WHERE username=%s", (hashed_password, self.username))
                    QMessageBox.information(self, "成功", "密码修改成功")
                    self.clear_input()
                else:
                    QMessageBox.warning(self, "错误", "当前密码不正确" )
                    return


    # 清空控件信息
    def clear_input(self):
        """清空输入框"""
        self.txt_OldPwd.clear()
        self.txt_NewPwd1.clear()
        self.txt_NewPwd2.clear()
        self.txt_OldPwd.setFocus()


if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = ChangePasswordWindow()
    window.show()

    sys.exit(app.exec())
