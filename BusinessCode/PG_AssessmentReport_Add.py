"""
毁伤评估报告添加/编辑窗口
"""
import sys
import os
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog

from UIs.Frm_PG_AssessmentReport_Add import Ui_Frm_PG_AssessmentReport_Add
from damage_models import AssessmentReport
from damage_models.sql_repository_dbhelper import AssessmentReportRepository, AssessmentResultRepository
from BusinessCode.AssessmentSelectorDialog import AssessmentSelectorDialog
from DBCode.DBHelper import DBHelper
from loguru import logger
from BusinessCode.UserContext import get_user


class AssessmentReportEditorMode(Enum):
    """编辑器模式"""
    Add = 1
    Edit = 2


class AssessmentReportEditor(QDialog):
    """毁伤评估报告编辑器"""

    finished_with_result = pyqtSignal(bool)

    def __init__(self, parent=None, mode: AssessmentReportEditorMode = AssessmentReportEditorMode.Add, edit_report_id: int = 0):
        super().__init__(parent)
        self.ui = Ui_Frm_PG_AssessmentReport_Add()
        self.ui.setupUi(self)

        self.mode = mode
        self.assessment = None
        self.edit_report_id = edit_report_id

        # 初始化UI组件
        self._init_comboboxes()
        self._set_default_values()
        self._wire_signals()

        # 加载数据（如果是编辑模式）
        if self.mode == AssessmentReportEditorMode.Edit:
            self.setWindowTitle("编辑毁伤评估报告")
            if edit_report_id == 0:
                QMessageBox.warning(self, "错误", "编辑模式下未传入报告ID")
                self.close()
                return
            try:
                self.load_data_from_db(edit_report_id)
            except Exception as e:
                logger.exception(e)
                QMessageBox.warning(self, "错误", f"加载数据失败：{e}")
                self.close()
                return
        else:
            self.setWindowTitle("添加毁伤评估报告")

        self.resize(580, 650)

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
        if self.mode == AssessmentReportEditorMode.Add:
            # 生成默认报告编号
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            self.ui.ed_report_code.setText(f"RPT_{timestamp}")

            # 设置占位符
            self.ui.ed_report_name.setPlaceholderText("例如：东部战区机场跑道毁伤评估报告")
            self.ui.ed_reviewer.setPlaceholderText("例如: 李参谋长")
            self.ui.te_comment.setPlaceholderText("请输入详细的评估结论，包括打击效果、修复时间预估、战役影响等...")

            # 设置创建人ID为默认值（当前登录用户ID，暂时设为1）
            self.current_user = get_user()
            self.ui.ed_creator_name.setText(self.current_user['UserName'])


    def _wire_signals(self):
        """绑定信号"""
        self.ui.btn_save.clicked.connect(self.on_save)
        self.ui.btn_cancel.clicked.connect(self.on_cancel)
        # 当选择评估ID后，自动填充关联信息
        self.ui.btn_select_assessment.clicked.connect(self.on_select_ammunition)

    def on_select_ammunition(self):
        """选择毁伤效能计算结果数据"""
        try:
            dialog = AssessmentSelectorDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                assessment = dialog.get_selected_assessment()
                if assessment:
                    # 填充信息
                    self.assessment = assessment
                    self.assessment_id = assessment.DAID
                    self.load_data_from_db_byDAID(self.assessment_id)
                    logger.info(f"已选择计算结果: {assessment.DAID}")
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"选择计算结果失败：{e}")

    def load_data_from_db_byDAID(self, damage_assessment_id: int):
        try:
            db = DBHelper()
            try:
                repo = AssessmentResultRepository(db)
                damage_assessment = repo.get_by_id(damage_assessment_id)

                if damage_assessment:
                    from damage_models.sql_repository_dbhelper import DamageSceneRepository, DamageParameterRepository
                    from am_models.sql_repository import SQLRepository as AmModelSQLRepository
                    from am_models.db import session_scope as am_session_scope
                    from target_model.sql_repository import SQLRepository as TargetModelSQLRepository
                    from target_model.db import session_scope as target_session_scope
                    from target_model.entities import AirportRunway, AircraftShelter, UndergroundCommandPost

                    scene_repo = DamageSceneRepository(db)
                    param_repo = DamageParameterRepository(db)
                    with am_session_scope() as session:
                        am_repo = AmModelSQLRepository(session)
                    with target_session_scope() as session:
                        target_repo = TargetModelSQLRepository(session)

                    self.assessment = damage_assessment
                    self.assessment_id = damage_assessment_id

                    scene_id = damage_assessment.DSID
                    param_id = damage_assessment.DPID
                    self.target_type = damage_assessment.TargetType
                    target_id = damage_assessment.TargetID
                    am_id = damage_assessment.AMID

                    self.scene = scene_repo.get_by_id(scene_id)
                    self.param = param_repo.get_by_id(param_id)
                    self.am = am_repo.get(am_id)
                    if self.target_type == 1:
                        self.target = target_repo.get(target_id, AirportRunway)
                        self.target_name = self.target.runway_name
                    elif self.target_type == 2:
                        self.target = target_repo.get(target_id, AircraftShelter)
                        self.target_name = self.target.shelter_name
                    elif self.target_type == 3:
                        self.target = target_repo.get(target_id, UndergroundCommandPost)
                        self.target_name = self.target.ucc_name

                    # 自动填充关联信息
                    self.ui.ed_scene_name.setText(self.scene.DSName)
                    self.ui.ed_parameter_id.setText(str(self.param.DPID))
                    self.ui.ed_ammunition_name.setText(self.am.am_name)
                    self.ui.ed_target_name.setText(self.target_name)
                    self.ui.ed_assessment_id.setText(str(damage_assessment_id))

                    # 设置目标类型
                    target_type_index = damage_assessment.TargetType - 1 if damage_assessment.TargetType > 0 else 0
                    self.ui.cmb_target_type.setCurrentIndex(target_type_index)

                    # 设置毁伤等级
                    if damage_assessment.DamageDegree:
                        degree_map = {"未达到轻度毁伤": 0, "轻度毁伤": 1, "中度毁伤": 2, "重度毁伤": 3, "完全摧毁": 4}
                        idx = degree_map.get(damage_assessment.DamageDegree, 3)
                        self.ui.cmb_damage_degree.setCurrentIndex(idx)

                    self.current_user = get_user()
                    self.ui.ed_creator_name.setText(self.current_user['UserName'])

                    logger.info(f"成功加载评估结果关联信息: DAID={damage_assessment_id}")
                else:
                    QMessageBox.warning(self, "警告", f"未找到ID为 {damage_assessment_id} 的评估结果")
            finally:
                db.close()
        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载关联信息失败：{e}")

    def load_data_from_db(self, report_id: int):
        """从数据库加载数据"""
        db = DBHelper()
        try:
            repo = AssessmentReportRepository(db)
            report = repo.get_by_id(report_id)

            if not report:
                raise Exception(f"未找到ID为 {report_id} 的报告")

            # 填充数据到界面
            self.ui.ed_report_code.setText(report.ReportCode)
            self.ui.ed_report_name.setText(report.ReportName)
            self.ui.ed_assessment_id.setText(str(report.ReportID))
            self.damage_assessment_ID = report.DAID
            self.load_data_from_db_byDAID(report.DAID)

            # 设置评估结论
            if report.Comment:
                self.ui.te_comment.setPlainText(report.Comment)

            self.creator = self.get_user_byID(report.Creator)
            # 设置人员信息
            if report.Creator:
                self.ui.ed_creator_name.setText(self.creator['UserName'])
            if report.Reviewer:
                self.ui.ed_reviewer.setText(report.Reviewer)

            logger.info(f"成功加载报告数据: ID={report_id}")
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            db.close()

    def on_save(self):
        """保存按钮点击"""
        try:
            # 验证必填字段
            if not self.ui.ed_report_code.text().strip():
                QMessageBox.warning(self, "验证失败", "报告编号不能为空")
                return
            if not self.ui.ed_report_name.text().strip():
                QMessageBox.warning(self, "验证失败", "报告名称不能为空")
                return
            if not self.assessment:
                QMessageBox.warning(self, "验证失败", "请选择毁伤评估结果")
                return

            # 构建实体对象
            report = AssessmentReport()
            # 设置基本信息
            report.ReportCode = self.ui.ed_report_code.text().strip()
            report.ReportName = self.ui.ed_report_name.text().strip()
            report.DAID = self.assessment_id

            # 设置关联信息
            if self.scene:
                report.DSID = self.scene.DSID
            if self.param:
                report.DPID = self.param.DPID
            if self.am:
                report.AMID = self.am.am_id
            if self.target:
                report.TargetID = self.target.id
                report.TargetType = self.target_type

            # 设置评估结果
            report.DamageDegree = self.ui.cmb_damage_degree.currentText()
            report.Comment = self.ui.te_comment.toPlainText().strip()

            # 设置人员信息
            if self.current_user:
                report.Creator = int(self.current_user['UID'])
            if self.ui.ed_reviewer.text().strip():
                report.Reviewer = self.ui.ed_reviewer.text().strip()

            # 保存到数据库
            db = DBHelper()
            try:
                repo = AssessmentReportRepository(db)

                if self.mode == AssessmentReportEditorMode.Add:
                    new_id = repo.add(report)
                    QMessageBox.information(self, "成功", f"添加成功，报告ID: {new_id}")
                else:
                    report.ReportID = self.edit_report_id
                    if repo.update(report):
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
        self.finished_with_result.ui.emit(False)
        self.close()

    def get_user_byID(self, user_id):
        db = DBHelper()
        try:
            query = "select UID, UserName FROM User_Info WHERE UID = %s"
            result = db.execute_query(query, (user_id,))
            if result:
                return result[0]
        finally:
            db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssessmentReportEditor()
    window.show()
    sys.exit(app.exec())

