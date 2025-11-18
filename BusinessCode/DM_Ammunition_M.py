import sys
from typing import Dict, List, Any

from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton, QHBoxLayout, QHeaderView, \
    QDialog

from BusinessCode.DM_Ammunition_Add import init_tables, AmmunitionEditor, AmmunitionEditorMode
from BusinessCode.DM_Ammunition_Export import ExportDialog
from UIs.Frm_Ammunition_M import Ui_Frm_AmmunitionManagement
from am_models import SQLRepository
from am_models.db import session_scope
from loguru import logger


class DYListWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Frm_AmmunitionManagement()
        self.ui.setupUi(self)
        self.setWindowTitle("弹药毁伤数据模型管理")

        # 数据库初始化
        try:
            init_tables()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "", f"初始化数据库失败：{e}")

        # 按钮绑定
        self.ui.btn_add.clicked.connect(self._on_btn_add_clicked)
        self.ui.btn_export.clicked.connect(self._on_btn_export_clicked)
        # 绑定双击信号
        self.ui.tb_dan.doubleClicked.connect(self._on_row_double_clicked)
        self.setup_table()
        self.setFixedSize(900, 600)

    def _on_btn_export_clicked(self):
        dlg = ExportDialog(self, session_scope)
        dlg.exec()

    def _on_btn_add_clicked(self):
        try:
            self.edit_win = AmmunitionEditor(parent=self, mode=AmmunitionEditorMode.AmmunitionEditorMode_Add)
            self.edit_win.finished_with_result.connect(self.on_edit_done)
            self.edit_win.show()
        except Exception as e:
            logger.exception(e)

    def setup_table(self):
        tv = self.ui.tb_dan

        headers = ["弹药类型", "国家/地区", "中文名称", "弹药型号", "弹药全重", "弹药长度", "弹体直径", "最大时速",
                   "战斗部", "爆炸当量", "操作", "_id"]
        table = QStandardItemModel(0, len(headers), tv)
        table.setHorizontalHeaderLabels(headers)
        tv.setModel(table)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)  # 不让最后一列自动吞空间
        for i in range(0, len(headers) - 1):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)  #设置列的宽度固定
        tv.setColumnWidth(0, 90)  # 弹药类型
        tv.setColumnWidth(1, 60)  # 国家/地区,
        tv.setColumnWidth(2, 150)  # 中文名称
        tv.setColumnWidth(3, 70)  # 弹药型号
        tv.setColumnWidth(4, 50)  #弹药全重
        tv.setColumnWidth(5, 50)  #弹药长度
        tv.setColumnWidth(6, 50)  # 弹体直径
        tv.setColumnWidth(7, 50)  #最大时速
        tv.setColumnWidth(8, 80)  # 战斗部类型
        tv.setColumnWidth(9, 70)  # 爆炸当量
        tv.setColumnWidth(10, 150)  # 操作

        tv.verticalHeader().setVisible(False)  # 隐藏行号（可选）
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

        # 从数据库读取数据
        db_data: List[Dict[str, Any]] = []
        with session_scope() as db_session:
            repo = SQLRepository(db_session)
            db_session.flush()
            db_session.expire_all()
            try:
                db_data = repo.list_columns(
                    ['am_id', 'am_type', "country", "chinese_name", "model_name", "weight_kg", "length_m", "diameter_m",
                     "max_speed_ma", "warhead_type", "explosion_equivalent_tnt_t"])
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "错误", f"读取数据库失败:{e}")
                self.close()
                return

        logger.debug(db_data)

        try:
            for row_id, am in enumerate(db_data):
                logger.debug(f"row_id: {row_id},am={am}")
                # ["弹药类型", "国家/地区", "中文名称", "弹药型号", "弹药全重", "弹药长度", "弹体直径", "最大时速","战斗部", "爆炸当量", "操作"]
                table.insertRow(row_id)
                table.setItem(row_id, 0, QStandardItem(am["am_type"]))
                table.setItem(row_id, 1, QStandardItem(am.get("country", "") or ""))
                table.setItem(row_id, 2, QStandardItem(am.get("chinese_name", "") or ""))
                table.setItem(row_id, 3, QStandardItem(am.get("model_name", "") or ""))

                table.setItem(row_id, 4, QStandardItem(str(am.get("weight_kg", "") or "")))
                table.setItem(row_id, 5, QStandardItem(str(am.get("length_m", "") or "")))
                table.setItem(row_id, 6, QStandardItem(str(am.get("diameter_m", "") or "")))
                table.setItem(row_id, 7, QStandardItem(str(am.get("max_speed_ma", "") or "")))

                table.setItem(row_id, 8, QStandardItem(am.get("warhead_type", "") or ""))
                table.setItem(row_id, 9, QStandardItem(str(am.get("explosion_equivalent_tnt_t", "") or "")))

                # 操作列：为本行插入按钮
                self._add_action_buttons(tv, table, row_id, len(headers) - 2, am_id=am["am_id"])

                # 隐藏的主键列
                table.setItem(row_id, len(headers) - 1, QStandardItem(str(am["am_id"])))

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"列举表格内容发生错误{e}")

        # 隐藏 _id 列
        tv.setColumnHidden(len(headers) - 1, True)

        logger.info("数据获取完毕")

    def _on_row_double_clicked(self, index: QModelIndex):
        tv = self.ui.tb_dan
        model = tv.model()
        row = index.row()

        # 隐藏列在最后一列
        id_col = model.columnCount() - 1
        am_id_str = model.index(row, id_col).data()
        try:
            am_id = int(am_id_str)
        except Exception:
            return

        # 直接复用你已有的编辑入口
        self._on_edit(tv, model, row, am_id)

    def _add_action_buttons(self, tv, table, row, col, am_id: int):
        w = QWidget(tv)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_edit = QPushButton("编辑", w)
        btn_del = QPushButton("删除", w)
        # 行号捕获到闭包里（也可把主键 ID 作为属性设置到按钮上）
        btn_edit.clicked.connect(lambda _=False, r=row: self._on_edit(tv, table, row, am_id))
        btn_del.clicked.connect(lambda _=False, r=row: self._on_delete(tv, table, row, am_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        index = table.index(row, col)
        tv.setIndexWidget(index, w)

    def _on_edit(self, tv, table, row, am_id: int):
        # 示例：弹窗显示当前行数据；实际可打开编辑对话框
        # logger.info(f"_on_edit model={table}, am_id={am_id}")

        try:
            self.edit_win = AmmunitionEditor(parent=self, mode=AmmunitionEditorMode.AmmunitionEditorMode_Edit,
                                             edit_amid=am_id)
            self.edit_win.finished_with_result.connect(self.on_edit_done)
            self.edit_win.show()
        except Exception as e:
            logger.exception(e)

    def on_edit_done(self, result):
        print("子窗口已关闭，结果：", result)
        self.setup_table()  # 刷新数据

    def _on_delete(self, tv, table, row, am_id: int):
        name = table.index(row, 3).data()
        ok = QMessageBox.question(tv, "确认删除", f"确定删除 {name}(am_id={am_id}) 这条记录吗？")
        if ok == QMessageBox.StandardButton.Yes:
            with session_scope() as db_session:
                repo = SQLRepository(db_session)
                if repo.delete(am_id):
                    QMessageBox.information(self, "成功", "删除成功")
                else:
                    QMessageBox.warning(self, "失败", "删除失败")
            self.setup_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DYListWindow()
    window.show()
    sys.exit(app.exec())
