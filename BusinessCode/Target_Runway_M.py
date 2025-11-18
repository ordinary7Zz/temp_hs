from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtGui import QStandardItem, QStandardItemModel, QGuiApplication
from PyQt6.QtWidgets import QApplication, QHeaderView, QHBoxLayout, QMessageBox, QPushButton, QWidget, QDialog
from UIs.Frm_Target_Runway_M import Ui_Frm_Target_Runway_M
from BusinessCode.Target_Runway_Add import Target_Runway_AddWindow
from BusinessCode.Target_Runway_Export import Target_Runway_ExportWindow
from target_model.db import Base, engine, session_scope
from target_model.entities import AirportRunway
from target_model.sql_repository import SQLRepository


def _fmt_number(value: float | None, unit: str) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):g} {unit}"
    except (TypeError, ValueError):
        return f"{value} {unit}".strip()


def _fmt_layer(thickness_cm: float | None, strength_mpa: float | None) -> str:
    parts: list[str] = []
    if thickness_cm is not None:
        try:
            parts.append(f"{float(thickness_cm):g} cm")
        except (TypeError, ValueError):
            parts.append(str(thickness_cm))
    if strength_mpa is not None:
        try:
            parts.append(f"{float(strength_mpa):g} MPa")
        except (TypeError, ValueError):
            parts.append(str(strength_mpa))
    return " / ".join(parts)


def _sum_layers(*values: float | None) -> str:
    total = 0.0
    has_value = False
    for value in values:
        if value is None:
            continue
        try:
            total += float(value)
            has_value = True
        except (TypeError, ValueError):
            return ""
    return f"{total:g} cm" if has_value else ""


class Target_Runway_MWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        # ---- 组合式 UI ----
        self.ui = Ui_Frm_Target_Runway_M()
        self.ui.setupUi(self)

        self.center_on_screen()  # 调用居中方法

        self._add_window: Target_Runway_AddWindow | None = None
        self._edit_window: Target_Runway_AddWindow | None = None

        self.ui.btn_add.clicked.connect(self.open_add_window)
        self.ui.btn_export.clicked.connect(self.open_export_dialog)
        self.refresh_table()  # load existing runway records when the window opens

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
        if self._add_window is None or not self._add_window.isVisible():
            self._add_window = Target_Runway_AddWindow(self)
        self._add_window.show()
        self._add_window.raise_()
        self._add_window.activateWindow()

    def open_export_dialog(self) -> None:
        dialog = Target_Runway_ExportWindow(self, session_scope)
        dialog.exec()

    def refresh_table(self) -> None:
        self.setup_table()

    # ------------------------------------------------------------------ data/table
    def setup_table(self) -> None:
        table_view = self.ui.tb_dan

        headers = [
            "机场名称",
            "国家/地区",
            "跑道长度",
            "跑道宽度",
            "跑道总厚度",
            "混凝土层",
            "水泥稳定层",
            "级配砂砾层",
            "土基压实层",
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

        runways: Iterable[AirportRunway]
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                runways = repo.list_all(AirportRunway)
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"[Runway_List] 数据库读取失败：{exc}")
            runways = []

        for row_index, runway in enumerate(runways):
            values = [
                getattr(runway, "runway_name", None) or "",
                runway.country or "",
                _fmt_number(getattr(runway, "r_length", None), "m"),
                _fmt_number(getattr(runway, "r_width", None), "m"),
                _sum_layers(
                    getattr(runway, "pccsc_thick", None),
                    getattr(runway, "ctbc_thick", None),
                    getattr(runway, "gcss_thick", None),
                    getattr(runway, "cs_thick", None),
                ),
                _fmt_layer(
                    getattr(runway, "pccsc_thick", None),
                    getattr(runway, "pccsc_strength", None),
                ),
                _fmt_layer(
                    getattr(runway, "ctbc_thick", None),
                    getattr(runway, "ctbc_strength", None),
                ),
                _fmt_layer(
                    getattr(runway, "gcss_thick", None),
                    getattr(runway, "gcss_strength", None),
                ),
                _fmt_layer(
                    getattr(runway, "cs_thick", None),
                    getattr(runway, "cs_strength", None),
                ),
            ]
            model.insertRow(row_index)
            for col_index, text in enumerate(values):
                model.setItem(row_index, col_index, QStandardItem(text))
            _add_action_buttons(
                table_view,
                model,
                row_index,
                len(headers) - 1,
                getattr(runway, "id", None),
            )


def _add_action_buttons(table_view, model, row, column, runway_id) -> None:
    widget = QWidget(table_view)
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    btn_edit = QPushButton("编辑", widget)
    btn_delete = QPushButton("删除", widget)

    btn_edit.clicked.connect(lambda _=False, r=row, rid=runway_id: _on_edit(table_view, model, r, rid))
    btn_delete.clicked.connect(lambda _=False, r=row, rid=runway_id: _on_delete(table_view, model, r, rid))

    layout.addWidget(btn_edit)
    layout.addWidget(btn_delete)
    widget.setLayout(layout)

    index = model.index(row, column)
    table_view.setIndexWidget(index, widget)


def _on_edit(table_view, model, row, runway_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]

    if runway_id is None:
        QMessageBox.information(table_view, "提示", "演示数据无法编辑，请新增真实记录。")
        return

    try:
        with session_scope() as session:
            repo = SQLRepository(session)
            entity = repo.get(runway_id, AirportRunway)
    except Exception as exc:
        QMessageBox.critical(table_view, "读取失败", f"读取数据库失败：{exc}")
        return

    if not entity:
        QMessageBox.warning(table_view, "提示", "未找到对应记录。")
        return

    editor = Target_Runway_AddWindow(window)
    editor.load_entity(entity)
    editor.show()
    editor.raise_()
    editor.activateWindow()

    window._edit_window = editor


def _on_delete(table_view, model, row, runway_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]
    name = model.index(row, 0).data() or "该记录"
    confirm = f"确定删除 {name} 吗？"
    if runway_id is not None:
        confirm += f"\n(ID={runway_id})"

    if QMessageBox.question(table_view, "确认删除", confirm) != QMessageBox.StandardButton.Yes:
        return

    if runway_id is not None:
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if not repo.delete(runway_id, AirportRunway):
                    QMessageBox.warning(table_view, "提示", "未找到数据库记录，无法删除。")
                    return
        except Exception as exc:
            QMessageBox.critical(table_view, "删除失败", f"删除数据库记录时出错：{exc}")
            return

    window.setup_table()


def init_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_tables()

    app = QApplication(sys.argv)
    window = Target_Runway_MWindow()
    window.show()
    sys.exit(app.exec())
