from __future__ import annotations

import base64
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
    QMainWindow,
    QApplication,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QPlainTextEdit,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QCheckBox,
    QLabel,
)

from BusinessCode.ImgHelper import ImgHelper
from BusinessCode.structure_preview import LayerVisualConfig, UndergroundStructureRenderer
from UIs.Frm_Target_UCC_Add import Ui_Frm_Target_UCC_Add
from target_model.db import session_scope
from target_model.entities import UndergroundCommandPost
from target_model.sql_repository import SQLRepository


class Target_UCC_AddWindow(QMainWindow,Ui_Frm_Target_UCC_Add):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(740, 660)
        self._ensure_initial_size()

        self._entity_id: int | None = None
        self._image_bytes: bytes | None = None
        self._image_source_path: str | None = None
        self._draft_file = Path.home() / ".underground_editor_draft.json"

        # 新建模式默认标题
        self.setWindowTitle("添加地下指挥所模型")
        if hasattr(self, "cmb_country") and hasattr(self.cmb_country, "clear"):
            self.cmb_country.clear()
        if hasattr(self, "cmb_country"):
            self.cmb_country.addItems(["中国", "美国", "俄罗斯", "法国", "英国", "德国", "其他"])

        # 连接信号
        self.btn_choose_image.clicked.connect(self.on_choose_image)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_save_store.clicked.connect(self.on_save_store)

        # 显示下方“剖面结构模型”区域（若存在）
        try:
            if hasattr(self, "groupBox"):
                self.groupBox.setVisible(True)
        except Exception:
            pass

        self._structure_preview_label = getattr(self, "lbl_image_2", None)
        self._structure_placeholder = (
            self._structure_preview_label.text() if self._structure_preview_label is not None else ""
        )
        ucc_texture_dir = PROJECT_ROOT / "UIstyles" / "images" / "ucc_layers"
        # 地下指挥所剖面纹理位于 UIstyles/images/ucc_layers（缺失时使用纯色填充）
        self._ucc_layer_configs: list[LayerVisualConfig] = [
            LayerVisualConfig("sp_soil_thk", "rock_layer.png", "#3c6b3f"),
            LayerVisualConfig("sp_protect_thk", "protective_layer.png", "#888d96"),
            LayerVisualConfig("sp_lining_thk", "lining_layer.png", "#a7a7a7"),
            LayerVisualConfig("sp_hq_wall_thk", "facility_layer.png", "#bb8751"),
        ]
        self._ucc_renderer = UndergroundStructureRenderer(
            ucc_texture_dir, self._ucc_layer_configs, facility_labels=("地下指挥中心", "支援补给中心")
        )
        if self._structure_preview_label is not None:
            self._structure_preview_label.installEventFilter(self)
        self._connect_ucc_preview_signals()
        self._apply_ucc_demo_defaults()
        self._update_ucc_preview()

        self._apply_required_marker_style()
        self._maybe_restore_draft()

    # ------------------------------------------------------------------ load / edit
    def load_entity(self, entity: "UndergroundCommandPost") -> None:
        self.setWindowTitle("编辑地下指挥所数据模型")
        self._entity_id = entity.id
        self._image_bytes = entity.shelter_picture or None
        self._image_source_path = None
        if self._image_bytes:
            try:
                ImgHelper.from_bytes(self._image_bytes).set_on_label(
                    self.lbl_image, scaled=True, keep_aspect=True, smooth=True
                )
            except Exception:
                self.lbl_image.clear()
        else:
            self.lbl_image.clear()

        self.ed_name.setText((entity.ucc_code or "").strip())
        self.ed_name_2.setText((entity.ucc_name or "").strip())
        self._set_combo_text("cmb_country", entity.country)
        self.ed_unit.setText((entity.base or "").strip())
        self.ed_location.setText((entity.location or "").strip())

        self.ed_soil_mat.setText((entity.rock_layer_materials or "").strip())
        self.sp_soil_thk.setValue(float(entity.rock_layer_thick or 0.0))
        self.sp_soil_fc.setValue(float(entity.rock_layer_strength or 0.0))

        self.ed_protect_mat.setText((entity.protective_layer_material or "").strip())
        self.sp_protect_thk.setValue(float(entity.protective_layer_thick or 0.0))
        self.sp_protect_fc.setValue(float(entity.protective_layer_strength or 0.0))

        self.ed_lining_mat.setText((entity.lining_layer_material or "").strip())
        self.sp_lining_thk.setValue(float(entity.lining_layer_thick or 0.0))
        self.sp_lining_fc.setValue(float(entity.lining_layer_strength or 0.0))

        self.ed_hq_wall.setText((entity.ucc_wall_materials or "").strip())
        self.sp_hq_wall_thk.setValue(float(entity.ucc_wall_thick or 0.0))
        self.sp_hq_fc.setValue(float(entity.ucc_wall_strength or 0.0))

        self.sp_hq_len.setValue(float(entity.ucc_length or 0.0))
        self.sp_hq_wid.setValue(float(entity.ucc_width or 0.0))
        self.sp_hq_hei.setValue(float(entity.ucc_height or 0.0))
        self._ucc_demo_applied = True
        self._update_ucc_preview()

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
        helper = ImgHelper.from_pixmap(pixmap)
        helper.resize(long_side=1280, keep_aspect=True)
        helper.compress_to_limit(200 * 1024, fmt="JPEG")
        self._image_bytes = helper.to_bytes(fmt="JPEG", quality=85)
        self._image_source_path = filename
        helper.set_on_label(self.lbl_image, scaled=True, keep_aspect=True, smooth=True)

    # ------------------------------------------------------------------ save / clear
    def on_save_store(self) -> None:
        if not self._ensure_required_fields():
            return
        try:
            entity = self._build_entity_from_form()
        except ValueError as exc:
            QMessageBox.warning(self, "数据不完整", str(exc))
            return

        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if self._entity_id is None:
                    repo.add(entity)
                else:
                    repo.update_entity(entity)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入数据库时出错：{exc}")
            return

        QMessageBox.information(self, "保存成功", "地下指挥所数据已保存到数据库。")
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
            ("UCCCode", getattr(self, "ed_name", None), lambda: bool(self.ed_name.text().strip())),
            ("UCCName", getattr(self, "ed_name_2", None), lambda: bool(self.ed_name_2.text().strip())),
            ("RockLayerMaterials", getattr(self, "ed_soil_mat", None),
             lambda: bool(self.ed_soil_mat.text().strip())),
            ("RockLayerThick", getattr(self, "sp_soil_thk", None), lambda: self.sp_soil_thk.value() > 0),
            ("ProtectiveLayerMaterial", getattr(self, "ed_protect_mat", None),
             lambda: bool(self.ed_protect_mat.text().strip())),
            ("ProtectiveLayerThick", getattr(self, "sp_protect_thk", None),
             lambda: self.sp_protect_thk.value() > 0),
            ("ProtectiveLayerStrength", getattr(self, "sp_protect_fc", None),
             lambda: self.sp_protect_fc.value() > 0),
            ("LiningLayerMaterial", getattr(self, "ed_lining_mat", None),
             lambda: bool(self.ed_lining_mat.text().strip())),
            ("LiningLayerThick", getattr(self, "sp_lining_thk", None), lambda: self.sp_lining_thk.value() > 0),
            ("LiningLayerStrength", getattr(self, "sp_lining_fc", None), lambda: self.sp_lining_fc.value() > 0),
            ("UCCWallMaterials", getattr(self, "ed_hq_wall", None), lambda: bool(self.ed_hq_wall.text().strip())),
            ("UCCWallThick", getattr(self, "sp_hq_wall_thk", None), lambda: self.sp_hq_wall_thk.value() > 0),
            ("UCCWallStrength", getattr(self, "sp_hq_fc", None), lambda: self.sp_hq_fc.value() > 0),
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
        combo = getattr(self, attr_name, None)
        if combo is None or not hasattr(combo, "currentText"):
            return fallback
        text = combo.currentText()
        text = text.strip() if isinstance(text, str) else ""
        return text or fallback

    # ------------------------------------------------------------------ UI helpers
    def _ensure_initial_size(self) -> None:
        """确保窗口与预览控件有基础尺寸，避免初始显示过小或布局异常。"""
        try:
            if hasattr(self, "lbl_image") and hasattr(self.lbl_image, "setMinimumSize"):
                self.lbl_image.setMinimumSize(QSize(240, 180))
        except Exception:
            # 安全兜底，不影响窗口创建
            pass

    def _set_combo_text(self, attr_name: str, value: str | None) -> None:
        """将指定下拉框设置为给定文本（若文本不存在则保持不变）。"""
        combo = getattr(self, attr_name, None)
        if combo is None or not hasattr(combo, "findText"):
            return
        text = (value or "").strip()
        if not text:
            return
        try:
            index = combo.findText(text)
            if index != -1:
                combo.setCurrentIndex(index)
        except Exception:
            pass

    def _build_entity_from_form(self) -> "UndergroundCommandPost":
        raw_code = (self.ed_name.text() or "").strip()
        name = (self.ed_name_2.text() or "").strip()
        if not name:
            raise ValueError("请填写指挥所名称")

        if raw_code:
            normalized_code = re.sub(r"\s+", "-", raw_code).upper()
        else:
            slug = re.sub(r"[^0-9A-Za-z]+", "-", name).strip("-").upper()
            normalized_code = f"UCC-{slug or '000001'}"

        country = (self.cmb_country.currentText() or "").strip()
        base_name = (self.ed_unit.text() or "").strip()
        location = (self.ed_location.text() or "").strip()

        def _text(value: str | None) -> str | None:
            value = (value or "").strip()
            return value or None

        def _float_or_none(value: float) -> float | None:
            return float(value) if value else None

        entity = UndergroundCommandPost(
            ucc_code=normalized_code,
            ucc_name=name,
            country=_text(country),
            base=_text(base_name),
            shelter_picture=self._image_bytes,
            location=_text(location),
            rock_layer_materials=self.ed_soil_mat.text().strip(),
            rock_layer_thick=float(self.sp_soil_thk.value()),
            rock_layer_strength=_float_or_none(self.sp_soil_fc.value()),
            protective_layer_material=self.ed_protect_mat.text().strip(),
            protective_layer_thick=float(self.sp_protect_thk.value()),
            protective_layer_strength=float(self.sp_protect_fc.value()),
            lining_layer_material=self.ed_lining_mat.text().strip(),
            lining_layer_thick=float(self.sp_lining_thk.value()),
            lining_layer_strength=float(self.sp_lining_fc.value()),
            ucc_wall_materials=self.ed_hq_wall.text().strip(),
            ucc_wall_thick=float(self.sp_hq_wall_thk.value()),
            ucc_wall_strength=float(self.sp_hq_fc.value()),
            ucc_length=_float_or_none(self.sp_hq_len.value()),
            ucc_width=_float_or_none(self.sp_hq_wid.value()),
            ucc_height=_float_or_none(self.sp_hq_hei.value()),
            ucc_status=None,
        )
        if self._entity_id is not None:
            entity.id = self._entity_id
        return entity

    # ------------------------------------------------------------------ draft helpers
    def _collect_form_state(self) -> dict[str, object]:
        state: dict[str, object] = {"entity_id": self._entity_id}
        if self._image_bytes:
            state["image_blob"] = base64.b64encode(self._image_bytes).decode("ascii")
        else:
            state["image_blob"] = None

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

        blob = state.get("image_blob")
        if isinstance(blob, str) and blob:
            try:
                self._image_bytes = base64.b64decode(blob)
            except Exception:
                self._image_bytes = None
        else:
            self._image_bytes = None
        self._image_source_path = None
        if self._image_bytes:
            try:
                ImgHelper.from_bytes(self._image_bytes).set_on_label(
                    self.lbl_image, scaled=True, keep_aspect=True, smooth=True
                )
            except Exception:
                self.lbl_image.clear()
        else:
            self.lbl_image.clear()

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

        self._ucc_demo_applied = True
        self._update_ucc_preview()

    def _connect_ucc_preview_signals(self) -> None:
        names = ("sp_soil_thk", "sp_protect_thk", "sp_lining_thk", "sp_hq_wall_thk")
        for name in names:
            widget = getattr(self, name, None)
            if isinstance(widget, QDoubleSpinBox):
                try:
                    widget.valueChanged.connect(self._update_ucc_preview)
                except Exception:
                    pass

    def _update_ucc_preview(self, *_: object) -> None:
        label = self._structure_preview_label
        renderer = getattr(self, "_ucc_renderer", None)
        if label is None or renderer is None:
            return
        layers: list[tuple[str, float]] = []
        for cfg in getattr(self, "_ucc_layer_configs", []):
            spin = getattr(self, cfg.spin_name, None)
            if spin is None or not hasattr(spin, "value"):
                continue
            try:
                value = float(spin.value())
            except Exception:
                continue
            if value > 0:
                layers.append((cfg.spin_name, value))
        if not layers:
            label.clear()
            placeholder = getattr(self, "_structure_placeholder", "")
            if placeholder:
                label.setText(placeholder)
            return
        pixmap = renderer.render(layers, label.size())
        if pixmap is None or pixmap.isNull():
            label.clear()
            placeholder = getattr(self, "_structure_placeholder", "")
            if placeholder:
                label.setText(placeholder)
            return
        label.setPixmap(pixmap)
        label.setText("")

    def eventFilter(self, obj, event):
        if obj is self._structure_preview_label and event.type() == QEvent.Type.Resize:
            self._update_ucc_preview()
        return super().eventFilter(obj, event)

    def _apply_ucc_demo_defaults(self, force: bool = False) -> None:
        if getattr(self, "_ucc_demo_applied", False) and not force:
            return
        field_names = ("sp_soil_thk", "sp_protect_thk", "sp_lining_thk", "sp_hq_wall_thk")
        current_values: list[float] = []
        for name in field_names:
            spin = getattr(self, name, None)
            if hasattr(spin, "value"):
                try:
                    current_values.append(float(spin.value()))
                except Exception:
                    current_values.append(0.0)
            else:
                current_values.append(0.0)
        if not force and any(value > 0 for value in current_values):
            self._ucc_demo_applied = True
            return
        defaults = {
            "sp_soil_thk": 1000.0,
            "sp_protect_thk": 200.0,
            "sp_lining_thk": 80.0,
            "sp_hq_wall_thk": 80.0,
        }
        for name, value in defaults.items():
            spin = getattr(self, name, None)
            if isinstance(spin, QDoubleSpinBox):
                spin.setValue(value)
        demo_texts = {
            "ed_soil_mat": "土壤岩层：花岗岩",
            "ed_protect_mat": "防护层：硅酸盐水泥",
            "ed_lining_mat": "衬砌层：钢筋混凝土",
            "ed_hq_wall": "地下指挥中心：钢筋混凝土",
        }
        for attr, text in demo_texts.items():
            widget = getattr(self, attr, None)
            if isinstance(widget, QLineEdit) and not widget.text():
                widget.setText(text)
        self._ucc_demo_applied = True
        self._update_ucc_preview()

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
        self._image_bytes = None
        self._image_source_path = None
        self._entity_id = None
        self._ucc_demo_applied = False
        self._apply_ucc_demo_defaults(force=True)

    # ------------------------------------------------------------------ draft restore
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

    def _apply_required_marker_style(self) -> None:
        for label in self.findChildren(QLabel):
            text = label.text()
            if not text or "color:#ff0000" in text:
                continue
            new_text = text
            replaced = False
            if "(*)" in new_text:
                new_text = new_text.replace(
                    "(*)", '<span style="color:#ff0000;">(*)</span>'
                )
                replaced = True
            if "（*）" in new_text:
                new_text = new_text.replace(
                    "（*）", '<span style="color:#ff0000;">(*)</span>'
                )
                replaced = True
            if replaced:
                label.setTextFormat(Qt.TextFormat.RichText)
                label.setText(new_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Target_UCC_AddWindow()
    window.show()
    sys.exit(app.exec())
