"""
毁伤评估报告详情查看对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QTextEdit, QPushButton, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ReportDetailDialog(QDialog):
    """报告详情查看对话框"""

    def __init__(self, report, parent=None):
        super().__init__(parent)
        self.report = report
        self.setWindowTitle(f"报告详情 - {report.ReportCode}")
        self.resize(800, 600)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("毁伤评估报告")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 分隔线
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line1)

        # 基本信息组
        gb_basic = QGroupBox("基本信息")
        gb_basic_layout = QGridLayout()
        gb_basic_layout.setSpacing(10)

        self.lbl_code = self._create_info_label("")
        self.lbl_name = self._create_info_label("")
        self.lbl_damage_degree = self._create_info_label("")
        self.lbl_created_time = self._create_info_label("")

        gb_basic_layout.addWidget(self._create_title_label("报告编号:"), 0, 0)
        gb_basic_layout.addWidget(self.lbl_code, 0, 1)
        gb_basic_layout.addWidget(self._create_title_label("报告名称:"), 0, 2)
        gb_basic_layout.addWidget(self.lbl_name, 0, 3)

        gb_basic_layout.addWidget(self._create_title_label("毁伤等级:"), 1, 0)
        gb_basic_layout.addWidget(self.lbl_damage_degree, 1, 1)
        gb_basic_layout.addWidget(self._create_title_label("创建时间:"), 1, 2)
        gb_basic_layout.addWidget(self.lbl_created_time, 1, 3)

        gb_basic.setLayout(gb_basic_layout)
        layout.addWidget(gb_basic)

        # 关联信息组
        gb_association = QGroupBox("关联信息")
        gb_association_layout = QGridLayout()
        gb_association_layout.setSpacing(10)

        self.lbl_assessment_id = self._create_info_label("")
        self.lbl_scene_id = self._create_info_label("")
        self.lbl_parameter_id = self._create_info_label("")
        self.lbl_ammunition_id = self._create_info_label("")
        self.lbl_target_type = self._create_info_label("")
        self.lbl_target_id = self._create_info_label("")

        gb_association_layout.addWidget(self._create_title_label("评估ID:"), 0, 0)
        gb_association_layout.addWidget(self.lbl_assessment_id, 0, 1)
        gb_association_layout.addWidget(self._create_title_label("场景ID:"), 0, 2)
        gb_association_layout.addWidget(self.lbl_scene_id, 0, 3)

        gb_association_layout.addWidget(self._create_title_label("参数ID:"), 1, 0)
        gb_association_layout.addWidget(self.lbl_parameter_id, 1, 1)
        gb_association_layout.addWidget(self._create_title_label("弹药ID:"), 1, 2)
        gb_association_layout.addWidget(self.lbl_ammunition_id, 1, 3)

        gb_association_layout.addWidget(self._create_title_label("目标类型:"), 2, 0)
        gb_association_layout.addWidget(self.lbl_target_type, 2, 1)
        gb_association_layout.addWidget(self._create_title_label("目标ID:"), 2, 2)
        gb_association_layout.addWidget(self.lbl_target_id, 2, 3)

        gb_association.setLayout(gb_association_layout)
        layout.addWidget(gb_association)

        # 人员信息组
        gb_personnel = QGroupBox("人员信息")
        gb_personnel_layout = QGridLayout()
        gb_personnel_layout.setSpacing(10)

        self.lbl_creator = self._create_info_label("")
        self.lbl_reviewer = self._create_info_label("")

        gb_personnel_layout.addWidget(self._create_title_label("创建人ID:"), 0, 0)
        gb_personnel_layout.addWidget(self.lbl_creator, 0, 1)
        gb_personnel_layout.addWidget(self._create_title_label("审核人:"), 0, 2)
        gb_personnel_layout.addWidget(self.lbl_reviewer, 0, 3)

        gb_personnel.setLayout(gb_personnel_layout)
        layout.addWidget(gb_personnel)

        # 评估结论组
        gb_comment = QGroupBox("评估结论")
        gb_comment_layout = QVBoxLayout()

        self.text_comment = QTextEdit()
        self.text_comment.setReadOnly(True)
        self.text_comment.setMinimumHeight(150)
        self.text_comment.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 10px;
                font-size: 11pt;
            }
        """)

        gb_comment_layout.addWidget(self.text_comment)
        gb_comment.setLayout(gb_comment_layout)
        layout.addWidget(gb_comment)

        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_close = QPushButton("关闭")
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.close)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _create_title_label(self, text):
        """创建标题标签"""
        label = QLabel(text)
        font = QFont()
        font.setBold(True)
        label.setFont(font)
        return label

    def _create_info_label(self, text):
        """创建信息标签"""
        label = QLabel(text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def load_data(self):
        """加载报告数据"""
        report = self.report

        # 基本信息
        self.lbl_code.setText(report.ReportCode or "")
        self.lbl_name.setText(report.ReportName or "")

        # 毁伤等级（带颜色标识）
        damage_degree = report.DamageDegree or "未评级"
        degree_color = {
            "未达到轻度毁伤": "#1890ff",
            "轻度毁伤": "#52c41a",
            "中度毁伤": "#faad14",
            "重度毁伤": "#ff7a45",
            "完全摧毁": "#f5222d"
        }.get(damage_degree, "#666")
        self.lbl_damage_degree.setText(f'<span style="color: {degree_color}; font-weight: bold;">{damage_degree}</span>')

        # 创建时间
        created_time = report.CreatedTime.strftime('%Y-%m-%d %H:%M:%S') if report.CreatedTime else "未知"
        self.lbl_created_time.setText(created_time)

        # 关联信息
        self.lbl_assessment_id.setText(str(report.DAID) if report.DAID else "")
        self.lbl_scene_id.setText(str(report.DSID) if report.DSID else "")
        self.lbl_parameter_id.setText(str(report.DPID) if report.DPID else "")
        self.lbl_ammunition_id.setText(str(report.AMID) if report.AMID else "")

        # 目标类型
        target_type_map = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}
        target_type_name = target_type_map.get(report.TargetType, "未知")
        self.lbl_target_type.setText(target_type_name)

        self.lbl_target_id.setText(str(report.TargetID) if report.TargetID else "")

        # 人员信息
        self.lbl_creator.setText(str(report.Creator) if report.Creator else "")
        self.lbl_reviewer.setText(report.Reviewer or "")

        # 评估结论
        self.text_comment.setPlainText(report.Comment or "暂无评估结论")

