"""
毁伤能力计算列表
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMessageBox, QPushButton,
    QHBoxLayout, QHeaderView, QDialog
)
from PyQt6.QtCore import pyqtSignal

from UIs.Frm_PG_AssessmentResult import Ui_Frm_PG_AssessmentResult
from damage_models.sql_repository_dbhelper import AssessmentResultRepository
from DBCode.DBHelper import DBHelper
from loguru import logger


class AssessmentResultListWindow(QDialog):
    """毁伤结果列表窗口"""

    def __init__(self, parent=None):
        try:
            super().__init__(parent)

            # 创建中心部件
            from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy
            cw = QWidget()
            self.ui = Ui_Frm_PG_AssessmentResult()
            self.ui.setupUi(cw)

            # 设置中心部件的大小策略为扩展
            cw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # 设置对话框布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(cw)

            self.setWindowTitle("毁伤能力计算")

            # 按钮绑定
            self.ui.btn_add.clicked.connect(self._on_btn_add_clicked)
            self.ui.btn_export.clicked.connect(self._on_btn_export_clicked)
            #self.ui.btn_search.clicked.connect(self._on_btn_search_clicked)

            self.setup_table()

            # 设置窗口大小
            self.resize(1000, 600)

            logger.info("毁伤能力计算窗口初始化成功")
        except Exception as e:
            logger.exception(f"毁伤能力计算窗口初始化失败: {e}")
            QMessageBox.critical(None, "错误", f"窗口初始化失败：{str(e)}\n\n详细信息请查看日志")
            raise

    def _on_btn_export_clicked(self):
        """导出按钮点击"""
        try:
            from BusinessCode.PG_AssessmentResult_Export import AssessmentResultExportDialog
            dlg = AssessmentResultExportDialog(self)
            dlg.exec()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"打开导出窗口失败：{e}")

    def _on_btn_add_clicked(self):
        """添加按钮点击"""
        try:
            from BusinessCode.PG_AssessmentResult_Add import AssessmentResultEditor, AssessmentResultEditorMode
            self.edit_win = AssessmentResultEditor(
                parent=self,
                mode=AssessmentResultEditorMode.Add
            )
            self.edit_win.finished_with_result.connect(self.on_edit_done)
            self.edit_win.show()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"打开添加窗口失败：{e}")

    # def _on_btn_search_clicked(self):
    #     """搜索按钮点击"""
    #     keyword = self.ui.ed_search.text().strip()
    #     self.setup_table(keyword)

    def setup_table(self, search_keyword: str = ""):
        """设置表格数据"""
        tv = self.ui.tb_assessment_result

        headers = [
            "结果ID", "场景ID", "参数ID", "弹药ID", "目标类型", "目标ID",
            "弹坑深度(m)", "弹坑直径(m)", "弹坑容积(m³)", "弹坑面积(m²)",
            "结构破坏", "毁伤等级", "创建时间", "操作"
        ]

        table = QStandardItemModel(0, len(headers), tv)
        table.setHorizontalHeaderLabels(headers)
        tv.setModel(table)

        hh = tv.horizontalHeader()
        # 所有列都根据内容调整
        for i in range(len(headers)):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        tv.verticalHeader().setVisible(False)
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

        # 从数据库读取数据
        db_data = []
        db = DBHelper()
        try:
            repo = AssessmentResultRepository(db)
            if search_keyword:
                db_data = repo.search(search_keyword)
            else:
                db_data = repo.get_all()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"读取数据库失败：{e}")
            return
        finally:
            db.close()

        logger.debug(f"查询到 {len(db_data)} 条毁伤结果记录")

        # 目标类型映射
        target_type_map = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}

        for row_id, result in enumerate(db_data):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QStandardItem(str(result.DAID or "")))
            table.setItem(row_id, 1, QStandardItem(str(result.DSID or "")))
            table.setItem(row_id, 2, QStandardItem(str(result.DPID or "")))
            table.setItem(row_id, 3, QStandardItem(str(result.AMID or "")))
            table.setItem(row_id, 4, QStandardItem(target_type_map.get(result.TargetType, "未知")))
            table.setItem(row_id, 5, QStandardItem(str(result.TargetID or "")))
            table.setItem(row_id, 6, QStandardItem(str(result.DADepth) if result.DADepth else ""))
            table.setItem(row_id, 7, QStandardItem(str(result.DADiameter) if result.DADiameter else ""))
            table.setItem(row_id, 8, QStandardItem(str(result.DAVolume) if result.DAVolume else ""))
            table.setItem(row_id, 9, QStandardItem(str(result.DAArea) if result.DAArea else ""))
            table.setItem(row_id, 10, QStandardItem(str(result.Discturction) if result.Discturction else ""))
            table.setItem(row_id, 11, QStandardItem(result.DamageDegree or ""))
            table.setItem(row_id, 12, QStandardItem(
                result.CreatedTime.strftime('%Y-%m-%d %H:%M:%S') if result.CreatedTime else ""
            ))

            # 操作列：添加编辑和删除按钮
            self._add_action_buttons(tv, table, row_id, len(headers) - 1, result.DAID)

        logger.info(f"毁伤结果数据加载完成，共 {len(db_data)} 条")

    def _add_action_buttons(self, tv, table, row, col, result_id: int):
        """添加操作按钮"""
        w = QWidget(tv)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_edit = QPushButton("编辑", w)
        btn_del = QPushButton("删除", w)

        btn_edit.clicked.connect(lambda: self._on_edit(result_id))
        btn_del.clicked.connect(lambda: self._on_delete(tv, table, row, result_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        index = table.index(row, col)
        tv.setIndexWidget(index, w)

    def _on_edit(self, result_id: int):
        """编辑结果"""
        try:
            from BusinessCode.PG_AssessmentResult_Add import AssessmentResultEditor, AssessmentResultEditorMode
            self.edit_win = AssessmentResultEditor(
                parent=self,
                mode=AssessmentResultEditorMode.Edit,
                edit_result_id=result_id
            )
            self.edit_win.finished_with_result.connect(self.on_edit_done)
            self.edit_win.show()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"打开编辑窗口失败：{e}")

    def on_edit_done(self, result):
        """编辑完成回调"""
        logger.info(f"编辑完成，结果：{result}")
        self.setup_table()

    def _on_delete(self, tv, table, row, result_id: int):
        """删除结果"""
        result_daid = table.index(row, 0).data()
        ok = QMessageBox.question(
            tv,
            "确认删除",
            f"确定删除毁伤结果 ID={result_daid} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ok == QMessageBox.StandardButton.Yes:
            db = DBHelper()
            try:
                repo = AssessmentResultRepository(db)
                if repo.delete(result_id):
                    QMessageBox.information(self, "成功", "删除成功")
                    self.setup_table()
                else:
                    QMessageBox.warning(self, "失败", "删除失败")
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"删除失败：{e}")
            finally:
                db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssessmentResultListWindow()
    window.show()
    sys.exit(app.exec())

