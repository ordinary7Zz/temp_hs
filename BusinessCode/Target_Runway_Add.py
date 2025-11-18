from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QMainWindow,
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
from BusinessCode.structure_preview import LayerVisualConfig, LayeredStructureRenderer
from UIs.Frm_Target_Runway_Add import Ui_Frm_Target_Runway_Add
from target_model.db import session_scope
from target_model.entities import AirportRunway
from target_model.sql_repository import SQLRepository


class Target_Runway_AddWindow(QMainWindow, Ui_Frm_Target_Runway_Add):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(770,700)
        # 兼容不同UI版本的控件名
        self.btn_choose_image = self._resolve_widget("btn_choose_image", "btn_choose_image_4")
        self.lbl_image = self._resolve_widget("lbl_image", "lbl_image_4", "lbl_image_5")
        self._secondary_image_label = getattr(self, "lbl_image_5", None)
        self.cmb_cement_type = self._resolve_widget("cmb_cement_type", "cmb_cement_type_3")

        # 记录图片占位文字
        self._image_placeholders: dict[str, str] = {}
        for img_label in (self.lbl_image, self._secondary_image_label):
            if img_label is not None:
                self._image_placeholders[img_label.objectName()] = img_label.text()

        layer_texture_dir = PROJECT_ROOT / "UIstyles" / "images" / "runway_layers"
        # 剖面纹理图片位于 UIstyles/images/runway_layers（缺失时会自动回退为纯色填充）
        self._structure_layer_configs: list[LayerVisualConfig] = [
            LayerVisualConfig("sp_thk_concrete", "surface_layer.png", "#bfc2c7"),
            LayerVisualConfig("sp_thk_cement", "cement_base_layer.png", "#a7a9b0"),
            LayerVisualConfig("sp_thk_crushed", "graded_gravel_layer.png", "#7f8865"),
            LayerVisualConfig("sp_thk_crushed_2", "subgrade_layer.png", "#b88c55"),
        ]
        self._structure_renderer = LayeredStructureRenderer(layer_texture_dir, self._structure_layer_configs)
        if self._secondary_image_label is not None:
            self._secondary_image_label.installEventFilter(self)

        # 预览标题前缀缓存
        self._preview_label_bases: dict[str, str] = {}
        for attr in ("lbl_name_2", "lbl_country_2", "lbl_length_2", "lbl_heading_2"):
            label = getattr(self, attr, None)
            if label is not None:
                self._preview_label_bases[attr] = label.text().strip()

        self._runway_code_input = getattr(self, "ed_runway_code", None)
        self._base_input = getattr(self, "ed_base", None) or getattr(self, "ed_airport_name_3", None)
        self._current_entity: "AirportRunway | None" = None

        self._entity_id: int | None = None
        self._image_path: str | None = None
        self._image_bytes: bytes | None = None
        self._image_source_path: str | None = None
        self._draft_file = Path.home() / ".runway_editor_draft.json"

        if hasattr(self, "cmb_country") and hasattr(self.cmb_country, "clear"):
            self.cmb_country.clear()
        if hasattr(self, "cmb_country"):
            self.cmb_country.addItems([ "美国", "印度", "日本", "中国", "中国台湾", "俄罗斯", "法国", "英国", "德国", "其他"])

        # 信号连接
        self.btn_choose_image.clicked.connect(self.on_choose_image)
        self._resolve_widget("btn_clear").clicked.connect(self.on_clear)
        self._resolve_widget("btn_save_store").clicked.connect(self.on_save_store)

        # 显示“剖面结构模型”区域（若存在）
        try:
            if hasattr(self, "gb_basic_2"):
                self.gb_basic_2.setVisible(True)
        except Exception:
            pass

        self._connect_preview_signals()
        self._apply_required_marker_style()
        self._maybe_restore_draft()
        self._update_preview()

    # ------------------------------------------------------------------ image selection
    def on_choose_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "选择跑道图片", str(Path.home()), "Images (*.png *.jpg *.jpeg *.bmp)"
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
        self._image_path = filename
        self._image_source_path = filename
        self._image_bytes = helper.to_bytes(fmt="JPEG", quality=85)
        self._set_preview_pixmap(helper.to_pixmap())

    # ------------------------------------------------------------------ load / save
    def load_entity(self, entity: "AirportRunway") -> None:
        self._current_entity = entity
        self._entity_id = entity.id
        self._image_bytes = entity.runway_picture if isinstance(entity.runway_picture, (bytes, bytearray)) else None
        self._image_path = None
        self._image_source_path = None
        self._set_preview_pixmap(None)
        if self._image_bytes:
            try:
                helper = ImgHelper.from_bytes(self._image_bytes)
                self._set_preview_pixmap(helper.to_pixmap())
            except Exception:
                self._set_preview_pixmap(None)
        self.setWindowTitle("编辑机场跑道模型")

        self.ed_airport_name.setText(entity.runway_name or "")
        if self._runway_code_input is not None:
            try:
                self._runway_code_input.setText(entity.runway_code or "")
            except Exception:
                pass
        if getattr(entity, "country", None) and hasattr(self, "cmb_country"):
            self.cmb_country.setCurrentText(entity.country)
        if self._base_input is not None and hasattr(self._base_input, "setText"):
            try:
                self._base_input.setText(entity.base or "")
            except Exception:
                pass

        self._set_length_spin(self.sp_length, getattr(self, "cmb_length_unit", None), entity.r_length)
        self._set_length_spin(self.sp_width, getattr(self, "cmb_width_unit", None), entity.r_width)

        self._set_thickness_spin(self.sp_thk_concrete, getattr(self, "cmb_thk_concrete_unit", None),
                                 entity.pccsc_thick)
        self._set_spin_value(self.sp_fc_concrete, entity.pccsc_strength)
        self._set_spin_value(self.sp_fr_concrete, entity.pccsc_flexural)
        self._set_spin_value(self.sp_thk_concrete_2, entity.pccsc_freeze)

        if self.cmb_cement_type is not None and entity.pccsc_cement:
            try:
                self.cmb_cement_type.setCurrentText(entity.pccsc_cement)
            except Exception:
                pass

        self._set_spin_value(self.sp_slab_w, entity.pccsc_block_size1)
        self._set_spin_value(self.sp_slab_l, entity.pccsc_block_size2)

        self._set_thickness_spin(self.sp_thk_cement, getattr(self, "cmb_thk_cement_unit", None),
                                 entity.ctbc_thick)
        self._set_spin_value(self.sp_fc_cement, entity.ctbc_strength)
        self._set_spin_value(self.sp_fr_cement, entity.ctbc_flexural)
        self._set_line_value("ed_cement_ratio", entity.ctbc_cement)
        self._set_line_value("ed_cement_ratio_2", entity.ctbc_compaction)

        self._set_thickness_spin(self.sp_thk_crushed, getattr(self, "cmb_thk_crushed_unit", None),
                                 entity.gcss_thick)
        self._set_spin_value(self.sp_cbr_subgrade_2, entity.gcss_strength)
        self._set_spin_value(self.sp_fr_concrete_2, entity.gcss_compaction)

        self._set_thickness_spin(self.sp_thk_crushed_2, getattr(self, "cmb_thk_crushed_unit_2", None),
                                 entity.cs_thick)
        self._set_spin_value(self.sp_cbr_subgrade_3, entity.cs_strength)
        self._set_spin_value(self.sp_fr_concrete_3, entity.cs_compaction)
        self._update_preview()

    def on_save_store(self) -> None:
        if not self._ensure_required_fields():
            return
        try:
            runway = self._build_entity_from_form()
        except ValueError as exc:
            QMessageBox.warning(self, "数据不完整", str(exc))
            return
        try:
            with session_scope() as session:
                repo = SQLRepository(session)
                if self._entity_id is None:
                    saved = repo.add(runway)
                    self._entity_id = getattr(saved, "id", None)
                    self._current_entity = saved
                else:
                    updated = repo.update_entity(runway)
                    self._current_entity = updated
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"写入数据库时出错：{exc}")
            return
        QMessageBox.information(self, "保存成功", "跑道数据已保存到数据库。")
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
            if validator():
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
            ("RunwayName", self.ed_airport_name, lambda: bool(self.ed_airport_name.text().strip())),
            ("Country", getattr(self, "cmb_country", None), lambda: bool(self._combo_text("cmb_country", ""))),
            ("RLength", getattr(self, "sp_length", None),
             lambda: getattr(self, "sp_length", None) is not None and self.sp_length.value() > 0),
            ("RWidth", getattr(self, "sp_width", None),
             lambda: getattr(self, "sp_width", None) is not None and self.sp_width.value() > 0),
            ("PCCSCThick", getattr(self, "sp_thk_concrete", None),
             lambda: getattr(self, "sp_thk_concrete", None) is not None and self.sp_thk_concrete.value() > 0),
            ("CTBCThick", getattr(self, "sp_thk_cement", None),
             lambda: getattr(self, "sp_thk_cement", None) is not None and self.sp_thk_cement.value() > 0),
            ("GCSSThick", getattr(self, "sp_thk_crushed", None),
             lambda: getattr(self, "sp_thk_crushed", None) is not None and self.sp_thk_crushed.value() > 0),
            ("CSThick", getattr(self, "sp_thk_crushed_2", None),
             lambda: getattr(self, "sp_thk_crushed_2", None) is not None and self.sp_thk_crushed_2.value() > 0),
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

    def _build_entity_from_form(self) -> "AirportRunway":
        runway_name = self._line_text("ed_airport_name").strip()
        if not runway_name:
            raise ValueError("请填写机场名称。")

        if self._entity_id is not None and self._current_entity is not None:
            runway_code = self._current_entity.runway_code
        else:
            code_text = self._line_text("ed_runway_code").strip()
            runway_code = code_text or runway_name
        if not runway_code:
            raise ValueError("请填写机场代码。")
        runway_code = re.sub(r"\s+", "-", runway_code.strip()).upper()

        country = self._combo_text("cmb_country", fallback="").strip()
        base_text = ""
        if self._base_input is not None and hasattr(self._base_input, "text"):
            base_text = self._base_input.text().strip()
        if not base_text:
            base_text = self._line_text("ed_airport_name_3")

        r_length = self._to_meters(self.sp_length.value(), self._combo_text("cmb_length_unit", "m"))
        r_width = self._to_meters(self.sp_width.value(), self._combo_text("cmb_width_unit", "m"))

        runway = AirportRunway(
            runway_code=runway_code,
            runway_name=runway_name,
            country=country or None,
            base=base_text or None,
            runway_picture=self._image_bytes,
            r_length=r_length,
            r_width=r_width,
            pccsc_thick=self._to_centimeters(
                self.sp_thk_concrete.value(), self._combo_text("cmb_thk_concrete_unit", "cm")
            ),
            pccsc_strength=self.sp_fc_concrete.value(),
            pccsc_flexural=self.sp_fr_concrete.value(),
            pccsc_freeze=self.sp_thk_concrete_2.value(),
            pccsc_cement=self._combo_text("cmb_cement_type", "").strip() or None,
            pccsc_block_size1=self.sp_slab_w.value(),
            pccsc_block_size2=self.sp_slab_l.value(),
            ctbc_thick=self._to_centimeters(
                self.sp_thk_cement.value(), self._combo_text("cmb_thk_cement_unit", "cm")
            ),
            ctbc_strength=self.sp_fc_cement.value(),
            ctbc_flexural=self.sp_fr_cement.value(),
            ctbc_cement=self._float_from_line("ed_cement_ratio"),
            ctbc_compaction=self._float_from_line("ed_cement_ratio_2"),
            gcss_thick=self._to_centimeters(
                self.sp_thk_crushed.value(), self._combo_text("cmb_thk_crushed_unit", "cm")
            ),
            gcss_strength=self.sp_cbr_subgrade_2.value(),
            gcss_compaction=self.sp_fr_concrete_2.value(),
            cs_thick=self._to_centimeters(
                self.sp_thk_crushed_2.value(), self._combo_text("cmb_thk_crushed_unit_2", "cm")
            ),
            cs_strength=self.sp_cbr_subgrade_3.value(),
            cs_compaction=self.sp_fr_concrete_3.value(),
            runway_status=getattr(self._current_entity, "runway_status", None),
        )
        if self._entity_id is not None:
            runway.id = self._entity_id
            if self._current_entity is not None:
                runway.created_time = self._current_entity.created_time
        return runway

    # ------------------------------------------------------------------ helpers
    def _resolve_widget(self, *names):
        for name in names:
            widget = getattr(self, name, None)
            if widget is not None:
                return widget
        raise AttributeError(f"Required widget not found (tried: {', '.join(names)})")

    @staticmethod
    def _set_spin_value(spin, value: float | None) -> None:
        if spin is None:
            return
        spin.setValue(float(value) if value is not None else 0.0)

    @staticmethod
    def _set_length_spin(spin, combo, value: float | None) -> None:
        if hasattr(combo, "setCurrentText"):
            try:
                combo.setCurrentText("m")
            except Exception:
                pass
        try:
            spin.setValue(float(value) if value is not None else 0.0)
        except (TypeError, ValueError):
            spin.setValue(0.0)

    @staticmethod
    def _set_thickness_spin(spin, combo, value: float | None) -> None:
        if hasattr(combo, "setCurrentText"):
            try:
                combo.setCurrentText("cm")
            except Exception:
                pass
        try:
            spin.setValue(float(value) if value is not None else 0.0)
        except (TypeError, ValueError):
            spin.setValue(0.0)

    @staticmethod
    def _to_meters(value: float, unit: str) -> float:
        unit = (unit or "").strip().lower()
        if unit == "ft":
            return value * 0.3048
        return value

    @staticmethod
    def _to_centimeters(value: float, unit: str) -> float:
        unit = (unit or "").strip().lower()
        if unit == "mm":
            return value / 10.0
        return value

    def _combo_text(self, attr_name: str, fallback: str = "") -> str:
        combo = getattr(self, attr_name, None)
        if combo is None or not hasattr(combo, "currentText"):
            return fallback
        text = combo.currentText()
        text = text.strip() if isinstance(text, str) else ""
        return text or fallback

    def _connect_preview_signals(self) -> None:
        names = [
            "sp_thk_concrete", "sp_thk_concrete_2", "sp_fc_concrete", "sp_fr_concrete",
            "sp_slab_l", "sp_slab_w", "cmb_cement_type", "sp_thk_cement",
            "sp_fc_cement", "sp_fr_cement", "ed_cement_ratio", "ed_cement_ratio_2",
            "sp_thk_crushed", "sp_cbr_subgrade_2", "sp_fr_concrete_2",
            "sp_thk_crushed_2", "sp_cbr_subgrade_3", "sp_fr_concrete_3",
        ]
        for name in names:
            widget = getattr(self, name, None)
            if widget is None:
                continue
            try:
                if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                    widget.valueChanged.connect(self._update_preview)
                elif isinstance(widget, QComboBox):
                    widget.currentTextChanged.connect(self._update_preview)
                elif isinstance(widget, QLineEdit):
                    widget.textChanged.connect(self._update_preview)
            except Exception:
                pass

    def _update_preview(self, *_: object) -> None:
        summaries = {
            "lbl_name_2": self._format_concrete_summary(),
            "lbl_country_2": self._format_cement_summary(),
            "lbl_length_2": self._format_gravel_summary(),
            "lbl_heading_2": self._format_subgrade_summary(),
        }
        for attr, parts in summaries.items():
            self._set_preview_label(attr, parts)
        self._update_structure_preview()

    def _update_structure_preview(self) -> None:
        label = self._secondary_image_label
        renderer = getattr(self, "_structure_renderer", None)
        if label is None or renderer is None:
            return
        layers: list[tuple[str, float]] = []
        for cfg in self._structure_layer_configs:
            thickness = self._spin_value(cfg.spin_name)
            if thickness is None or thickness <= 0:
                continue
            layers.append((cfg.spin_name, thickness))
        if not layers:
            placeholder = self._image_placeholders.get(label.objectName(), "")
            label.clear()
            label.setText(placeholder or "（未设置厚度）")
            return
        pixmap = renderer.render(layers, label.size())
        if pixmap is None or pixmap.isNull():
            placeholder = self._image_placeholders.get(label.objectName(), "")
            label.clear()
            label.setText(placeholder or "无法生成剖面图")
            return
        label.setPixmap(pixmap)
        label.setText("")

    def eventFilter(self, obj, event):
        if obj is self._secondary_image_label and event.type() == QEvent.Type.Resize:
            self._update_structure_preview()
        return super().eventFilter(obj, event)

    def _spin_value(self, name: str) -> float | None:
        widget = getattr(self, name, None)
        if widget is None or not hasattr(widget, "value"):
            return None
        try:
            value = float(widget.value())
        except Exception:
            return None
        return value

    def _line_text(self, name: str, default: str = "") -> str:
        widget = getattr(self, name, None)
        if widget is None or not hasattr(widget, "text"):
            return default
        text = widget.text()
        text = text.strip() if isinstance(text, str) else ""
        return text or default

    def _text_or_none(self, name: str) -> str | None:
        value = self._line_text(name)
        return value or None

    def _float_from_line(self, name: str) -> float | None:
        text = self._line_text(name)
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _set_line_value(self, name: str, value: float | str | None) -> None:
        widget = getattr(self, name, None)
        if widget is None or not hasattr(widget, "setText"):
            return
        if value is None or value == "":
            widget.setText("")
        elif isinstance(value, str):
            widget.setText(value)
        else:
            widget.setText(f"{float(value):g}")

    def _set_preview_label(self, attr: str, parts: list[str]) -> None:
        label = getattr(self, attr, None)
        if label is None:
            return
        base = self._preview_label_bases.get(attr, label.text().strip())
        prefix = base
        if "：" in prefix:
            prefix = prefix.split("：", 1)[0]
        elif ":" in prefix:
            prefix = prefix.split(":", 1)[0]
        prefix = prefix.strip()
        # 需求：冒号后的文字全部不显示，只保留标题（层名）
        label.setText(prefix)

    def _format_concrete_summary(self) -> list[str]:
        parts: list[str] = []
        thickness = self._spin_value("sp_thk_concrete")
        if thickness and thickness > 0:
            parts.append(f"{thickness:g} cm")
        fc = self._spin_value("sp_fc_concrete")
        if fc and fc > 0:
            parts.append(f"抗压≥{fc:g} MPa")
        fr = self._spin_value("sp_fr_concrete")
        if fr and fr > 0:
            parts.append(f"抗折≥{fr:g} MPa")
        fatigue = self._spin_value("sp_thk_concrete_2")
        if fatigue and fatigue > 0:
            parts.append(f"抗冻融循环≥{fatigue:g} 次")
        slab_l = self._spin_value("sp_slab_l")
        slab_w = self._spin_value("sp_slab_w")
        if slab_l and slab_w and slab_l > 0 and slab_w > 0:
            parts.append(f"{slab_l:g} × {slab_w:g} m")
        cement_type = self._combo_text("cmb_cement_type", "")
        if cement_type:
            parts.append(cement_type)
        return parts

    def _format_cement_summary(self) -> list[str]:
        parts: list[str] = []
        thickness = self._spin_value("sp_thk_cement")
        if thickness and thickness > 0:
            parts.append(f"{thickness:g} cm")
        fc = self._spin_value("sp_fc_cement")
        if fc and fc > 0:
            parts.append(f"抗压≥{fc:g} MPa")
        fr = self._spin_value("sp_fr_cement")
        if fr and fr > 0:
            parts.append(f"抗折≥{fr:g} MPa")
        ratio = self._line_text("ed_cement_ratio")
        if ratio:
            parts.append(f"水泥掺量 {ratio}")
        compaction = self._line_text("ed_cement_ratio_2")
        if compaction:
            suffix = "%" if not compaction.endswith("%") else ""
            parts.append(f"夯实密实度 {compaction}{suffix}")
        return parts

    def _format_gravel_summary(self) -> list[str]:
        parts: list[str] = []
        thickness = self._spin_value("sp_thk_crushed")
        if thickness and thickness > 0:
            parts.append(f"{thickness:g} cm")
        cbr = self._spin_value("sp_cbr_subgrade_2")
        if cbr and cbr > 0:
            parts.append(f"强度承载比≥{cbr:g}%")
        modulus = self._spin_value("sp_fr_concrete_2")
        if modulus and modulus > 0:
            parts.append(f"压实模量≥{modulus:g} MPa")
        return parts

    def _format_subgrade_summary(self) -> list[str]:
        parts: list[str] = []
        thickness = self._spin_value("sp_thk_crushed_2")
        if thickness and thickness > 0:
            parts.append(f"{thickness:g} cm")
        cbr = self._spin_value("sp_cbr_subgrade_3")
        if cbr and cbr > 0:
            parts.append(f"强度承载比≥{cbr:g}%")
        modulus = self._spin_value("sp_fr_concrete_3")
        if modulus and modulus > 0:
            parts.append(f"压实模量≥{modulus:g} MPa")
        return parts

    def _set_preview_pixmap(self, pixmap: QPixmap | None) -> None:
        if self.lbl_image is None:
            return
        if pixmap is None or pixmap.isNull():
            placeholder = self._image_placeholders.get(self.lbl_image.objectName(), "")
            if placeholder:
                self.lbl_image.setText(placeholder)
            else:
                self.lbl_image.clear()
            return
        target_size = self.lbl_image.size()
        scaled = pixmap if target_size.isEmpty() else pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_image.setText("")
        self.lbl_image.setPixmap(scaled)

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
                state[f"combo:{name}"] = {"index": widget.currentIndex(), "text": widget.currentText()}

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
        self._image_path = None
        self._image_source_path = None
        self._set_preview_pixmap(None)
        if self._image_bytes:
            try:
                helper = ImgHelper.from_bytes(self._image_bytes)
                self._set_preview_pixmap(helper.to_pixmap())
            except Exception:
                self._set_preview_pixmap(None)

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
        self._update_preview()

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

        self._set_preview_pixmap(None)
        self._entity_id = None
        self._image_path = None
        self._image_source_path = None
        self._image_bytes = None
        self._current_entity = None
        self._update_preview()

    def _maybe_restore_draft(self) -> None:
        if not self._draft_file.exists():
            return
        answer = QMessageBox.question(
            self,
            "恢复草稿",
            "检测到上次暂存的草稿，是否恢复？",
        )
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
    window = Target_Runway_AddWindow()
    window.show()
    sys.exit(app.exec())
