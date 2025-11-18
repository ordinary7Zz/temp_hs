from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtGui import QStandardItem, QStandardItemModel, QGuiApplication
from PyQt6.QtWidgets import QApplication, QHeaderView, QHBoxLayout, QMessageBox, QPushButton, QWidget, QDialog
from UIs.Frm_Target_Shelter_M import Ui_Frm_Target_Shelter_M
from BusinessCode.Target_Shelter_Add import Target_Shelter_AddWindow
from BusinessCode.Target_Shelter_Export import Target_Shelter_ExportWindow
from target_model.db import session_scope
from target_model.entities import AircraftShelter
from target_model.sql_repository import SQLRepository


def _format_m(value: float | None) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):g} m"
    except (TypeError, ValueError):
        return str(value)


class Target_Shelter_MWindow(QDialog,Ui_Frm_Target_Shelter_M):
    def __init__(self) -> None:
        super().__init__()
        # ---- 组合式 UI ----
        self.setupUi(self)

        self.center_on_screen()  # 调用居中方法

        self._add_window: Target_Shelter_AddWindow | None = None
        self._edit_window: Target_Shelter_AddWindow | None = None

        self.btn_add.clicked.connect(self.open_add_window)
        self.btn_export.clicked.connect(self.open_export_dialog)
        self.refresh_table()  # load existing shelter records when the window opens

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
            self._add_window = Target_Shelter_AddWindow(self)
        self._add_window.show()
        self._add_window.raise_()
        self._add_window.activateWindow()

    def open_export_dialog(self) -> None:
        dialog = Target_Shelter_ExportWindow(self, session_scope)
        dialog.exec()

    def refresh_table(self) -> None:
        self.setup_table()

    # ------------------------------------------------------------------ data/table
    def setup_table(self) -> None:
        table_view = self.tb_dan

        headers = [
            "名称 / 代码",
            "国家/地区",
            "基地/部队",
            "库容净长(m)",
            "库容净宽(m)",
            "库容净高(m)",
            "伪装层材料",
            "遮弹层材料",
            "结构层材料",
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

        shelters: Iterable[AircraftShelter]
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                shelters = repo.list_all(AircraftShelter)
        except Exception as exc:  # pragma: no cover
            print(f"[Shelter_List] database fetch failed: {exc}")
            shelters = []

        for row_index, shelter in enumerate(shelters):
            name = getattr(shelter, "shelter_name", "") or ""
            code = getattr(shelter, "shelter_code", "") or ""
            display_name = f"{name} / {code}" if (name and code) else (name or code)

            values = [
                display_name,
                getattr(shelter, "country", "") or "",
                getattr(shelter, "base", "") or "",
                _format_m(getattr(shelter, "shelter_length", None)),
                _format_m(getattr(shelter, "shelter_width", None)),
                _format_m(getattr(shelter, "shelter_height", None)),
                getattr(shelter, "mask_layer_material", "") or "",
                getattr(shelter, "soil_layer_material", "") or "",
                getattr(shelter, "structure_layer_material", "") or "",
            ]
            model.insertRow(row_index)
            for col_index, text_value in enumerate(values):
                model.setItem(row_index, col_index, QStandardItem(text_value))
            _add_action_buttons(
                table_view,
                model,
                row_index,
                len(headers) - 1,
                getattr(shelter, "id", None),
            )


def _add_action_buttons(table_view, model, row, column, shelter_id) -> None:
    widget = QWidget(table_view)
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    btn_edit = QPushButton("编辑", widget)
    btn_delete = QPushButton("删除", widget)

    btn_edit.clicked.connect(lambda _=False, r=row, sid=shelter_id: _on_edit(table_view, model, r, sid))
    btn_delete.clicked.connect(lambda _=False, r=row, sid=shelter_id: _on_delete(table_view, model, r, sid))

    layout.addWidget(btn_edit)
    layout.addWidget(btn_delete)
    widget.setLayout(layout)

    index = model.index(row, column)
    table_view.setIndexWidget(index, widget)


def _on_edit(table_view, model, row, shelter_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]

    if shelter_id is None:
        QMessageBox.information(table_view, "提示", "演示数据无法编辑，请新增真实记录。")
        return

    try:
        with session_scope() as session:
            repo = SQLRepository(session)
            entity = repo.get(shelter_id, AircraftShelter)
    except Exception as exc:
        QMessageBox.critical(table_view, "读取失败", f"读取数据库失败：{exc}")
        return

    if not entity:
        QMessageBox.warning(table_view, "提示", "未找到对应记录。")
        return

    editor = Target_Shelter_AddWindow(window)
    editor.load_entity(entity)
    editor.show()
    editor.raise_()
    editor.activateWindow()
    window._edit_window = editor


def _on_delete(table_view, model, row, shelter_id) -> None:
    window: DYListWindow = table_view.window()  # type: ignore[assignment]
    name = model.index(row, 0).data() or "该记录"
    confirm = f"确定删除 {name} 吗？"
    if shelter_id is not None:
        confirm += f"\n(ID={shelter_id})"

    if QMessageBox.question(table_view, "确认删除", confirm) != QMessageBox.StandardButton.Yes:
        return

    if shelter_id is not None:
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if not repo.delete(shelter_id, AircraftShelter):
                    QMessageBox.warning(table_view, "提示", "未找到数据库记录，无法删除。")
                    return
        except Exception as exc:
            QMessageBox.critical(table_view, "删除失败", f"删除数据库记录时出错：{exc}")
            return

    window.setup_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Target_Shelter_MWindow()
    window.show()
    sys.exit(app.exec())
