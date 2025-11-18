"""
目标选择对话框
用于在毁伤场景中选择打击目标（跑道、掩体、地下指挥所）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLineEdit, QLabel, QMessageBox, QHeaderView, QComboBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from DBCode.DBHelper import DBHelper
from loguru import logger


class TargetSelectorDialog(QDialog):
    """目标选择对话框"""

    def __init__(self, parent=None, target_type: int = 1):
        """
        target_type: 1-跑道, 2-掩体, 3-地下目标
        """
        super().__init__(parent)
        self.target_type = target_type
        self.selected_target = None

        # 设置窗口标题
        type_names = {1: "机场跑道", 2: "单机掩蔽库", 3: "地下指挥所"}
        self.setWindowTitle(f"选择{type_names.get(target_type, '目标')}")
        self.resize(1000, 600)

        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("目标类型:"))

        self.cmb_target_type = QComboBox()
        self.cmb_target_type.addItems(["机场跑道", "单机掩蔽库", "地下指挥所"])
        self.cmb_target_type.setCurrentIndex(self.target_type - 1)
        self.cmb_target_type.currentIndexChanged.connect(self._on_type_changed)
        search_layout.addWidget(self.cmb_target_type)

        search_layout.addWidget(QLabel("搜索:"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("输入目标名称或代码...")
        search_layout.addWidget(self.ed_search)

        self.btn_search = QPushButton("搜索")
        self.btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self.btn_search)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 表格区域
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table_view.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table_view)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_select = QPushButton("选择")
        self.btn_select.clicked.connect(self._on_select)
        btn_layout.addWidget(self.btn_select)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _on_type_changed(self, index):
        """目标类型改变"""
        self.target_type = index + 1
        self._load_data()

    def _load_data(self, keyword: str = ""):
        """加载目标数据"""
        db = DBHelper()
        try:
            # 根据目标类型选择不同的表
            if self.target_type == 1:  # 跑道
                table_name = "Runway_Info"
                id_field = "RunwayID"
                code_field = "RunwayCode"
                name_field = "RunwayName"
                status_field = "RunwayStatus"
                extra_fields = "Country, Base, RLength, RWidth"
                headers = ["跑道ID", "跑道代码", "跑道名称", "国家", "基地", "长度(m)", "宽度(m)"]

            elif self.target_type == 2:  # 掩体
                table_name = "Shelter_Info"
                id_field = "ShelterID"
                code_field = "ShelterCode"
                name_field = "ShelterName"
                status_field = "ShelterStatus"
                extra_fields = "Country, Base, ShelterWidth, ShelterHeight, ShelterLength"
                headers = ["掩蔽库ID", "掩蔽库代码", "掩蔽库名称", "国家", "基地", "宽(m)", "高(m)", "长(m)"]

            else:  # 地下指挥所
                table_name = "UCC_Info"
                id_field = "UCCID"
                code_field = "UCCCode"
                name_field = "UCCName"
                status_field = "UCCStatus"
                extra_fields = "Country, Base, Location"
                headers = ["指挥所ID", "指挥所代码", "指挥所名称", "国家", "基地", "位置"]

            # 构建SQL查询
            if keyword:
                sql = f"""
                SELECT {id_field}, {code_field}, {name_field}, {extra_fields}
                FROM {table_name}
                WHERE {status_field} = 1
                AND ({code_field} LIKE %s OR {name_field} LIKE %s)
                ORDER BY {id_field} DESC
                """
                pattern = f'%{keyword}%'
                result = db.execute_query(sql, (pattern, pattern))
            else:
                sql = f"""
                SELECT {id_field}, {code_field}, {name_field}, {extra_fields}
                FROM {table_name}
                WHERE {status_field} = 1
                ORDER BY {id_field} DESC
                LIMIT 100
                """
                result = db.execute_query(sql)

            # 设置表格模型
            model = QStandardItemModel(0, len(headers))
            model.setHorizontalHeaderLabels(headers)

            if result:
                for row_data in result:
                    row = []
                    for key in row_data.keys():
                        value = row_data[key]
                        row.append(QStandardItem(str(value) if value is not None else ''))
                    model.appendRow(row)

            self.table_view.setModel(model)

            # 调整列宽
            header = self.table_view.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载目标数据失败：{e}")
        finally:
            db.close()

    def _on_search(self):
        """搜索按钮点击"""
        keyword = self.ed_search.text().strip()
        self._load_data(keyword)

    def _on_row_double_clicked(self, index):
        """双击行事件"""
        self._on_select()

    def _on_select(self):
        """选择按钮点击"""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "提示", "请先选择一条目标记录")
            return

        # 获取选中行的目标ID
        row = selection.currentIndex().row()
        model = self.table_view.model()
        target_id = int(model.item(row, 0).text())

        # 从数据库查询完整的目标信息
        db = DBHelper()
        try:
            # 根据目标类型查询不同的表
            if self.target_type == 1:  # 机场跑道
                sql = """
                SELECT RunwayID, RunwayCode, RunwayName, Country, Base, 
                       RLength, RWidth, PCCSCThick, PCCSCStrength, PCCSCFlexural,
                       CTBCThick, GCSSThick, CSThick
                FROM Runway_Info 
                WHERE RunwayID = %s
                """
                result = db.execute_query(sql, (target_id,))
                if result and len(result) > 0:
                    data = result[0]
                    self.selected_target = {
                        'TargetType': 1,
                        'TargetID': data.get('RunwayID'),
                        'TargetCode': data.get('RunwayCode', ''),
                        'TargetName': data.get('RunwayName', ''),
                        'Country': data.get('Country', ''),
                        'Base': data.get('Base', ''),
                        'RLength': data.get('RLength'),
                        'RWidth': data.get('RWidth'),
                        'PCCSCThick': data.get('PCCSCThick'),
                        'PCCSCStrength': data.get('PCCSCStrength'),
                        'PCCSCFlexural': data.get('PCCSCFlexural'),
                        'CTBCThick': data.get('CTBCThick'),
                        'GCSSThick': data.get('GCSSThick'),
                        'CSThick': data.get('CSThick'),
                    }

            elif self.target_type == 2:  # 单机掩蔽库
                sql = """
                SELECT ShelterID, ShelterCode, ShelterName, Country, Base,
                       ShelterWidth, ShelterHeight, ShelterLength,
                       CaveWidth, CaveHeight, StructuralForm
                FROM Shelter_Info 
                WHERE ShelterID = %s
                """
                result = db.execute_query(sql, (target_id,))
                if result and len(result) > 0:
                    data = result[0]
                    self.selected_target = {
                        'TargetType': 2,
                        'TargetID': data.get('ShelterID'),
                        'TargetCode': data.get('ShelterCode', ''),
                        'TargetName': data.get('ShelterName', ''),
                        'Country': data.get('Country', ''),
                        'Base': data.get('Base', ''),
                        'ShelterWidth': data.get('ShelterWidth'),
                        'ShelterHeight': data.get('ShelterHeight'),
                        'ShelterLength': data.get('ShelterLength'),
                        'CaveWidth': data.get('CaveWidth'),
                        'CaveHeight': data.get('CaveHeight'),
                        'StructuralForm': data.get('StructuralForm')
                    }

            else:  # 地下指挥所
                sql = """
                SELECT UCCID, UCCCode, UCCName, Country, Base, Location,
                       RockLayerMaterials, RockLayerThick, RockLayerStrength, 
                       UCCWallMaterials, UCCWallThick, UCCWallStrength, 
                       UCCWidth, UCCLength, UCCHeight
                FROM UCC_Info 
                WHERE UCCID = %s
                """
                result = db.execute_query(sql, (target_id,))
                if result and len(result) > 0:
                    data = result[0]
                    self.selected_target = {
                        'TargetType': 3,
                        'TargetID': data.get('UCCID'),
                        'TargetCode': data.get('UCCCode', ''),
                        'TargetName': data.get('UCCName', ''),
                        'Country': data.get('Country', ''),
                        'Base': data.get('Base', ''),
                        'Location': data.get('Location', ''),
                        'RockLayerMaterials': data.get('RockLayerMaterials'),
                        'RockLayerThick': data.get('RockLayerThick'),
                        'RockLayerStrength': data.get('RockLayerStrength'),
                        'UCCWallMaterials': data.get('UCCWallMaterials'),
                        'UCCWallThick': data.get('UCCWallThick'),
                        'UCCWallStrength': data.get('UCCWallStrength'),
                        'UCCWidth': data.get('UCCWidth'),
                        'UCCLength': data.get('UCCLength'),
                        'UCCHeight': data.get('UCCHeight'),
                    }

            if self.selected_target:
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "无法获取目标详细信息")

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"查询目标信息失败：{e}")
        finally:
            db.close()

    def get_selected_target(self):
        """获取选中的目标信息"""
        return self.selected_target


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = TargetSelectorDialog(target_type=1)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        target = dialog.get_selected_target()
        print("选中的目标:", target)
"""
弹药选择对话框
用于在毁伤场景中选择弹药
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLineEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from DBCode.DBHelper import DBHelper
from loguru import logger


class AmmunitionSelectorDialog(QDialog):
    """弹药选择对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择弹药")
        self.resize(1000, 600)

        self.selected_ammunition = None  # 选中的弹药信息
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索弹药:"))
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("输入弹药名称或型号...")
        search_layout.addWidget(self.ed_search)

        self.btn_search = QPushButton("搜索")
        self.btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self.btn_search)

        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 表格区域
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table_view.doubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table_view)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_select = QPushButton("选择")
        self.btn_select.clicked.connect(self._on_select)
        btn_layout.addWidget(self.btn_select)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _load_data(self, keyword: str = ""):
        """加载弹药数据"""
        db = DBHelper()
        try:
            if keyword:
                sql = """
                SELECT AMID, AMName, AMNameCN, AMType, AMModel, Country, 
                       WarheadType, WarheadName, ChargeAmount
                FROM Ammunition_Info 
                WHERE AMStatus = 1 
                AND (AMName LIKE %s OR AMNameCN LIKE %s OR AMModel LIKE %s)
                ORDER BY AMID DESC
                """
                pattern = f'%{keyword}%'
                result = db.execute_query(sql, (pattern, pattern, pattern))
            else:
                sql = """
                SELECT AMID, AMName, AMNameCN, AMType, AMModel, Country, 
                       WarheadType, WarheadName, ChargeAmount
                FROM Ammunition_Info 
                WHERE AMStatus = 1
                ORDER BY AMID DESC
                LIMIT 100
                """
                result = db.execute_query(sql)

            # 设置表格模型
            headers = ["弹药ID", "官方名称", "中文名称", "弹药类型", "弹药型号",
                      "国家", "战斗部类型", "战斗部名称", "装药量(kg)"]

            model = QStandardItemModel(0, len(headers))
            model.setHorizontalHeaderLabels(headers)

            if result:
                for row_data in result:
                    row = []
                    row.append(QStandardItem(str(row_data.get('AMID', ''))))
                    row.append(QStandardItem(row_data.get('AMName', '')))
                    row.append(QStandardItem(row_data.get('AMNameCN', '')))
                    row.append(QStandardItem(row_data.get('AMType', '')))
                    row.append(QStandardItem(row_data.get('AMModel', '')))
                    row.append(QStandardItem(row_data.get('Country', '')))
                    row.append(QStandardItem(row_data.get('WarheadType', '')))
                    row.append(QStandardItem(row_data.get('WarheadName', '')))
                    row.append(QStandardItem(str(row_data.get('ChargeAmount', ''))))
                    model.appendRow(row)

            self.table_view.setModel(model)

            # 调整列宽
            header = self.table_view.horizontalHeader()
            for i in range(len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        except Exception as e:
            logger.exception(e)
            QMessageBox.warning(self, "错误", f"加载弹药数据失败：{e}")
        finally:
            db.close()

    def _on_search(self):
        """搜索按钮点击"""
        keyword = self.ed_search.text().strip()
        self._load_data(keyword)

    def _on_row_double_clicked(self, index):
        """双击行事件"""
        self._on_select()

    def _on_select(self):
        """选择按钮点击"""
        selection = self.table_view.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "提示", "请先选择一条弹药记录")
            return

        # 获取选中行的数据
        row = selection.currentIndex().row()
        model = self.table_view.model()

        self.selected_ammunition = {
            'AMID': int(model.item(row, 0).text()),
            'AMName': model.item(row, 1).text(),
            'AMNameCN': model.item(row, 2).text(),
            'AMType': model.item(row, 3).text(),
            'AMModel': model.item(row, 4).text(),
            'AMCode': model.item(row, 4).text(),  # 使用型号作为代码
        }

        self.accept()

    def get_selected_ammunition(self):
        """获取选中的弹药信息"""
        return self.selected_ammunition


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = AmmunitionSelectorDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        ammo = dialog.get_selected_ammunition()
        print("选中的弹药:", ammo)

