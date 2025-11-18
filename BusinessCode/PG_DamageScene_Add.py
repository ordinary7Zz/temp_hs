"""
毁伤场景添加/编辑窗口
"""
import sys
import os
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QHeaderView, QWidget
)

from UIs.Frm_PG_DamageScene_Add import Ui_Frm_PG_DamageScene_Add
from damage_models import DamageScene, DamageParameter
from damage_models.sql_repository_dbhelper import DamageSceneRepository, DamageParameterRepository
from DBCode.DBHelper import DBHelper
from BusinessCode.AmmunitionSelector import AmmunitionSelectorDialog
from BusinessCode.TargetSelector import TargetSelectorDialog
from loguru import logger
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtCore import QT_VERSION
from typing import Dict, List, Any



class DamageSceneEditorMode(Enum):
    """编辑器模式"""
    Add = 1
    Edit = 2


class DamageSceneEditor(QDialog):
    """毁伤场景编辑器"""

    finished_with_result = pyqtSignal(bool)

    def __init__(self, parent=None, mode: DamageSceneEditorMode = DamageSceneEditorMode.Add, edit_scene_id: int = 0):
        super().__init__(parent)
        self.ui = Ui_Frm_PG_DamageScene_Add()
        self.ui.setupUi(self)

        self.mode = mode
        self.edit_scene_id = edit_scene_id
        self.parameters = []  # 存储场景关联的参数列表

        self.ammunition_id = 0
        self.target_id = 0
        self.ammunition = None
        self.target = None

        # 先初始化所有UI组件
        self._init_comboboxes()
        self._set_default_values()
        self._wire_signals()
        self.target_type = 1

        # 再加载数据（如果是编辑模式）
        if self.mode == DamageSceneEditorMode.Edit:
            self.setWindowTitle("编辑毁伤场景")
            if edit_scene_id == 0:
                QMessageBox.warning(self, "错误", "编辑模式下未传入场景ID")
                self.close()
                return
            try:
                self.load_data_from_db(edit_scene_id)
                self.fill_ammunition_info()
                self.fill_target_info()
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"加载数据失败：{e}")
                self.close()
                return
        else:
            self.setWindowTitle("添加毁伤场景")

        self.resize(1000, 800)

    def _init_comboboxes(self):
        """初始化下拉框"""
        # 目标类型
        if self.ui.cmb_target_type.count() == 0:
            self.ui.cmb_target_type.clear()
            self.ui.cmb_target_type.addItems(["机场跑道", "单机掩蔽库", "地下指挥所"])
        # 打击目标选项框，根据这个切换特殊参数的stack页面
        self.ui.cmb_target_type.currentIndexChanged.connect(self._switch_target_param)


    def _set_default_values(self):
        """设置默认值（仅在添加模式下）"""
        if self.mode == DamageSceneEditorMode.Add:
            # 生成默认场景编号
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.ui.ed_scene_code.setText(f"DS_{timestamp}")
            # 设置默认名称（用户可修改）
            self.ui.ed_scene_name.setPlaceholderText("例如：东部战区机场跑道打击场景")
            # 为其他输入框设置占位符文本
            #self.ui.ed_ammunition_code.setPlaceholderText("点击【选择弹药】按钮选择")
            #self.ui.ed_ammunition_id.setPlaceholderText("自动填充")
            #self.ui.ed_target_code.setPlaceholderText("点击【选择目标】按钮选择")
            #self.ui.ed_target_id.setPlaceholderText("自动填充")

    def _wire_signals(self):
        """绑定信号"""
        self.ui.btn_save.clicked.connect(self.on_save)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_select_ammunition.clicked.connect(self.on_select_ammunition)
        self.ui.btn_select_target.clicked.connect(self.on_select_target)
        self.ui.btn_add_param.clicked.connect(self._on_add_parameter)

    def on_select_ammunition(self):
        """选择弹药"""
        try:
            dialog = AmmunitionSelectorDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                ammo = dialog.get_selected_ammunition()
                if ammo:
                    # 填充弹药信息
                    #self.ui.ed_ammunition_id.setText(str(ammo['AMID']))
                    self.ammunition = ammo
                    self.ammunition_id = ammo.am_id
                    #self.ui.ed_ammunition_code.setText(ammo.model_name)
                    self.fill_ammunition_info()
                    logger.info(f"已选择弹药: {ammo.am_id} - {ammo.am_name}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"选择弹药失败：{e}")

    def fill_ammunition_info(self):
        # 显示弹药详细信息（每行一个属性，蓝色属性名+黑色属性值）
        self.ui.ed_am_type.setText(self.ammunition.am_type)
        self.ui.ed_am_name.setText(self.ammunition.am_name)
        self.ui.ed_warhead_type.setText(self.ammunition.warhead_type)
        self.ui.ed_warhead_name.setText(self.ammunition.warhead_name)
        self.ui.ed_weight_kg.setText(str(self.ammunition.weight_kg))
        self.ui.ed_launch_mass_kg.setText(str(self.ammunition.launch_mass_kg))

    def fill_target_info(self):
        # 显示目标详细信息（每行一个属性，蓝色属性名+黑色属性值）
        type_names = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}
        # 根据目标类型显示不同的关键信息
        if self.target_type == 1:  # 机场跑道
            self.ui.ed_runway_name.setText(self.target.runway_name)
            self.ui.ed_runway_code.setText(self.target.runway_code)
            self.ui.ed_r_length.setText(str(self.target.r_length))
            self.ui.ed_r_width.setText(str(self.target.r_width))
            self.ui.ed_runway_country.setText(self.target.country)
            self.ui.ed_ctbc_thick.setText(str(self.target.ctbc_thick))
            self.ui.ed_pccsc_thick.setText(str(self.target.pccsc_thick))
            self.ui.ed_gcss_thick.setText(str(self.target.gcss_thick))

        elif self.target_type == 2:  # 单机掩蔽库
            self.ui.ed_shelter_name.setText(self.target.shelter_name)
            self.ui.ed_shelter_code.setText(self.target.shelter_code)
            self.ui.ed_shelter_country.setText(self.target.country)
            self.ui.ed_shelter_height.setText(str(self.target.shelter_height))
            self.ui.ed_shelter_length.setText(str(self.target.shelter_length))
            self.ui.ed_shelter_width.setText(str(self.target.shelter_width))

        elif self.target_type == 3:  # 地下指挥所
            self.ui.ed_ucc_name.setText(self.target.ucc_name)
            self.ui.ed_ucc_code.setText(self.target.ucc_code)
            self.ui.ed_ucc_country.setText(self.target.country)
            self.ui.ed_rock_layer_thick.setText(str(self.target.rock_layer_thick))
            self.ui.ed_protective_layer_thick.setText(str(self.target.protective_layer_thick))
            self.ui.ed_lining_layer_thick.setText(str(self.target.lining_layer_thick))

    def on_select_target(self):
        """选择目标"""
        try:
            # 获取当前选择的目标类型
            target_type = self.ui.cmb_target_type.currentIndex() + 1  # 1-跑道, 2-掩体, 3-地下目标
            self.target_type = target_type
            dialog = TargetSelectorDialog(self, target_type=target_type)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                target = dialog.get_selected_target()
                if target:
                    self.target = target
                    # 填充目标信息
                    #self.ui.ed_target_id.setText(str(target['TargetID']))
                    if self.target_type == 1:
                        self.ui.ed_runway_code.setText(target.runway_code)
                        target_name = target.runway_name
                    elif self.target_type == 2:
                        self.ui.ed_shelter_code.setText(target.shelter_code)
                        target_name = target.shelter_name
                    elif self.target_type == 3:
                        self.ui.ed_ucc_code.setText(target.ucc_code)
                        target_name = target.ucc_name
                    self.target_id = target.id
                    self.target = target
                    self.fill_target_info()
                    logger.info(f"已选择目标: {target.id} - {target_name}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"选择目标失败：{e}")

    def _on_add_parameter(self):
        """添加参数"""
        try:
            # 检查是否已填写场景编号
            scene_code = self.ui.ed_scene_code.text().strip()
            if not scene_code:
                QMessageBox.warning(self, "提示", "请先填写场景编号")
                return

            warhead_type = ""
            if self.ammunition and self.ammunition.warhead_type:
                warhead_type = self.ammunition.warhead_type
            # 创建一个临时的参数对象
            param = DamageParameter(
                DPID=None,
                DSID=self.edit_scene_id if self.edit_scene_id else 0,
                DSCode=scene_code,
                Carrier="",
                GuidanceMode="",
                WarheadType=warhead_type,
                ChargeAmount=None,
                DropHeight=None,
                DropSpeed=None,
                DropMode="",
                FlightRange=None,
                ElectroInterference="",
                WeatherConditions="",
                WindSpeed=None,
                DPStatus=1
            )

            # 打开参数编辑对话框
            from BusinessCode.ParameterQuickEditor import ParameterQuickEditor
            dialog = ParameterQuickEditor(self, param, scene_code)

            logger.info(f"打开参数快速编辑器，场景编号: {scene_code}")

            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_param = dialog.get_parameter()
                self.parameters.append(updated_param)
                db = DBHelper()
                try:
                    repo = DamageParameterRepository(db)
                    #self.parameters = repo.add(updated_param)
                except Exception as e:
                    logger.exception(e)
                finally:
                    db.close()
                self._setup_table()
                logger.info(f"参数添加成功，当前参数数量: {len(self.parameters)}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.critical(self, "错误", f"添加参数失败：{str(e)}\n\n详细信息请查看日志")

    def _on_edit_parameter(self, index: int):
        """编辑参数"""
        try:
            if 0 <= index < len(self.parameters):
                param = self.parameters[index]
                scene_code = self.ui.ed_scene_code.text().strip()

                from BusinessCode.ParameterQuickEditor import ParameterQuickEditor
                dialog = ParameterQuickEditor(self, param, scene_code)

                logger.info(f"编辑参数，索引: {index}")

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.parameters[index] = dialog.get_parameter()
                    #self._refresh_parameter_table()
                    self._setup_table()
                    logger.info(f"参数编辑成功，索引: {index}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.critical(self, "错误", f"编辑参数失败：{str(e)}\n\n详细信息请查看日志")

    def _on_delete_parameter(self, index: int):
        """删除参数"""
        if 0 <= index < len(self.parameters):
            param = self.parameters[index]
            param_desc = f"投放平台: {param.Carrier or '未设置'}\n战斗部: {param.WarheadType or '未设置'}"

            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除该参数吗？\n\n{param_desc}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # 如果参数已经存在于数据库中（有DPID），需要从数据库删除
                if param.DPID:
                    db = DBHelper()
                    try:
                        from damage_models.sql_repository_dbhelper import DamageParameterRepository
                        repo = DamageParameterRepository(db)
                        success = repo.delete(param.DPID)
                        if success:
                            logger.info(f"已从数据库删除参数 ID={param.DPID}")
                        else:
                            logger.warning(f"从数据库删除参数 ID={param.DPID} 失败")
                    except Exception as e:
                        logger.exception(e)
                        QMessageBox.warning(self, "错误", f"从数据库删除参数失败：{e}")
                        return
                    finally:
                        db.close()

                # 从内存列表中删除
                self.parameters.pop(index)
                #self._refresh_parameter_table()
                self._setup_table()
                logger.info(f"参数已删除，剩余 {len(self.parameters)} 个参数")

    def _load_scene_parameters(self, scene_id: int):
        """加载场景关联的参数"""
        db = DBHelper()
        try:
            repo = DamageParameterRepository(db)
            self.parameters = repo.get_by_scene_id(scene_id)
            # self._setup_table(self.edit_scene_id)
        except Exception as e:
            logger.exception(e)
        finally:
            db.close()

    def load_data_from_db(self, scene_id: int):
        db = DBHelper()
        try:
            repo = DamageSceneRepository(db)
            scene = repo.get_by_id(scene_id)

            if not scene:
                raise ValueError(f"找不到ID为{scene_id}的场景")

            # 填充表单
            self.ui.ed_scene_code.setText(scene.DSCode)
            self.ui.ed_scene_name.setText(scene.DSName)
            self.ui.ed_offensive.setText(scene.DSOffensive or "")
            self.ui.ed_defensive.setText(scene.DSDefensive or "")
            self.ui.ed_battle.setText(scene.DSBattle or "")

            #self.ui.ed_ammunition_code.setText(scene.AMCode)
            #self.ui.ed_ammunition_id.setText(str(scene.AMID))
            self.ammunition_id = scene.AMID
            from am_models.sql_repository import SQLRepository as AmModelSQLRepository
            from am_models.db import session_scope as AmSessionScope
            with AmSessionScope() as session:
                am_repo = AmModelSQLRepository(session)
            self.ammunition = am_repo.get(self.ammunition_id)

            # 目标类型：1=跑道, 2=掩体, 3=地下目标
            if scene.TargetType in [1, 2, 3]:
                self.ui.cmb_target_type.setCurrentIndex(scene.TargetType - 1)
            #self.ui.ed_target_id.setText(str(scene.TargetID))
            self.target_type = scene.TargetType
            self.target_id = scene.TargetID
            #self.ui.ed_target_code.setText(scene.TargetCode)
            from target_model.sql_repository import SQLRepository as TargetModelSQLRepository
            from target_model.db import session_scope as TargetModelSessionScope
            with TargetModelSessionScope() as session:
                target_repo = TargetModelSQLRepository(session)
            from target_model.entities import AirportRunway, AircraftShelter, UndergroundCommandPost
            if scene.TargetType == 1:
                entity_cls = AirportRunway
            elif scene.TargetType == 2:
                entity_cls = AircraftShelter
            else:
                entity_cls = UndergroundCommandPost
            self.target = target_repo.get(self.target_id, entity_cls)

            # 加载关联的参数
            self._load_scene_parameters(scene_id)
            self._setup_table()
        finally:
            db.close()

    def collect_form_data(self) -> dict:
        """收集表单数据"""
        # 目标类型映射
        target_type = self.ui.cmb_target_type.currentIndex() + 1  # 1, 2, 3

        if target_type == 1:
            TargetCode = self.ui.ed_runway_code.text().strip()
        elif target_type == 2:
            TargetCode = self.ui.ed_shelter_code.text().strip()
        elif target_type == 3:
            TargetCode = self.ui.ed_ucc_code.text().strip()
        data = {
            'DSCode': self.ui.ed_scene_code.text().strip(),
            'DSName': self.ui.ed_scene_name.text().strip(),
            'DSOffensive': self.ui.ed_offensive.text().strip() or None,
            'DSDefensive': self.ui.ed_defensive.text().strip() or None,
            'DSBattle': self.ui.ed_battle.text().strip() or None,
            'AMID': int(self.ammunition_id),
            'AMCode': self.ui.ed_am_type.text().strip(),
            'TargetType': target_type,
            'TargetID': int(self.target_id),
            'TargetCode': TargetCode,
            'DSStatus': 1  # 固定为1(未删除)
        }

        return data

    def on_save(self):
        """保存按钮点击"""
        # 验证必填字段
        must_filled = []
        if not self.ui.ed_scene_code.text().strip():
            must_filled.append("场景编号")
        if not self.ui.ed_scene_name.text().strip():
            must_filled.append("场景名称")
        if not self.ui.ed_am_type.text().strip():
            must_filled.append("弹药代码")
        if self.target_type == 1:
            if not self.ui.ed_runway_name.text().strip():
                must_filled.append("机场信息")
        elif self.target_type == 2:
            if not self.ui.ed_shelter_name.text().strip():
                must_filled.append("单机掩蔽库信息")
        elif self.target_type == 3:
            if not self.ui.ed_ucc_name.text().strip():
                must_filled.append("地下指挥所信息")

        if must_filled:
            # print(self.ui.ed_scene_code.text().strip())
            QMessageBox.warning(self, "必填信息缺失", f"必须填写：{'、'.join(must_filled)}")
            return

        try:
            data = self.collect_form_data()

            # 创建实体
            scene = DamageScene(
                DSID=self.edit_scene_id if self.mode == DamageSceneEditorMode.Edit else None,
                DSCode=data['DSCode'],
                DSName=data['DSName'],
                DSOffensive=data['DSOffensive'],
                DSDefensive=data['DSDefensive'],
                DSBattle=data['DSBattle'],
                AMID=data['AMID'],
                AMCode=data['AMCode'],
                TargetType=data['TargetType'],
                TargetID=data['TargetID'],
                TargetCode=data['TargetCode'],
                DSStatus=data['DSStatus']
            )

            # 保存到数据库
            db = DBHelper()
            try:
                repo = DamageSceneRepository(db)
                param_repo = DamageParameterRepository(db)

                if self.mode == DamageSceneEditorMode.Add:
                    scene_id = repo.add(scene)
                    if scene_id == 0:
                        QMessageBox.warning(self, "错误", f"弹药代码或名称重复")
                        return

                    # 保存关联的参数
                    saved_count = 0
                    for param in self.parameters:
                        param.DSID = scene_id['DSID']
                        param.DSCode = data['DSCode']
                        param_repo.add(param)
                        saved_count += 1

                    msg = f"毁伤场景已添加"
                    if saved_count > 0:
                        msg += f"\n同时添加了 {saved_count} 个关联参数"
                    QMessageBox.information(self, "保存成功", msg)
                    logger.info("添加毁伤场景: {}", scene_id)
                else:
                    success = repo.update(scene)
                    if success:
                        # 更新关联的参数
                        saved_count = 0
                        for param in self.parameters:
                            if param.DPID:
                                param_repo.update(param)
                            else:
                                param.DSID = self.edit_scene_id
                                param.DSCode = data['DSCode']
                                param_repo.add(param)
                            saved_count += 1

                        msg = "场景已更新"
                        if saved_count > 0:
                            msg += f"\n同时保存了 {saved_count} 个关联参数"
                        QMessageBox.information(self, "保存成功", msg)
                    else:
                        QMessageBox.warning(self, "保存失败", "更新失败，场景不存在")
                        return
                    logger.info("更新毁伤场景: ", {scene.DSID})
            finally:
                db.close()

            # 通知父窗口
            self.finished_with_result.emit(True)
            self.close()

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"保存失败：{e}")

    def _setup_table(self):
        tv = self.ui.tb_paramter_info
        # 移除现有的模型，这会清空表格中所有的数据
        tv.setModel(None)

        headers = ["参数ID", "投放平台", "制导方式", "战斗部类型", "装药量(kg)", "投弹高度", "投弹速度", "操作"]
        table = QStandardItemModel(0, len(headers), tv)
        table.setHorizontalHeaderLabels(headers)
        tv.setModel(table)

        # hh = tv.horizontalHeader()
        # hh.setStretchLastSection(False)  # 不让最后一列自动吞空间
        # for i in range(0, len(headers)):
        #     hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # --- 设置固定列宽 ---
        # 顺序对应 headers 中的列
        column_widths = [80, 120, 100, 100, 100, 100, 100, 120]
        for i, width in enumerate(column_widths):
            tv.setColumnWidth(i, width)

        tv.verticalHeader().setVisible(False)  # 隐藏行号（可选）
        tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
        tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)
        logger.debug(self.parameters)
        row_id = 0
        try:
            for idx, param in enumerate(self.parameters):
                logger.debug(f"idx:{idx}, row_id: {row_id}, param:{param}")

                # 填充数据
                table.setItem(row_id, 0, QStandardItem(str(param.DPID or "新增")))
                table.setItem(row_id, 1, QStandardItem(param.Carrier or ""))
                table.setItem(row_id, 2, QStandardItem(param.GuidanceMode or ""))
                table.setItem(row_id, 3, QStandardItem(param.WarheadType or ""))
                table.setItem(row_id, 4, QStandardItem(str(param.ChargeAmount or "")))
                table.setItem(row_id, 5, QStandardItem(str(param.DropHeight or "")))
                table.setItem(row_id, 6, QStandardItem(str(param.DropSpeed or "")))

                # 添加操作按钮
                self._add_action_param_buttons(tv, table, row_id, len(headers) - 1, param_id=idx)
                row_id = row_id + 1
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"列举表格内容发生错误{e}")

    def _add_action_param_buttons(self, tv, table, row, col, param_id: int):
        w = QWidget(tv)
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        btn_edit = QPushButton("编辑", w)
        btn_del = QPushButton("删除", w)
        # 行号捕获到闭包里（也可把主键 ID 作为属性设置到按钮上）
        btn_edit.clicked.connect(lambda _=False, r=row: self._on_edit_parameter(param_id))
        btn_del.clicked.connect(lambda _=False, r=row: self._on_delete_parameter(param_id))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        w.setLayout(layout)

        index = table.index(row, col)
        tv.setIndexWidget(index, w)

    def _switch_target_param(self):
        self.ui.stackedWidget.setCurrentIndex(self.ui.cmb_target_type.currentIndex())
        print(self.ui.cmb_target_type.currentIndex())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DamageSceneEditor(mode=DamageSceneEditorMode.Add)
    window.show()
    sys.exit(app.exec())

