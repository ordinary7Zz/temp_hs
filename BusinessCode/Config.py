# config.py
from __future__ import annotations
import os
from pathlib import Path
from configparser import ConfigParser, NoSectionError, NoOptionError
from typing import Dict, Tuple, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QWidget, QLineEdit, QFormLayout, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox

CONFIG_DIR = Path.home() / ".hs_2025"  # 或者当前目录Path(".")
CONFIG_PATH = CONFIG_DIR / "config.ini"

# 首次运行标识文件名
FIRST_RUN_MARK = ".first_run_done"
FIRST_RUN_MARK_PATH = CONFIG_DIR / FIRST_RUN_MARK

SECTION_MYSQL = "mysql"

_DEFAULTS = {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "3306",
    "DB_USER": "root",
    "DB_PASS": "123456",
    "DB_NAME": "damassessment_db",
}


def is_first_run(create_marker: bool = False) -> bool:
    """
    判断是否为首次打开软件：
    - 若 CONFIG_DIR 下不存在标识文件，则视为首次运行（返回 True）
    - 当 create_marker=True 且判定为首次运行时，会自动创建标识文件
    """
    try:
        if FIRST_RUN_MARK_PATH.exists():
            return False
        # 不存在 => 首次运行
        if create_marker:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            # 原子写入（尽量避免并发竞争）
            FIRST_RUN_MARK_PATH.write_text("ok", encoding="utf-8")
        return True
    except Exception:
        # 任何异常都不阻塞软件启动，保守按“首次”处理
        return True


def mark_first_run_done() -> None:
    """
    主动写入首次运行标识。适用于你在完成初始化（如引导向导、首次配置）后再调用。
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    FIRST_RUN_MARK_PATH.write_text("ok", encoding="utf-8")


def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, str]:
    """读取配置（不存在则用默认值并写入文件）。"""
    cfg = ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(CONFIG_PATH, encoding="utf-8")
    if not cfg.has_section(SECTION_MYSQL):
        cfg.add_section(SECTION_MYSQL)
    # 合并默认值
    for k, v in _DEFAULTS.items():
        if not cfg.has_option(SECTION_MYSQL, k):
            cfg.set(SECTION_MYSQL, k, v)
    _ensure_dir(CONFIG_PATH)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)
    # 返回 dict
    return {k: cfg.get(SECTION_MYSQL, k) for k in _DEFAULTS.keys()}


def save_config(values: Dict[str, str]) -> None:
    """写入配置（仅 mysql 节）。"""
    cfg = ConfigParser()
    if CONFIG_PATH.exists():
        cfg.read(CONFIG_PATH, encoding="utf-8")
    if not cfg.has_section(SECTION_MYSQL):
        cfg.add_section(SECTION_MYSQL)
    for k in _DEFAULTS.keys():
        if k in values and values[k] is not None:
            cfg.set(SECTION_MYSQL, k, str(values[k]))
    _ensure_dir(CONFIG_PATH)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cfg.write(f)


def validate_config(values: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """基础校验：host 非空、port 为 1-65535、user 非空、db 名非空。"""
    host = (values.get("DB_HOST") or "").strip()
    if not host:
        return False, "DB_HOST 不能为空"
    port = values.get("DB_PORT", "").strip()
    if not port.isdigit():
        return False, "DB_PORT 必须是数字"
    p = int(port)
    if not (1 <= p <= 65535):
        return False, "DB_PORT 必须在 1~65535 之间"
    user = (values.get("DB_USER") or "").strip()
    if not user:
        return False, "DB_USER 不能为空"
    db = (values.get("DB_NAME") or "").strip()
    if not db:
        return False, "DB_NAME 不能为空"
    return True, None


def get_sqlalchemy_url(values: Dict[str, str]) -> str:
    """生成 SQLAlchemy MySQL 连接串（pymysql 驱动为例）。"""
    host = values["DB_HOST"]
    port = int(values["DB_PORT"])
    user = values["DB_USER"]
    pwd = values.get("DB_PASS", "")
    db = values["DB_NAME"]
    # 注意：若用户名/密码有特殊字符，可在此进行 urlencode
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"


# config.py
from typing import Tuple, Dict, Optional


def test_mysql_connection(values: Dict[str, str],
                          check_db_exists: bool = True,
                          try_use_db: bool = True) -> Tuple[bool, str]:
    """
    测试到 MySQL 的连接，并（可选）检测 DB_NAME 是否存在。
    - check_db_exists=True 时，会查询 information_schema.SCHEMATA 判断库是否存在
    - try_use_db=True 时，会再执行一次 `SELECT 1`/`USE <db>` 验证当前用户是否能访问该库
    """
    try:
        import pymysql
    except Exception:
        return False, "未安装 pymysql，请先安装：pip install pymysql"

    ok, err = validate_config(values)
    if not ok:
        return False, err or "配置不合法"

    host = values["DB_HOST"].strip()
    port = int(values["DB_PORT"])
    user = values["DB_USER"].strip()
    pwd = values.get("DB_PASS", "")
    db = values["DB_NAME"].strip()

    # 1) 先连服务器（不指定 database，避免库不存在时直接报错）
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=pwd,
            charset="utf8mb4", connect_timeout=5,
            read_timeout=5, write_timeout=5,
        )
    except Exception as e:
        return False, f"无法连接到 MySQL 服务器：{e}"

    try:
        with conn.cursor() as cur:
            # 2) 检查库是否存在
            if check_db_exists:
                cur.execute(
                    "SELECT 1 FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s",
                    (db,)
                )
                row = cur.fetchone()
                if not row:
                    return False, f"数据库不存在：{db}"

            # 3) （可选）验证对该库的访问权限
            if try_use_db:
                # 对部分受限账号，直接 USE 可能被拒绝；兼容两种方式
                try:
                    cur.execute(f"USE `{db}`")
                    cur.execute("SELECT 1")
                    _ = cur.fetchone()
                except Exception as e:
                    return False, f"已连接服务器，但无法访问数据库 `{db}`：{e}"

        return True, "连接成功，数据库存在且可访问"
    finally:
        try:
            conn.close()
        except Exception:
            pass


class ConfigEditorDialog(QDialog):
    configSaved = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Mysql数据库配置")
        self.setMinimumWidth(420)

        self.ed_host = QLineEdit()
        self.ed_port = QLineEdit()
        self.ed_user = QLineEdit()
        self.ed_pass = QLineEdit()
        self.ed_name = QLineEdit()

        self.ed_port.setValidator(QIntValidator(1, 65535, self))
        self.ed_pass.setEchoMode(QLineEdit.EchoMode.Password)

        form = QFormLayout()
        form.addRow("主机名：", self.ed_host)
        form.addRow("端口：", self.ed_port)
        form.addRow("用户名：", self.ed_user)
        form.addRow("密码：", self.ed_pass)
        form.addRow("数据库名：", self.ed_name)

        # 底部按钮
        self.btn_test = QPushButton("测试连接")
        self.btn_save = QPushButton("保存")
        self.btn_cancel = QPushButton("取消")
        btns = QHBoxLayout()
        btns.addWidget(self.btn_test)
        btns.addStretch(1)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addLayout(btns)

        self.btn_test.clicked.connect(self._on_test)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_cancel.clicked.connect(self.reject)

        # 载入现有配置
        self._load_values()

    def _load_values(self):
        cfg = load_config()
        self.ed_host.setText(cfg.get("DB_HOST", ""))
        self.ed_port.setText(cfg.get("DB_PORT", "3306"))
        self.ed_user.setText(cfg.get("DB_USER", ""))
        self.ed_pass.setText(cfg.get("DB_PASS", ""))
        self.ed_name.setText(cfg.get("DB_NAME", ""))

    def _collect(self) -> Dict[str, str]:
        return {
            "DB_HOST": self.ed_host.text().strip(),
            "DB_PORT": self.ed_port.text().strip(),
            "DB_USER": self.ed_user.text().strip(),
            "DB_PASS": self.ed_pass.text(),  # 密码允许空与空格
            "DB_NAME": self.ed_name.text().strip(),
        }

    def _on_test(self):
        values = self._collect()
        ok, msg = test_mysql_connection(values)
        if ok:
            QMessageBox.information(self, "测试连接", msg)
        else:
            QMessageBox.warning(self, "测试连接", msg)

    def _on_save(self):
        values = self._collect()
        ok, err = validate_config(values)
        if not ok:
            QMessageBox.warning(self, "校验失败", err or "配置不合法")
            return
        try:
            save_config(values)
            self.configSaved.emit(values)
            QMessageBox.information(self, "保存成功", f"配置已保存到{CONFIG_PATH}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))
