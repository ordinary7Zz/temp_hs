"""
场景选择对话框
用于在毁伤参数中选择毁伤场景
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLineEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from DBCode.DBHelper import DBHelper
from loguru import logger


class SceneSelectorDialog(QDialog):
    """场景选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择毁伤场景")
        self.resize(1000, 600)

        self.selected_scene = None
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索场景:"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("输入场景编号或名称...")
        search_layout.addWidget(self.ed_search)

        self.btn_search = QPushButton("搜索")
        self.btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self.btn_search)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 表格区域
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table_view.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table_view)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_select = QPushButton("选择")
        self.btn_select.clicked.connect(self._on_select)
        btn_layout.addWidget(self.btn_select)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _load_data(self, keyword: str = ""):
        """加载场景数据"""
        db = DBHelper()
        try:
            if keyword:
                sql = """
                SELECT DSID, DSCode, DSName, DSOffensive, DSDefensive, DSBattle,
                       AMCode, TargetCode, DSStatus
                FROM DamageScene_Info
                WHERE (DSCode LIKE %s OR DSName LIKE %s)
                ORDER BY DSID DESC
                """
                pattern = f'%{keyword}%'
                result = db.execute_query(sql, (pattern, pattern))
            else:
                sql = """
                SELECT DSID, DSCode, DSName, DSOffensive, DSDefensive, DSBattle,
                       AMCode, TargetCode, DSStatus
                FROM DamageScene_Info
                ORDER BY DSID DESC
                LIMIT 100
                """
                result = db.execute_query(sql)

            # 设置表格模型
            headers = ["场景ID", "场景编号", "场景名称", "进攻方", "假想敌",
                      "所在战场", "弹药代码", "目标代码", "状态"]

            model = QStandardItemModel(0, len(headers))
            model.setHorizontalHeaderLabels(headers)

            if result:
                status_map = {0: "草稿", 1: "活跃", 2: "归档"}
                for row_data in result:
                    row = []
                    row.append(QStandardItem(str(row_data.get('DSID', ''))))
                    row.append(QStandardItem(row_data.get('DSCode', '')))
                    row.append(QStandardItem(row_data.get('DSName', '')))
                    row.append(QStandardItem(row_data.get('DSOffensive', '')))
                    row.append(QStandardItem(row_data.get('DSDefensive', '')))
                    row.append(QStandardItem(row_data.get('DSBattle', '')))
                    row.append(QStandardItem(row_data.get('AMCode', '')))
                    row.append(QStandardItem(row_data.get('TargetCode', '')))
                    status = status_map.get(row_data.get('DSStatus'), '')
                    row.append(QStandardItem(status))
                    model.appendRow(row)

            self.table_view.setModel(model)

            # 调整列宽
            header = self.table_view.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载场景数据失败：{e}")
        finally:
            db.close()

    def _on_search(self):
        """搜索按钮点击"""
        keyword = self.ed_search.text().strip()
        self._load_data(keyword)

    def _on_row_double_clicked(self, index):
        """双击行事件"""
        self._on_select()

    def _on_select(self):
        """选择按钮点击"""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "提示", "请先选择一条场景记录")
            return

        # 获取选中行的数据
        row = selection.currentIndex().row()
        model = self.table_view.model()

        self.selected_scene = {
            'DSID': int(model.item(row, 0).text()),
            'DSCode': model.item(row, 1).text(),
            'DSName': model.item(row, 2).text(),
        }

        self.accept()

    def get_selected_scene(self):
        """获取选中的场景信息"""
        return self.selected_scene


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = SceneSelectorDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        scene = dialog.get_selected_scene()
        print("选中的场景:", scene)

