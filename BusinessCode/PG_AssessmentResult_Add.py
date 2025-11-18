"""
毁伤结果添加/编辑窗口
"""
import sys
import os
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from UIs.Frm_PG_AssessmentResult_Add import Ui_Frm_PG_AssessmentResult_Add
from damage_models import AssessmentResult
from damage_models.sql_repository_dbhelper import AssessmentResultRepository
from DBCode.DBHelper import DBHelper
from loguru import logger


class AssessmentResultEditorMode(Enum):
    """编辑器模式"""
    Add = 1
    Edit = 2


class AssessmentResultEditor(QDialog):
    """毁伤结果编辑器"""

    finished_with_result = pyqtSignal(bool)

    def __init__(self, parent=None, mode: AssessmentResultEditorMode = AssessmentResultEditorMode.Add, edit_result_id: int = 0):
        super().__init__(parent)
        self.ui = Ui_Frm_PG_AssessmentResult_Add()
        self.ui.setupUi(self)

        self.mode = mode
        self.edit_result_id = edit_result_id

        # 初始化UI组件
        self._init_comboboxes()
        self._set_default_values()
        self._wire_signals()

        # 加载数据（如果是编辑模式）
        if self.mode == AssessmentResultEditorMode.Edit:
            self.setWindowTitle("编辑毁伤结果")
            if edit_result_id == 0:
                QMessageBox.warning(self, "错误", "编辑模式下未传入结果ID")
                self.close()
                return
            try:
                self.load_data_from_db(edit_result_id)
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"加载数据失败：{e}")
                self.close()
                return
        else:
            self.setWindowTitle("添加毁伤能力计算结果")

        #self.resize(650, 500)

    def _init_comboboxes(self):
        """初始化下拉框"""
        # 目标类型
        if self.ui.cmb_target_type.count() == 0:
            self.ui.cmb_target_type.clear()
            self.ui.cmb_target_type.addItems(["机场跑道", "单机掩蔽库", "地下指挥所"])

        # 毁伤等级
        if self.ui.cmb_damage_degree.count() == 0:
            self.ui.cmb_damage_degree.clear()
            self.ui.cmb_damage_degree.addItems(["未达到轻度毁伤", "轻度毁伤", "中度毁伤", "重度毁伤", "完全摧毁"])

    def _set_default_values(self):
        """设置默认值（仅在添加模式下）"""
        if self.mode == AssessmentResultEditorMode.Add:
            # 设置占位符提示用户点击选择按钮
            self.ui.ed_scene_id.setPlaceholderText("点击【选择场景】按钮")
            self.ui.ed_parameter_id.setPlaceholderText("点击【选择参数】按钮")
            self.ui.ed_ammunition_id.setPlaceholderText("点击【选择弹药】按钮")
            self.ui.ed_target_id.setPlaceholderText("点击【选择目标】按钮")

            # 设置默认毁伤等级
            self.ui.cmb_damage_degree.setCurrentIndex(3)  # 默认重度毁伤

            # 设置默认目标类型
            self.ui.cmb_target_type.setCurrentIndex(0)  # 默认跑道

    def _wire_signals(self):
        """绑定信号"""
        self.ui.btn_save.clicked.connect(self.on_save)
        self.ui.btn_cancel.clicked.connect(self.on_cancel)

        # 绑定场景选择按钮
        self.ui.btn_select_scene.clicked.connect(self.on_select_scene)
        # 绑定参数选择按钮
        self.ui.btn_select_param.clicked.connect(self.on_select_param)

        # 绑定计算毁伤结果按钮
        self.ui.btn_calculate_damage.clicked.connect(self.on_calculate_damage)

    def load_data_from_db(self, result_id: int):
        """从数据库加载数据"""
        db = DBHelper()
        try:
            repo = AssessmentResultRepository(db)
            result = repo.get_by_id(result_id)

            if not result:
                raise Exception(f"未找到ID为 {result_id} 的毁伤结果")

            # 填充数据到界面
            self.ui.ed_scene_id.setText(str(result.DSID))
            self.ui.ed_parameter_id.setText(str(result.DPID))
            self.ui.ed_ammunition_id.setText(str(result.AMID))
            self.ui.ed_target_id.setText(str(result.TargetID))

            # 设置目标类型
            target_type_index = result.TargetType - 1 if result.TargetType > 0 else 0
            self.ui.cmb_target_type.setCurrentIndex(target_type_index)

            # 设置弹坑参数
            if result.DADepth is not None:
                self.ui.ed_depth.setText(str(result.DADepth))
            if result.DADiameter is not None:
                self.ui.ed_diameter.setText(str(result.DADiameter))
            if result.DAVolume is not None:
                self.ui.ed_volume.setText(str(result.DAVolume))
            if result.DAArea is not None:
                self.ui.ed_area.setText(str(result.DAArea))
            if result.DALength is not None:
                self.ui.ed_length.setText(str(result.DALength))
            if result.DAWidth is not None:
                self.ui.ed_width.setText(str(result.DAWidth))

            # 设置毁伤评估
            if result.Discturction is not None:
                self.ui.ed_discturction.setText(str(result.Discturction))

            if result.DamageDegree:
                degree_map = {"未达到轻度毁伤": 0, "轻度毁伤": 1, "中度毁伤": 2, "重度毁伤": 3, "完全摧毁": 4}
                idx = degree_map.get(result.DamageDegree, 3)
                self.ui.cmb_damage_degree.setCurrentIndex(idx)

            logger.info(f"成功加载毁伤结果数据: ID={result_id}")
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            db.close()

    def on_select_scene(self):
        """选择场景"""
        try:
            from BusinessCode.SceneSelectorDialog import SceneSelectorDialog
            from damage_models.sql_repository_dbhelper import DamageParameterRepository

            dialog = SceneSelectorDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                scene = dialog.get_selected_scene()
                if scene:
                    # 填充场景ID
                    self.ui.ed_scene_id.setText(str(scene['DSID']))

                    # 自动填充关联的弹药ID、目标类型和目标ID
                    if scene['AMID']:
                        self.ui.ed_ammunition_id.setText(str(scene['AMID']))
                    if scene['TargetType']:
                        self.ui.cmb_target_type.setCurrentIndex(scene['TargetType'] - 1)
                    if scene['TargetID']:
                        self.ui.ed_target_id.setText(str(scene['TargetID']))

                    QMessageBox.information(self, "选择成功",
                        f"已选择场景：{scene['DSCode']} - {scene['DSName']}\n"
                        f"并自动填充了关联的弹药和目标信息")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"选择场景失败：{e}")

    def on_select_param(self):
        """选择参数"""
        try:
            from BusinessCode.ParamSelectorDialog import ParamSelectorDialog
            from damage_models.sql_repository_dbhelper import DamageParameterRepository
            dialog = ParamSelectorDialog(self, int(self.ui.ed_scene_id.text()))
            if dialog.exec() == QDialog.DialogCode.Accepted:
                param = dialog.get_selected_param()
                if param:
                    # 填充参数ID
                    self.ui.ed_parameter_id.setText(str(param.DPID))
                    QMessageBox.information(self, "选择成功",
                        f"已选择参数：ID={param.DPID}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", "场景选择有误")
    def on_calculate_damage(self):
        """计算毁伤结果按钮点击"""
        try:
            # 验证必要的输入
            if not self.ui.ed_scene_id.text().strip():
                QMessageBox.warning(self, "提示", "请先选择场景")
                return
            if not self.ui.ed_parameter_id.text().strip():
                QMessageBox.warning(self, "提示", "场景没有关联的参数，无法计算")
                return
            if not self.ui.ed_ammunition_id.text().strip():
                QMessageBox.warning(self, "提示", "场景没有关联的弹药，无法计算")
                return
            if not self.ui.ed_target_id.text().strip():
                QMessageBox.warning(self, "提示", "场景没有关联的目标，无法计算")
                return

            # 获取输入参数
            scene_id = int(self.ui.ed_scene_id.text().strip())
            parameter_id = int(self.ui.ed_parameter_id.text().strip())
            ammunition_id = int(self.ui.ed_ammunition_id.text().strip())
            target_type = self.ui.cmb_target_type.currentIndex() + 1
            target_id = int(self.ui.ed_target_id.text().strip())

            logger.info(f"开始计算毁伤结果: 场景ID={scene_id}, 参数ID={parameter_id}, "
                       f"弹药ID={ammunition_id}, 目标类型={target_type}, 目标ID={target_id}")

            # 显示计算进度
            QMessageBox.information(self, "提示", "正在计算毁伤结果，请稍候...")

            # 调用计算模块
            from BusinessCode.DamageCalculator import calculate_damage
            result = calculate_damage(scene_id, parameter_id, ammunition_id, target_type, target_id)

            # 填充计算结果到界面
            self.ui.ed_depth.setText(str(result['da_depth']))
            self.ui.ed_diameter.setText(str(result['da_diameter']))
            self.ui.ed_volume.setText(str(result['da_volume']))
            self.ui.ed_area.setText(str(result['da_area']))
            self.ui.ed_length.setText(str(result['da_length']))
            self.ui.ed_width.setText(str(result['da_width']))
            self.ui.ed_discturction.setText(str(result['discturction']))

            # 设置毁伤等级
            damage_degree = result['damage_degree']
            degree_map = {"未达到轻度毁伤": 0, "轻度毁伤": 1, "中度毁伤": 2, "重度毁伤": 3, "完全摧毁": 4}
            idx = degree_map.get(damage_degree, 3)
            self.ui.cmb_damage_degree.setCurrentIndex(idx)

            logger.info("毁伤结果计算完成并填充到界面")
            QMessageBox.information(self, "成功",
                f"毁伤结果计算完成！\n\n"
                f"弹坑深度: {result['da_depth']} m\n"
                f"弹坑直径: {result['da_diameter']} m\n"
                f"结构破坏程度: {result['discturction']}\n"
                f"毁伤等级: {damage_degree}")

        except ValueError as ve:
            logger.error(f"输入参数错误: {ve}")
            QMessageBox.warning(self, "输入错误", f"请确保所有ID都是有效的数字")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"计算毁伤结果失败：{e}")

    def on_save(self):
        """保存按钮点击"""
        try:
            # 验证必填字段
            if not self.ui.ed_scene_id.text().strip():
                QMessageBox.warning(self, "验证失败", "场景ID不能为空")
                return
            if not self.ui.ed_parameter_id.text().strip():
                QMessageBox.warning(self, "验证失败", "参数ID不能为空")
                return
            if not self.ui.ed_ammunition_id.text().strip():
                QMessageBox.warning(self, "验证失败", "弹药ID不能为空")
                return
            if not self.ui.ed_target_id.text().strip():
                QMessageBox.warning(self, "验证失败", "目标ID不能为空")
                return

            # 构建实体对象
            result = AssessmentResult()

            # 设置关联信息
            result.DSID = int(self.ui.ed_scene_id.text().strip())
            result.DPID = int(self.ui.ed_parameter_id.text().strip())
            result.AMID = int(self.ui.ed_ammunition_id.text().strip())
            result.TargetType = self.ui.cmb_target_type.currentIndex() + 1
            result.TargetID = int(self.ui.ed_target_id.text().strip())

            # 设置弹坑参数
            if self.ui.ed_depth.text().strip():
                result.DADepth = float(self.ui.ed_depth.text().strip())
            if self.ui.ed_diameter.text().strip():
                result.DADiameter = float(self.ui.ed_diameter.text().strip())
            if self.ui.ed_volume.text().strip():
                result.DAVolume = float(self.ui.ed_volume.text().strip())
            if self.ui.ed_area.text().strip():
                result.DAArea = float(self.ui.ed_area.text().strip())
            if self.ui.ed_length.text().strip():
                result.DALength = float(self.ui.ed_length.text().strip())
            if self.ui.ed_width.text().strip():
                result.DAWidth = float(self.ui.ed_width.text().strip())

            # 设置毁伤评估
            if self.ui.ed_discturction.text().strip():
                result.Discturction = float(self.ui.ed_discturction.text().strip())
            result.DamageDegree = self.ui.cmb_damage_degree.currentText()

            # 保存到数据库
            db = DBHelper()
            try:
                repo = AssessmentResultRepository(db)

                if self.mode == AssessmentResultEditorMode.Add:
                    new_id = repo.add(result)
                    QMessageBox.information(self, "成功", f"添加成功，ID: {new_id}")
                else:
                    result.DAID = self.edit_result_id
                    if repo.update(result):
                        QMessageBox.information(self, "成功", "更新成功")
                    else:
                        QMessageBox.warning(self, "失败", "更新失败")

                self.finished_with_result.emit(True)
                self.close()

            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"保存失败：{e}")
            finally:
                db.close()

        except ValueError as ve:
            QMessageBox.warning(self, "输入错误", f"数值格式不正确：{ve}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"保存失败：{e}")

    def on_cancel(self):
        """取消按钮点击"""
        self.finished_with_result.emit(False)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssessmentResultEditor()
    window.show()
    sys.exit(app.exec())
