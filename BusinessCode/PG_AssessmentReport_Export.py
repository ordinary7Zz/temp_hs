"""
毁伤评估报告导出功能
"""
import os
import sys
from datetime import datetime
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QProgressBar, QMessageBox, QFileDialog, QApplication
)

from damage_models import AssessmentReport, CSVExporter, JSONExporter
from damage_models.sql_repository_dbhelper import AssessmentReportRepository
from DBCode.DBHelper import DBHelper
from loguru import logger


class ExportWorker(QThread):
    """导出工作线程"""
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    error = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, out_dir: str, fmt: str, parent=None):
        super().__init__(parent)
        self.out_dir = out_dir
        self.fmt = fmt.lower().strip()

    def run(self):
        """执行导出"""
        db = DBHelper()
        try:
            self.message.emit("正在读取数据...")
            repo = AssessmentReportRepository(db)
            items: List[AssessmentReport] = repo.get_all()

            self.progress.emit(30)

            if not items:
                self.error.emit("没有数据可导出")
                return

            # 生成文件名
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            if self.fmt == "csv":
                filename = os.path.join(self.out_dir, f"AssessmentReport_{ts}.csv")
                self.message.emit("正在生成CSV文件...")

                exporter = CSVExporter()
                data = exporter.export(items)

                with open(filename, 'wb') as f:
                    f.write(data)

                self.progress.emit(100)
                self.done.emit(filename)

            elif self.fmt == "json":
                filename = os.path.join(self.out_dir, f"AssessmentReport_{ts}.json")
                self.message.emit("正在生成JSON文件...")

                exporter = JSONExporter()
                data = exporter.export(items)

                with open(filename, 'wb') as f:
                    f.write(data)

                self.progress.emit(100)
                self.done.emit(filename)

            else:
                self.error.emit(f"不支持的导出格式：{self.fmt}")

        except Exception as e:
            logger.exception(e)
            self.error.emit(f"导出失败：{e}")
        finally:
            db.close()


class AssessmentReportExportDialog(QDialog):
    """毁伤评估报告导出对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出毁伤评估报告")
        self.setModal(True)
        self.resize(500, 200)

        self.worker = None
        self._init_ui()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 导出路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("导出路径："))
        self.ed_path = QLineEdit()
        self.ed_path.setText(os.path.expanduser("~/Desktop"))
        path_layout.addWidget(self.ed_path)

        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self._on_browse)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        # 导出格式
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("导出格式："))
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(["CSV", "JSON"])
        fmt_layout.addWidget(self.cmb_format)
        fmt_layout.addStretch()
        layout.addLayout(fmt_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.lbl_status = QLabel("准备就绪")
        layout.addWidget(self.lbl_status)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_export = QPushButton("开始导出")
        self.btn_export.clicked.connect(self._on_export)
        btn_layout.addWidget(self.btn_export)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _on_browse(self):
        """浏览文件夹"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            self.ed_path.text()
        )
        if directory:
            self.ed_path.setText(directory)

    def _on_export(self):
        """开始导出"""
        out_dir = self.ed_path.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "提示", "请选择导出路径")
            return

        if not os.path.isdir(out_dir):
            QMessageBox.warning(self, "提示", "导出路径不存在")
            return

        # 禁用导出按钮
        self.btn_export.setEnabled(False)

        # 创建工作线程
        self.worker = ExportWorker(out_dir, self.cmb_format.currentText())
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.message.connect(self.lbl_status.setText)
        self.worker.error.connect(self._on_export_error)
        self.worker.done.connect(self._on_export_done)
        self.worker.start()

    def _on_export_error(self, msg: str):
        """导出出错"""
        self.btn_export.setEnabled(True)
        self.lbl_status.setText(f"错误：{msg}")
        QMessageBox.critical(self, "导出失败", msg)

    def _on_export_done(self, filename: str):
        """导出完成"""
        self.btn_export.setEnabled(True)
        self.lbl_status.setText(f"导出成功：{filename}")
        QMessageBox.information(self, "成功", f"文件已导出到：\n{filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = AssessmentReportExportDialog()
    dialog.show()
    sys.exit(app.exec())

