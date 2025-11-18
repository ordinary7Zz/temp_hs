"""
弹药选择对话框
用于在毁伤场景中选择弹药
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


class AmmunitionSelectorDialog(QDialog):
    """弹药选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择弹药")
        self.resize(1000, 600)

        self.selected_ammunition = None  # 选中的弹药信息
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 搜索区域
        # search_layout = QHBoxLayout()
        # search_layout.addWidget(QLabel("搜索弹药:"))
        # self.ed_search = QLineEdit()
        # self.ed_search.setPlaceholderText("输入弹药名称或型号...")
        # search_layout.addWidget(self.ed_search)
        #
        # self.btn_search = QPushButton("搜索")
        # self.btn_search.clicked.connect(self._on_search)
        # search_layout.addWidget(self.btn_search)
        #
        # search_layout.addStretch()
        # layout.addLayout(search_layout)

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
        """加载弹药数据"""
        db = DBHelper()
        try:
            if keyword:
                sql = """
                SELECT AMID, AMName, AMNameCN, AMType, AMModel, Country, 
                       WarheadType, WarheadName, ChargeAmount
                FROM Ammunition_Info 
                AND (AMName LIKE %s OR AMNameCN LIKE %s OR AMModel LIKE %s)
                ORDER BY AMID DESC
                """
                pattern = f'%{keyword}%'
                result = db.execute_query(sql, (pattern, pattern, pattern))
            else:
                sql = """
                SELECT AMID, AMName, AMNameCN, AMType, AMModel, Country, 
                       WarheadType, WarheadName, ChargeAmount
                FROM Ammunition_Info 
                ORDER BY AMID DESC
                LIMIT 100
                """
                result = db.execute_query(sql)

            # 设置表格模型
            headers = ["弹药ID", "官方名称", "中文名称", "弹药类型", "弹药型号",
                      "国家", "战斗部类型", "战斗部名称", "装药量(kg)"]

            model = QStandardItemModel(0, len(headers))
            model.setHorizontalHeaderLabels(headers)

            if result:
                for row_data in result:
                    row = []
                    row.append(QStandardItem(str(row_data.get('AMID', ''))))
                    row.append(QStandardItem(row_data.get('AMName', '')))
                    row.append(QStandardItem(row_data.get('AMNameCN', '')))
                    row.append(QStandardItem(row_data.get('AMType', '')))
                    row.append(QStandardItem(row_data.get('AMModel', '')))
                    row.append(QStandardItem(row_data.get('Country', '')))
                    row.append(QStandardItem(row_data.get('WarheadType', '')))
                    row.append(QStandardItem(row_data.get('WarheadName', '')))
                    row.append(QStandardItem(str(row_data.get('ChargeAmount', ''))))
                    model.appendRow(row)

            self.table_view.setModel(model)

            # 调整列宽
            header = self.table_view.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载弹药数据失败：{e}")
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
            QMessageBox.warning(self, "提示", "请先选择一条弹药记录")
            return

        # 获取选中行的弹药ID
        row = selection.currentIndex().row()
        model = self.table_view.model()
        amid = int(model.item(row, 0).text())

        # 从数据库查询完整的弹药信息
        db = DBHelper()
        try:
            from am_models.sql_repository import SQLRepository as AmModelSQLRepository
            from am_models.db import session_scope as AmSessionScope
            with AmSessionScope() as session:
                am_repo = AmModelSQLRepository(session)
            result = am_repo.get(amid)

            if result:
                self.selected_ammunition = result
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "无法获取弹药详细信息")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"查询弹药信息失败：{e}")
        finally:
            db.close()

    def get_selected_ammunition(self):
        """获取选中的弹药信息"""
        return self.selected_ammunition


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AmmunitionSelectorDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        ammo = dialog.get_selected_ammunition()
        print("选中的弹药:", ammo)

