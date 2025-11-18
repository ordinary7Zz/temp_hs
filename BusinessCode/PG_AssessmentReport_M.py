"""
毁伤评估报告管理列表
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMessageBox, QPushButton,
    QHBoxLayout, QHeaderView, QDialog, QFileDialog
)
from PyQt6.QtCore import pyqtSignal

from UIs.Frm_PG_AssessmentReport import Ui_Frm_PG_AssessmentReport
from damage_models.sql_repository_dbhelper import AssessmentReportRepository
from DBCode.DBHelper import DBHelper
from loguru import logger


class AssessmentReportListWindow(QDialog):
    """毁伤评估报告列表窗口"""

    def __init__(self, parent=None):
        try:
            super().__init__(parent)

            # 创建中心部件
            from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy
            cw = QWidget()
            self.ui = Ui_Frm_PG_AssessmentReport()
            self.ui.setupUi(cw)

            # 设置中心部件的大小策略为扩展
            cw.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # 设置对话框布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(cw)

            self.setWindowTitle("毁伤评估报告管理")

            # 按钮绑定
            self.ui.btn_add.clicked.connect(self._on_btn_add_clicked)
            self.ui.btn_export.clicked.connect(self._on_btn_export_clicked)
            #self.ui.btn_search.clicked.connect(self._on_btn_search_clicked)

            self.setup_table()

            # 设置窗口大小
            self.resize(1100, 600)

            logger.info("毁伤评估报告管理窗口初始化成功")
        except Exception as e:
            logger.exception(f"毁伤评估报告管理窗口初始化失败: {e}")
            QMessageBox.critical(None, "错误", f"窗口初始化失败：{str(e)}\n\n详细信息请查看日志")
            raise

    def _on_btn_export_clicked(self):
        """导出按钮点击"""
        try:
            from BusinessCode.PG_AssessmentReport_Export import AssessmentReportExportDialog
            dlg = AssessmentReportExportDialog(self)
            dlg.exec()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"打开导出窗口失败：{e}")

    def _on_btn_add_clicked(self):
        """添加按钮点击"""
        try:
            from BusinessCode.PG_AssessmentReport_Add import AssessmentReportEditor, AssessmentReportEditorMode
            self.edit_win = AssessmentReportEditor(
                parent=self,
                mode=AssessmentReportEditorMode.Add
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
        tv = self.ui.tb_assessment_report

        headers = [
            "报告ID", "报告编号", "报告名称", "评估ID", "场景ID",
            "毁伤等级", "创建人ID", "审核人", "创建时间", "操作"
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
            repo = AssessmentReportRepository(db)
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

        logger.debug(f"查询到 {len(db_data)} 条毁伤评估报告记录")

        for row_id, report in enumerate(db_data):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QStandardItem(str(report.ReportID or "")))
            table.setItem(row_id, 1, QStandardItem(report.ReportCode))
            table.setItem(row_id, 2, QStandardItem(report.ReportName))
            table.setItem(row_id, 3, QStandardItem(str(report.DAID or "")))
            table.setItem(row_id, 4, QStandardItem(str(report.DSID or "")))
            table.setItem(row_id, 5, QStandardItem(report.DamageDegree or ""))
            table.setItem(row_id, 6, QStandardItem(str(report.Creator or "")))
            table.setItem(row_id, 7, QStandardItem(report.Reviewer or ""))
            table.setItem(row_id, 8, QStandardItem(
                report.CreatedTime.strftime('%Y-%m-%d %H:%M:%S') if report.CreatedTime else ""
            ))

            # 操作列：添加查看、编辑和删除按钮
            self._add_action_buttons(tv, table, row_id, len(headers) - 1, report.ReportID)

        logger.info(f"毁伤评估报告数据加载完成，共 {len(db_data)} 条")

    def _add_action_buttons(self, tv, table, row, col, report_id: int):
        """添加操作按钮"""
        w = QWidget(tv)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_view = QPushButton("查看", w)
        btn_edit = QPushButton("编辑", w)
        btn_export = QPushButton("导出", w)
        btn_del = QPushButton("删除", w)

        btn_view.clicked.connect(lambda: self._on_view(report_id))
        btn_edit.clicked.connect(lambda: self._on_edit(report_id))
        btn_export.clicked.connect(lambda: self._on_export_report(report_id))
        btn_del.clicked.connect(lambda: self._on_delete(tv, table, row, report_id))

        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_export)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        index = table.index(row, col)
        tv.setIndexWidget(index, w)

    def _on_view(self, report_id: int):
        """查看报告"""
        try:
            db = DBHelper()
            try:
                repo = AssessmentReportRepository(db)
                report = repo.get_by_id(report_id)

                if report:
                    # 使用专门的报告详情对话框
                    from BusinessCode.ReportDetailDialog import ReportDetailDialog
                    detail_dialog = ReportDetailDialog(report, self)
                    detail_dialog.exec()
                else:
                    QMessageBox.warning(self, "错误", "未找到该报告")
            finally:
                db.close()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"查看失败：{e}")

    def _on_export_report(self, report_id: int):
        """导出单个报告为PDF或Word"""
        try:
            from BusinessCode.ReportExporter import export_report_to_file
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QButtonGroup, QDialogButtonBox, QLabel

            # 创建格式选择对话框
            format_dialog = QDialog(self)
            format_dialog.setWindowTitle("选择导出格式")
            format_dialog.setFixedWidth(300)

            layout = QVBoxLayout(format_dialog)

            # 添加说明标签
            label = QLabel("请选择导出文件格式:")
            layout.addWidget(label)

            # 创建单选按钮组
            btn_group = QButtonGroup(format_dialog)
            radio_pdf = QRadioButton("PDF格式 (*.pdf)")
            radio_word = QRadioButton("Word格式 (*.docx)")
            radio_pdf.setChecked(True)  # 默认选择PDF

            btn_group.addButton(radio_pdf)
            btn_group.addButton(radio_word)

            layout.addWidget(radio_pdf)
            layout.addWidget(radio_word)

            # 添加确定/取消按钮
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(format_dialog.accept)
            button_box.rejected.connect(format_dialog.reject)
            layout.addWidget(button_box)

            # 显示对话框
            if format_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            # 根据选择确定导出格式
            export_format = "pdf" if radio_pdf.isChecked() else "word"

            # 选择保存位置
            if export_format == "pdf":
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "保存PDF文件", f"评估报告_{report_id}.pdf", "PDF文件 (*.pdf)"
                )
            else:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "保存Word文件", f"评估报告_{report_id}.docx", "Word文件 (*.docx)"
                )

            if not file_path:
                return

            # 执行导出
            success, message = export_report_to_file(report_id, file_path, export_format)

            if success:
                QMessageBox.information(self, "成功", f"报告已成功导出到:\n{file_path}")
            else:
                QMessageBox.warning(self, "失败", f"导出失败:\n{message}")

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"导出失败：{e}")

    def _on_edit(self, report_id: int):
        """编辑报告"""
        try:
            from BusinessCode.PG_AssessmentReport_Add import AssessmentReportEditor, AssessmentReportEditorMode
            self.edit_win = AssessmentReportEditor(
                parent=self,
                mode=AssessmentReportEditorMode.Edit,
                edit_report_id=report_id
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

    def _on_delete(self, tv, table, row, report_id: int):
        """删除报告"""
        report_code = table.index(row, 1).data()
        ok = QMessageBox.question(
            tv,
            "确认删除",
            f"确定删除报告 {report_code} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ok == QMessageBox.StandardButton.Yes:
            db = DBHelper()
            try:
                repo = AssessmentReportRepository(db)
                if repo.delete(report_id):
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
    window = AssessmentReportListWindow()
    window.show()
    sys.exit(app.exec())

