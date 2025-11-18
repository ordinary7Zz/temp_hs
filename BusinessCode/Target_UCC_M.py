from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel, QGuiApplication
from PyQt6.QtWidgets import QApplication, QHeaderView, QHBoxLayout, QMessageBox, QPushButton, QWidget, QDialog
from UIs.Frm_Target_UCC_M import Ui_Frm_Target_UCC_M
from BusinessCode.Target_UCC_Add import Target_UCC_AddWindow
from BusinessCode.Target_UCC_Export import Target_UCC_ExportWindow
from target_model.db import session_scope
from target_model.entities import UndergroundCommandPost
from target_model.sql_repository import SQLRepository


class Target_UCC_MWindow(QDialog,Ui_Frm_Target_UCC_M):
    def __init__(self) -> None:
        super().__init__()
        # ---- 组合式 UI ----
        self.setupUi(self)

        self.center_on_screen()  # 调用居中方法

        self._add_window: Target_UCC_AddWindow | None = None
        self._edit_window: Target_UCC_AddWindow | None = None

        self.btn_add.clicked.connect(self.open_add_window)
        self.btn_export.clicked.connect(self.open_export_dialog)
        self.refresh_table()  # load existing underground command post records at startup

    # 窗体居中显示
    def center_on_screen(self):
        """PyQt6中窗体居中的核心方法"""
        # 获取屏幕的几何信息（主屏幕）
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        # 获取当前窗体的几何信息
        window_geometry = self.frameGeometry()
        # 计算屏幕中心点
        center_point = screen_geometry.center()
        # 将窗体的中心点移动到屏幕中心点
        window_geometry.moveCenter(center_point)
        # 移动窗体到计算好的位置（避免边框偏移）
        self.move(window_geometry.topLeft())

    # ------------------------------------------------------------------ actions
    def open_add_window(self) -> None:
        if self._add_window is None:
            try:
                self._add_window = Target_UCC_AddWindow(self)
                self._add_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
                self._add_window.destroyed.connect(lambda *_: self._clear_add_window())
            except Exception as exc:
                QMessageBox.critical(self, "错误", f"无法打开新增窗口：{exc}")
                self._add_window = None
                return

        self._add_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._add_window.show()
        self._add_window.raise_()
        self._add_window.activateWindow()

    def _clear_add_window(self) -> None:
        self._add_window = None

    def open_export_dialog(self) -> None:
        dialog = Target_UCC_ExportWindow(self, session_scope)
        dialog.exec()

    def refresh_table(self) -> None:
        self.setup_table()

    # ------------------------------------------------------------------ data/table
    def setup_table(self) -> None:
        table_view = self.tb_dan

        headers = [
            "代码/名称",
            "国家/地区",
            "基地/部队",
            "所在位置",
            "土壤岩层材料",
            "土壤岩层厚度(cm)",
            "防护层材料",
            "衣采层材料",
            "UCC墙体材料",
            "操作",
        ]
        model = QStandardItemModel(0, len(headers), table_view)
        model.setHorizontalHeaderLabels(headers)
        table_view.setModel(model)

        header = table_view.horizontalHeader()
        header.setStretchLastSection(False)
        if headers:
            for idx in range(len(headers) - 1):
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.ResizeToContents)

        table_view.verticalHeader().setVisible(False)
        table_view.setSelectionBehavior(table_view.SelectionBehavior.SelectRows)
        table_view.setEditTriggers(table_view.EditTrigger.NoEditTriggers)

        posts: Iterable[UndergroundCommandPost]
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                posts = repo.list_all(UndergroundCommandPost)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[Underground_List] database fetch failed: {exc}")
            posts = []

        for row_index, post in enumerate(posts):
            code = getattr(post, "ucc_code", "") or ""
            name = getattr(post, "ucc_name", "") or ""
            display_name = f"{code} / {name}" if (code and name) else (code or name)

            values = [
                display_name,
                getattr(post, "country", "") or "",
                getattr(post, "base", "") or "",
                getattr(post, "location", "") or "",
                getattr(post, "rock_layer_materials", "") or "",
                _format_value(getattr(post, "rock_layer_thick", None), " cm", precision=0),
                getattr(post, "protective_layer_material", "") or "",
                getattr(post, "lining_layer_material", "") or "",
                getattr(post, "ucc_wall_materials", "") or "",
            ]
            model.insertRow(row_index)
            for col, text_value in enumerate(values):
                model.setItem(row_index, col, QStandardItem(text_value))

            _add_action_buttons(
                table_view,
                model,
                row_index,
                len(headers) - 1,
                getattr(post, "id", None),
            )


def _add_action_buttons(table_view, model, row, column, post_id) -> None:
    widget = QWidget(table_view)
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    btn_edit = QPushButton("编辑", widget)
    btn_delete = QPushButton("删除", widget)

    btn_edit.clicked.connect(lambda _=False, r=row, pid=post_id: _on_edit(table_view, model, r, pid))
    btn_delete.clicked.connect(lambda _=False, r=row, pid=post_id: _on_delete(table_view, model, r, pid))

    layout.addWidget(btn_edit)
    layout.addWidget(btn_delete)
    widget.setLayout(layout)

    index = model.index(row, column)
    table_view.setIndexWidget(index, widget)


def _on_edit(table_view, model, row, post_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]

    if post_id is None:
        QMessageBox.information(table_view, "提示", "演示数据无法编辑，请新增真实记录。")
        return

    try:
        with session_scope() as session:
            repo = SQLRepository(session)
            entity = repo.get(post_id, UndergroundCommandPost)
    except Exception as exc:
        QMessageBox.critical(table_view, "读取失败", f"读取数据库失败：{exc}")
        return

    if not entity:
        QMessageBox.warning(table_view, "提示", "未找到对应记录。")
        return

    editor = Target_UCC_AddWindow(window)
    editor.load_entity(entity)
    editor.show()
    editor.raise_()
    editor.activateWindow()
    window._edit_window = editor


def _on_delete(table_view, model, row, post_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]
    name = model.index(row, 0).data() or "该记录"
    confirm = f"确定删除 {name} 吗？"
    if post_id is not None:
        confirm += f"\n(ID={post_id})"

    if QMessageBox.question(table_view, "确认删除", confirm) != QMessageBox.StandardButton.Yes:
        return

    if post_id is not None:
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if not repo.delete(post_id, UndergroundCommandPost):
                    QMessageBox.warning(table_view, "提示", "未找到数据库记录，无法删除。")
                    return
        except Exception as exc:
            QMessageBox.critical(table_view, "删除失败", f"删除数据库记录时出错：{exc}")
            return

    window.setup_table()


def _format_value(value: float | None, unit: str = "", precision: int = 2) -> str:
    if value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number == 0:
        return ""
    formatted = f"{number:.{precision}f}".rstrip("0").rstrip(".")
    return f"{formatted}{unit}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Target_UCC_MWindow()
    window.show()
    sys.exit(app.exec())
