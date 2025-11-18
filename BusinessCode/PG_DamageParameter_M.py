"""
毁伤参数管理列表
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

from UIs.Frm_PG_DamageParameter import Ui_Frm_PG_DamageParameter
from BusinessCode.PG_DamageParameter_Add import DamageParameterEditor, DamageParameterEditorMode
from BusinessCode.PG_DamageParameter_Export import DamageParameterExportDialog
from damage_models.sql_repository_dbhelper import DamageParameterRepository
from DBCode.DBHelper import DBHelper
from loguru import logger


class DamageParameterListWindow(QDialog):
    """毁伤参数列表窗口"""

    def __init__(self, parent=None):
        try:
            super().__init__(parent)

            # 创建中心部件
            from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy
            cw = QWidget()
            self.ui = Ui_Frm_PG_DamageParameter()
            self.ui.setupUi(cw)

            # 设置中心部件的大小策略为扩展
            cw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # 设置对话框布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(cw)

            self.setWindowTitle("毁伤参数管理")

            # 按钮绑定
            # 注意：毁伤参数只能通过场景界面添加，不提供独立添加功能
            self.ui.btn_add.setVisible(False)  # 隐藏添加按钮
            self.ui.btn_export.clicked.connect(self._on_btn_export_clicked)
            #self.ui.btn_search.clicked.connect(self._on_btn_search_clicked)

            self.setup_table()

            logger.info("毁伤参数管理窗口初始化成功")
        except Exception as e:
            logger.exception(f"毁伤参数管理窗口初始化失败: {e}")
            QMessageBox.critical(None, "错误", f"窗口初始化失败：{str(e)}\n\n详细信息请查看日志")
            raise

    def _on_btn_export_clicked(self):
        """导出按钮点击"""
        try:
            dlg = DamageParameterExportDialog(self)
            dlg.exec()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"打开导出窗口失败：{e}")
            QMessageBox.warning(self, "错误", f"打开添加窗口失败：{e}")

    # def _on_btn_search_clicked(self):
    #     """搜索按钮点击"""
    #     keyword = self.ui.ed_search.text().strip()
    #     self.setup_table(keyword)

    def setup_table(self, search_keyword: str = ""):
        """设置表格数据"""
        tv = self.ui.tb_damage_parameter

        headers = [
            "参数ID", "场景编号", "投放平台", "制导方式", "战斗部类型",
            "装药量(kg)", "投弹高度", "投弹速度(m/s)", "投弹方式",
            "射程(km)", "电磁干扰", "天气", "风速(m/s)", "操作"
        ]

        table = QStandardItemModel(0, len(headers), tv)
        table.setHorizontalHeaderLabels(headers)
        tv.setModel(table)

        hh = tv.horizontalHeader()
        # 所有列都根据内容调整，不使用拉伸模式
        for i in range(len(headers)):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        tv.verticalHeader().setVisible(False)
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

        # 从数据库读取数据
        db_data = []
        db = DBHelper()
        try:
            repo = DamageParameterRepository(db)
            db_data = repo.get_all()

            # 简单搜索过滤
            if search_keyword:
                db_data = [p for p in db_data if search_keyword in p.DSCode]
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"读取数据库失败：{e}")
            return
        finally:
            db.close()

        logger.debug(f"查询到 {len(db_data)} 条毁伤参数记录")

        for row_id, param in enumerate(db_data):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QStandardItem(str(param.DPID or "")))
            table.setItem(row_id, 1, QStandardItem(param.DSCode))
            table.setItem(row_id, 2, QStandardItem(param.Carrier or ""))
            table.setItem(row_id, 3, QStandardItem(param.GuidanceMode or ""))
            table.setItem(row_id, 4, QStandardItem(param.WarheadType))
            table.setItem(row_id, 5, QStandardItem(str(param.ChargeAmount or "")))
            table.setItem(row_id, 6, QStandardItem(str(param.DropHeight or "")))
            table.setItem(row_id, 7, QStandardItem(str(param.DropSpeed or "")))
            table.setItem(row_id, 8, QStandardItem(param.DropMode or ""))
            table.setItem(row_id, 9, QStandardItem(str(param.FlightRange or "")))
            table.setItem(row_id, 10, QStandardItem(param.ElectroInterference or ""))
            table.setItem(row_id, 11, QStandardItem(param.WeatherConditions or ""))
            table.setItem(row_id, 12, QStandardItem(str(param.WindSpeed or "")))

            # 操作列
            self._add_action_buttons(tv, table, row_id, len(headers) - 1, param.DPID)

        logger.info(f"毁伤参数数据加载完成，共 {len(db_data)} 条")


    def _add_action_buttons(self, tv, table, row, col, param_id: int):
        """添加操作按钮"""
        w = QWidget(tv)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_edit = QPushButton("编辑", w)
        btn_del = QPushButton("删除", w)

        btn_edit.clicked.connect(lambda: self._on_edit(param_id))
        btn_del.clicked.connect(lambda: self._on_delete(tv, table, row, param_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        index = table.index(row, col)
        tv.setIndexWidget(index, w)

    def _on_edit(self, param_id: int):
        """编辑参数"""
        try:
            self.edit_win = DamageParameterEditor(
                parent=self,
                mode=DamageParameterEditorMode.Edit,
                edit_param_id=param_id
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

    def _on_delete(self, tv, table, row, param_id: int):
        """删除参数"""
        scene_code = table.index(row, 1).data()
        ok = QMessageBox.question(
            tv,
            "确认删除",
            f"确定删除参数 [{scene_code}] (ID={param_id}) 吗？"
        )
        if ok == QMessageBox.StandardButton.Yes:
            db = DBHelper()
            try:
                repo = DamageParameterRepository(db)
                if repo.delete(param_id):
                    QMessageBox.information(self, "成功", "删除成功")
                    self.setup_table()
                else:
                    QMessageBox.warning(self, "失败", "删除失败，记录不存在")
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"删除失败：{e}")
            finally:
                db.close()

    def _adjust_window_size(self):
        """调整窗口大小以适应所有列"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DamageParameterListWindow()
    window.show()
    sys.exit(app.exec())

