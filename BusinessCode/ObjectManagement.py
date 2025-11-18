import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from UIs.Frm_ObjectiveManagement import Ui_Frm_ObjectiveManagement  # 导入自动生成的界面类

project_root = Path(__file__).parent.parent  # __file__是当前文件路径，parent是父目录
sys.path.append(str(project_root))

class ObjectiveManagementWindow(QMainWindow, Ui_Frm_ObjectiveManagement):
    def __init__(self):
        super().__init__()
        # 初始化界面（调用Ui_MainWindow的setupUi方法）
        self.setupUi(self)


if __name__ == "__main__":
    # 运行应用
    app = QApplication(sys.argv)
    window = ObjectiveManagementWindow()
    window.show()
    sys.exit(app.exec())