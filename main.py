import sys
from pathlib import Path
from loguru import logger
from PyQt6.QtWidgets import QApplication, QMessageBox

from BusinessCode.Config import ConfigEditorDialog, is_first_run, mark_first_run_done
from DBCode.init_database import initialize_database
from BusinessCode.Login import LoginWindow, load_skin

if __name__ == "__main__":
    # 初始化日志
    logger.add("logs/app.log", level="DEBUG")

    app = QApplication(sys.argv)
    load_skin(app)

    # 首次强制检查 / 编辑
    try:
        if is_first_run():
            logger.info("首次打开软件，打开数据库信息配置界面")
            dlg = ConfigEditorDialog()
            dlg.configSaved.connect(mark_first_run_done)
            if dlg.exec() != dlg.accepted:
                pass
    except Exception as e:
        logger.exception(e)
        exit(-1)

    window = LoginWindow()

    # 初始化数据库
    try:
        initialize_database()
    except Exception as e:
        logger.exception(e)
        QMessageBox.critical(window, "Error", f"初始化数据库失败:{e}")
        sys.exit(-1)

    window.show()

    sys.exit(app.exec())
