from __future__ import annotations
import base64
from dataclasses import dataclass
from typing import Optional, Tuple

from PyQt6.QtCore import Qt, QRect, QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QWidget, QLabel


@dataclass
class _ImageState:
    """内部状态：以 QPixmap 为核心（便于显示与处理），同时可保留原始二进制/格式信息。"""
    pixmap: QPixmap
    orig_bytes: Optional[bytes] = None  # 初始导入的二进制（如果有）
    orig_fmt: Optional[str] = None  # 可能的原始格式（'PNG'/'JPEG'等，大写）


class ImgHelper:
    """
    使用示例：
        # 读取文件 -> 压到 200KB -> 存库（二进制）
        h = ImgHelper.from_file(r'E:\pic\demo.jpg').resize(long_side=1280).compress_to_limit(200*1024, fmt="JPEG")
        blob = h.to_bytes(fmt="JPEG", quality=90)
        # INSERT INTO images(img_blob) VALUES (%s)  (pymysql 用 binary 参数)

        # 从库中读出 BLOB -> 显示
        h2 = ImgHelper.from_bytes(db_row.img_blob)
        h2.set_on_label(self.ui.lblPreview, scaled=True, keep_aspect=True)

        # 从 QLabel 当前显示回存（例如截屏保存回库）
        pm = self.ui.lblPreview.pixmap()
        if pm:
            h3 = ImgHelper.from_pixmap(pm).compress_to_limit(150*1024, fmt="JPEG")
            blob2 = h3.to_bytes(fmt="JPEG", quality=85)
    """

    # ---------- 构造 ----------
    def __init__(self, state: _ImageState):
        self._st = state

    @classmethod
    def from_file(cls, path: str) -> "ImgHelper":
        pm = QPixmap(path)
        return cls(_ImageState(pixmap=pm, orig_bytes=None, orig_fmt=_guess_format_from_suffix(path)))

    @classmethod
    def from_pixmap(cls, pm: QPixmap) -> "ImgHelper":
        return cls(_ImageState(pixmap=pm, orig_bytes=None, orig_fmt=None))

    @classmethod
    def from_bytes(cls, data: bytes) -> "ImgHelper":
        img = QImage()
        img.loadFromData(data)
        pm = QPixmap.fromImage(img)
        fmt = _guess_format_from_bytes(data)
        return cls(_ImageState(pixmap=pm, orig_bytes=data, orig_fmt=fmt))

    @classmethod
    def from_base64(cls, b64: str) -> "ImgHelper":
        data = base64.b64decode(b64) if b64 else b""
        return cls.from_bytes(data)

    @classmethod
    def from_widget(cls, widget: QWidget) -> "ImgHelper":
        pm = widget.grab()
        return cls.from_pixmap(pm)

    # ---------- 导出 ----------
    def to_pixmap(self) -> QPixmap:
        return self._st.pixmap

    def to_qimage(self) -> QImage:
        return self._st.pixmap.toImage()

    def to_bytes(self, fmt: Optional[str] = None, quality: Optional[int] = None) -> bytes:
        """
        输出二进制（默认使用 fmt 指定的编码；未指定时优先使用原始格式，再退回 PNG）。
        """
        img = self.to_qimage()
        use_fmt = (fmt or self._st.orig_fmt or "PNG").upper()

        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, use_fmt, quality if quality is not None else -1)
        data: QByteArray = buf.data()
        buf.close()
        return bytes(data)

    def to_base64(self, fmt: Optional[str] = None, quality: Optional[int] = None) -> str:
        return base64.b64encode(self.to_bytes(fmt=fmt, quality=quality)).decode("ascii")

    # ---------- UI ----------
    def set_on_label(self, label: QLabel, scaled: bool = True, keep_aspect: bool = True, smooth: bool = True):
        pm = self.to_pixmap()
        if pm.isNull():
            label.clear()
            return
        if scaled:
            target_size = label.size()
            if target_size.isEmpty() or target_size.width() <= 0 or target_size.height() <= 0:
                return
            pm = pm.scaled(
                target_size,
                Qt.AspectRatioMode.KeepAspectRatio if keep_aspect else Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation if smooth else Qt.TransformationMode.FastTransformation,
            )
        label.setPixmap(pm)

    # ---------- 处理：缩放 / 裁切 ----------
    def resize(self,
               width: Optional[int] = None,
               height: Optional[int] = None,
               long_side: Optional[int] = None,
               keep_aspect: bool = True,
               smooth: bool = True) -> "ImgHelper":
        """
        返回 self（便于链式调用）：
          - 指定 width/height（二者其一且 keep_aspect=True：等比）
          - 或指定 long_side：按最长边等比到该尺寸
        """
        pm = self._st.pixmap
        if pm.isNull():
            return self

        mode = Qt.TransformationMode.SmoothTransformation if smooth else Qt.TransformationMode.FastTransformation

        if long_side:
            w, h = pm.width(), pm.height()
            if w == 0 or h == 0:
                return self
            if w >= h:
                new_w, new_h = long_side, int(h * (long_side / w))
            else:
                new_w, new_h = int(w * (long_side / h)), long_side
            self._st.pixmap = pm.scaled(new_w, new_h,
                                        Qt.AspectRatioMode.KeepAspectRatio if keep_aspect else Qt.AspectRatioMode.IgnoreAspectRatio,
                                        mode)
            return self

        if width is None and height is None:
            return self

        if keep_aspect and (width is None or height is None):
            if width is not None:
                self._st.pixmap = pm.scaledToWidth(width, mode)
            else:
                self._st.pixmap = pm.scaledToHeight(height, mode)
            return self

        # 非等比缩放
        w = width if width is not None else pm.width()
        h = height if height is not None else pm.height()
        self._st.pixmap = pm.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio, mode)
        return self

    def crop(self, rect: QRect) -> "ImgHelper":
        pm = self._st.pixmap
        if pm.isNull():
            return self
        r = rect.intersected(QRect(0, 0, pm.width(), pm.height()))
        self._st.pixmap = pm.copy(r)
        return self

    # ---------- 压缩 ----------
    def compress_quality(self, fmt: str = "JPEG", quality: int = 85) -> "ImgHelper":
        """
        以指定质量导出后再重新加载为当前状态（便于继续链式处理）
        """
        b = self.to_bytes(fmt=fmt, quality=quality)
        self._st = ImgHelper.from_bytes(b)._st
        self._st.orig_fmt = fmt.upper()
        return self

    def compress_to_limit(self,
                          max_bytes: int = 200 * 1024,
                          fmt: str = "JPEG",
                          min_quality: int = 30,
                          step: int = 5,
                          min_long_side: int = 320) -> Tuple[int, int]:
        """
        将当前图像压到不超过 max_bytes：
        1) 先在当前尺寸下，quality 95→min_quality 逐步尝试
        2) 仍超限则按比例缩小（每次 0.8 倍），同时重置质量重试；不低于 min_long_side
        返回：(最终质量, 最终长边像素)
        """
        if self._st.pixmap.isNull():
            return -1, 0

        def _encode_size(q: int) -> Tuple[int, bytes]:
            data = self.to_bytes(fmt=fmt, quality=q)
            return len(data), data

        # 当前尺寸先降质量
        q = 95
        while q >= min_quality:
            size, data = _encode_size(q)
            if size <= max_bytes:
                self._st = ImgHelper.from_bytes(data)._st
                self._st.orig_fmt = fmt.upper()
                return q, max(self._st.pixmap.width(), self._st.pixmap.height())
            q -= step

        # 仍超限则缩图
        pm = self._st.pixmap
        long_side = max(pm.width(), pm.height())
        while long_side > min_long_side:
            long_side = int(long_side * 0.8)
            self.resize(long_side=long_side, keep_aspect=True)
            q = 90
            while q >= min_quality:
                size, data = _encode_size(q)
                if size <= max_bytes:
                    self._st = ImgHelper.from_bytes(data)._st
                    self._st.orig_fmt = fmt.upper()
                    return q, max(self._st.pixmap.width(), self._st.pixmap.height())
                q -= step

        # 实在压不下：用最低质量
        size, data = _encode_size(min_quality)
        self._st = ImgHelper.from_bytes(data)._st
        self._st.orig_fmt = fmt.upper()
        return min_quality, max(self._st.pixmap.width(), self._st.pixmap.height())


# ---------- 辅助 ----------
def _guess_format_from_suffix(path: str) -> Optional[str]:
    p = path.lower()
    if p.endswith(".jpg") or p.endswith(".jpeg"):
        return "JPEG"
    if p.endswith(".png"):
        return "PNG"
    if p.endswith(".bmp"):
        return "BMP"
    if p.endswith(".webp"):
        return "WEBP"
    if p.endswith(".gif"):
        return "GIF"
    return None


def _guess_format_from_bytes(data: bytes) -> Optional[str]:
    if not data or len(data) < 12:
        return None
    sig = data[:12]
    if sig.startswith(b"\xFF\xD8\xFF"):
        return "JPEG"
    if sig.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if sig.startswith(b"BM"):
        return "BMP"
    if sig[:4] == b"RIFF" and sig[8:12] == b"WEBP":
        return "WEBP"
    if sig[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    return None
