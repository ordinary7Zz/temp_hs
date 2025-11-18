import os
import sys
from copy import copy
from decimal import Decimal, InvalidOperation
from typing import Any, Optional, Dict, List

from PyQt6.QtGui import QStandardItemModel, QStandardItem

from BusinessCode.DM_Ammunition_Add import AmmunitionEditor, AmmunitionEditorMode
from BusinessCode.DM_Ammunition_Export import show_export_dialog
from BusinessCode.am_semantic_search import build_semantic_index_from_db, smart_query, SemanticIndex
from DBCode.DBHelper import DBHelper
from am_models import Ammunition
from am_models.db import session_scope as am_session, session_scope
from am_models.gui_adapter import to_decimal_or_none
from am_models.sql_repository import SQLRepository as am_repository
from PyQt6.QtCore import pyqtSignal, QThread, QModelIndex
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QDialog, QHeaderView
)
from loguru import logger
from sqlalchemy import select

from UIs.Frm_Search_Ammunition import Ui_Frm_Q_Ammunition
from am_models.orm import AmmunitionORM
from damage_models import AssessmentResultRepository, DamageSceneRepository

local_model_dir = r"./models/ammo_index"  # 你的实际路径


class SemanticIndexWorker(QThread):
    message = pyqtSignal(str)
    done = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, session_or_scope, orm_cls, prefer_model, parent=None, rebuild: bool = False):
        super().__init__(parent)
        self.session_or_scope = session_or_scope
        self.orm_cls = orm_cls
        self.prefer_model = prefer_model
        self.rebuild = rebuild

    def run(self):
        try:
            if os.path.exists(local_model_dir + ".tfidf.joblib") and self.rebuild == False:
                logger.debug(f"{local_model_dir}存在")
                try:
                    self.message.emit("正在加载本地离线语义索引 ...")
                    idx = SemanticIndex.load_index(local_model_dir)
                    self.message.emit("已加载本地离线语义索引")
                    self.done.emit(idx)
                except Exception as e:
                    logger.exception(f"加载离线模型{local_model_dir}出错:{e}")
            else:
                if self.rebuild:
                    logger.debug(f"正在重建{local_model_dir}")
                    self.message.emit("正在重新构建语义索引 ...")
                else:
                    logger.debug(f"不存在{local_model_dir}")
                    self.message.emit("正在构建语义索引 ...")
                sem_idx = build_semantic_index_from_db(
                    self.session_or_scope, self.orm_cls,
                    id_attr="am_id", prefer_model=self.prefer_model
                )
                if sem_idx == None:
                    self.message.emit("索引未构建，可能因为数据条目为0")
                else:
                    self.message.emit("索引构建完成")
                    sem_idx.save_index(local_model_dir)
                    self.done.emit(sem_idx)
        except Exception as e:
            logger.exception(e)
            self.error.emit(f"构建语义索引失败：{e!s}")


class AmmunitionSearch(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # ---- 组合式 UI ----
        self.ui = Ui_Frm_Q_Ammunition()
        self.ui.setupUi(self)

        self.setFixedSize(800, 600)
        self._init_comboboxes()

        self.ui.btn_combination.clicked.connect(self.combination_search)
        self.ui.btn_nlp_search.clicked.connect(self.nlp_search)
        self.ui.btn_export.clicked.connect(self.export)
        self.ui.btn_condition_reset.clicked.connect(self.reset)
        self.ui.btn_nlp_rebuild.clicked.connect(self.rebuild_nlp)

        # 绑定双击信号
        self.ui.tv_result.doubleClicked.connect(self._on_row_double_clicked)

        self.am_results: List[Ammunition] = []

        if self.ui.cmb_topk.count() == 0:
            self.ui.cmb_topk.addItems(["前3个", "前5个", "前10个"])
        self.topK_choice = [3, 5, 10]

        self.sem_idx = None
        self._start_build_semantic_index()

    def _on_row_double_clicked(self, index: QModelIndex):
        tv = self.ui.tv_result
        model = tv.model()
        row = index.row()

        # 隐藏列在最后一列
        id_col = model.columnCount() - 1
        am_id_str = model.index(row, id_col).data()
        try:
            am_id = int(am_id_str)
        except Exception:
            return

        # 直接复用你已有的编辑入口
        self._on_view(tv, model, row, am_id)

    def _on_view(self, tv, table, row, am_id: int):
        # 示例：弹窗显示当前行数据；实际可打开编辑对话框
        # logger.info(f"_on_edit model={table}, am_id={am_id}")

        try:
            self.edit_win = AmmunitionEditor(parent=self, mode=AmmunitionEditorMode.AmmunitionEditorMode_RO,
                                             edit_amid=am_id)
            self.edit_win.show()
        except Exception as e:
            logger.exception(e)

    def validate_decimal(self) -> list[str]:
        must_decimal_ed = [
            self.ui.txt_len_a, self.ui.txt_len_b,
            self.ui.txt_d_a, self.ui.txt_d_b,
            self.ui.txt_maxspeed_a, self.ui.txt_maxspeed_b,
        ]
        must_decimal_ed_name = [
            "弹药长度a", "弹药长度b",
            "弹药直径a", "弹药直径b",
            "最大时速a", "最大时速b"
        ]
        need_decimal = []
        for i, led in enumerate(must_decimal_ed):
            led.setStyleSheet("")
            if led.text() == "":
                continue
            if to_decimal_or_none(led.text()) == None:
                need_decimal.append(must_decimal_ed_name[i].replace(":", "").replace("：", ""))
                led.setStyleSheet("background-color: rgb(250, 128, 114);")
        return need_decimal

    def validate_must_filled(self) -> list[str]:
        must_filled = []
        if self.ui.checkBox_2.isChecked() and self.ui.txt_country.text() == "":
            must_filled.append("国家 / 地区")
        if self.ui.checkBox_3.isChecked() and self.ui.txt_am_no.text() == "":
            must_filled.append("弹药编号")
        if self.ui.checkBox_4.isChecked() and (self.ui.txt_len_a.text() == "" or self.ui.txt_len_b.text() == ""):
            must_filled.append("弹药长度")
        if self.ui.checkBox_5.isChecked() and (self.ui.txt_d_a.text() == "" or self.ui.txt_d_b.text() == ""):
            must_filled.append("弹药直径")
        if self.ui.checkBox_6.isChecked() and (
                self.ui.txt_maxspeed_a.text() == "" or self.ui.txt_maxspeed_b.text() == ""):
            must_filled.append("最大时速")
        if self.ui.checkBox_7.isChecked() and self.ui.txt_hs_level.text() == "":
            must_filled.append("毁伤等级")
        if self.ui.checkBox_8.isChecked() and self.ui.txt_hs_scene.text() == "":
            must_filled.append("毁伤场景")
        if self.ui.checkBox_9.isChecked() and self.ui.txt_weight.text() == "":
            must_filled.append("弹药全重")
        return must_filled

    def rebuild_nlp(self):
        self._start_build_semantic_index(rebuild=True)

    def _start_build_semantic_index(self, rebuild: bool = False):
        # 1) 禁用输入框与按钮（可按需扩展更多控件）
        self._set_sem_controls_enabled(False)

        # 2) 创建后台线程
        with am_session() as session:
            self._sem_worker = SemanticIndexWorker(
                session_or_scope=session,
                orm_cls=AmmunitionORM,
                prefer_model="paraphrase-multilingual-MiniLM-L12-v2",
                rebuild=rebuild,
            )
        # 3) 信号连接
        self._sem_worker.message.connect(self._on_sem_message)
        self._sem_worker.done.connect(self._on_sem_done)
        self._sem_worker.error.connect(self._on_sem_error)
        self._sem_worker.finished.connect(self._on_sem_finished)
        # 4) 启动
        self._sem_worker.start()

    # --- 控件启禁 ---
    def _set_sem_controls_enabled(self, enabled: bool):
        try:
            self.ui.txt_nlp.setEnabled(enabled)
            self.ui.btn_nlp_search.setEnabled(enabled)
            self.ui.btn_nlp_rebuild.setEnabled(enabled)
        except Exception:
            pass

    def _on_sem_message(self, msg: str):
        self.ui.lb_noti.setText(msg)
        return

    def _on_sem_done(self, sem_idx_obj):
        self.sem_idx = sem_idx_obj
        self.ui.lb_noti.setText("语义索引已准备就绪")

    def _on_sem_error(self, err: str):
        QMessageBox.critical(self, "错误", err)

    def _on_sem_finished(self):
        self._set_sem_controls_enabled(True)
        self._sem_worker = None

    def _init_comboboxes(self):
        if self.ui.comboBox.count() == 0:
            self.ui.comboBox.addItems(["钻地弹", "空地导弹", "子母弹", "巡航导弹", "布撒器", "其他"])

    def combination_search(self):
        # 判断是否完成必填
        must_filled = self.validate_must_filled()
        if len(must_filled) > 0:
            QMessageBox.warning(self, "必填信息缺失", f"必须填写：{'，'''.join(must_filled)}")
            return

        # 校验数字
        need_decimal = self.validate_decimal()
        if len(need_decimal) > 0:
            QMessageBox.warning(self, "类型错误", f"以下项必须为数字：{'，'''.join(need_decimal)}")
            return

        logger.debug("开始combination_search")
        self.ui.lb_noti.setText("")
        condition_data = {
            "am_type_enabled": self.ui.checkBox.isChecked(),
            "am_type": self.ui.comboBox.currentText(),
            "country_enabled": self.ui.checkBox_2.isChecked(),
            "country": self.ui.txt_country.text(),
            "am_model_enabled": self.ui.checkBox_3.isChecked(),
            "am_model": self.ui.txt_am_no.text(),
            "am_length_enabled": self.ui.checkBox_4.isChecked(),
            "am_length_a": _to_decimal_or_none(self.ui.txt_len_a.text()),
            "am_length_b": _to_decimal_or_none(self.ui.txt_len_b.text()),
            "am_diameter_enabled": self.ui.checkBox_5.isChecked(),
            "am_diameter_a": _to_decimal_or_none(self.ui.txt_d_a.text()),
            "am_diameter_b": _to_decimal_or_none(self.ui.txt_d_b.text()),
            "max_speed_enabled": self.ui.checkBox_6.isChecked(),
            "max_speed_a": _to_decimal_or_none(self.ui.txt_maxspeed_a.text()),
            "max_speed_b": _to_decimal_or_none(self.ui.txt_maxspeed_b.text()),
            "damage_parameter_damage_level_enabled": self.ui.checkBox_7.isChecked(),
            "damage_parameter_damage_level": self.ui.txt_hs_level.text(),
            "damage_parameter_name_enabled": self.ui.checkBox_8.isChecked(),
            "damage_parameter_name": self.ui.txt_hs_scene.text(),
            "am_weight_enabled": self.ui.checkBox_9.isChecked(),
            "am_weight": _to_decimal_or_none(self.ui.txt_weight.text()),
        }

        logger.debug(f"condition_data={condition_data}")

        try:
            res_ams = self._query_ammunition_by_conditions(condition_data)
            for _, res_am in enumerate(res_ams):
                logger.debug(f"查询到={res_am.am_name}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"数据库查询发生错误{e}")
            return

        self.ui.lb_noti.setText(f"检索到{len(res_ams)}条结果")

        try:
            self.am_results = copy(res_ams)
            self.setup_table(res_ams)
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"更新表格发生错误{e}")
            return

    def _query_ammunition_by_conditions(self, condition_data: Dict[str, Any]) -> list[Ammunition]:
        def _has_value(v: Any) -> bool:
            if v is None:
                return False
            if isinstance(v, str):
                return v.strip() != ""
            return True

        am_stmt = select(AmmunitionORM)
        ar_amids = []
        ds_amids = []
        logger.debug(f"am_stmt={am_stmt}")
        filters: List[Any] = []

        # 1) 弹药类型
        if condition_data.get("am_type_enabled", False):
            val = condition_data.get("am_type")
            if _has_value(val):
                filters.append(AmmunitionORM.am_type == val.strip())

        # 2) 国家
        if condition_data.get("country_enabled", False):
            val = condition_data.get("country")
            if _has_value(val):
                filters.append(AmmunitionORM.country.like(f"%{val.strip()}%"))

        # 3) 型号
        if condition_data.get("am_model_enabled", False):
            val = condition_data.get("am_model")
            if _has_value(val):
                filters.append(AmmunitionORM.model_name.like(f"%{val.strip()}%"))

        # 4) 长度区间
        if condition_data.get("am_length_enabled", False):
            a_ = condition_data.get("am_length_a")
            b_ = condition_data.get("am_length_b")
            col = AmmunitionORM.length_m
            if a_ is not None and b_ is not None:
                filters.append(col.between(a_, b_))
            elif a_ is not None:
                filters.append(col >= a_)
            elif b_ is not None:
                filters.append(col <= b_)

        # 5) 直径区间
        if condition_data.get("am_diameter_enabled", False):
            a_ = condition_data.get("am_diameter_a")
            b_ = condition_data.get("am_diameter_b")
            col = AmmunitionORM.diameter_m
            if a_ is not None and b_ is not None:
                filters.append(col.between(a_, b_))
            elif a_ is not None:
                filters.append(col >= a_)
            elif b_ is not None:
                filters.append(col <= b_)

        # 6) 最大速度区间
        if condition_data.get("max_speed_enabled", False):
            a_ = condition_data.get("max_speed_a")
            b_ = condition_data.get("max_speed_b")
            col = AmmunitionORM.max_speed_ma
            if a_ is not None and b_ is not None:
                filters.append(col.between(a_, b_))
            elif a_ is not None:
                filters.append(col >= a_)
            elif b_ is not None:
                filters.append(col <= b_)

        # 7) 重量
        if condition_data.get("am_weight_enabled", False):
            w = condition_data.get("am_weight")
            if w is not None:
                filters.append(AmmunitionORM.weight_kg == w)

        if filters:
            am_stmt = am_stmt.where(*filters)

        with am_session() as session:
            res_orm = session.execute(am_stmt).scalars().all()

        logger.debug(f"检索结果：: {len(res_orm)}")

        # 评估/场景交叉过滤
        if condition_data.get("damage_parameter_damage_level_enabled", False):
            try:
                ar_repo = AssessmentResultRepository(DBHelper())
                ar_am = ar_repo.search(condition_data.get("damage_parameter_damage_level"))
                logger.debug(f"检索毁伤结果表：ar_am={ar_am}")
                for am in ar_am:
                    ar_amids.append(am.AMID)
            except Exception as e:
                logger.exception(f"检索毁伤结果表失败{e}")

        if condition_data.get("damage_parameter_name_enabled", False):
            try:
                ds_repo = DamageSceneRepository(DBHelper())
                ds_am = ds_repo.search(condition_data.get("damage_parameter_damage_level"))
                logger.debug(f"检索毁伤场景表：ds_am={ds_am}")
                for am in ds_am:
                    ds_amids.append(am.AMID)
            except Exception as e:
                logger.exception(f"检索毁伤参数表失败{e}")

        result: List[Ammunition] = [am_repository.to_entity(r, False) for r in res_orm]
        if not result:
            return []

        set_b = set(ar_amids)
        set_c = set(ds_amids)

        if condition_data.get("damage_parameter_damage_level_enabled", False) and condition_data.get(
                "damage_parameter_name_enabled", False):
            return [obj for obj in result if obj.am_id in set_b and obj.am_id in set_c]
        elif condition_data.get("damage_parameter_damage_level_enabled", False):
            return [obj for obj in result if obj.am_id in set_b]
        elif condition_data.get("damage_parameter_name_enabled", False):
            return [obj for obj in result if obj.am_id in set_c]

        return result

    def setup_table(self, data: List[Ammunition]) -> None:
        tv = self.ui.tv_result

        headers = ["弹药类型", "国家/地区", "中文名称", "弹药型号", "弹药全重", "弹药长度", "弹体直径", "最大时速",
                   "战斗部", "爆炸当量", "_id"]
        table = QStandardItemModel(0, len(headers), tv)
        table.setHorizontalHeaderLabels(headers)
        tv.setModel(table)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)  # 不让最后一列自动吞空间
        for i in range(0, len(headers) - 1):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        tv.verticalHeader().setVisible(False)
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

        for row_id, am in enumerate(data):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QStandardItem(am.am_type))
            table.setItem(row_id, 1, QStandardItem(am.country))
            table.setItem(row_id, 2, QStandardItem(am.am_name))
            table.setItem(row_id, 3, QStandardItem(am.model_name))
            table.setItem(row_id, 4, QStandardItem(str(am.weight_kg)))
            table.setItem(row_id, 5, QStandardItem(str(am.length_m)))
            table.setItem(row_id, 6, QStandardItem(str(am.diameter_m)))
            table.setItem(row_id, 7, QStandardItem(str(am.max_speed_ma)))
            table.setItem(row_id, 8, QStandardItem(am.warhead_type))
            table.setItem(row_id, 9, QStandardItem(str(am.explosion_equivalent_TNT_T)))

            # 隐藏的主键列
            table.setItem(row_id, len(headers) - 1, QStandardItem(str(am.am_id)))

        # 隐藏 _id 列
        tv.setColumnHidden(len(headers) - 1, True)

        logger.debug("表格更新完毕")

    def nlp_search(self):
        text = self.ui.txt_nlp.text().strip()
        if not text:
            QMessageBox.information(self, "提示", "请输入检索描述")
            return

        # 可选：自然语言 → 组合检索条件
        def _to_condition(_: str) -> dict:
            return {}

        def _combine_filter(session, condition) -> list:
            return self._query_ammunition_by_conditions(condition)

        top_k = 3
        if self.ui.cmb_topk.currentIndex() < len(self.topK_choice):
            top_k = self.topK_choice[self.ui.cmb_topk.currentIndex()]

        try:
            with am_session() as session:
                rows = smart_query(
                    session=session,
                    idx=self.sem_idx,
                    query=text,
                    combine_filter=_combine_filter,
                    to_condition=_to_condition,
                    topk=top_k
                )
        except Exception as e:
            logger.exception(f"检索失败：{e}")
            QMessageBox.warning(self, "错误", f"查询失败：{e}")
            return

        self.ui.lb_noti.setText("语义检索结果按照相关度排序")
        try:
            self.am_results = copy(rows)
            self.setup_table(rows)
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"更新表格发生错误{e}")
            return

    def reset(self):
        logger.debug("开始reset")
        line_edits = [
            self.ui.txt_country,
            self.ui.txt_am_no,
            self.ui.txt_len_a, self.ui.txt_len_b,
            self.ui.txt_d_a, self.ui.txt_d_b,
            self.ui.txt_maxspeed_a, self.ui.txt_maxspeed_b,
            self.ui.txt_hs_level, self.ui.txt_hs_scene,
            self.ui.txt_weight,
        ]
        check_boxes = [
            self.ui.checkBox,
            self.ui.checkBox_2,
            self.ui.checkBox_3,
            self.ui.checkBox_4,
            self.ui.checkBox_5,
            self.ui.checkBox_6,
            self.ui.checkBox_9,
        ]

        for w in line_edits:
            w.clear()

        for w in check_boxes:
            w.setChecked(False)

    def export(self):
        logger.debug(f"self.am_results: {self.am_results}")
        show_export_dialog(self, items=self.am_results)
        pass


def _to_decimal_or_none(x: Any) -> Optional[Decimal]:
    if x is None:
        return None
    if isinstance(x, Decimal):
        return x
    s = str(x).strip()
    if s == "":
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AmmunitionSearch()
    win.show()
    sys.exit(app.exec())
