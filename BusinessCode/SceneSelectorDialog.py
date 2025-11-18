"""
场景选择器对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from DBCode.DBHelper import DBHelper
from damage_models.sql_repository_dbhelper import DamageSceneRepository
from loguru import logger


class SceneSelectorDialog(QDialog):
    """场景选择器对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_scene = None
        self.setWindowTitle("选择毁伤场景")
        self.resize(900, 600)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # # 搜索栏
        # search_layout = QHBoxLayout()
        # search_layout.addWidget(QLabel("搜索:"))
        # self.ed_search = QLineEdit()
        # self.ed_search.setPlaceholderText("输入场景编号或名称...")
        # search_layout.addWidget(self.ed_search)
        # self.btn_search = QPushButton("搜索")
        # self.btn_search.clicked.connect(self.load_data)
        # search_layout.addWidget(self.btn_search)
        # search_layout.addStretch()
        # layout.addLayout(search_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "场景ID", "场景编号", "场景名称", "弹药ID", "目标类型", "状态"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_ok = QPushButton("确定")
        self.btn_ok.clicked.connect(self.on_ok)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def load_data(self):
        """加载场景数据"""
        try:
            db = DBHelper()
            try:
                repo = DamageSceneRepository(db)
                # search_keyword = self.ed_search.text().strip()

                scenes = repo.get_all()

                self.table.setRowCount(0)

                target_type_map = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}

                for scene in scenes:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    self.table.setItem(row, 0, QTableWidgetItem(str(scene.DSID)))
                    self.table.setItem(row, 1, QTableWidgetItem(scene.DSCode or ""))
                    self.table.setItem(row, 2, QTableWidgetItem(scene.DSName or ""))
                    self.table.setItem(row, 3, QTableWidgetItem(str(scene.AMID) if scene.AMID else ""))
                    self.table.setItem(row, 4, QTableWidgetItem(target_type_map.get(scene.TargetType, "")))
                    self.table.setItem(row, 5, QTableWidgetItem(str(scene.DSStatus) if scene.DSStatus is not None else ""))

                    # 存储完整数据
                    self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, scene)

            finally:
                db.close()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载场景数据失败：{e}")

    def on_double_click(self):
        """双击选择"""
        self.on_ok()

    def on_ok(self):
        """确定按钮"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            scene = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_scene = {
                'DSID': scene.DSID,
                'DSCode': scene.DSCode,
                'DSName': scene.DSName,
                'AMID': scene.AMID,
                'TargetType': scene.TargetType,
                'TargetID': scene.TargetID
            }
            self.accept()
        else:
            QMessageBox.warning(self, "提示", "请选择一个场景")

    def get_selected_scene(self):
        """获取选择的场景"""
        return self.selected_scene
