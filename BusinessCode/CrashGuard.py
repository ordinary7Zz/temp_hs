# CrashGuard.py
from __future__ import annotations
import os, sys, time, logging, traceback, threading, asyncio, warnings, platform, signal
from logging.handlers import RotatingFileHandler

import loguru

LOG_DIR = os.path.join(os.path.expanduser("~"), ".hs_2025", "logs")
LOG_FILE = os.path.join(LOG_DIR, "crash.log")
MAX_LOG_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

_logger: loguru.Logger | None = None


def _ensure_logger() -> logging.Logger:
    global _logger
    if _logger:
        return _logger
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger("crashguard")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
        # 控制台可选
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        logger.addHandler(sh)
    _logger = logger
    return logger


def _fmt_crash(prefix: str, exc: BaseException | None, tb=None, extra: dict | None = None) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append(f"{prefix} @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"PID={os.getpid()}  Python={sys.version.split()[0]}  Platform={platform.platform()}")
    lines.append(f"Executable={sys.executable}  CWD={os.getcwd()}")
    if extra:
        for k, v in extra.items():
            lines.append(f"{k}: {v}")
    if exc is not None:
        if tb is None:
            tb = exc.__traceback__
        lines.append("Exception: " + repr(exc))
        lines.extend(traceback.format_exception(type(exc), exc, tb))
    return "\n".join(lines)


# ---- sys.excepthook：主线程未捕获异常 ----
def _excepthook(exc_type, exc, tb):
    logger = _ensure_logger()
    logger.critical(_fmt_crash("UNCAUGHT EXCEPTION (main thread)", exc, tb))
    # 对 GUI 程序：避免解释器直接退出时静默
    try:
        from PyQt6.QtWidgets import QMessageBox, QApplication
        app = QApplication.instance()
        if app is not None:
            QMessageBox.critical(None, "程序异常", f"{exc!r}\n崩溃日志已写入：{LOG_FILE}")
    except Exception:
        pass


# ---- threading.excepthook：子线程未捕获异常（Py3.8+） ----
def _threading_excepthook(args: threading.ExceptHookArgs):
    logger = _ensure_logger()
    extra = {"thread_name": args.thread.name}
    logger.critical(_fmt_crash("UNCAUGHT EXCEPTION (thread)", args.exc_value, args.exc_traceback, extra))
    # 可选：这里不要弹窗，避免线程环境 UI 冲突


# ---- sys.unraisablehook：如 __del__ 等环境的无法抛出的异常 ----
def _unraisablehook(unraisable: sys.UnraisableHookArgs):
    logger = _ensure_logger()
    extra = {"object": repr(unraisable.object)}
    logger.error(_fmt_crash("UNRAISABLE EXCEPTION", unraisable.exc_value, unraisable.exc_traceback, extra))


# ---- asyncio：事件循环的异常/未处理任务 ----
def _asyncio_exception_handler(loop: asyncio.AbstractEventLoop, context: dict):
    logger = _ensure_logger()
    msg = context.get("message", "asyncio exception")
    exc = context.get("exception")
    tb = exc.__traceback__ if exc else None
    logger.error(_fmt_crash(f"ASYNCIO ERROR: {msg}", exc, tb))


# ---- Qt：把 Qt 自己的 qDebug/qWarning/qCritical 也落盘（可选） ----
def _install_qt_message_handler():
    try:
        from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
        def _qt_handler(mode, context, message):
            logger = _ensure_logger()
            text = f"Qt[{mode}] {context.file}:{context.line} {message}"
            if mode in (QtMsgType.QtFatalMsg, QtMsgType.QtCriticalMsg):
                logger.error(text)
            else:
                pass

        qInstallMessageHandler(_qt_handler)
    except Exception:
        pass


# ---- warnings 统一导入 logging ----
def _install_warnings_to_logging():
    logging.captureWarnings(True)
    warnings.simplefilter("default")


# ---- faulthandler：记录崩溃（SIGSEGV等）堆栈到文件 ----
def _install_faulthandler():
    try:
        import faulthandler
        f = open(os.path.join(LOG_DIR, "fault.log"), "a", encoding="utf-8")
        faulthandler.enable(file=f, all_threads=True)
    except Exception:
        pass


# ---- 处理 SIGTERM/SIGINT，优雅退出并落日志（可选） ----
def _install_signals():
    logger = _ensure_logger()

    def _handler(sig, frame):
        logger.info(f"Received signal: {signal.Signals(sig).name}, exiting.")
        # 这里可以做清理
        sys.exit(0 if sig in (signal.SIGINT, signal.SIGTERM) else 1)

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, _handler)
        except Exception:
            pass


def install_crash_guard(*, for_qt: bool = True, set_asyncio: bool = True):
    """
    在程序入口调用：install_crash_guard()
    """
    _ensure_logger()

    # 主线程/子线程/不可抛异常
    sys.excepthook = _excepthook
    threading.excepthook = _threading_excepthook  # type: ignore[attr-defined]
    sys.unraisablehook = _unraisablehook

    # asyncio
    if set_asyncio:
        try:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(_asyncio_exception_handler)
        except Exception:
            pass

    # Qt 消息
    if for_qt:
        _install_qt_message_handler()

    _install_warnings_to_logging()
    _install_faulthandler()
    _install_signals()


def _close_faulthandler():
    """关闭 faulthandler 及文件句柄（幂等）。"""
    global _FAULT_FH
    try:
        import faulthandler
        try:
            faulthandler.disable()
        except Exception:
            pass
    except Exception:
        pass
    if _FAULT_FH:
        try:
            _FAULT_FH.flush()
            _FAULT_FH.close()
        except Exception:
            pass
        _FAULT_FH = None


def shutdown_crash_guard():
    try:
        _close_faulthandler()
    except Exception:
        pass
