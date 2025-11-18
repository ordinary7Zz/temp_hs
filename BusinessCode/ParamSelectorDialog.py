"""
参数选择器对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from DBCode.DBHelper import DBHelper
from damage_models.sql_repository_dbhelper import DamageParameterRepository
from loguru import logger


class ParamSelectorDialog(QDialog):
    """参数选择器对话框"""

    def __init__(self, parent=None, scene_id: int = 0):
        super().__init__(parent)
        self.selected_param = None
        self.scene_id = scene_id
        self.setWindowTitle("选择毁伤参数")
        self.resize(900, 600)
        self.setup_ui()
        self.load_data()


    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "参数ID", "投放平台", "制导方式", "战斗部类型", "装药量", "投弹高度"
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
        """加载参数数据"""
        try:
            db = DBHelper()
            try:
                repo = DamageParameterRepository(db)
                params = repo.get_by_scene_id(self.scene_id)

                self.table.setRowCount(0)

                target_type_map = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}

                for param in params:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    self.table.setItem(row, 0, QTableWidgetItem(str(param.DPID)))
                    self.table.setItem(row, 1, QTableWidgetItem(param.Carrier))
                    self.table.setItem(row, 2, QTableWidgetItem(param.GuidanceMode))
                    self.table.setItem(row, 3, QTableWidgetItem(param.WarheadType))
                    self.table.setItem(row, 4, QTableWidgetItem(str(param.ChargeAmount)))
                    self.table.setItem(row, 5, QTableWidgetItem(str(param.DropHeight)))

                    # 存储完整数据
                    self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, param)

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
            param = self.table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_param = param
            self.accept()
        else:
            QMessageBox.warning(self, "提示", "请选择一个场景")

    def get_selected_param(self):
        """获取选择的场景"""
        return self.selected_param
