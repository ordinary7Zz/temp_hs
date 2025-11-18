from __future__ import annotations

import os
import sys
from dataclasses import dataclass, fields
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Type

from loguru import logger
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QFileDialog,
    QDialog,
    QHeaderView,
    QMessageBox,
)
from sqlalchemy import func, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from BusinessCode.semantic_search import SemanticIndex, build_semantic_index_from_db
from target_model.db import session_scope as target_session
from target_model.entities import AirportRunway, AircraftShelter, UndergroundCommandPost
from target_model.exporters import CSVExporter, JSONExporter
from target_model.orm import (
    AircraftShelterORM,
    AirportRunwayORM,
    UndergroundCommandPostORM,
)
from UIs import (
    Frm_Search_Runway as RunwayUI,
    Frm_Search_Shelter as ShelterUI,
    Frm_Search_UCC as UCCUI,
)


def _to_decimal(text: str) -> Optional[Decimal]:
    s = (text or "").strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _to_display(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value.normalize())
    if isinstance(value, float):
        return f"{value:.4g}".rstrip("0").rstrip(".")
    return str(value)


@dataclass(frozen=True)
class ColumnDef:
    header: str
    extractor: Callable[[Any], Any]


class TargetSemanticIndexWorker(QThread):
    message = pyqtSignal(str)
    done = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(
        self,
        *,
        session_factory,
        orm_cls,
        id_attr: str,
        model_path: str,
        prefer_model: Optional[str],
        rebuild: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.session_factory = session_factory
        self.orm_cls = orm_cls
        self.id_attr = id_attr
        self.model_path = model_path
        self.prefer_model = prefer_model
        self.rebuild = rebuild

    def run(self) -> None:
        try:
            base = os.path.splitext(self.model_path)[0]
            tfidf_file = base + ".tfidf.joblib"
            existing_index = os.path.exists(tfidf_file)
            if existing_index and not self.rebuild:
                try:
                    self.message.emit("正在加载语义索引 ...")
                    idx = SemanticIndex.load_index(base)
                    self.done.emit(idx)
                    self.message.emit("语义索引加载完成")
                    return
                except Exception as exc:
                    logger.exception(exc)
                    self.message.emit("索引加载失败，改为重新构建 ...")

            self.message.emit("正在构建语义索引 ...")
            with self.session_factory() as session:
                idx = build_semantic_index_from_db(
                    session, self.orm_cls, id_attr=self.id_attr, prefer_model=self.prefer_model
                )
            if idx is None:
                self.message.emit("当前模型无数据，无法构建索引")
                self.done.emit(None)
                return
            idx.save_index(base)
            self.done.emit(idx)
            self.message.emit("语义索引构建完成")
        except Exception as exc:
            logger.exception(exc)
            self.error.emit(f"构建语义索引失败: {exc}")


class _BaseTargetSearchDialog(QDialog):
    """Shared behaviours for the three target search dialogs."""

    category: str = ""
    ui_class: Optional[type] = None
    entity_cls: Optional[Type[Any]] = None
    orm_cls: Optional[Type[Any]] = None
    id_attr: str = "id"
    semantic_model_path: str = "./models/target_index"
    prefer_model: Optional[str] = "paraphrase-multilingual-MiniLM-L12-v2"
    table_columns: Sequence[ColumnDef] = ()
    line_edit_names: Sequence[str] = ()
    check_box_names: Sequence[str] = ()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        if self.ui_class is None or self.entity_cls is None or self.orm_cls is None:
            raise ValueError("ui_class/entity_cls/orm_cls must be defined")

        self.ui = self.ui_class()  # type: ignore[call-arg]
        self.ui.setupUi(self)

        self.results: List[Any] = []
        self.sem_idx: Optional[SemanticIndex] = None
        self._sem_worker: Optional[TargetSemanticIndexWorker] = None

        self._init_navigation()
        self._connect_common_slots()
        self._setup_field_dependencies()
        self._start_build_semantic_index()

    # ------------------------------------------------------------------ navigation
    def _init_navigation(self) -> None:
        nav_buttons = {
            "runway": getattr(self.ui, "btn_combination_2", None),
            "shelter": getattr(self.ui, "btn_combination_3", None),
            "ucc": getattr(self.ui, "btn_combination_4", None),
        }
        for key, button in nav_buttons.items():
            if button is None:
                continue
            if key == self.category:
                button.setEnabled(False)
                continue
            button.clicked.connect(lambda _=False, nav_key=key: self._handle_navigation(nav_key))

    def _handle_navigation(self, nav_key: str) -> None:
        target_cls = TARGET_DIALOGS.get(nav_key)
        if not target_cls or isinstance(self, target_cls):
            return
        parent = self.parent()
        self.done(0)
        dialog = target_cls(parent=parent)
        dialog.exec()

    # ------------------------------------------------------------------ UI wiring
    def _connect_common_slots(self) -> None:
        getattr(self.ui, "btn_combination", None) and self.ui.btn_combination.clicked.connect(
            self.combination_search
        )
        getattr(self.ui, "btn_condition_reset", None) and self.ui.btn_condition_reset.clicked.connect(
            self.reset
        )
        getattr(self.ui, "btn_nlp_rebuild", None) and self.ui.btn_nlp_rebuild.clicked.connect(
            lambda: self._start_build_semantic_index(rebuild=True)
        )
        getattr(self.ui, "btn_nlp_search", None) and self.ui.btn_nlp_search.clicked.connect(
            self.nlp_search
        )
        getattr(self.ui, "btn_export", None) and self.ui.btn_export.clicked.connect(self.export_results)

    def _checkbox_dependencies(self) -> Dict[str, Sequence[str]]:
        return {}

    def _setup_field_dependencies(self) -> None:
        mapping = self._checkbox_dependencies() or {}
        for chk_name, widget_names in mapping.items():
            checkbox = getattr(self.ui, chk_name, None)
            if checkbox is None:
                continue

            def handler(checked: bool, names=tuple(widget_names)) -> None:
                self._set_dependency_widgets(names, checked)

            try:
                checkbox.toggled.connect(handler)
            except Exception:
                continue
            handler(checkbox.isChecked())

    def _set_dependency_widgets(self, widget_names: Sequence[str], enabled: bool) -> None:
        for name in widget_names:
            widget = getattr(self.ui, name, None)
            if widget is None:
                continue
            widget.setEnabled(enabled)
            if not enabled and hasattr(widget, "clear"):
                try:
                    widget.clear()
                except Exception:
                    pass

    # ------------------------------------------------------------------ semantic index
    def _start_build_semantic_index(self, rebuild: bool = False) -> None:
        self._set_sem_controls_enabled(False)
        self._sem_worker = TargetSemanticIndexWorker(
            session_factory=target_session,
            orm_cls=self.orm_cls,
            id_attr=self.id_attr,
            model_path=self.semantic_model_path,
            prefer_model=self.prefer_model,
            rebuild=rebuild,
            parent=self,
        )
        self._sem_worker.message.connect(self._on_sem_message)
        self._sem_worker.done.connect(self._on_sem_done)
        self._sem_worker.error.connect(self._on_sem_error)
        self._sem_worker.finished.connect(self._on_sem_finished)
        self._sem_worker.start()

    def _set_sem_controls_enabled(self, enabled: bool) -> None:
        for name in ("txt_nlp", "btn_nlp_search", "btn_nlp_rebuild"):
            widget = getattr(self.ui, name, None)
            if widget:
                widget.setEnabled(enabled)

    def _on_sem_message(self, msg: str) -> None:
        self._set_status(msg)

    def _on_sem_done(self, sem_idx_obj) -> None:
        self.sem_idx = sem_idx_obj
        if sem_idx_obj is not None:
            self._set_status("语义索引准备就绪")

    def _on_sem_error(self, err: str) -> None:
        QMessageBox.critical(self, "错误", err)

    def _on_sem_finished(self) -> None:
        self._set_sem_controls_enabled(True)
        self._sem_worker = None

    # ------------------------------------------------------------------ core actions
    def combination_search(self) -> None:
        condition = self._collect_conditions()
        if not self._has_conditions(condition):
            QMessageBox.information(self, "提示", "请先勾选并填写至少一个检索条件")
            return
        try:
            data = self._query_by_conditions(condition)
        except Exception as exc:
            logger.exception(exc)
            QMessageBox.warning(self, "提示", f"查询失败: {exc}")
            return
        self.results = data
        self._populate_table(data)
        self._set_status(f"共找到 {len(data)} 条记录")

    def nlp_search(self) -> None:
        if self.sem_idx is None:
            QMessageBox.information(self, "提示", "语义索引尚未准备好")
            return
        text = getattr(self.ui, "txt_nlp", None)
        query = text.text().strip() if text else ""
        if not query:
            QMessageBox.information(self, "提示", "请输入检索关键词")
            return

        cand_ids = self.sem_idx.search(query, topk=50)
        if not cand_ids:
            self._set_status("索引中没有数据")
            return
        stmt = select(self.orm_cls).where(getattr(self.orm_cls, self.id_attr).in_(cand_ids))
        with target_session() as session:
            rows = session.execute(stmt).scalars().all()
        entities = [self._to_entity(row) for row in rows]
        by_id = {getattr(e, self.id_attr): e for e in entities}
        ordered = [by_id[id_] for id_ in cand_ids if id_ in by_id]
        self.results = ordered
        self._populate_table(ordered)
        self._set_status(f"智能检索返回 {len(ordered)} 条结果")

    def _has_conditions(self, condition: Dict[str, Any]) -> bool:
        for key, value in condition.items():
            if key.endswith('_enabled'):
                if value and self._value_present(condition.get(key[:-8])):
                    return True
            elif self._value_present(value):
                return True
        return False

    @staticmethod
    def _value_present(value: Any) -> bool:
        if value in (None, '', False):
            return False
        if isinstance(value, str):
            return bool(value.strip())
        return True


    def reset(self) -> None:
        for name in self.line_edit_names:
            widget = getattr(self.ui, name, None)
            if widget:
                widget.clear()
        for name in self.check_box_names:
            widget = getattr(self.ui, name, None)
            if widget:
                widget.setChecked(False)
        self._set_status("已重置检索条件")

    def export_results(self) -> None:
        if not self.results:
            QMessageBox.information(self, "提示", "没有可导出的结果")
            return
        default_name = f"{self.category}_targets"
        path, chosen_filter = QFileDialog.getSaveFileName(
            self,
            "导出查询结果",
            f"{default_name}.csv",
            "CSV 文件 (*.csv);;JSON 文件 (*.json)",
        )
        if not path:
            return
        suffix = Path(path).suffix.lower()
        if not suffix:
            suffix = ".csv"
            path = f"{path}{suffix}"

        try:
            if suffix == ".json" or "json" in (chosen_filter or "").lower():
                data = JSONExporter().export(self.results)
            else:
                data = CSVExporter().export(self.results)
            Path(path).write_bytes(data)
            QMessageBox.information(self, "提示", f"导出成功：{path}")
        except Exception as exc:
            logger.exception(exc)
            QMessageBox.warning(self, "错误", f"导出失败：{exc}")

    # ------------------------------------------------------------------ helpers
    def _populate_table(self, data: List[Any]) -> None:
        tv = getattr(self.ui, "tv_result", None)
        if tv is None:
            return
        headers = [col.header for col in self.table_columns]
        model = QStandardItemModel(0, len(headers), tv)
        model.setHorizontalHeaderLabels(headers)
        for row_idx, item in enumerate(data):
            model.insertRow(row_idx)
            for col_idx, col in enumerate(self.table_columns):
                value = col.extractor(item)
                model.setItem(row_idx, col_idx, QStandardItem(_to_display(value)))

        tv.setModel(model)
        header = tv.horizontalHeader()
        resize_mode = (
            QHeaderView.ResizeMode.ResizeToContents if self.category == "runway"
            else QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(resize_mode)
        if self.category != "runway":
            header.setStretchLastSection(True)
        tv.verticalHeader().setVisible(False)
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

    def _set_status(self, text: str) -> None:
        label = getattr(self.ui, "lb_noti", None)
        if label:
            label.setText(text)

    def _to_entity(self, orm_obj: Any) -> Any:
        field_names = [f.name for f in fields(self.entity_cls)]
        payload = {name: getattr(orm_obj, name, None) for name in field_names}
        return self.entity_cls(**payload)

    # ---- hooks for subclasses ---------------------------------------------------
    def _collect_conditions(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _query_by_conditions(self, condition: Dict[str, Any]) -> List[Any]:
        raise NotImplementedError

    # Utilities for subclasses
    @staticmethod
    def _apply_range_filter(filters: List[Any], column, start: Optional[Decimal], end: Optional[Decimal]) -> None:
        if start is not None and end is not None:
            filters.append(column.between(start, end))
        elif start is not None:
            filters.append(column >= start)
        elif end is not None:
            filters.append(column <= end)

    @staticmethod
    def _keyword_match(entity: Any, keyword: str, attrs: Iterable[str]) -> bool:
        text = " ".join(
            _to_display(getattr(entity, attr, "")) for attr in attrs if getattr(entity, attr, None) is not None
        ).lower()
        return keyword.lower() in text

    def _widget_text(self, *names: str) -> str:
        for name in names:
            widget = getattr(self.ui, name, None)
            if widget is not None and hasattr(widget, "text"):
                return widget.text().strip()
        return ""

    def _widget_decimal(self, *names: str) -> Optional[Decimal]:
        for name in names:
            widget = getattr(self.ui, name, None)
            if widget is not None and hasattr(widget, "text"):
                return _to_decimal(widget.text())
        return None

    def _checkbox_checked(self, *names: str) -> bool:
        for name in names:
            widget = getattr(self.ui, name, None)
            if widget is not None and hasattr(widget, "isChecked"):
                return widget.isChecked()
        return False


# =============================================================================
# Runway search
# =============================================================================


def _runway_total_thickness(runway: AirportRunway) -> Optional[float]:
    parts = [
        runway.pccsc_thick,
        runway.ctbc_thick,
        runway.gcss_thick,
        runway.cs_thick,
    ]
    values = [float(p) for p in parts if p is not None]
    if not values:
        return None
    return sum(values)


RUNWAY_COLUMNS: Sequence[ColumnDef] = (
    ColumnDef("目标名称", lambda r: r.runway_name),
    ColumnDef("目标编号", lambda r: r.runway_code),
    ColumnDef("国家/地区", lambda r: r.country or ""),
    ColumnDef("机场/基地", lambda r: r.base or ""),
    ColumnDef("跑道长度(m)", lambda r: r.r_length),
    ColumnDef("跑道宽度(m)", lambda r: r.r_width),
    ColumnDef("结构总厚度(cm)", _runway_total_thickness),
    ColumnDef("面层材料", lambda r: r.pccsc_cement or ""),
    ColumnDef("水泥稳定基层", lambda r: r.ctbc_cement or ""),
    ColumnDef("级配砂砾垫层", lambda r: _to_display(r.gcss_strength)),
)


class RunwayTargetSearchDialog(_BaseTargetSearchDialog):
    category = "runway"
    ui_class = RunwayUI.Ui_Frm_Q_Ammunition
    entity_cls = AirportRunway
    orm_cls = AirportRunwayORM
    semantic_model_path = "./models/runway_index"
    table_columns = RUNWAY_COLUMNS
    line_edit_names = (
        "RunwayName01",
        "Base02",
        "Country01",
        "RLength01",
        "RLength03",
        "RWidth01",
        "RWidth03",
        "txt_maxspeed_a",
        "txt_maxspeed_b",
        "PCCSC01",
        "CTBC01",
        "GCSS01",
        "CS01",
        "txt_country_2",
        "txt_country",
        "txt_am_no",
        "txt_len_a",
        "txt_len_b",
        "txt_d_a",
        "txt_d_b",
        "txt_hs_level",
        "txt_hs_scene",
        "txt_hs_scene_2",
        "txt_hs_scene_3",
    )
    check_box_names = (
        "RunwayName",
        "Base",
        "Country",
        "RLength",
        "RWidth",
        "checkBox",
        "PCCSC",
        "CTBC",
        "GCSS",
        "CS",
        "checkBox_2",
        "checkBox_3",
        "checkBox_4",
        "checkBox_5",
        "checkBox_6",
        "checkBox_7",
        "checkBox_8",
        "checkBox_9",
        "checkBox_10",
    )

    def _collect_conditions(self) -> Dict[str, Any]:
        return {
            "name_enabled": self._checkbox_checked("RunwayName", "checkBox"),
            "name": self._widget_text("RunwayName01", "txt_country_2"),
            "code_enabled": self._checkbox_checked("checkBox_2"),
            "code": self._widget_text("txt_country"),
            "base_enabled": self._checkbox_checked("Base"),
            "base": self._widget_text("Base02"),
            "country_enabled": self._checkbox_checked("Country", "checkBox_3"),
            "country": self._widget_text("Country01", "txt_am_no"),
            "length_enabled": self._checkbox_checked("RLength", "checkBox_4"),
            "length_min": self._widget_decimal("RLength01", "txt_len_a"),
            "length_max": self._widget_decimal("RLength03", "txt_len_b"),
            "width_enabled": self._checkbox_checked("RWidth", "checkBox_5"),
            "width_min": self._widget_decimal("RWidth01", "txt_d_a"),
            "width_max": self._widget_decimal("RWidth03", "txt_d_b"),
            "thickness_enabled": self._checkbox_checked("checkBox", "checkBox_6"),
            "thickness_min": self._widget_decimal("txt_maxspeed_a"),
            "thickness_max": self._widget_decimal("txt_maxspeed_b"),
            "pccsc_enabled": self._checkbox_checked("PCCSC", "checkBox_7"),
            "pccsc_keyword": self._widget_text("PCCSC01", "txt_hs_level"),
            "ctbc_enabled": self._checkbox_checked("CTBC", "checkBox_8"),
            "ctbc_keyword": self._widget_text("CTBC01", "txt_hs_scene"),
            "gcss_enabled": self._checkbox_checked("GCSS", "checkBox_9"),
            "gcss_keyword": self._widget_text("GCSS01", "txt_hs_scene_2"),
            "cs_enabled": self._checkbox_checked("CS", "checkBox_10"),
            "cs_keyword": self._widget_text("CS01", "txt_hs_scene_3"),
        }

    def _checkbox_dependencies(self) -> Dict[str, Sequence[str]]:
        deps: Dict[str, Sequence[str]] = {
            "RunwayName": ("RunwayName01",),
            "Base": ("Base02",),
            "Country": ("Country01",),
            "RLength": ("RLength01", "RLength03"),
            "RWidth": ("RWidth01", "RWidth03"),
            "checkBox": ("txt_maxspeed_a", "txt_maxspeed_b"),
            "PCCSC": ("PCCSC01",),
            "CTBC": ("CTBC01",),
            "GCSS": ("GCSS01",),
            "CS": ("CS01",),
            "checkBox_2": ("txt_country",),
            "checkBox_3": ("txt_am_no",),
            "checkBox_4": ("txt_len_a", "txt_len_b"),
            "checkBox_5": ("txt_d_a", "txt_d_b"),
            "checkBox_6": ("txt_maxspeed_a", "txt_maxspeed_b"),
            "checkBox_7": ("txt_hs_level",),
            "checkBox_8": ("txt_hs_scene",),
            "checkBox_9": ("txt_hs_scene_2",),
            "checkBox_10": ("txt_hs_scene_3",),
        }
        return deps

    def _query_by_conditions(self, cond: Dict[str, Any]) -> List[AirportRunway]:
        filters: List[Any] = []
        if cond.get("name_enabled") and cond.get("name"):
            filters.append(self.orm_cls.runway_name.like(f"%{cond['name']}%"))
        if cond.get("code_enabled") and cond.get("code"):
            filters.append(self.orm_cls.runway_code.like(f"%{cond['code']}%"))
        if cond.get("base_enabled") and cond.get("base"):
            filters.append(self.orm_cls.base.like(f"%{cond['base']}%"))
        if cond.get("country_enabled") and cond.get("country"):
            filters.append(self.orm_cls.country.like(f"%{cond['country']}%"))
        if cond.get("length_enabled"):
            self._apply_range_filter(filters, self.orm_cls.r_length, cond.get("length_min"), cond.get("length_max"))
        if cond.get("width_enabled"):
            self._apply_range_filter(filters, self.orm_cls.r_width, cond.get("width_min"), cond.get("width_max"))
        if cond.get("thickness_enabled"):
            total = (
                func.coalesce(self.orm_cls.pccsc_thick, 0)
                + func.coalesce(self.orm_cls.ctbc_thick, 0)
                + func.coalesce(self.orm_cls.gcss_thick, 0)
                + func.coalesce(self.orm_cls.cs_thick, 0)
            )
            self._apply_range_filter(filters, total, cond.get("thickness_min"), cond.get("thickness_max"))

        stmt = select(self.orm_cls)
        if filters:
            stmt = stmt.where(*filters)
        with target_session() as session:
            rows = session.execute(stmt).scalars().all()
        entities = [self._to_entity(row) for row in rows]

        def apply_keyword(flag_key: str, keyword_key: str, attrs: Sequence[str]) -> None:
            keyword = cond.get(keyword_key, "")
            if cond.get(flag_key) and keyword:
                entities[:] = [e for e in entities if self._keyword_match(e, keyword, attrs)]

        apply_keyword(
            "pccsc_enabled",
            "pccsc_keyword",
            ("pccsc_cement", "pccsc_strength", "pccsc_flexural", "pccsc_freeze", "pccsc_block_size1", "pccsc_block_size2"),
        )
        apply_keyword("ctbc_enabled", "ctbc_keyword", ("ctbc_cement", "ctbc_strength", "ctbc_flexural", "ctbc_compaction"))
        apply_keyword("gcss_enabled", "gcss_keyword", ("gcss_strength", "gcss_compaction"))
        apply_keyword("cs_enabled", "cs_keyword", ("cs_strength", "cs_compaction"))
        return entities


# =============================================================================
# Shelter search
# =============================================================================


SHELTER_COLUMNS: Sequence[ColumnDef] = (
    ColumnDef("目标名称", lambda s: s.shelter_name),
    ColumnDef("目标编号", lambda s: s.shelter_code),
    ColumnDef("国家/地区", lambda s: s.country or ""),
    ColumnDef("所属基地", lambda s: s.base or ""),
    ColumnDef("库容净高(m)", lambda s: s.shelter_height),
    ColumnDef("库容净宽(m)", lambda s: s.shelter_width),
    ColumnDef("库容净长(m)", lambda s: s.shelter_length),
    ColumnDef("结构形式", lambda s: s.structural_form or ""),
)


class ShelterTargetSearchDialog(_BaseTargetSearchDialog):
    category = "shelter"
    ui_class = ShelterUI.Ui_Frm_Q_Ammunition
    entity_cls = AircraftShelter
    orm_cls = AircraftShelterORM
    semantic_model_path = "./models/shelter_index"
    table_columns = SHELTER_COLUMNS
    line_edit_names = (
        "ShelterName01",
        "Base01",
        "Country01",
        "ShelterHeight01",
        "ShelterWidth01",
        "ShelterLength01",
        "txt_country_2",
        "txt_country",
        "txt_am_no",
        "txt_len_a",
        "txt_d_b",
        "txt_maxspeed_a",
    )
    check_box_names = (
        "ShelterName",
        "Base",
        "Country",
        "ShelterHeight",
        "ShelterWidth",
        "ShelterLength",
        "checkBox",
        "checkBox_2",
        "checkBox_3",
        "checkBox_4",
        "checkBox_5",
        "checkBox_6",
    )

    def _collect_conditions(self) -> Dict[str, Any]:
        return {
            "name_enabled": self._checkbox_checked("ShelterName", "checkBox"),
            "name": self._widget_text("ShelterName01", "txt_country_2"),
            "code_enabled": self._checkbox_checked("checkBox_2"),
            "code": self._widget_text("txt_country"),
            "base_enabled": self._checkbox_checked("Base"),
            "base": self._widget_text("Base01"),
            "country_enabled": self._checkbox_checked("Country", "checkBox_3"),
            "country": self._widget_text("Country01", "txt_am_no"),
            "height_enabled": self._checkbox_checked("ShelterHeight", "checkBox_4"),
            "height_min": self._widget_decimal("ShelterHeight01", "txt_len_a"),
            "width_enabled": self._checkbox_checked("ShelterWidth", "checkBox_5"),
            "width_min": self._widget_decimal("ShelterWidth01", "txt_d_b"),
            "length_enabled": self._checkbox_checked("ShelterLength", "checkBox_6"),
            "length_min": self._widget_decimal("ShelterLength01", "txt_maxspeed_a"),
        }

    def _checkbox_dependencies(self) -> Dict[str, Sequence[str]]:
        deps: Dict[str, Sequence[str]] = {
            "ShelterName": ("ShelterName01",),
            "Base": ("Base01",),
            "Country": ("Country01",),
            "ShelterHeight": ("ShelterHeight01",),
            "ShelterWidth": ("ShelterWidth01",),
            "ShelterLength": ("ShelterLength01",),
            "checkBox": ("txt_country_2",),
            "checkBox_2": ("txt_country",),
            "checkBox_3": ("txt_am_no",),
            "checkBox_4": ("txt_len_a",),
            "checkBox_5": ("txt_d_b",),
            "checkBox_6": ("txt_maxspeed_a",),
        }
        return deps

    def _query_by_conditions(self, cond: Dict[str, Any]) -> List[AircraftShelter]:
        filters: List[Any] = []
        if cond.get("name_enabled") and cond.get("name"):
            filters.append(self.orm_cls.shelter_name.like(f"%{cond['name']}%"))
        if cond.get("code_enabled") and cond.get("code"):
            filters.append(self.orm_cls.shelter_code.like(f"%{cond['code']}%"))
        if cond.get("base_enabled") and cond.get("base"):
            filters.append(self.orm_cls.base.like(f"%{cond['base']}%"))
        if cond.get("country_enabled") and cond.get("country"):
            filters.append(self.orm_cls.country.like(f"%{cond['country']}%"))
        if cond.get("height_enabled") and cond.get("height_min") is not None:
            filters.append(self.orm_cls.shelter_height >= cond["height_min"])
        if cond.get("width_enabled") and cond.get("width_min") is not None:
            filters.append(self.orm_cls.shelter_width >= cond["width_min"])
        if cond.get("length_enabled") and cond.get("length_min") is not None:
            filters.append(self.orm_cls.shelter_length >= cond["length_min"])

        stmt = select(self.orm_cls)
        if filters:
            stmt = stmt.where(*filters)
        with target_session() as session:
            rows = session.execute(stmt).scalars().all()
        return [self._to_entity(row) for row in rows]


# =============================================================================
# UCC search
# =============================================================================


UCC_COLUMNS: Sequence[ColumnDef] = (
    ColumnDef("目标名称", lambda x: x.ucc_name),
    ColumnDef("目标代码", lambda x: x.ucc_code),
    ColumnDef("国家/地区", lambda x: x.country or ""),
    ColumnDef("所在基地", lambda x: x.base or ""),
    ColumnDef("位置", lambda x: x.location or ""),
    ColumnDef("土壤岩层材料", lambda x: x.rock_layer_materials or ""),
    ColumnDef("防护层材料", lambda x: x.protective_layer_material or ""),
    ColumnDef("衬砌层材料", lambda x: x.lining_layer_material or ""),
)


class UCCTargetSearchDialog(_BaseTargetSearchDialog):
    category = "ucc"
    ui_class = UCCUI.Ui_Frm_Q_Ammunition
    entity_cls = UndergroundCommandPost
    orm_cls = UndergroundCommandPostORM
    semantic_model_path = "./models/ucc_index"
    table_columns = UCC_COLUMNS
    line_edit_names = (
        "UCCName_2",
        "Base02",
        "Country01",
        "RockLayerMaterials01",
        "ProtectiveLayerMaterial01",
        "LiningLayerMaterial01",
        "txt_country_2",
        "txt_country",
        "txt_am_no",
        "txt_len_a",
        "txt_d_b",
        "txt_maxspeed_a",
    )
    check_box_names = (
        "UCCName",
        "Base",
        "Country",
        "RockLayerMaterials",
        "ProtectiveLayerMaterial",
        "LiningLayerMaterial",
        "checkBox",
        "checkBox_2",
        "checkBox_3",
        "checkBox_4",
        "checkBox_5",
        "checkBox_6",
    )

    def _collect_conditions(self) -> Dict[str, Any]:
        return {
            "name_enabled": self._checkbox_checked("UCCName", "checkBox"),
            "name": self._widget_text("UCCName_2", "txt_country_2"),
            "code_enabled": self._checkbox_checked("checkBox_2"),
            "code": self._widget_text("txt_country"),
            "base_enabled": self._checkbox_checked("Base"),
            "base": self._widget_text("Base02"),
            "country_enabled": self._checkbox_checked("Country", "checkBox_3"),
            "country": self._widget_text("Country01", "txt_am_no"),
            "rock_enabled": self._checkbox_checked("RockLayerMaterials", "checkBox_4"),
            "rock_keyword": self._widget_text("RockLayerMaterials01", "txt_len_a"),
            "protective_enabled": self._checkbox_checked("ProtectiveLayerMaterial", "checkBox_5"),
            "protective_keyword": self._widget_text("ProtectiveLayerMaterial01", "txt_d_b"),
            "lining_enabled": self._checkbox_checked("LiningLayerMaterial", "checkBox_6"),
            "lining_keyword": self._widget_text("LiningLayerMaterial01", "txt_maxspeed_a"),
        }

    def _checkbox_dependencies(self) -> Dict[str, Sequence[str]]:
        deps: Dict[str, Sequence[str]] = {
            "UCCName": ("UCCName_2",),
            "Base": ("Base02",),
            "Country": ("Country01",),
            "RockLayerMaterials": ("RockLayerMaterials01",),
            "ProtectiveLayerMaterial": ("ProtectiveLayerMaterial01",),
            "LiningLayerMaterial": ("LiningLayerMaterial01",),
            "checkBox": ("txt_country_2",),
            "checkBox_2": ("txt_country",),
            "checkBox_3": ("txt_am_no",),
            "checkBox_4": ("txt_len_a",),
            "checkBox_5": ("txt_d_b",),
            "checkBox_6": ("txt_maxspeed_a",),
        }
        return deps

    def _query_by_conditions(self, cond: Dict[str, Any]) -> List[UndergroundCommandPost]:
        filters: List[Any] = []
        if cond.get("name_enabled") and cond.get("name"):
            filters.append(self.orm_cls.ucc_name.like(f"%{cond['name']}%"))
        if cond.get("code_enabled") and cond.get("code"):
            filters.append(self.orm_cls.ucc_code.like(f"%{cond['code']}%"))
        if cond.get("base_enabled") and cond.get("base"):
            filters.append(self.orm_cls.base.like(f"%{cond['base']}%"))
        if cond.get("country_enabled") and cond.get("country"):
            filters.append(self.orm_cls.country.like(f"%{cond['country']}%"))

        stmt = select(self.orm_cls)
        if filters:
            stmt = stmt.where(*filters)
        with target_session() as session:
            rows = session.execute(stmt).scalars().all()
        entities = [self._to_entity(row) for row in rows]

        def apply(keyword_flag: str, keyword_key: str, attr: str) -> None:
            text = cond.get(keyword_key, "")
            if cond.get(keyword_flag) and text:
                entities[:] = [e for e in entities if text.lower() in (_to_display(getattr(e, attr, "")).lower())]

        apply("rock_enabled", "rock_keyword", "rock_layer_materials")
        apply("protective_enabled", "protective_keyword", "protective_layer_material")
        apply("lining_enabled", "lining_keyword", "lining_layer_material")
        return entities


TARGET_DIALOGS: Dict[str, Type[_BaseTargetSearchDialog]] = {
    "runway": RunwayTargetSearchDialog,
    "shelter": ShelterTargetSearchDialog,
    "ucc": UCCTargetSearchDialog,
}

__all__ = [
    "RunwayTargetSearchDialog",
    "ShelterTargetSearchDialog",
    "UCCTargetSearchDialog",
]
