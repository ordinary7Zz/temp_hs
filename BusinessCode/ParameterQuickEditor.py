"""
参数快速编辑器
用于在场景添加界面中快速添加/编辑参数
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QLabel, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from damage_models import DamageParameter
from loguru import logger


class ParameterQuickEditor(QDialog):
    """参数快速编辑器"""

    def __init__(self, parent=None, parameter: DamageParameter = None, scene_code: str = ""):
        try:
            super().__init__(parent)
            self.parameter = parameter
            self.scene_code = scene_code

            self.setWindowTitle("编辑毁伤参数" if parameter and parameter.DPID else "添加毁伤参数")
            self.setModal(True)
            self.resize(600, 500)

            logger.info(f"初始化参数快速编辑器，场景: {scene_code}")

            self._init_ui()

            if parameter:
                self._load_parameter_data(parameter)
            else:
                # 如果没有传入参数，设置默认值
                self._set_default_values()

            logger.info("参数快速编辑器初始化完成")
        except Exception as e:
            logger.exception(f"参数快速编辑器初始化失败: {e}")
            raise

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 场景信息
        scene_label = QLabel(f"所属场景: {self.scene_code}")
        scene_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(scene_label)

        # 基本参数分组
        basic_group = QGroupBox("基本参数")
        basic_layout = QFormLayout()

        self.ed_carrier = QLineEdit()
        self.ed_carrier.setPlaceholderText("如: F-15E战斗轰炸机")
        basic_layout.addRow("投放平台:", self.ed_carrier)

        self.ed_guidance_mode = QLineEdit()
        self.ed_guidance_mode.setPlaceholderText("如: GPS/INS制导")
        basic_layout.addRow("制导方式:", self.ed_guidance_mode)

        # 战斗部类型下拉框
        self.cmb_warhead_type = QComboBox()
        self.cmb_warhead_type.addItems([
            "爆破战斗部",
            "聚能战斗部",
            "破片战斗部",
            "穿甲战斗部",
            "子母弹战斗部"
        ])
        # 设置红色星号
        warhead_label = QLabel('<span style="color: red;">*</span>战斗部类型:')
        basic_layout.addRow(warhead_label, self.cmb_warhead_type)

        self.ed_charge_amount = QLineEdit()
        self.ed_charge_amount.setPlaceholderText("如: 295.0")
        basic_layout.addRow("装药量(kg):", self.ed_charge_amount)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # 投放参数分组
        drop_group = QGroupBox("投放参数")
        drop_layout = QFormLayout()

        self.ed_drop_height = QLineEdit()
        self.ed_drop_height.setPlaceholderText("如: 10000.0")
        drop_layout.addRow("投弹高度:", self.ed_drop_height)

        self.ed_drop_speed = QLineEdit()
        self.ed_drop_speed.setPlaceholderText("如: 800.0")
        drop_layout.addRow("投弹速度(m/s):", self.ed_drop_speed)

        self.ed_drop_mode = QLineEdit()
        self.ed_drop_mode.setPlaceholderText("如: 水平投弹")
        drop_layout.addRow("投弹方式:", self.ed_drop_mode)

        self.ed_flight_range = QLineEdit()
        self.ed_flight_range.setPlaceholderText("如: 20.0")
        drop_layout.addRow("射程(km):", self.ed_flight_range)

        drop_group.setLayout(drop_layout)
        layout.addWidget(drop_group)

        # 环境参数分组
        env_group = QGroupBox("环境参数")
        env_layout = QFormLayout()

        self.cmb_electro_interference = QComboBox()
        self.cmb_electro_interference.addItems(["无", "低", "中", "高"])
        env_layout.addRow("电磁干扰等级:", self.cmb_electro_interference)

        self.cmb_weather_conditions = QComboBox()
        self.cmb_weather_conditions.addItems(["晴", "多云", "阴", "雨", "雪"])
        env_layout.addRow("天气状况:", self.cmb_weather_conditions)

        self.ed_wind_speed = QLineEdit()
        self.ed_wind_speed.setPlaceholderText("如: 5.0")
        env_layout.addRow("环境风速(m/s):", self.ed_wind_speed)

        env_group.setLayout(env_layout)
        layout.addWidget(env_group)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.on_save)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _load_parameter_data(self, param: DamageParameter):
        """加载参数数据"""
        self.ed_carrier.setText(param.Carrier or "")
        self.ed_guidance_mode.setText(param.GuidanceMode or "")

        # 设置战斗部类型（下拉框）
        if param.WarheadType:
            idx = self.cmb_warhead_type.findText(param.WarheadType)
            if idx >= 0:
                self.cmb_warhead_type.setCurrentIndex(idx)

        self.ed_charge_amount.setText(str(param.ChargeAmount) if param.ChargeAmount else "")
        self.ed_drop_height.setText(str(param.DropHeight) if param.DropHeight else "")
        self.ed_drop_speed.setText(str(param.DropSpeed) if param.DropSpeed else "")
        self.ed_drop_mode.setText(param.DropMode or "")
        self.ed_flight_range.setText(str(param.FlightRange) if param.FlightRange else "")

        # 设置下拉框
        if param.ElectroInterference:
            idx = self.cmb_electro_interference.findText(param.ElectroInterference)
            if idx >= 0:
                self.cmb_electro_interference.setCurrentIndex(idx)

        if param.WeatherConditions:
            idx = self.cmb_weather_conditions.findText(param.WeatherConditions)
            if idx >= 0:
                self.cmb_weather_conditions.setCurrentIndex(idx)

        self.ed_wind_speed.setText(str(param.WindSpeed) if param.WindSpeed else "")

    def _set_default_values(self):
        """设置默认值"""
        # 设置默认投放平台
        self.ed_carrier.setText("F-15E战斗轰炸机")

        # 设置默认制导方式
        self.ed_guidance_mode.setText("GPS/INS制导")

        # 设置默认战斗部类型（下拉框）
        self.cmb_warhead_type.setCurrentIndex(0)  # 默认选择"爆破战斗部"

        # 设置默认装药量
        self.ed_charge_amount.setText("295.0")

        # 设置默认投弹高度
        self.ed_drop_height.setText("10000.0")

        # 设置默认投弹速度
        self.ed_drop_speed.setText("800.0")

        # 设置默认投弹方式
        self.ed_drop_mode.setText("水平投弹")

        # 设置默认射程
        self.ed_flight_range.setText("20.0")

        # 设置默认电磁干扰等级
        self.cmb_electro_interference.setCurrentIndex(1)  # 低

        # 设置默认天气状况
        self.cmb_weather_conditions.setCurrentIndex(0)  # 晴

        # 设置默认风速
        self.ed_wind_speed.setText("5.0")

    def on_save(self):
        """保存按钮点击"""
        # 验证必填字段
        if not self.cmb_warhead_type.currentText():  # 检查下拉框
            QMessageBox.warning(self, "必填信息缺失", "战斗部类型为必填项")
            return

        try:
            # 更新参数对象
            self.parameter.Carrier = self.ed_carrier.text().strip() or None
            self.parameter.GuidanceMode = self.ed_guidance_mode.text().strip() or None
            self.parameter.WarheadType = self.cmb_warhead_type.currentText()  # 从下拉框获取

            charge_text = self.ed_charge_amount.text().strip()
            self.parameter.ChargeAmount = float(charge_text) if charge_text else None

            height_text = self.ed_drop_height.text().strip()
            self.parameter.DropHeight = float(height_text) if height_text else None

            speed_text = self.ed_drop_speed.text().strip()
            self.parameter.DropSpeed = float(speed_text) if speed_text else None

            self.parameter.DropMode = self.ed_drop_mode.text().strip() or None

            range_text = self.ed_flight_range.text().strip()
            self.parameter.FlightRange = float(range_text) if range_text else None

            self.parameter.ElectroInterference = self.cmb_electro_interference.currentText()
            self.parameter.WeatherConditions = self.cmb_weather_conditions.currentText()

            wind_text = self.ed_wind_speed.text().strip()
            self.parameter.WindSpeed = float(wind_text) if wind_text else None

            self.parameter.DPStatus = 1

            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "输入错误", f"数值格式错误：{e}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"保存失败：{e}")

    def get_parameter(self) -> DamageParameter:
        """获取参数对象"""
        return self.parameter


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    param = DamageParameter(
        DPID=None,
        DSID=0,
        DSCode="TEST_001",
        Carrier="",
        GuidanceMode="",
        WarheadType="",
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

    dialog = ParameterQuickEditor(None, param, "TEST_001")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        result = dialog.get_parameter()
        print("保存的参数:", result)

