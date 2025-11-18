import sys

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QPushButton, QHBoxLayout, QHeaderView
from UIs.Frm_ShelterModelManagement import Ui_Frm_ShelterModelManagement


class DYListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        cw = QWidget(self)
        self.setCentralWidget(cw)
        self.ui = Ui_Frm_ShelterModelManagement()
        self.ui.setupUi(cw)
        self.setWindowTitle("单机掩蔽库数据管理列表")
        setup_table(self)


def setup_table(self):
    tv = self.ui.tb_dan

    headers = ["名称/编号", "国家/地区", "基地/部队", "库容净长", "库容净宽", "库容净高", "顶层材料", "覆土层材料",
               "拱克材料", "操作"]
    model = QStandardItemModel(0, len(headers), tv)
    model.setHorizontalHeaderLabels(headers)
    tv.setModel(model)

    hh = tv.horizontalHeader()
    hh.setStretchLastSection(False)  # 不让最后一列自动吞空间
    for i in range(0, len(headers)):
        hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    tv.verticalHeader().setVisible(False)  # 隐藏行号（可选）
    tv.setSelectionBehavior(tv.SelectionBehavior.SelectRows)
    tv.setEditTriggers(tv.EditTrigger.NoEditTriggers)

    # 示例数据
    data = [
        ["隐蔽库-001", "中国", "西北防空旅", "45.0 m", "22.0 m", "9.5 m", "C40钢筋混凝土", "素土夯实层", "钢筋弧拱结构",
         "查看/编辑"],
        ["隐蔽库-002", "美国", "内华达空军基地", "50.0 m", "25.0 m", "10.0 m", "C45高强混凝土", "碎石砂层",
         "钢筋船形拱", "查看/编辑"],
        ["隐蔽库-003", "俄罗斯", "加里宁格勒防空团", "42.0 m", "20.0 m", "8.5 m", "C35钢筋混凝土", "黏土防护层",
         "钢拱加筋层", "查看/编辑"],
        ["隐蔽库-004", "法国", "土伦空军基地", "47.5 m", "23.5 m", "9.0 m", "C40钢筋混凝土", "砂砾土层",
         "钢筋加固船型拱", "查看/编辑"],
        ["隐蔽库-005", "印度", "德里防空司令部", "40.0 m", "19.0 m", "8.0 m", "C30钢筋混凝土", "混合土层", "钢结构拱顶",
         "查看/编辑"],
        ["隐蔽库-006", "以色列", "内盖夫空军基地", "46.0 m", "22.5 m", "9.2 m", "C45钢筋混凝土", "碎石+砂层",
         "复合加筋拱", "查看/编辑"],
        ["隐蔽库-007", "英国", "布莱兹诺顿空军基地", "44.0 m", "21.0 m", "8.8 m", "C40钢筋混凝土", "砂质粘土层",
         "钢筋弧形拱", "查看/编辑"],
        ["隐蔽库-008", "日本", "青森空军要塞", "41.0 m", "20.0 m", "8.5 m", "C35钢筋混凝土", "混合砂层",
         "钢拱混凝土复合体", "查看/编辑"],
        ["隐蔽库-009", "德国", "莱茵空军中心", "48.0 m", "24.0 m", "9.6 m", "C45钢筋混凝土", "碎石层", "高强钢拱壳",
         "查看/编辑"],
        ["隐蔽库-010", "阿联酋", "迪拜防空区", "52.0 m", "26.0 m", "10.5 m", "C50高强混凝土", "细砂+碎石层",
         "钢筋复合拱顶", "查看/编辑"],
    ]
    for row, rowData in enumerate(data):
        model.insertRow(row)
        for i, data in enumerate(rowData):
            model.setItem(row, i, QStandardItem(data))

        # 4) 操作列：为本行插入按钮
        _add_action_buttons(tv, model, row, len(headers) - 1)


def _add_action_buttons(tv, model, row, col):
    """
    在 (row, col) 放一个小容器，里面有“编辑/删除”两个按钮。
    注意：setIndexWidget 适合小中等数据量（几百行以内），
    大数据量建议用 delegate（见下方备注）。
    """
    w = QWidget(tv)
    layout = QHBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)

    btn_edit = QPushButton("编辑", w)
    btn_del = QPushButton("删除", w)
    # 行号捕获到闭包里（也可把主键 ID 作为属性设置到按钮上）
    btn_edit.clicked.connect(lambda _=False, r=row: _on_edit(tv, model, r))
    btn_del.clicked.connect(lambda _=False, r=row: _on_delete(tv, model, r))

    layout.addWidget(btn_edit)
    layout.addWidget(btn_del)
    w.setLayout(layout)

    index = model.index(row, col)
    tv.setIndexWidget(index, w)


def _on_edit(tv, model, row):
    # 示例：弹窗显示当前行数据；实际可打开编辑对话框
    id_ = model.index(row, 0).data()
    name = model.index(row, 1).data()
    cal = model.index(row, 2).data()
    typ = model.index(row, 3).data()
    QMessageBox.information(tv, "编辑",
                            f"准备编辑：\nID={id_}\n名称={name}\n口径={cal}\n类型={typ}")


def _on_delete(tv, model, row):
    id_ = model.index(row, 0).data()
    ok = QMessageBox.question(tv, "确认删除", f"确定删除 ID={id_} 这条记录吗？")
    if ok == QMessageBox.StandardButton.Yes:
        model.removeRow(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DYListWindow()
    window.show()
    sys.exit(app.exec())
