import sys
from pathlib import Path
from venv import logger

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from BusinessCode.Config import ConfigEditorDialog
from DBCode.DBHelper import DBHelper
from UIs.Frm_MainWindow import Ui_Frm_MainWindow  # 导入自动生成的界面类
from BusinessCode.XT_UserManagement import UserManagement
from BusinessCode.XT_DataRestore import DataRestore
from BusinessCode.DM_Ammunition_M import DYListWindow
from BusinessCode.Target_UCC_M import Target_UCC_MWindow
from BusinessCode.Target_Shelter_M import Target_Shelter_MWindow
from BusinessCode.Target_Runway_M import Target_Runway_MWindow
from BusinessCode.PG_DamageScene_M import DamageSceneListWindow
from BusinessCode.PG_DamageParameter_M import DamageParameterListWindow
from BusinessCode.PG_AssessmentResult_M import AssessmentResultListWindow
from BusinessCode.PG_AssessmentReport_M import AssessmentReportListWindow
from BusinessCode.Search_Ammunition import AmmunitionSearch
from BusinessCode.ChangePassword import ChangePasswordWindow
from BusinessCode.Search_Report import AssessmentReportSearchDialog
from BusinessCode.Search_Targets import RunwayTargetSearchDialog
from BusinessCode.UserContext import set_user

# 1. 获取项目根目录的绝对路径（根据实际结构调整）
# 这里假设main.py的父目录（folder_a）与项目根目录（project）的关系是：project/folder_a/main.py
# 因此通过"./"回到项目根目录
project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录

# 2. 将项目根目录添加到Python的模块搜索路径
sys.path.append(str(project_root))


class MainWindow(QMainWindow):
    def __init__(self, username, truename, urole):
        # 先初始化父类 QMainWindow
        super(QMainWindow, self).__init__()  # 显式指定初始化 QMainWindow
        self.ui = Ui_Frm_MainWindow()
        # 再调用界面类的 setupUi 方法，传入自身（MainWindow 实例）
        self.ui.setupUi(self)  # 关键：将 MainWindow 作为参数传给 setupUi
        # 设置工具栏
        self.init_toolbar()
        # 设置状态栏
        self.username = username
        self.truename = truename
        self.urole = urole
        self.user_label = QLabel(f"当前登录用户姓名：{self.truename}，   用户身份：{self.urole}")
        self.ui.statusbar.addPermanentWidget(self.user_label, 1)
        self.setRoleAccess()  # 设置用户访问权限

        sql = """SELECT UID, UserName FROM User_Info WHERE UserName LIKE %s"""
        db = DBHelper()

        user_res = db.execute_query(sql, (username,))
        set_user(user_res[0]['UID'], user_res[0]['UserName'])


        # 添加主窗口的菜单事件
        self.ui.menu_AmmunitionManagement.triggered.connect(self.menu_AmmunitionManagement_click)
        self.ui.menu_RunwayManagement.triggered.connect(self.menu_RunwayManagement_click)
        self.ui.menu_ShelterManagement.triggered.connect(self.menu_ShelterManagement_click)
        self.ui.menu_UCCManagement.triggered.connect(self.menu_UCCManagement_click)
        self.ui.menu_DamageScene.triggered.connect(self.menu_DamageScene_click)
        self.ui.menu_DamageParameter.triggered.connect(self.menu_DamageParameter_click)
        self.ui.menu_DamageAssessment.triggered.connect(self.menu_AssessmentResult_click)
        self.ui.menu_AssessmentReport.triggered.connect(self.menu_AssessmentReport_click)
        self.ui.menu_ReportQuery.triggered.connect(self.menu_ReportQuery_click)
        self.ui.menu_AmmunitionQuery.triggered.connect(self.menu_AmmunitionQuery_click)
        self.ui.menu_TargetQuery.triggered.connect(self.menu_TargetQuery_click)

        self.ui.menu_UserMag.triggered.connect(self.menu_usermag_click)
        self.ui.menu_ChangePwd.triggered.connect(self.menu_changepwd_click)
        self.ui.menu_DataRestore.triggered.connect(self.menu_datarestore_click)
        self.ui.menu_Config.triggered.connect(self.menu_config_click)

    def init_toolbar(self):
        # ====== 2. 设置工具栏高度 ======
        # 方法1：设置最小高度（推荐，简单直接）
        self.ui.toolBar.setMinimumHeight(60)  # 高度设置为60px

        # 添加 QPushButton
        btn_amm = QPushButton("弹药毁伤数据模型管理", self)
        btn_amm.setIcon(QIcon("./UIStyles/images/ico1.png"))
        btn_amm.setToolTip("弹药毁伤数据模型管理")
        btn_amm.setIconSize(QSize(32, 32))  # 32x32像素
        self.ui.toolBar.addWidget(btn_amm)  # 添加按钮到工具栏
        btn_amm.clicked.connect(self.menu_AmmunitionManagement_click)

        self.ui.toolBar.addSeparator()

        # 添加 QPushButton
        btn_runway = QPushButton("机场跑道数据管理", self)
        btn_runway.setIcon(QIcon("./UIStyles/images/ico1_72.png"))
        btn_runway.setToolTip("机场跑道数据管理")
        btn_runway.setIconSize(QSize(32, 32))  # 32x32像素
        self.ui.toolBar.addWidget(btn_runway)  # 添加按钮到工具栏
        btn_runway.clicked.connect(self.menu_RunwayManagement_click)

        # 添加 QPushButton
        btn_shelter = QPushButton("单机掩蔽库数据管理", self)
        btn_shelter.setIcon(QIcon("./UIStyles/images/ico_2_72.png"))
        btn_shelter.setToolTip("单机掩蔽库数据管理")
        btn_shelter.setIconSize(QSize(32, 32))  # 32x32像素
        self.ui.toolBar.addWidget(btn_shelter)  # 添加按钮到工具栏
        btn_shelter.clicked.connect(self.menu_ShelterManagement_click)

        # 添加 QPushButton
        btn_ucc = QPushButton("地下指挥所数据管理", self)
        btn_ucc.setIcon(QIcon("./UIStyles/images/ico_3_72.png"))
        btn_ucc.setToolTip("地下指挥所数据管理")
        btn_ucc.setIconSize(QSize(32, 32))  # 32x32像素
        self.ui.toolBar.addWidget(btn_ucc)  # 添加按钮到工具栏
        btn_ucc.clicked.connect(self.menu_UCCManagement_click)

        self.ui.toolBar.addSeparator()

        btn_calc = QPushButton("毁伤效能计算评估", self)
        btn_calc.setIcon(QIcon("./UIStyles/images/ico3_72.png"))
        btn_calc.setToolTip("毁伤效能计算评估")
        btn_calc.setIconSize(QSize(32, 32))
        self.ui.toolBar.addWidget(btn_calc)
        btn_calc.clicked.connect(self.menu_AssessmentResult_click)

    # 根据用户角色设置访问权限
    def setRoleAccess(self):
        # 如果是系统用户，则不能查看用户管理，数据备份，系统配置
        if (self.urole == "系统用户"):
            self.ui.menu_DataRestore.setVisible(False)
            self.ui.menu_UserMag.setVisible(False)
            self.ui.menu_Config.setVisible(False)

    # 单击机场跑道数据管理
    def menu_AmmunitionManagement_click(self):
        self.frm_AmmunitionManage = DYListWindow()
        self.frm_AmmunitionManage.exec()

    # 单击机场跑道数据管理
    def menu_RunwayManagement_click(self):
        self.frm_RunwayManage = Target_Runway_MWindow()
        self.frm_RunwayManage.exec()

    # 单击掩蔽库数据管理
    def menu_ShelterManagement_click(self):
        self.frm_ShelterManage = Target_Shelter_MWindow()
        self.frm_ShelterManage.exec()

    # 地下指挥所数据管理
    def menu_UCCManagement_click(self):
        self.frm_UCCManage = Target_UCC_MWindow()
        self.frm_UCCManage.exec()

    # 毁伤场景设置
    def menu_DamageScene_click(self):
        self.frm_DamageScene = DamageSceneListWindow()
        self.frm_DamageScene.exec()

    # 毁伤参数管理
    def menu_DamageParameter_click(self):
        self.frm_DamageParameter = DamageParameterListWindow()
        self.frm_DamageParameter.exec()

    # 毁伤能力计算
    def menu_AssessmentResult_click(self):
        self.frm_AssessmentResult = AssessmentResultListWindow()
        self.frm_AssessmentResult.exec()

    # 毁伤评估报告管理
    def menu_AssessmentReport_click(self):
        self.frm_AssessmentReport = AssessmentReportListWindow()
        self.frm_AssessmentReport.exec()

    def menu_ReportQuery_click(self):
        self.frm_AssessmentReportSearch = AssessmentReportSearchDialog(self)
        self.frm_AssessmentReportSearch.exec()

    def menu_AmmunitionQuery_click(self):
        self.Frm_Search_Ammunition = AmmunitionSearch()
        self.Frm_Search_Ammunition.exec()

    # 打击目标检索
    def menu_TargetQuery_click(self):
        """Open the default runway intelligent search dialog."""
        self.frm_TargetSearch = RunwayTargetSearchDialog(self)
        self.frm_TargetSearch.exec()

    # 系统用户管理
    def menu_usermag_click(self):
        self.frm_usermag = UserManagement()
        self.frm_usermag.exec()

    def menu_changepwd_click(self):
        self.frm_changepwd = ChangePasswordWindow(self.username)
        self.frm_changepwd.exec()

    # 数据备份和恢复
    def menu_datarestore_click(self):
        self.frm_datarestore = DataRestore(self.username)
        self.frm_datarestore.exec()

    def menu_config_click(self):
        self.frm_config = ConfigEditorDialog()
        self.frm_config.show()


if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
