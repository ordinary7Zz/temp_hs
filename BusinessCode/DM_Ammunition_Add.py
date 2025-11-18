import json
import logging
import sys
from contextlib import suppress
from enum import Enum
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QMessageBox, QDialog, QLineEdit, QLayout
)
from PyQt6.QtGui import QPixmap
from loguru import logger

from BusinessCode.ImgHelper import ImgHelper
from UIs.Frm_Ammunition_Add import Ui_AmmunitionEditorWindow
from am_models import SQLRepository, Ammunition
from am_models.db import Base, engine, session_scope
from am_models.gui_adapter import ui_json_to_ammunition, ammunition_to_ui_json, to_decimal_or_none


class AmmunitionEditorMode(Enum):
    AmmunitionEditorMode_Edit = 1
    AmmunitionEditorMode_Add = 2
    AmmunitionEditorMode_RO = 3


class AmmunitionEditor(QDialog):
    finished_with_result = pyqtSignal(bool)
    all_line_edits = []

    def __init__(self, parent=None, mode: "AmmunitionEditorMode" = None, edit_amid: int = 0):
        super().__init__(parent)

        # ------------ 组合式 UI ------------
        self.ui = Ui_AmmunitionEditorWindow()
        self.ui.setupUi(self)

        self.all_line_edits = [self.ui.ed_service_year, self.ui.ed_name_cn, self.ui.ed_vendor, self.ui.ed_name_offi,
                               self.ui.ed_short, self.ui.ed_type,
                               self.ui.ed_model, self.ui.ed_submodel, self.ui.ed_weight_full, self.ui.ed_len,
                               self.ui.ed_diameter,
                               self.ui.ed_tex, self.ui.ed_struct, self.ui.ed_power, self.ui.ed_wingspan_o,
                               self.ui.ed_wingspan_c,
                               self.ui.ed_max_speed, self.ui.ed_launch_mass, self.ui.ed_radar_face,
                               self.ui.ed_warhead_name,
                               self.ui.ed_destroy_el,
                               self.ui.ed_fuze, self.ui.ed_destroy_mec, self.ui.ed_charge, self.ui.ed_precision,
                               self.ui.ed_target,
                               self.ui.ed_carrier, self.ui.ed_guidance, self.ui.ed_exp_payload, self.ui.ed_coverage_ar,
                               self.ui.ed_range,
                               self.ui.ed_drop_h, self.ui.ed_drop_speed, self.ui.ed_drop_mode, self.ui.ed_penetration,
                               self.ui.ed_bp_02,
                               self.ui.ed_bp_2, self.ui.ed_bp_4, self.ui.ed_dispersion_2, self.ui.ed_dispersion_9,
                               self.ui.ed_dispersion_5, self.ui.ed_dispersion_6, self.ui.ed_dispersion_7,
                               self.ui.ed_pp_dmjl_2,
                               self.ui.ed_pp_s, self.ui.ed_pp_quality, self.ui.ed_pp_dmjl, self.ui.ed_pp_dmjl_3,
                               self.ui.ed_pp_dmjl_4,
                               self.ui.ed_cj_1, self.ui.ed_cj_2, self.ui.ed_cj_3, self.ui.ed_zm_4,
                               self.ui.ed_zm_18, self.ui.ed_zm_15, self.ui.ed_zm_13, self.ui.ed_zm_14, self.ui.ed_zm_16,
                               self.ui.ed_zm_17]

        self.image_pm = None
        self.image_dir = ""

        self.mode = mode
        self.edit_amid = edit_amid

        self.ui.stackedWidget.setCurrentIndex(0)  # 特有参数分页控件置为第一页
        self.warhead_stack_ref = [0, 1, 2, 3, 0, 1, 2]  # 战斗部选项框和分页控件页码映射

        # 本地草稿文件路径
        self._draft_file = Path.home() / ".am_editor_draft.json"

        if self.mode == AmmunitionEditorMode.AmmunitionEditorMode_Edit:
            self.setWindowTitle("编辑弹药毁伤模型")
            if edit_amid == 0:
                QMessageBox.warning(self, "错误", "现在处于编辑模式，但未传入am_id")
            try:
                self.load_data_from_db(edit_amid)
            except Exception as e:
                logger.exception(e)
                self.close()
                return
        elif self.mode == AmmunitionEditorMode.AmmunitionEditorMode_Add:
            self.setWindowTitle("添加弹药毁伤模型")
            self._maybe_offer_restore_draft()
        else:
            self.setWindowTitle("查看弹药毁伤模型")
            if edit_amid == 0:
                QMessageBox.warning(self, "错误", "现在处于预览模式，但未传入am_id")
            try:
                self.load_data_from_db(edit_amid)
            except Exception as e:
                logger.exception(e)
                self.close()
                return
            self._set_readonly()

        self._init_comboboxes()
        self._wire_signals()
        self.resize(1065, 716)

    # ------- 初始化与信号 -------
    def _init_comboboxes(self):
        if self.ui.cmb_country.count() == 0:
            self.ui.cmb_country.addItems(["中国", "美国", "俄罗斯", "法国", "英国", "德国", "印度", "中国台湾", "其他"])
        if self.ui.cmb_user.count() == 0:
            self.ui.cmb_user.addItems(["空军", "陆军", "海军", "联合"])
        if self.ui.cmb_warhead.count() == 0:
            self.ui.cmb_warhead.addItems(
                ["爆破战斗部", "聚能穿甲战斗部", "破片战斗部", "钻地侵彻战斗部", "子母弹战斗部（爆破子弹）",
                 "子母弹战斗部（聚能穿甲子弹）", "子母弹战斗部（破片子弹）"])
            if self.ui.cmb_warhead.count() != len(self.warhead_stack_ref):
                logger.critical("self.ui.cmb_warhead.count() != len(self.warhead_stack_ref)")

        # 战斗部选项框，根据这个切换特殊参数的stack页面
        self.ui.cmb_warhead.currentIndexChanged.connect(self._switch_zdb_param)

    def _switch_zdb_param(self):
        self.ui.stackedWidget.setCurrentIndex(self.warhead_stack_ref[self.ui.cmb_warhead.currentIndex()])

    def _wire_signals(self):
        self.ui.btn_choose_image.clicked.connect(self.on_choose_image)
        self.ui.btn_clear.clicked.connect(self.on_clear)
        # self.ui.btn_save_temp.clicked.connect(self.on_save_temp)
        self.ui.btn_save_store.clicked.connect(self.on_save_store)

    # ------- 槽函数 -------
    def on_choose_image(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "选择弹药图片", str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not fn:
            return
        pm = QPixmap(fn)
        if pm.isNull():
            QMessageBox.warning(self, "错误", "无法加载图片")
            return
        self.image_pm = pm
        self.image_dir = str(fn)
        self.ui.lbl_image.setPixmap(pm)

    def _set_readonly(self):
        # 所有输入框只读
        for w in self.all_line_edits:
            w.setReadOnly(True)

        # 隐藏按钮
        for i in range(self.ui.bottomHBox.count()):
            item = self.ui.bottomHBox.itemAt(i)
            if item.widget():
                item.widget().hide()
        self.ui.btn_choose_image.hide()

        # 下拉框
        self.ui.cmb_country.setDisabled(True)
        self.ui.cmb_warhead.setDisabled(True)
        self.ui.cmb_user.setDisabled(True)

    def on_clear(self):
        # 简单清空所有 QLineEdit / QTextEdit；复选框复位

        for w in self.all_line_edits:
            w.clear()
            w.setStyleSheet("")

        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.lbl_image.clear()
        self.image_pm = None
        self.image_dir = ""
        self.ui.lbl_image.setText("（预览区）")

    def on_save_temp(self):
        """将当前表单内容保存为本地草稿（JSON）"""
        try:
            data = self.collect_form_data()
            self._draft_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            QMessageBox.information(self, "暂存", f"草稿已保存到：\n{self._draft_file}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "暂存失败", f"写入草稿失败：{e}")

    def validate_length_limits(self) -> list[str]:
        """
        按照 orm.py 中 String(N) 的长度限制，对 UI 文本输入做长度校验。
        返回 提示信息列表。
        """

        # （控件, 最大长度, 提示文案）——文案里把长度写进去，例如“战斗部类型（60）”
        fields = [
            # 基本信息
            (self.ui.cmb_country, 60, "国家/地区（60）"),
            (self.ui.cmb_user, 60, "基地/部队（60）"),
            (self.ui.ed_type, 60, "弹药类型（60）"),
            (self.ui.ed_name_offi, 100, "官方名称（100）"),
            (self.ui.ed_name_cn, 100, "中文名称（100）"),
            (self.ui.ed_short, 60, "简称（60）"),
            (self.ui.ed_model, 60, "弹药型号（60）"),
            (self.ui.ed_submodel, 60, "型号子类（60）"),
            (self.ui.ed_vendor, 60, "制造商（60）"),
            (self.ui.ed_service_year, 60, "服役时间（60）"),

            # 构造与动力（只列 String 字段）
            (self.ui.ed_tex, 60, "弹体材质（60）"),
            (self.ui.ed_struct, 60, "结构（60）"),
            (self.ui.ed_radar_face, 60, "雷达截面（60）"),
            (self.ui.ed_power, 60, "动力装置（60）"),

            # 战斗部与飞控（String / Text 中限定为 String 的）
            (self.ui.cmb_warhead, 60, "战斗部类型（60）"),
            (self.ui.ed_warhead_name, 60, "战斗部名称（60）"),
            (self.ui.ed_destroy_el, 60, "毁伤元（60）"),
            (self.ui.ed_fuze, 60, "引信（60）"),
            (self.ui.ed_destroy_mec, 60, "破坏机制（60）"),
            (self.ui.ed_target, 60, "打击目标（60）"),
            (self.ui.ed_carrier, 60, "载机/投放平台（60）"),
            (self.ui.ed_guidance, 60, "制导方式（60）"),
            (self.ui.ed_penetration, 60, "穿透能力（60）"),
            (self.ui.ed_drop_h, 60, "投弹高度范围（60）"),
            (self.ui.ed_drop_mode, 60, "投弹方式（60）"),
            (self.ui.ed_coverage_ar, 60, "布撒范围（60）"),

            # 特有参数：爆破战斗部 / 聚能战斗部 / 子母弹战斗部里的 String 字段
            (self.ui.ed_bp_02, 60, "炸药成分（60）"),  # exb_component
            (self.ui.ed_dispersion_6, 60, "衬套材料（60）"),  # eb_cover_material
            (self.ui.ed_zm_14, 60, "子弹型号（60）"),  # cbs_bullet_model
        ]

        over_limit: list[str] = []

        for widget, max_len, label in fields:
            # 根据控件类型取文本
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
            else:
                # 其它类型暂不处理
                continue

            if text and len(text) > max_len:
                over_limit.append(label)

        return over_limit

    def validate_must_filled(self) -> list[str]:
        must_filled = []
        if self.ui.ed_name_cn.text() == "":
            must_filled.append("中文名称")
        if self.ui.ed_name_offi.text() == "":
            must_filled.append("官方名称")
        if self.ui.ed_type.text() == "":
            must_filled.append("弹药类型")
        if self.ui.ed_model.text() == "":
            must_filled.append("弹药型号")
        if self.ui.ed_warhead_name.text() == "":
            must_filled.append("战斗部名称")
        if self.ui.ed_weight_full.text() == "":
            must_filled.append("弹药全重")
        if self.ui.ed_launch_mass.text() == "":
            must_filled.append("发射质量")
        return must_filled

    def validate_decimal(self) -> list[str]:
        must_decimal_ed = [
            # 战斗部参数
            self.ui.ed_charge, self.ui.ed_precision, self.ui.ed_exp_payload, self.ui.ed_range, self.ui.ed_drop_speed,
            # 构造与动力参数
            self.ui.ed_weight_full, self.ui.ed_len, self.ui.ed_diameter, self.ui.ed_wingspan_c, self.ui.ed_wingspan_o,
            self.ui.ed_max_speed, self.ui.ed_launch_mass,
            # 爆破战斗部
            self.ui.ed_bp_2, self.ui.ed_bp_4,
            # 聚能战斗部
            self.ui.ed_dispersion_2, self.ui.ed_dispersion_9, self.ui.ed_dispersion_5, self.ui.ed_dispersion_7,
            # 破片战斗部
            self.ui.ed_pp_dmjl_2, self.ui.ed_pp_s, self.ui.ed_pp_dmjl_3, self.ui.ed_pp_dmjl_4, self.ui.ed_pp_dmjl,
            # 穿甲战斗部
            self.ui.ed_cj_1, self.ui.ed_cj_2, self.ui.ed_cj_3,
            # 子母
            self.ui.ed_zm_5, self.ui.ed_zm_4, self.ui.ed_zm_16, self.ui.ed_zm_17
        ]
        must_decimal_ed_name = [
            # 战斗部参数
            self.ui.lbl_charge.text(), self.ui.lbl_precision.text(), self.ui.lbl_exp_payload.text(),
            self.ui.lbl_range.text(), self.ui.lbl_drop_speed.text(),
            # 构造与动力参数
            self.ui.lbl_prop.text(), self.ui.lbl_len.text(), self.ui.lbl_diam.text(), self.ui.lbl_span_c.text(),
            self.ui.lbl_span_o.text(),
            self.ui.lbl_g.text(), self.ui.lbl_body.text(),
            # 爆破战斗部
            self.ui.lbl_bp_3.text(), self.ui.lbl_bp_5.text(),
            # 聚能战斗部
            self.ui.lbl_dispersion_2.text(), self.ui.lbl_dispersion_9.text(), self.ui.lbl_dispersion_5.text(),
            self.ui.lbl_dispersion_7.text(),
            # 破片战斗部
            self.ui.lbl_pp_dmjl_2.text(), self.ui.lbl_pp_2.text(), self.ui.lbl_pp_dmjl_3.text(),
            self.ui.lbl_pp_dmjl_4.text(), self.ui.lbl_pp_dmjl.text(),
            # 穿甲战斗部
            self.ui.lbl_cj_1.text(), self.ui.lbl_cj_2.text(), self.ui.lbl_cj_3.text(),
            # 子母
            self.ui.lbl_zm_5.text(), self.ui.lbl_zm_4.text(), self.ui.lbl_zm_16.text(), self.ui.lbl_zm_17
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

    def on_save_store(self):

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

        # 收集表单信息
        data = self.collect_form_data()

        # 图片
        image_add = None
        logger.debug(f"self.image_pm={self.image_pm},self.image_dir={self.image_dir}")
        if self.image_pm is not None:
            if self.image_dir != "":  # 新添加的图片 or 修改过
                h = ImgHelper.from_pixmap(self.image_pm).resize(long_side=1280)
                h.compress_to_limit(200 * 1024, fmt="JPEG")
                image_add = h.to_bytes(fmt="JPEG", quality=70)
            else:
                # 原来就有图片
                image_add = ImgHelper.from_pixmap(self.image_pm).to_bytes()

        am = ui_json_to_ammunition(data, image_add)
        am.am_id = self.edit_amid
        with session_scope() as db_session:
            repo = SQLRepository(db_session)
            repo.add_update_method(am)
            try:
                if self.mode == AmmunitionEditorMode.AmmunitionEditorMode_Add:
                    am = repo.add(am)
                    QMessageBox.information(self, "保存并入库", "已保存")
                else:
                    am.update()
                    QMessageBox.information(self, "保存并入库", "已更新")
                db_session.commit()

                # 入库成功后，自动删除草稿
                with suppress(Exception):
                    if self._draft_file.exists():
                        self._draft_file.unlink()

                # 给父窗口传递信息
                self.finished_with_result.emit(True)

                self.close()
            except Exception as e:
                logging.exception(e)
                QMessageBox.warning(self, "错误", f"添加/编辑数据发生错误：{e}")

    # ========== 草稿：恢复/应用 ==========
    def _maybe_offer_restore_draft(self):
        """新增模式下，若存在草稿文件，弹窗询问是否恢复。"""
        try:
            if not self._draft_file.exists():
                return
            ret = QMessageBox.question(
                self, "发现草稿",
                "检测到上次未提交的草稿。\n是否恢复草稿内容？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if ret == QMessageBox.StandardButton.Yes:
                data = json.loads(self._draft_file.read_text(encoding="utf-8"))
                self._apply_ui_json(data)
            elif ret == QMessageBox.StandardButton.No:
                # 用户选择丢弃草稿
                with suppress(Exception):
                    self._draft_file.unlink()
            else:
                # Cancel：保持现状，不做改变
                pass
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "草稿恢复失败", f"读取草稿失败：{e}")

    def _apply_ui_json(self, data: dict):
        """将 UI JSON（collect_form_data 的同构字典）写回到界面控件。"""

        self._init_comboboxes()

        def S(x):
            return "" if x is None else str(x)

        def set_combo_text(cmb, text, auto_insert: bool = False):
            t = S(text)
            if t == "":
                return
            idx = cmb.findText(t)
            if idx >= 0:
                cmb.setCurrentIndex(idx)
            else:
                if auto_insert:
                    cmb.insertItem(0, t)
                cmb.setCurrentIndex(0)

        basic = (data or {}).get("basic", {}) or {}
        struct = (data or {}).get("struct", {}) or {}
        wf = (data or {}).get("warhead_fcs", {}) or {}
        sp = (data or {}).get("warhead_params", {}) or {}

        # 基本信息
        set_combo_text(self.ui.cmb_country, basic.get("country"), True)
        set_combo_text(self.ui.cmb_user, basic.get("used_by"), True)
        self.ui.ed_type.setText(S(basic.get("ammunition_type")))
        self.ui.ed_name_offi.setText(S(basic.get("official_name")))
        self.ui.ed_name_cn.setText(S(basic.get("chinese_name")))
        self.ui.ed_short.setText(S(basic.get("short_name")))
        self.ui.ed_model.setText(S(basic.get("model_name")))
        self.ui.ed_submodel.setText(S(basic.get("submodel_name")))
        self.ui.ed_vendor.setText(S(basic.get("manufacturer") or basic.get("vendor")))
        self.ui.ed_service_year.setText(S(basic.get("attended_time")))

        # 存草稿的话，就image_dir
        self.image_dir = basic.get("image_dir", "")
        if self.image_dir != "":
            if Path(self.image_dir).exists():
                pm = QPixmap(self.image_dir)
                self.ui.lbl_image.setPixmap(pm)
            else:
                # 图片不存在
                QMessageBox.warning(self, "提示", "图片不存在，请重新选择")

        # 构造与动力
        self.ui.ed_weight_full.setText(S(struct.get("weight_kg")))
        self.ui.ed_len.setText(S(struct.get("length_m")))
        self.ui.ed_diameter.setText(S(struct.get("diameter_m")))
        self.ui.ed_tex.setText(S(struct.get("texture")))
        self.ui.ed_wingspan_c.setText(S(struct.get("wingspan_close_mm")))
        self.ui.ed_wingspan_o.setText(S(struct.get("wingspan_open_mm")))
        self.ui.ed_struct.setText(S(struct.get("structure")))
        self.ui.ed_max_speed.setText(S(struct.get("max_speed_ma")))
        self.ui.ed_radar_face.setText(S(struct.get("radar_cross_section")))
        self.ui.ed_power.setText(S(struct.get("power_plant")))
        self.ui.ed_launch_mass.setText(S(struct.get("launch_mass_kg")))

        # 战斗部与飞控
        set_combo_text(self.ui.cmb_warhead, wf.get("warhead_type"))
        self.ui.ed_warhead_name.setText(S(wf.get("warhead_name")))
        self.ui.ed_destroy_el.setText(S(wf.get("destroying_elements")))
        self.ui.ed_fuze.setText(S(wf.get("fuze")))
        self.ui.ed_charge.setText(S(wf.get("explosion_equivalent_TNT_T")))
        self.ui.ed_precision.setText(S(wf.get("precision_m")))
        self.ui.ed_destroy_mec.setText(S(wf.get("destroying_mechanism")))
        self.ui.ed_target.setText(S(wf.get("target")))
        self.ui.ed_carrier.setText(S(wf.get("carrier")))
        self.ui.ed_guidance.setText(S(wf.get("guidance_mode")))
        self.ui.ed_exp_payload.setText(S(wf.get("explosive_payload_kg")))
        self.ui.ed_penetration.setText(S(wf.get("penetrating_power")))
        self.ui.ed_drop_h.setText(S(wf.get("drop_height_range_m")))
        self.ui.ed_drop_speed.setText(S(wf.get("drop_speed_kmh")))
        self.ui.ed_drop_mode.setText(S(wf.get("drop_mode")))
        self.ui.ed_coverage_ar.setText(S(wf.get("coverage_area")))
        self.ui.ed_range.setText(S(wf.get("range_km")))

        # 特有参数（分战斗部类型）
        self._switch_zdb_param()

        bw = (sp.get("blast_warhead") or {})
        self.ui.ed_bp_02.setText(S(bw.get("explosive_comp")))
        self.ui.ed_bp_2.setText(S(bw.get("explosive_thermal_explosion")))
        self.ui.ed_bp_4.setText(S(bw.get("actual_charge_mass")))

        sc = (sp.get("shaped_charge_warhead") or {})
        self.ui.ed_dispersion_2.setText(S(sc.get("explosive_density")))
        self.ui.ed_dispersion_9.setText(S(sc.get("charge_detonation_velocity")))
        self.ui.ed_dispersion_5.setText(S(sc.get("detonation_pressure")))
        self.ui.ed_dispersion_6.setText(S(sc.get("liner_material")))
        self.ui.ed_dispersion_7.setText(S(sc.get("liner_cone_angle")))

        frag = (sp.get("fragmentation_warhead") or {})
        self.ui.ed_pp_dmjl_2.setText(S(frag.get("explosive_thermal_explosion")))
        self.ui.ed_pp_dmjl_4.setText(S(frag.get("case_mass_fragment")))
        set_combo_text(self.ui.cmb_pp_shape, frag.get("fragment_shape"))
        self.ui.ed_pp_s.setText(S(frag.get("fragment_surface_area")))
        self.ui.ed_pp_quality.setText(S(frag.get("fragment_mass")))
        self.ui.ed_pp_dmjl_3.setText(S(frag.get("charge_diameter")))
        self.ui.ed_pp_dmjl.setText(S(frag.get("charge_length")))

        ap = (sp.get("armor_piercing_warhead") or {})
        self.ui.ed_cj_1.setText(S(ap.get("projectile_mass")))
        self.ui.ed_cj_3.setText(S(ap.get("projectile_nose_length")))
        self.ui.ed_cj_2.setText(S(ap.get("projectile_diameter")))

        cl = (sp.get("cluster_warhead") or {})
        self.ui.ed_zm_5.setText(S(cl.get("warhead_mass")))
        self.ui.ed_zm_4.setText(S(cl.get("warhead_ref_area")))
        self.ui.ed_zm_15.setText(S(cl.get("warhead_drag_coefficient")))
        self.ui.ed_zm_13.setText(S(cl.get("submunition_count")))
        self.ui.ed_zm_14.setText(S(cl.get("submunition_model")))
        self.ui.ed_zm_16.setText(S(cl.get("submunition_mass")))
        self.ui.ed_zm_17.setText(S(cl.get("max_diameter")))
        self.ui.ed_zm_18.setText(S(cl.get("submunition_ref_area")))

    # ------- 表单数据 -------
    def load_data_from_db(self, am_id: int):
        def S(x):
            """None/空 -> ''，其他转为 str。"""
            if x is None:
                return ""
            s = str(x)
            return s

        def set_combo_text(cmb, text):
            """安全设置 QComboBox 文本：优先选择已有项，否则临时插入到第0项。"""
            t = S(text)
            if t == "":
                return
            idx = cmb.findText(t)
            if idx >= 0:
                cmb.setCurrentIndex(idx)
            else:
                cmb.insertItem(0, t)
                cmb.setCurrentIndex(0)

        with session_scope() as db_session:
            repo = SQLRepository(db_session)
            try:
                am: "Ammunition" = repo.get(am_id)
                if not am:
                    QMessageBox.warning(self, "错误", f"未找到记录：am_id={am_id}")
                    return
                self._apply_from_entity(am)
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"读取数据发生错误：{e}")

    # === 统一封装：实体 -> UI ===
    def _apply_from_entity(self, am: "Ammunition"):
        """把 Ammunition 实体转换为 UI JSON 后，复用 _apply_ui_json 写回界面。"""
        try:
            data = ammunition_to_ui_json(am)
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"转换 UI 数据失败：{e}")
            return

        # 图片直接写入 self.image_pm
        if am.am_image_blob is not None:
            self.image_pm = ImgHelper.from_bytes(am.am_image_blob).to_pixmap()
            self.ui.lbl_image.setPixmap(self.image_pm)

        self._apply_ui_json(data)

    def collect_form_data(self) -> dict:
        # 基本信息
        basic = {
            "country": self.ui.cmb_country.currentText(),
            "used_by": self.ui.cmb_user.currentText(),
            "ammunition_type": self.ui.ed_type.text(),
            "official_name": self.ui.ed_name_offi.text(),
            "chinese_name": self.ui.ed_name_cn.text(),
            "short_name": self.ui.ed_short.text(),
            "model_name": self.ui.ed_model.text(),
            "submodel_name": self.ui.ed_submodel.text(),
            "manufacturer": self.ui.ed_vendor.text(),
            "vendor": self.ui.ed_vendor.text(),
            "attended_time": self.ui.ed_service_year.text(),
            "image_dir": self.image_dir,
        }

        # 构造与动力（数值 + 单位成对）
        struct = {
            "weight_kg": self.ui.ed_weight_full.text(),
            "length_m": self.ui.ed_len.text(),
            "diameter_m": self.ui.ed_diameter.text(),
            "texture": self.ui.ed_tex.text(),
            "wingspan_close_mm": self.ui.ed_wingspan_c.text(),
            "wingspan_open_mm": self.ui.ed_wingspan_o.text(),
            "structure": self.ui.ed_struct.text(),
            "max_speed_ma": self.ui.ed_max_speed.text(),
            "radar_cross_section": self.ui.ed_radar_face.text(),
            "power_plant": self.ui.ed_power.text(),
            "launch_mass_kg": self.ui.ed_launch_mass.text(),
        }

        # 战斗部与飞控
        wf = {
            "warhead_type": self.ui.cmb_warhead.currentText(),
            "warhead_name": self.ui.ed_warhead_name.text(),
            "destroying_elements": self.ui.ed_destroy_el.text(),
            "fuze": self.ui.ed_fuze.text(),
            "explosion_equivalent_TNT_T": self.ui.ed_charge.text(),
            "precision_m": self.ui.ed_precision.text(),
            "destroying_mechanism": self.ui.ed_destroy_mec.text(),
            "target": self.ui.ed_target.text(),
            "carrier": self.ui.ed_carrier.text(),
            "guidance_mode": self.ui.ed_guidance.text(),
            "explosive_payload_kg": self.ui.ed_exp_payload.text(),
            "penetrating_power": self.ui.ed_penetration.text(),
            "drop_height_range_m": self.ui.ed_drop_h.text(),
            "drop_speed_kmh": self.ui.ed_drop_speed.text(),
            "drop_mode": self.ui.ed_drop_mode.text(),
            "coverage_area": self.ui.ed_coverage_ar.text(),
            "range_km": self.ui.ed_range.text(),
        }

        # 特有参数
        special = {
            "blast_warhead": {
                "explosive_comp": self.ui.ed_bp_02.text(),
                "explosive_thermal_explosion": self.ui.ed_bp_2.text(),
                "actual_charge_mass": self.ui.ed_bp_4.text(),
            },
            "shaped_charge_warhead": {
                "explosive_density": self.ui.ed_dispersion_2.text(),
                "charge_detonation_velocity": self.ui.ed_dispersion_9.text(),
                "detonation_pressure": self.ui.ed_dispersion_5.text(),
                "liner_material": self.ui.ed_dispersion_6.text(),
                "liner_cone_angle": self.ui.ed_dispersion_7.text(),
            },
            "fragmentation_warhead": {
                "explosive_thermal_explosion": self.ui.ed_pp_dmjl_2.text(),
                "case_mass_fragment": self.ui.ed_pp_dmjl_4.text(),
                "fragment_shape": self.ui.cmb_pp_shape.currentText(),
                "fragment_surface_area": self.ui.ed_pp_s.text(),
                "fragment_mass": self.ui.ed_pp_quality.text(),
                "charge_diameter": self.ui.ed_pp_dmjl_3.text(),
                "charge_length": self.ui.ed_pp_dmjl.text(),
            },
            "armor_piercing_warhead": {
                "projectile_mass": self.ui.ed_cj_1.text(),
                "projectile_nose_length": self.ui.ed_cj_3.text(),
                "projectile_diameter": self.ui.ed_cj_2.text(),
            },
            "cluster_warhead": {
                "warhead_mass": self.ui.ed_zm_5.text(),
                "warhead_ref_area": self.ui.ed_zm_4.text(),
                "warhead_drag_coefficient": self.ui.ed_zm_15.text(),
                "submunition_count": self.ui.ed_zm_13.text(),
                "submunition_model": self.ui.ed_zm_14.text(),
                "submunition_mass": self.ui.ed_zm_16.text(),
                "max_diameter": self.ui.ed_zm_17.text(),
                "submunition_ref_area": self.ui.ed_zm_18.text(),
            },
        }

        return {"basic": basic, "struct": struct, "warhead_fcs": wf, "warhead_params": special}


def init_tables() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # 数据库初始化
    init_tables()

    app = QApplication(sys.argv)
    win = AmmunitionEditor()
    win.show()
    sys.exit(app.exec())
