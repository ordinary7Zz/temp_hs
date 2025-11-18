from __future__ import annotations

import json
import sys
from pathlib import Path
import re
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtCore import QEvent, QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
)

from BusinessCode.structure_preview import LayerVisualConfig, ShelterStructureRenderer
from UIs.Frm_Target_Shelter_Add import Ui_Frm_Target_Shelter_Add
from target_model.db import session_scope
from target_model.entities import AircraftShelter
from target_model.sql_repository import SQLRepository


class Target_Shelter_AddWindow(QMainWindow, Ui_Frm_Target_Shelter_Add):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(820, 690)

        self._entity_id: int | None = None
        self._image_path: str | None = None
        self._draft_file = Path.home() / ".shelter_editor_draft.json"
        self._current_entity: "AircraftShelter | None" = None
        self._thickness_unit_factor = 100.0  # UI 显示单位为 m，存储为 cm

        # 新建模式默认标题
        self.cmb_country.addItems(["中国", "美国", "俄罗斯", "法国", "英国", "德国", "其他"])

        # 信号
        self.btn_choose_image.clicked.connect(self.on_choose_image)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_save_store.clicked.connect(self.on_save_store)

        self._structure_preview_label = getattr(self, "lbl_image_3", None)
        self._structure_placeholder = (
            self._structure_preview_label.text() if self._structure_preview_label is not None else ""
        )
        shelter_texture_dir = PROJECT_ROOT / "UIstyles" / "images" / "shelter_layers"
        # 剖面纹理图片放在 UIstyles/images/shelter_layers（缺失时自动用备用色填充）
        self._arch_layer_configs: list[LayerVisualConfig] = [
            LayerVisualConfig("sp_top_thk", "top_layer.png", "#4d6b41"),
            LayerVisualConfig("sp_cover_thk", "soil_layer.png", "#c09b6c"),
            LayerVisualConfig("sp_arch1_thk", "disper_layer.png", "#9a8d80"),
            LayerVisualConfig("sp_arch2_thk", "structure_layer.png", "#6a6260"),
        ]
        self._base_layer_configs: list[LayerVisualConfig] = [
            LayerVisualConfig("cushion_layer", "cushion_layer.png", "#aca27c"),
            LayerVisualConfig("foundation_layer", "foundation_layer.png", "#b97839"),
        ]
        self._base_layer_defaults: list[float] = [30.0, 100.0]
        self._structure_renderer = ShelterStructureRenderer(
            shelter_texture_dir, self._arch_layer_configs, self._base_layer_configs
        )
        if self._structure_preview_label is not None:
            self._structure_preview_label.installEventFilter(self)
        self._connect_structure_preview_signals()
        self._update_structure_preview()
        self._apply_demo_defaults()

        self._maybe_restore_draft()

    # ------------------------------------------------------------------ image selection
    def on_choose_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择图片", str(Path.home()), "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not filename:
            return
        pixmap = QPixmap(filename)
        if pixmap.isNull():
            QMessageBox.warning(self, "错误", "无法加载图片")
            return
        target_size = self.lbl_image.size()
        scaled = pixmap if target_size.isEmpty() else pixmap.scaled(
            target_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_image.setPixmap(scaled)
        self._image_path = filename

    # ------------------------------------------------------------------ load / save
    def load_entity(self, entity: "AircraftShelter") -> None:
        self._current_entity = entity
        self._entity_id = entity.id
        self._image_path = entity.shelter_picture or None
        self.lbl_image.clear()
        if self._image_path:
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                self.lbl_image.setPixmap(pixmap)

        self._set_line_edit("ed_repo_name", entity.shelter_name)
        self._set_line_edit("ed_code", entity.shelter_code)
        self._set_combo_text("cmb_country", entity.country)
        self._set_line_edit("ed_unit", entity.base)

        self._set_length_spin(self.sp_clear_l, getattr(self, "cmb_clear_l_unit", None), entity.shelter_length)
        self._set_length_spin(self.sp_clear_w, getattr(self, "cmb_clear_w_unit", None), entity.shelter_width)
        self._set_length_spin(self.sp_clear_h, getattr(self, "cmb_clear_h_unit", None), entity.shelter_height)

        self.sp_door_w.setValue(float(entity.cave_width or 0.0))
        self.sp_door_h.setValue(float(entity.cave_height or 0.0))
        self._set_combo_text("cmb_structure", entity.structural_form)
        self._set_combo_text("cmb_door_mat", entity.door_material)
        self.sp_door_thk.setValue(self._cm_to_ui(entity.door_thick))

        self._set_line_edit("ed_top_mat", entity.mask_layer_material)
        self.sp_top_thk.setValue(self._cm_to_ui(entity.mask_layer_thick))
        self._set_line_edit("ed_cover_mat", entity.soil_layer_material)
        self.sp_cover_thk.setValue(self._cm_to_ui(entity.soil_layer_thick))
        self._set_line_edit("ed_arch1_mat", entity.disper_layer_material)
        self.sp_arch1_thk.setValue(self._cm_to_ui(entity.disper_layer_thick))
        self._set_combo_text("cmb_arch1_rebar", entity.disper_layer_reinforcement)
        self._set_line_edit("ed_arch2_mat", entity.structure_layer_material)
        self.sp_arch2_thk.setValue(self._cm_to_ui(entity.structure_layer_thick))
        self._set_combo_text("cmb_arch2_rebar", entity.structure_layer_reinforcement)

        self.sp_blast.setValue(float(entity.explosion_resistance or 0.0))
        self.sp_ke.setValue(float(entity.anti_kinetic or 0.0))
        self.sp_pen.setValue(float(entity.resistance_depth or 0.0))
        self.sp_nuclear.setValue(float(entity.nuclear_blast or 0.0))
        self.sp_shield.setValue(float(entity.radiation_shielding or 0.0))
        self.sp_fire.setValue(float(entity.fire_resistance or 0.0))

        self._update_structure_preview()
        self.setWindowTitle("编辑单机掩蔽库数据模型")

    def on_save_store(self) -> None:
        if not self._ensure_required_fields():
            return
        try:
            shelter = self._build_entity_from_form()
        except ValueError as exc:
            QMessageBox.warning(self, "数据不完整", str(exc))
            return

        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if self._entity_id is None:
                    repo.add(shelter)
                else:
                    repo.update_entity(shelter)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入数据库时出错：{exc}")
            return

        QMessageBox.information(self, "保存成功", "掩蔽库数据已保存到数据库。")
        if self._draft_file.exists():
            try:
                self._draft_file.unlink()
            except Exception:
                pass

        parent = self.parent()
        if parent and hasattr(parent, "refresh_table"):
            parent.refresh_table()  # type: ignore[attr-defined]
        self.close()

    def on_clear(self) -> None:
        self._clear_form()

    # ------------------------------------------------------------------ validation
    def _ensure_required_fields(self) -> bool:
        missing: list[tuple[str, object]] = []

        for label_name, widget, validator in self._required_field_specs():
            try:
                valid = validator()
            except Exception:
                valid = False
            if valid:
                continue
            label_widget = getattr(self, label_name, None)
            label_text = getattr(label_widget, "text", lambda: label_name)()
            missing.append((self._normalize_label(label_text), widget))

        if not missing:
            return True

        missing_labels = "、".join(label for label, _ in missing)
        QMessageBox.warning(self, "数据不完整", f"请先填写以下必填项：\n{missing_labels}")

        first_widget = next((w for _, w in missing if hasattr(w, "setFocus")), None)
        if first_widget is not None:
            try:
                first_widget.setFocus()
            except Exception:
                pass
        return False

    def _required_field_specs(self) -> list[tuple[str, object, Callable[[], bool]]]:
        return [
            ("ShelterName", getattr(self, "ed_repo_name", None), lambda: bool(self.ed_repo_name.text().strip())),
            ("ShelterCode", getattr(self, "ed_code", None), lambda: bool(self.ed_code.text().strip())),
            ("ShelterWidth", getattr(self, "sp_clear_w", None), lambda: self.sp_clear_w.value() > 0),
            ("ShelterLength", getattr(self, "sp_clear_l", None), lambda: self.sp_clear_l.value() > 0),
            ("ShelterHeight", getattr(self, "sp_clear_h", None), lambda: self.sp_clear_h.value() > 0),
            ("MaskLayerMaterial", getattr(self, "ed_top_mat", None),
             lambda: bool(self.ed_top_mat.text().strip())),
            ("MaskLayerThick", getattr(self, "sp_top_thk", None), lambda: self.sp_top_thk.value() > 0),
            ("SoilLayerMaterial", getattr(self, "ed_cover_mat", None),
             lambda: bool(self.ed_cover_mat.text().strip())),
            ("SoilLayerThick", getattr(self, "sp_cover_thk", None), lambda: self.sp_cover_thk.value() > 0),
            ("DisperLayerMaterial", getattr(self, "ed_arch1_mat", None),
             lambda: bool(self.ed_arch1_mat.text().strip())),
            ("DisperLayerThick", getattr(self, "sp_arch1_thk", None), lambda: self.sp_arch1_thk.value() > 0),
            ("StructureLayerMaterial", getattr(self, "ed_arch2_mat", None),
             lambda: bool(self.ed_arch2_mat.text().strip())),
            ("StructureLayerThick", getattr(self, "sp_arch2_thk", None), lambda: self.sp_arch2_thk.value() > 0),
        ]

    @staticmethod
    def _normalize_label(text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        stripped = re.sub(r"<[^>]+>", "", text)
        cleaned = (
            stripped.replace("：", "")
            .replace(":", "")
            .replace("*", "")
            .replace("＊", "")
            .replace("（必填）", "")
            .replace("(必填)", "")
            .strip()
        )
        return cleaned or stripped.strip()

    def _combo_text(self, attr_name: str, fallback: str = "") -> str:
        widget = getattr(self, attr_name, None)
        if widget is None:
            return fallback
        if isinstance(widget, QLineEdit):
            text = widget.text()
        elif hasattr(widget, "currentText"):
            text = widget.currentText()
        else:
            return fallback
        text = text.strip() if isinstance(text, str) else ""
        return text or fallback

    def _cm_to_ui(self, value: float | None) -> float:
        if value is None:
            return 0.0
        try:
            return float(value) / self._thickness_unit_factor
        except (TypeError, ValueError):
            return 0.0

    def _ui_to_cm(self, value: float | None) -> float | None:
        if value is None:
            return None
        try:
            val = float(value)
        except (TypeError, ValueError):
            return None
        return val * self._thickness_unit_factor if val > 0 else None

    def _build_entity_from_form(self) -> "AircraftShelter":
        name = self._line_text("ed_repo_name")
        if not name:
            raise ValueError("请填写掩蔽库名称。")

        code = self._line_text("ed_code").upper()
        if not code:
            slug = re.sub(r"\s+", "-", name).upper()
            code = f"SH-{slug or '000001'}"
        else:
            code = re.sub(r"\s+", "-", code).upper()

        country = self._combo_text("cmb_country", "").strip() or None
        base = self._line_text("ed_unit") or None

        shelter = AircraftShelter(
            shelter_code=code,
            shelter_name=name,
            country=country,
            base=base,
            shelter_picture=self._image_path,
            shelter_length=self.sp_clear_l.value(),
            shelter_width=self.sp_clear_w.value(),
            shelter_height=self.sp_clear_h.value(),
            cave_width=self.sp_door_w.value() or None,
            cave_height=self.sp_door_h.value() or None,
            structural_form=self._combo_text("cmb_structure", "") or None,
            door_material=self._combo_text("cmb_door_mat", "") or None,
            door_thick=self._ui_to_cm(self.sp_door_thk.value()),
            mask_layer_material=self._line_text("ed_top_mat") or None,
            mask_layer_thick=self._ui_to_cm(self.sp_top_thk.value()),
            soil_layer_material=self._line_text("ed_cover_mat") or None,
            soil_layer_thick=self._ui_to_cm(self.sp_cover_thk.value()),
            disper_layer_material=self._line_text("ed_arch1_mat") or None,
            disper_layer_thick=self._ui_to_cm(self.sp_arch1_thk.value()),
            disper_layer_reinforcement=self._combo_text("cmb_arch1_rebar", "") or None,
            structure_layer_material=self._line_text("ed_arch2_mat") or None,
            structure_layer_thick=self._ui_to_cm(self.sp_arch2_thk.value()),
            structure_layer_reinforcement=self._combo_text("cmb_arch2_rebar", "") or None,
            explosion_resistance=self.sp_blast.value() or None,
            anti_kinetic=self.sp_ke.value() or None,
            resistance_depth=self.sp_pen.value() or None,
            nuclear_blast=self.sp_nuclear.value() or None,
            radiation_shielding=self.sp_shield.value() or None,
            fire_resistance=self.sp_fire.value() or None,
            shelter_status=getattr(self._current_entity, "shelter_status", None),
        )
        if self._entity_id is not None:
            shelter.id = self._entity_id
            if self._current_entity is not None:
                shelter.created_time = self._current_entity.created_time
        return shelter

    # ------------------------------------------------------------------ helpers
    def _set_length_spin(self, spin, combo, value: float | None) -> None:
        if value is None:
            spin.setValue(0.0)
            return
        unit = ""
        if combo is not None and hasattr(combo, "currentText"):
            unit = (combo.currentText() or "").strip().lower()
        if unit in ("cm", "厘米"):
            spin.setValue(value * 100.0)
        elif unit in ("mm", "毫米"):
            spin.setValue(value * 1000.0)
        elif unit in ("ft", "feet", "英尺"):
            spin.setValue(value / 0.3048)
        else:
            spin.setValue(value)

    def _unit_text(self, attr_name: str, fallback: str = "") -> str:
        combo = getattr(self, attr_name, None)
        if combo is None or not hasattr(combo, "currentText"):
            return fallback
        text = combo.currentText()
        text = text.strip() if isinstance(text, str) else ""
        return text or fallback

    def _line_text(self, attr_name: str, default: str = "") -> str:
        widget = getattr(self, attr_name, None)
        if widget is None or not hasattr(widget, "text"):
            return default
        text = widget.text()
        text = text.strip() if isinstance(text, str) else ""
        return text or default

    def _set_line_edit(self, attr_name: str, value: str | None) -> None:
        widget = getattr(self, attr_name, None)
        if widget is not None and hasattr(widget, "setText"):
            widget.setText((value or "").strip())

    def _set_combo_text(self, attr_name: str, value: str | None) -> None:
        widget = getattr(self, attr_name, None)
        if widget is None:
            return
        if isinstance(widget, QLineEdit):
            widget.setText("" if value in (None, "") else str(value).strip())
            return
        if not hasattr(widget, "setCurrentText") or value in (None, ""):
            return
        try:
            widget.setCurrentText(str(value))
        except Exception:
            pass

    # ------------------------------------------------------------------ draft helpers
    def _collect_form_state(self) -> dict[str, object]:
        state: dict[str, object] = {
            "entity_id": self._entity_id,
            "image_path": self._image_path,
        }

        for widget in self.findChildren(QLineEdit):
            name = widget.objectName()
            if name:
                state[f"line:{name}"] = widget.text()

        for widget in self.findChildren(QPlainTextEdit):
            name = widget.objectName()
            if name:
                state[f"plain:{name}"] = widget.toPlainText()

        for widget in self.findChildren(QTextEdit):
            name = widget.objectName()
            if name:
                state[f"text:{name}"] = widget.toPlainText()

        for widget in self.findChildren(QDoubleSpinBox):
            name = widget.objectName()
            if name:
                state[f"dspin:{name}"] = widget.value()

        for widget in self.findChildren(QSpinBox):
            name = widget.objectName()
            if name:
                state[f"spin:{name}"] = widget.value()

        for widget in self.findChildren(QComboBox):
            name = widget.objectName()
            if name:
                state[f"combo:{name}"] = {
                    "index": widget.currentIndex(),
                    "text": widget.currentText(),
                }

        for widget in self.findChildren(QCheckBox):
            name = widget.objectName()
            if name:
                state[f"check:{name}"] = widget.isChecked()

        return state

    def _apply_form_state(self, state: dict[str, object]) -> None:
        entity_id = state.get("entity_id")
        self._entity_id = int(entity_id) if isinstance(entity_id, int) else None

        self._image_path = state.get("image_path") if isinstance(state.get("image_path"), str) else None
        self.lbl_image.clear()
        if self._image_path:
            pixmap = QPixmap(self._image_path)
            if not pixmap.isNull():
                self.lbl_image.setPixmap(pixmap)

        for widget in self.findChildren(QLineEdit):
            key = f"line:{widget.objectName()}"
            if key in state:
                widget.setText(str(state[key]))

        for widget in self.findChildren(QPlainTextEdit):
            key = f"plain:{widget.objectName()}"
            if key in state:
                widget.setPlainText(str(state[key]))

        for widget in self.findChildren(QTextEdit):
            key = f"text:{widget.objectName()}"
            if key in state:
                widget.setPlainText(str(state[key]))

        for widget in self.findChildren(QDoubleSpinBox):
            key = f"dspin:{widget.objectName()}"
            if key in state:
                try:
                    widget.setValue(float(state[key]))
                except (TypeError, ValueError):
                    pass

        for widget in self.findChildren(QSpinBox):
            key = f"spin:{widget.objectName()}"
            if key in state:
                try:
                    widget.setValue(int(state[key]))
                except (TypeError, ValueError):
                    pass

        for widget in self.findChildren(QComboBox):
            key = f"combo:{widget.objectName()}"
            data = state.get(key)
            if isinstance(data, dict):
                text = data.get("text")
                index = data.get("index")
                if isinstance(text, str) and widget.findText(text) != -1:
                    widget.setCurrentText(text)
                elif isinstance(index, int) and 0 <= index < widget.count():
                    widget.setCurrentIndex(index)

        for widget in self.findChildren(QCheckBox):
            key = f"check:{widget.objectName()}"
            if key in state:
                widget.setChecked(bool(state[key]))
        self._update_structure_preview()

    def _clear_form(self) -> None:
        for widget in self.findChildren(QLineEdit):
            widget.clear()
        for widget in self.findChildren(QPlainTextEdit):
            widget.clear()
        for widget in self.findChildren(QTextEdit):
            widget.clear()
        for widget in self.findChildren(QDoubleSpinBox):
            widget.setValue(0.0)
        for widget in self.findChildren(QSpinBox):
            widget.setValue(0)
        for widget in self.findChildren(QComboBox):
            if widget.count():
                widget.setCurrentIndex(0)
        for widget in self.findChildren(QCheckBox):
            widget.setChecked(False)

        self.lbl_image.clear()
        self._entity_id = None
        self._image_path = None
        self._update_structure_preview()

    def _connect_structure_preview_signals(self) -> None:
        for name in ("sp_top_thk", "sp_cover_thk", "sp_arch1_thk", "sp_arch2_thk"):
            widget = getattr(self, name, None)
            if isinstance(widget, QDoubleSpinBox):
                try:
                    widget.valueChanged.connect(self._update_structure_preview)
                except Exception:
                    pass

    def _update_structure_preview(self, *_: object) -> None:
        label = self._structure_preview_label
        renderer = getattr(self, "_structure_renderer", None)
        if label is None or renderer is None:
            return

        arch_layers: list[tuple[str, float]] = []
        for cfg in getattr(self, "_arch_layer_configs", []):
            spin = getattr(self, cfg.spin_name, None)
            if spin is None or not hasattr(spin, "value"):
                continue
            try:
                value = float(spin.value())
            except Exception:
                continue
            value_cm = value * self._thickness_unit_factor
            if value_cm > 0:
                arch_layers.append((cfg.spin_name, value_cm))

        if not arch_layers:
            label.clear()
            if self._structure_placeholder:
                label.setText(self._structure_placeholder)
            return

        base_layers: list[tuple[str, float]] = []
        for cfg, thickness in zip(self._base_layer_configs, self._base_layer_defaults):
            if thickness and thickness > 0:
                base_layers.append((cfg.spin_name, thickness))

        pixmap = renderer.render(arch_layers, base_layers, label.size())
        if pixmap is None or pixmap.isNull():
            label.clear()
            if self._structure_placeholder:
                label.setText(self._structure_placeholder)
            return

        label.setPixmap(pixmap)
        label.setText("")

    def eventFilter(self, obj, event):
        if obj is self._structure_preview_label and event.type() == QEvent.Type.Resize:
            self._update_structure_preview()
        return super().eventFilter(obj, event)

    def _apply_demo_defaults(self) -> None:
        if getattr(self, "_demo_defaults_applied", False):
            return
        self._demo_defaults_applied = True
        sample_texts = {
            "ed_top_mat": "迷彩网",
            "ed_cover_mat": "钢纤维增强混凝土",
            "ed_arch1_mat": "多孔硬化体",
            "ed_arch2_mat": "C30混凝土",
            "cmb_door_mat": "高强钢板",
        }
        for attr, value in sample_texts.items():
            widget = getattr(self, attr, None)
            if isinstance(widget, QLineEdit):
                widget.setText(value)
        sample_spins = {
            "sp_door_thk": 0.5,
            "sp_top_thk": 0.5,
            "sp_cover_thk": 2.0,
            "sp_arch1_thk": 2.0,
            "sp_arch2_thk": 1.0,
        }
        for attr, value in sample_spins.items():
            spin = getattr(self, attr, None)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue(value)
        self._update_structure_preview()

    def _maybe_restore_draft(self) -> None:
        if not self._draft_file.exists():
            return
        answer = QMessageBox.question(self, "恢复草稿", "检测到上次暂存的草稿，是否恢复？")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            data = json.loads(self._draft_file.read_text(encoding="utf-8"))
        except Exception as exc:
            QMessageBox.warning(self, "恢复失败", f"读取草稿失败：{exc}")
            return
        if isinstance(data, dict):
            self._apply_form_state(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Target_Shelter_AddWindow()
    window.show()
    sys.exit(app.exec())
