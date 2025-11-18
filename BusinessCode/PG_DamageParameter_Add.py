"""
毁伤参数添加/编辑窗口
"""
import sys
import os
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from UIs.Frm_PG_DamageParameter_Add import Ui_Frm_PG_DamageParameter_Add
from damage_models import DamageParameter
from damage_models.sql_repository_dbhelper import DamageParameterRepository
from DBCode.DBHelper import DBHelper
from BusinessCode.SceneSelector import SceneSelectorDialog
from loguru import logger


class DamageParameterEditorMode(Enum):
    """编辑器模式"""
    Add = 1
    Edit = 2


class DamageParameterEditor(QDialog):
    """毁伤参数编辑器"""

    finished_with_result = pyqtSignal(bool)

    def __init__(self, parent=None, mode: DamageParameterEditorMode = DamageParameterEditorMode.Add, edit_param_id: int = 0):
        super().__init__(parent)
        self.ui = Ui_Frm_PG_DamageParameter_Add()
        self.ui.setupUi(self)

        self.mode = mode
        self.edit_param_id = edit_param_id

        if self.mode == DamageParameterEditorMode.Edit:
            self.setWindowTitle("编辑毁伤参数")
            if edit_param_id == 0:
                QMessageBox.warning(self, "错误", "编辑模式下未传入参数ID")
                self.close()
                return
            try:
                self.load_data_from_db(edit_param_id)
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"加载数据失败：{e}")
                self.close()
                return
        else:
            self.setWindowTitle("添加毁伤参数")

        self._init_comboboxes()
        self._set_default_values()
        self._wire_signals()
        #self.resize(500, 550)

    def _init_comboboxes(self):
        """初始化下拉框"""
        # 电磁干扰等级
        if self.ui.cmb_electro_interference.count() == 0:
            self.ui.cmb_electro_interference.clear()
            self.ui.cmb_electro_interference.addItems(["无", "低", "中", "高"])

        # 天气状况
        if self.ui.cmb_weather_conditions.count() == 0:
            self.ui.cmb_weather_conditions.clear()
            self.ui.cmb_weather_conditions.addItems(["晴", "多云", "阴", "雨", "雪"])

    def _set_default_values(self):
        """设置默认值（仅在添加模式下）"""
        if self.mode == DamageParameterEditorMode.Add:
            # 设置默认投放平台
            self.ui.ed_carrier.setText("F-15E战斗轰炸机")

            # 设置默认制导方式
            self.ui.ed_guidance_mode.setText("GPS/INS制导")

            # 设置默认战斗部类型（下拉框）
            self.ui.cmb_warhead_type.setCurrentIndex(0)  # 默认选择"爆破战斗部"

            # 设置默认装药量
            self.ui.ed_charge_amount.setText("295.0")

            # 设置默认投弹高度
            self.ui.ed_drop_height.setText("10000.0")

            # 设置默认投弹速度
            self.ui.ed_drop_speed.setText("800.0")

            # 设置默认投弹方式
            self.ui.ed_drop_mode.setText("水平投弹")

            # 设置默认射程
            self.ui.ed_flight_range.setText("20.0")

            # 设置默认电磁干扰等级
            self.ui.cmb_electro_interference.setCurrentIndex(1)  # 低

            # 设置默认天气状况
            self.ui.cmb_weather_conditions.setCurrentIndex(0)  # 晴

            # 设置默认风速
            self.ui.ed_wind_speed.setText("5.0")

            # 设置占位符
            self.ui.ed_scene_code.setPlaceholderText("点击【选择场景】按钮选择")
            self.ui.ed_scene_id.setPlaceholderText("自动填充")

    def _wire_signals(self):
        """绑定信号"""
        self.ui.btn_save.clicked.connect(self.on_save)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_select_scene.clicked.connect(self.on_select_scene)

    def on_select_scene(self):
        """选择场景"""
        try:
            dialog = SceneSelectorDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                scene = dialog.get_selected_scene()
                if scene:
                    # 填充场景信息
                    self.ui.ed_scene_id.setText(str(scene['DSID']))
                    self.ui.ed_scene_code.setText(scene['DSCode'])

                    # 显示选择的场景信息
                    scene_info = f"{scene['DSName']} ({scene['DSCode']})"
                    QMessageBox.information(self, "选择成功", f"已选择场景：\n{scene_info}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"选择场景失败：{e}")

    def load_data_from_db(self, param_id: int):
        db = DBHelper()
        try:
            repo = DamageParameterRepository(db)
            param = repo.get_by_id(param_id)

            if not param:
                raise ValueError(f"找不到ID为{param_id}的参数")

            # 填充表单
            self.ui.ed_scene_code.setText(param.DSCode)
            self.ui.ed_scene_id.setText(str(param.DSID))

            self.ui.ed_carrier.setText(param.Carrier or "")
            self.ui.ed_guidance_mode.setText(param.GuidanceMode or "")

            # 设置战斗部类型（下拉框）
            if param.WarheadType:
                idx = self.ui.cmb_warhead_type.findText(param.WarheadType)
                if idx >= 0:
                    self.ui.cmb_warhead_type.setCurrentIndex(idx)

            self.ui.ed_charge_amount.setText(str(param.ChargeAmount) if param.ChargeAmount else "")

            self.ui.ed_drop_height.setText(str(param.DropHeight) if param.DropHeight else "")
            self.ui.ed_drop_speed.setText(str(param.DropSpeed) if param.DropSpeed else "")
            self.ui.ed_drop_mode.setText(param.DropMode or "")
            self.ui.ed_flight_range.setText(str(param.FlightRange) if param.FlightRange else "")

            # 电磁干扰
            if param.ElectroInterference:
                idx = self.ui.cmb_electro_interference.findText(param.ElectroInterference)
                if idx >= 0:
                    self.ui.cmb_electro_interference.setCurrentIndex(idx)

            # 天气
            if param.WeatherConditions:
                idx = self.ui.cmb_weather_conditions.findText(param.WeatherConditions)
                if idx >= 0:
                    self.ui.cmb_weather_conditions.setCurrentIndex(idx)

            self.ui.ed_wind_speed.setText(str(param.WindSpeed) if param.WindSpeed else "")
        finally:
            db.close()

    def collect_form_data(self) -> dict:
        """收集表单数据"""
        data = {
            'DSID': int(self.ui.ed_scene_id.text()) if self.ui.ed_scene_id.text() else 0,
            'DSCode': self.ui.ed_scene_code.text().strip(),
            'Carrier': self.ui.ed_carrier.text().strip() or None,
            'GuidanceMode': self.ui.ed_guidance_mode.text().strip() or None,
            'WarheadType': self.ui.cmb_warhead_type.currentText(),  # 从下拉框获取
            'ChargeAmount': float(self.ui.ed_charge_amount.text()) if self.ui.ed_charge_amount.text() else None,
            'DropHeight': float(self.ui.ed_drop_height.text()) if self.ui.ed_drop_height.text() else None,
            'DropSpeed': float(self.ui.ed_drop_speed.text()) if self.ui.ed_drop_speed.text() else None,
            'DropMode': self.ui.ed_drop_mode.text().strip() or None,
            'FlightRange': float(self.ui.ed_flight_range.text()) if self.ui.ed_flight_range.text() else None,
            'ElectroInterference': self.ui.cmb_electro_interference.currentText() or None,
            'WeatherConditions': self.ui.cmb_weather_conditions.currentText() or None,
            'WindSpeed': float(self.ui.ed_wind_speed.text()) if self.ui.ed_wind_speed.text() else None
        }

        return data

    def on_save(self):
        """保存按钮点击"""
        # 验证必填字段
        must_filled = []
        if not self.ui.ed_scene_code.text().strip():
            must_filled.append("场景编号")
        if not self.ui.cmb_warhead_type.currentText():  # 检查下拉框
            must_filled.append("战斗部类型")

        if must_filled:
            QMessageBox.warning(self, "必填信息缺失", f"必须填写：{'、'.join(must_filled)}")
            return

        try:
            data = self.collect_form_data()

            # 创建实体
            param = DamageParameter(
                DPID=self.edit_param_id if self.mode == DamageParameterEditorMode.Edit else None,
                DSID=data['DSID'],
                DSCode=data['DSCode'],
                Carrier=data['Carrier'],
                GuidanceMode=data['GuidanceMode'],
                WarheadType=data['WarheadType'],
                ChargeAmount=data['ChargeAmount'],
                DropHeight=data['DropHeight'],
                DropSpeed=data['DropSpeed'],
                DropMode=data['DropMode'],
                FlightRange=data['FlightRange'],
                ElectroInterference=data['ElectroInterference'],
                WeatherConditions=data['WeatherConditions'],
                WindSpeed=data['WindSpeed']
                #DPStatus=data['DPStatus']
            )

            # 保存到数据库
            db = DBHelper()
            try:
                repo = DamageParameterRepository(db)

                if self.mode == DamageParameterEditorMode.Add:
                    param_id = repo.add(param)
                    QMessageBox.information(self, "保存成功", f"参数已添加，ID={param_id}")
                else:
                    success = repo.update(param)
                    if success:
                        QMessageBox.information(self, "保存成功", "参数已更新")
                    else:
                        QMessageBox.warning(self, "保存失败", "更新失败，参数不存在")
                        return
            finally:
                db.close()

            # 通知父窗口
            self.finished_with_result.emit(True)
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "输入错误", f"数值格式错误：{e}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"保存失败：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DamageParameterEditor(mode=DamageParameterEditorMode.Add)
    window.show()
    sys.exit(app.exec())

