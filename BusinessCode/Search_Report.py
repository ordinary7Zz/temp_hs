"""评估报告智能检索窗口"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHeaderView,
    QMessageBox,
    QDialog,
)

from BusinessCode.ReportDetailDialog import ReportDetailDialog
from BusinessCode.ReportExporter import export_report_to_file
from DBCode.DBHelper import DBHelper
from UIs.Frm_Search_Report import Ui_Frm_Search_Report

TARGET_TYPE_LABELS = {
    1: "机场跑道",
    2: "单机掩蔽库",
    3: "地下指挥所",
}


@dataclass
class ReportRow:
    report_id: int
    report_code: str
    report_name: str
    ammunition_model: str | None
    ammunition_type: str | None
    target_type: str
    target_name: str | None
    damage_degree: str | None
    comment: str | None
    created_time: str | None
    reviewer: str | None


class AssessmentReportSearchDialog(QDialog):
    """毁伤评估报告的组合检索窗口。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_Frm_Search_Report()
        self.ui.setupUi(self)

        self.setWindowTitle("评估报告智能检索")
        self._results: List[ReportRow] = []

        self._checkbox_map: Dict[str, Sequence[str]] = {
            "ReportCode": ("ReportNumber_2",),
            "ReportName": ("ReportName_2",),
            "AMModel": ("AMModel_2",),
            "AMType": ("AMType_2",),
            "TargetName": ("TargetName_2",),
            "Targets": ("Targets_2",),
            "DamageScene": ("DamageScene_2",),
            "DamageDegree": ("DamageDegree_2",),
            "Comment": ("Comment_2",),
        }

        self._setup_dropdowns()
        self._setup_checkbox_dependencies()
        self._setup_table()
        self._connect_slots()

        # NLP 检索暂未实现，直接隐藏
        self.ui.groupBox_2.hide()

    # ------------------------------------------------------------------ setup
    def _setup_dropdowns(self) -> None:
        self._init_combo(self.ui.Targets_2, ["", *TARGET_TYPE_LABELS.values()])

        damage_degrees = self._fetch_distinct(
            "SELECT DISTINCT DamageDegree FROM Assessment_Report WHERE DamageDegree IS NOT NULL AND DamageDegree <> ''"
        )
        self._init_combo(self.ui.DamageDegree_2, ["", *damage_degrees])

        am_types = self._fetch_distinct(
            "SELECT DISTINCT AMType FROM Ammunition_Info WHERE AMType IS NOT NULL AND AMType <> ''"
        )
        self._init_combo(self.ui.AMType_2, ["", *am_types])

    def _init_combo(self, widget: QComboBox, items: Sequence[str]) -> None:
        widget.clear()
        widget.addItems(items)
        widget.setEditable(True)
        widget.setCurrentIndex(0)

    def _setup_checkbox_dependencies(self) -> None:
        for chk_name, widget_names in self._checkbox_map.items():
            checkbox = getattr(self.ui, chk_name, None)
            if checkbox is None:
                continue

            def handler(checked: bool, names=tuple(widget_names)) -> None:
                self._set_widgets_enabled(names, checked)

            checkbox.toggled.connect(handler)
            handler(checkbox.isChecked())

    def _set_widgets_enabled(self, widget_names: Sequence[str], enabled: bool) -> None:
        for name in widget_names:
            widget = getattr(self.ui, name, None)
            if widget is None:
                continue
            widget.setEnabled(enabled)
            if not enabled:
                if hasattr(widget, "clear"):
                    widget.clear()
                elif hasattr(widget, "setCurrentIndex"):
                    widget.setCurrentIndex(0)

    def _setup_table(self) -> None:
        headers = [
            "报告编号",
            "报告名称",
            "弹药型号",
            "弹药类型",
            "目标类型",
            "目标名称",
            "毁伤等级",
            "评估结论",
            "创建时间",
            "审核人",
        ]
        tv = self.ui.tv_result
        model = QStandardItemModel(0, len(headers), tv)
        model.setHorizontalHeaderLabels(headers)
        tv.setModel(model)
        header = tv.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        tv.verticalHeader().setVisible(False)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)

    def _connect_slots(self) -> None:
        self.ui.btn_combination.clicked.connect(self.combination_search)
        self.ui.btn_condition_reset.clicked.connect(self.reset)
        self.ui.btn_export.clicked.connect(self._export_selected)
        self.ui.tv_result.doubleClicked.connect(lambda _: self._view_selected())

    # ------------------------------------------------------------------ events
    def combination_search(self) -> None:
        condition = self._collect_conditions()
        if not condition:
            QMessageBox.information(self, "提示", "请先勾选并填写至少一个检索条件")
            return
        try:
            rows = self._query_reports(condition)
        except Exception as exc:
            logger.exception(exc)
            QMessageBox.warning(self, "错误", f"查询失败：{exc}")
            return
        self._populate_table(rows)
        self.ui.lb_noti.setText(f"共找到 {len(rows)} 条记录")

    def reset(self) -> None:
        for chk_name, widgets in self._checkbox_map.items():
            checkbox = getattr(self.ui, chk_name, None)
            if checkbox:
                checkbox.setChecked(False)
                self._set_widgets_enabled(widgets, False)
        self._results.clear()
        self._setup_table()
        self.ui.lb_noti.clear()

    def _view_selected(self) -> None:
        row = self._current_row()
        if row is None:
            return
        from damage_models.sql_repository_dbhelper import AssessmentReportRepository

        db = DBHelper()
        try:
            repo = AssessmentReportRepository(db)
            report = repo.get_by_id(row.report_id)
            if not report:
                QMessageBox.warning(self, "提示", "未找到该报告。")
                return
            dlg = ReportDetailDialog(report, self)
            dlg.exec()
        finally:
            db.close()

    def _export_selected(self) -> None:
        row = self._current_row()
        if row is None:
            QMessageBox.information(self, "提示", "请先选中一条记录")
            return
        file_path, chosen = QFileDialog.getSaveFileName(
            self,
            "导出评估报告",
            f"report_{row.report_code}.pdf",
            "PDF 文件 (*.pdf);;Word 文件 (*.docx)",
        )
        if not file_path:
            return
        suffix = Path(file_path).suffix.lower() if Path(file_path).suffix else None
        if not suffix:
            suffix = ".docx" if chosen and "word" in chosen.lower() else ".pdf"
            file_path = f"{file_path}{suffix}"
        fmt = "word" if suffix in (".docx", ".doc") else "pdf"
        ok, msg = export_report_to_file(row.report_id, file_path, fmt)
        if ok:
            QMessageBox.information(self, "提示", f"导出成功：{file_path}")
        else:
            QMessageBox.warning(self, "错误", msg)

    # ------------------------------------------------------------------ helpers
    def _current_row(self) -> ReportRow | None:
        index = self.ui.tv_result.currentIndex()
        if not index.isValid():
            return None
        row = index.row()
        if 0 <= row < len(self._results):
            return self._results[row]
        return None

    def _collect_conditions(self) -> Dict[str, str | int]:
        cond: Dict[str, str | int] = {}
        if self.ui.ReportCode.isChecked():
            value = self.ui.ReportNumber_2.text().strip()
            if value:
                cond["report_code"] = value
        if self.ui.ReportName.isChecked():
            value = self.ui.ReportName_2.text().strip()
            if value:
                cond["report_name"] = value
        if self.ui.AMModel.isChecked():
            value = self.ui.AMModel_2.text().strip()
            if value:
                cond["am_model"] = value
        if self.ui.AMType.isChecked():
            value = self.ui.AMType_2.currentText().strip()
            if value:
                cond["am_type"] = value
        if self.ui.Targets.isChecked():
            text = self.ui.Targets_2.currentText().strip()
            for key, label in TARGET_TYPE_LABELS.items():
                if label == text:
                    cond["target_type"] = key
                    break
        if self.ui.TargetName.isChecked():
            value = self.ui.TargetName_2.text().strip()
            if value:
                cond["target_name"] = value
        if self.ui.DamageScene.isChecked():
            value = self.ui.DamageScene_2.text().strip()
            if value:
                cond["scene_name"] = value
        if self.ui.DamageDegree.isChecked():
            value = self.ui.DamageDegree_2.currentText().strip()
            if value:
                cond["damage_degree"] = value
        if self.ui.Comment.isChecked():
            value = self.ui.Comment_2.text().strip()
            if value:
                cond["comment"] = value
        return cond

    def _query_reports(self, cond: Dict[str, str | int]) -> List[ReportRow]:
        sql = [
            "SELECT ar.ReportID, ar.ReportCode, ar.ReportName, ar.DamageDegree, ar.Comment,",
            "       ar.CreatedTime, ar.Reviewer,",
            "       ai.AMModel, ai.AMType,",
            "       ds.DSName AS SceneName,",
            "       CASE ar.TargetType WHEN 1 THEN '机场跑道' WHEN 2 THEN '单机掩蔽库' WHEN 3 THEN '地下指挥所' ELSE '未知' END AS TargetTypeName,",
            "       COALESCE(r.RunwayName, sh.ShelterName, u.UCCName) AS TargetName",
            "FROM Assessment_Report ar",
            "LEFT JOIN Ammunition_Info ai ON ai.AMID = ar.AMID",
            "LEFT JOIN DamageScene_Info ds ON ds.DSID = ar.DSID",
            "LEFT JOIN Runway_Info r ON ar.TargetType = 1 AND ar.TargetID = r.RunwayID",
            "LEFT JOIN Shelter_Info sh ON ar.TargetType = 2 AND ar.TargetID = sh.ShelterID",
            "LEFT JOIN UCC_Info u ON ar.TargetType = 3 AND ar.TargetID = u.UCCID",
        ]
        where: List[str] = []
        params: List[str | int] = []
        like = lambda val: f"%{val}%"

        if value := cond.get("report_code"):
            where.append("ar.ReportCode LIKE %s")
            params.append(like(value))
        if value := cond.get("report_name"):
            where.append("ar.ReportName LIKE %s")
            params.append(like(value))
        if value := cond.get("am_model"):
            where.append("ai.AMModel LIKE %s")
            params.append(like(value))
        if value := cond.get("am_type"):
            where.append("ai.AMType LIKE %s")
            params.append(like(value))
        if value := cond.get("target_type"):
            where.append("ar.TargetType = %s")
            params.append(value)
        if value := cond.get("target_name"):
            where.append("COALESCE(r.RunwayName, sh.ShelterName, u.UCCName) LIKE %s")
            params.append(like(value))
        if value := cond.get("scene_name"):
            where.append("ds.DSName LIKE %s")
            params.append(like(value))
        if value := cond.get("damage_degree"):
            where.append("ar.DamageDegree LIKE %s")
            params.append(like(value))
        if value := cond.get("comment"):
            where.append("ar.Comment LIKE %s")
            params.append(like(value))

        if where:
            sql.append("WHERE " + " AND ".join(where))
        sql.append("ORDER BY ar.ReportID DESC")

        db = DBHelper()
        try:
            rows = db.execute_query("\n".join(sql), params)
        finally:
            db.close()

        results: List[ReportRow] = []
        for row in rows or []:
            created = row.get("CreatedTime")
            created_str = created.strftime("%Y-%m-%d %H:%M") if created else ""
            results.append(
                ReportRow(
                    report_id=row.get("ReportID"),
                    report_code=row.get("ReportCode", ""),
                    report_name=row.get("ReportName", ""),
                    ammunition_model=row.get("AMModel"),
                    ammunition_type=row.get("AMType"),
                    target_type=row.get("TargetTypeName", "未知"),
                    target_name=row.get("TargetName"),
                    damage_degree=row.get("DamageDegree"),
                    comment=row.get("Comment"),
                    created_time=created_str,
                    reviewer=row.get("Reviewer"),
                )
            )
        return results

    def _populate_table(self, rows: List[ReportRow]) -> None:
        self._results = rows
        headers = [
            "报告编号",
            "报告名称",
            "弹药型号",
            "弹药类型",
            "目标类型",
            "目标名称",
            "毁伤等级",
            "评估结论",
            "创建时间",
            "审核人",
        ]
        tv = self.ui.tv_result
        model = QStandardItemModel(0, len(headers), tv)
        model.setHorizontalHeaderLabels(headers)
        for row_idx, report in enumerate(rows):
            model.insertRow(row_idx)
            values = [
                report.report_code,
                report.report_name,
                report.ammunition_model or "",
                report.ammunition_type or "",
                report.target_type,
                report.target_name or "",
                report.damage_degree or "",
                report.comment or "",
                report.created_time or "",
                report.reviewer or "",
            ]
            for col, value in enumerate(values):
                item = QStandardItem(str(value))
                item.setEditable(False)
                model.setItem(row_idx, col, item)
        tv.setModel(model)
        header = tv.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        tv.resizeRowsToContents()

    def _fetch_distinct(self, sql: str) -> List[str]:
        db = DBHelper()
        try:
            rows = db.execute_query(sql)
        finally:
            db.close()
        values: List[str] = []
        for row in rows or []:
            value = next(iter(row.values()))
            if isinstance(value, str):
                values.append(value)
        return values


if __name__ == "__main__":
    app = QApplication([])
    dlg = AssessmentReportSearchDialog()
    dlg.show()
    app.exec()

