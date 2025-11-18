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


class AssessmentSelectorDialog(QDialog):
    """弹药选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择毁伤效能评估结果")
        self.resize(1000, 600)

        self.selected_assessment = None  # 选中的弹药信息
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
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

    def _load_data(self):
        """加载毁伤效能计算结果数据"""
        db = DBHelper()
        try:
            from damage_models.sql_repository_dbhelper import AssessmentResultRepository
            assessment_repo = AssessmentResultRepository(db)
            assessments = assessment_repo.get_all()
            # 设置表格模型
            headers = ["毁伤结果ID", "场景ID", "弹坑深度", "弹坑直径", "弹坑容积",
                      "弹坑面积", "弹坑长度", "弹坑宽度", "结构破坏程度", "毁伤等级"]

            model = QStandardItemModel(0, len(headers))
            model.setHorizontalHeaderLabels(headers)

            if assessments:
                for row_data in assessments:
                    row = []
                    row.append(QStandardItem(str(row_data.DAID)))
                    row.append(QStandardItem(str(row_data.DSID)))
                    row.append(QStandardItem(str(row_data.DADepth)))
                    row.append(QStandardItem(str(row_data.DADiameter)))
                    row.append(QStandardItem(str(row_data.DAVolume)))
                    row.append(QStandardItem(str(row_data.DAArea)))
                    row.append(QStandardItem(str(row_data.DALength)))
                    row.append(QStandardItem(str(row_data.DAWidth)))
                    row.append(QStandardItem(str(row_data.Discturction)))
                    row.append(QStandardItem(row_data.DamageDegree))
                    model.appendRow(row)

            self.table_view.setModel(model)

            # 调整列宽
            header = self.table_view.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载毁伤效能计算结果数据失败：{e}")
        finally:
            db.close()

    def _on_row_double_clicked(self, index):
        """双击行事件"""
        self._on_select()

    def _on_select(self):
        """选择按钮点击"""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "提示", "请先选择一条计算结果记录")
            return

        # 获取选中行的结果ID
        row = selection.currentIndex().row()
        model = self.table_view.model()
        assessment_id = int(model.item(row, 0).text())

        # 从数据库查询完整的弹药信息
        db = DBHelper()
        try:
            from damage_models.sql_repository_dbhelper import AssessmentResultRepository
            assessment_repo = AssessmentResultRepository(db)
            damage_assessment = assessment_repo.get_by_id(assessment_id)

            if damage_assessment:
                self.selected_assessment = damage_assessment
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "无法获取毁伤效能计算结果详细信息")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"查询弹药信息失败：{e}")
        finally:
            db.close()

    def get_selected_assessment(self):
        """获取选中的弹药信息"""
        return self.selected_assessment


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AssessmentSelectorDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        assessment = dialog.get_selected_assessment()
        print("选中的毁伤计算结果:", assessment)

