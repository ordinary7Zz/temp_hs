import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QGraphicsScene
)
from PyQt6.QtGui import QPixmap, QBrush

from UIs.Frm_Shelter_Add import  Ui_ShelterEditor


class ShelterEditor(QMainWindow, Ui_ShelterEditor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.adjustSize()
        self.setFixedSize(self.size())

        self.setWindowTitle("编辑单机掩蔽库数据")
        self.btn_choose_image.clicked.connect(self.on_choose_image)
        self.cmb_country.addItems(["中国", "美国", "俄罗斯", "法国", "英国", "德国", "其他"])

    def on_choose_image(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "选择图片", str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not fn:
            return
        pm = QPixmap(fn)
        if pm.isNull():
            QMessageBox.warning(self, "错误", "无法加载图片")
            return
        self.lbl_image.setPixmap(pm)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ShelterEditor()
    win.show()
    sys.exit(app.exec())
