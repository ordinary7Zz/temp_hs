from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QPointF, QRect, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap


@dataclass(frozen=True)
class LayerVisualConfig:
    spin_name: str
    filename: str
    fallback_color: str


class LayeredStructureRenderer:
    """Render stacked rectangular layers whose heights follow provided thickness values."""

    def __init__(
        self,
        base_dir: Path,
        configs: Sequence[LayerVisualConfig],
        default_size: QSize | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._configs = list(configs)
        self._config_by_spin = {cfg.spin_name: cfg for cfg in self._configs}
        self._default_size = default_size if default_size is not None else QSize(540, 140)
        self._textures: dict[str, QPixmap | None] = {}
        self._load_textures()

    def _load_textures(self) -> None:
        for cfg in self._configs:
            path = self._base_dir / cfg.filename
            pixmap = QPixmap(str(path)) if path.exists() else QPixmap()
            self._textures[cfg.spin_name] = pixmap if not pixmap.isNull() else None

    def render(
        self,
        layers: Sequence[tuple[str, float]],
        target_size: QSize | None = None,
    ) -> QPixmap | None:
        if not layers:
            return None
        total = sum(thickness for _, thickness in layers if thickness and thickness > 0)
        if total <= 0:
            return None
        size = self._effective_size(target_size)
        width = max(1, size.width())
        height = max(1, size.height())
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f6f6f6"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        scale = height / total
        y = 0
        separators: list[int] = []
        remaining = height

        for idx, (key, thickness) in enumerate(layers):
            if thickness <= 0:
                continue
            cfg = self._config_by_spin.get(key)
            if cfg is None:
                continue
            is_last = idx == len(layers) - 1
            if is_last:
                layer_height = remaining
            else:
                layer_height = max(1, int(round(thickness * scale)))
                min_remaining = remaining - (len(layers) - idx - 1)
                min_remaining = max(min_remaining, 1)
                layer_height = max(1, min(layer_height, min_remaining))
            rect = QRect(0, y, width, layer_height)
            texture = self._textures.get(key)
            if texture is not None and not texture.isNull():
                painter.drawTiledPixmap(rect, texture)
            else:
                painter.fillRect(rect, self._fallback_color(cfg))
            y += layer_height
            remaining = max(0, remaining - layer_height)
            if idx < len(layers) - 1:
                separators.append(y)

        self._draw_separators(painter, width, separators)
        self._draw_border(painter, width, height)
        painter.end()
        return pixmap

    def _effective_size(self, size: QSize | None) -> QSize:
        if size is None or size.isEmpty():
            return QSize(self._default_size)
        width = size.width() if size.width() > 0 else self._default_size.width()
        height = size.height() if size.height() > 0 else self._default_size.height()
        return QSize(width, height)

    @staticmethod
    def _draw_separators(painter: QPainter, width: int, positions: Sequence[int]) -> None:
        pen = QPen(QColor("#e9e9e9"))
        pen.setWidth(1)
        painter.setPen(pen)
        for pos in positions:
            painter.drawLine(1, pos, width - 2, pos)

    @staticmethod
    def _draw_border(painter: QPainter, width: int, height: int) -> None:
        pen = QPen(QColor("#4a4a4a"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(0, 0, width - 1, height - 1)

    @staticmethod
    def _fallback_color(cfg: LayerVisualConfig) -> QColor:
        color = QColor(cfg.fallback_color)
        if color.isValid():
            return color
        return QColor("#b0b0b0")


class ShelterStructureRenderer:
    """Render an arch-style shelter cross-section with optional base layers."""

    def __init__(
        self,
        base_dir: Path,
        arch_configs: Sequence[LayerVisualConfig],
        base_configs: Sequence[LayerVisualConfig] | None = None,
        default_size: QSize | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._arch_configs = list(arch_configs)
        self._base_configs = list(base_configs) if base_configs else []
        self._arch_config_map = {cfg.spin_name: cfg for cfg in self._arch_configs}
        self._base_config_map = {cfg.spin_name: cfg for cfg in self._base_configs}
        self._default_size = default_size if default_size is not None else QSize(640, 160)
        self._textures: dict[str, QPixmap | None] = {}
        self._load_textures()

    def _load_textures(self) -> None:
        for cfg in [*self._arch_configs, *self._base_configs]:
            path = self._base_dir / cfg.filename
            pixmap = QPixmap(str(path)) if path.exists() else QPixmap()
            self._textures[cfg.spin_name] = pixmap if not pixmap.isNull() else None

    def render(
        self,
        arch_layers: Sequence[tuple[str, float]],
        base_layers: Sequence[tuple[str, float]] | None = None,
        target_size: QSize | None = None,
    ) -> QPixmap | None:
        arch_sequence = [
            (self._arch_config_map[key], thickness)
            for key, thickness in arch_layers
            if thickness > 0 and key in self._arch_config_map
        ]
        if not arch_sequence:
            return None
        base_sequence: list[tuple[LayerVisualConfig, float]] = []
        if base_layers:
            base_sequence = [
                (self._base_config_map[key], thickness)
                for key, thickness in base_layers
                if thickness > 0 and key in self._base_config_map
            ]

        arch_total = sum(thickness for _, thickness in arch_sequence)
        base_total = sum(thickness for _, thickness in base_sequence)

        if arch_total <= 0:
            return None

        size = self._effective_size(target_size)
        width = max(1, size.width())
        height = max(1, size.height())

        top_margin = 10
        bottom_margin = 12
        side_margin = 32

        usable_height = max(1.0, height - top_margin - bottom_margin)
        total_units = arch_total + base_total
        scale_by_height = usable_height / max(total_units, 1.0)
        scale_by_width = ((width - 2 * side_margin) / 2) / arch_total
        scale = max(0.1, min(scale_by_height, scale_by_width))

        base_height = base_total * scale
        outer_radius = arch_total * scale
        if outer_radius <= 1.0:
            return None

        center_y = height - bottom_margin - base_height
        center = QPointF(width / 2.0, center_y)

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f5f7fb"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        max_allowed_width = max(20, width - side_margin)
        preferred_width = min(max_allowed_width, int(outer_radius * 2.2))
        base_width = max(int(outer_radius * 1.4), preferred_width)
        base_width = min(max_allowed_width, base_width)
        base_left = int((width - base_width) / 2)

        self._draw_base_layers(painter, base_left, base_width, center_y, base_sequence, scale)
        inner_radius = self._draw_arch_layers(painter, center, outer_radius, arch_sequence, scale)
        self._fill_interior(painter, center, inner_radius)
        self._draw_outline(painter, center, outer_radius, base_left, base_width)
        painter.end()
        return pixmap

    def _effective_size(self, size: QSize | None) -> QSize:
        if size is None or size.isEmpty():
            return QSize(self._default_size)
        width = size.width() if size.width() > 0 else self._default_size.width()
        height = size.height() if size.height() > 0 else self._default_size.height()
        return QSize(width, height)

    def _draw_base_layers(
        self,
        painter: QPainter,
        base_left: int,
        base_width: int,
        base_top: float,
        base_sequence: Sequence[tuple[LayerVisualConfig, float]],
        scale: float,
    ) -> None:
        if not base_sequence:
            return
        y = base_top
        for idx, (cfg, thickness) in enumerate(base_sequence):
            layer_height = thickness * scale
            if idx == len(base_sequence) - 1:
                rect_height = max(1, int(round(layer_height)))
            else:
                rect_height = max(1, int(round(layer_height)))
            rect = QRect(
                base_left,
                int(round(y)),
                base_width,
                rect_height,
            )
            self._fill_rect_with_texture(painter, rect, cfg)
            y += rect_height

    def _draw_arch_layers(
        self,
        painter: QPainter,
        center: QPointF,
        outer_radius: float,
        arch_sequence: Sequence[tuple[LayerVisualConfig, float]],
        scale: float,
    ) -> float:
        current_outer = outer_radius
        for cfg, thickness in arch_sequence:
            layer_height = thickness * scale
            inner_radius = max(0.5, current_outer - layer_height)
            path = self._semi_ring_path(center, current_outer, inner_radius)
            self._fill_path_with_texture(painter, path, cfg)
            current_outer = inner_radius
        return max(0.5, current_outer)

    def _fill_interior(self, painter: QPainter, center: QPointF, radius: float) -> None:
        rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        path = QPainterPath()
        path.moveTo(center.x() - radius, center.y())
        path.arcTo(rect, 180, -180)
        path.lineTo(center.x() + radius, center.y())
        path.closeSubpath()
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QColor("#fdfdfd"))
        painter.restore()

    def _draw_outline(
        self,
        painter: QPainter,
        center: QPointF,
        outer_radius: float,
        base_left: int,
        base_width: int,
    ) -> None:
        rect = QRectF(center.x() - outer_radius, center.y() - outer_radius, outer_radius * 2, outer_radius * 2)
        pen = QPen(QColor("#4a4a4a"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 16 * 180)
        painter.drawLine(base_left, int(round(center.y())), base_left + base_width, int(round(center.y())))

    def _fill_rect_with_texture(self, painter: QPainter, rect: QRect, cfg: LayerVisualConfig) -> None:
        texture = self._textures.get(cfg.spin_name)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        if texture is not None and not texture.isNull():
            painter.drawTiledPixmap(rect, texture)
        else:
            painter.fillRect(rect, QColor(cfg.fallback_color))
        painter.restore()

    def _fill_path_with_texture(self, painter: QPainter, path: QPainterPath, cfg: LayerVisualConfig) -> None:
        texture = self._textures.get(cfg.spin_name)
        painter.save()
        painter.setClipPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        bounding_rect = path.boundingRect().toRect()
        if texture is not None and not texture.isNull():
            painter.drawTiledPixmap(bounding_rect, texture)
        else:
            painter.fillPath(path, QColor(cfg.fallback_color))
        painter.restore()

    @staticmethod
    def _semi_ring_path(center: QPointF, outer_radius: float, inner_radius: float) -> QPainterPath:
        outer_rect = QRectF(center.x() - outer_radius, center.y() - outer_radius, outer_radius * 2, outer_radius * 2)
        inner_rect = QRectF(center.x() - inner_radius, center.y() - inner_radius, inner_radius * 2, inner_radius * 2)
        path = QPainterPath()
        path.moveTo(center.x() - outer_radius, center.y())
        path.arcTo(outer_rect, 180, -180)
        if inner_radius > 0.5:
            path.lineTo(center.x() + inner_radius, center.y())
            path.arcTo(inner_rect, 0, 180)
        else:
            path.lineTo(center.x(), center.y())
        path.closeSubpath()
        return path


class UndergroundStructureRenderer:
    """Render underground command-post layers with embedded facility boxes."""

    def __init__(
        self,
        base_dir: Path,
        configs: Sequence[LayerVisualConfig],
        facility_labels: Sequence[str] | None = None,
        default_size: QSize | None = None,
    ) -> None:
        self._base_dir = base_dir
        self._configs = list(configs)
        self._config_map = {cfg.spin_name: cfg for cfg in self._configs}
        self._facility_labels = list(facility_labels or [])
        self._default_size = default_size if default_size is not None else QSize(560, 150)
        self._textures: dict[str, QPixmap | None] = {}
        self._load_textures()

    def _load_textures(self) -> None:
        for cfg in self._configs:
            path = self._base_dir / cfg.filename
            pixmap = QPixmap(str(path)) if path.exists() else QPixmap()
            self._textures[cfg.spin_name] = pixmap if not pixmap.isNull() else None

    def render(self, layers: Sequence[tuple[str, float]], target_size: QSize | None = None) -> QPixmap | None:
        sequence = [
            (self._config_map[key], thickness)
            for key, thickness in layers
            if thickness > 0 and key in self._config_map
        ]
        if not sequence:
            return None
        total = sum(thickness for _, thickness in sequence)
        if total <= 0:
            return None

        size = self._effective_size(target_size)
        width = max(1, size.width())
        height = max(1, size.height())
        top_margin = 6
        bottom_margin = 10
        side_margin = 8
        usable_height = max(1, height - top_margin - bottom_margin)

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor("#f6f8fb"))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        scale = usable_height / total
        y = top_margin
        remaining = usable_height
        last_rect: QRect | None = None

        for idx, (cfg, thickness) in enumerate(sequence):
            is_last = idx == len(sequence) - 1
            desired_height = thickness * scale
            if is_last:
                layer_height = remaining
            else:
                min_remaining = remaining - (len(sequence) - idx - 1)
                min_remaining = max(min_remaining, 1)
                layer_height = max(1, min(int(round(desired_height)), min_remaining))
            rect = QRect(
                side_margin,
                int(round(y)),
                width - 2 * side_margin,
                max(1, int(round(layer_height))),
            )
            self._fill_rect_with_texture(painter, rect, cfg)
            y += rect.height()
            remaining = max(0, usable_height - (y - top_margin))
            last_rect = rect

        self._draw_facilities(painter, last_rect)
        border_pen = QPen(QColor("#4a4a4a"))
        border_pen.setWidth(2)
        painter.setPen(border_pen)
        painter.drawRect(side_margin // 2, top_margin // 2, width - side_margin, height - top_margin)
        painter.end()
        return pixmap

    def _effective_size(self, size: QSize | None) -> QSize:
        if size is None or size.isEmpty():
            return QSize(self._default_size)
        width = size.width() if size.width() > 0 else self._default_size.width()
        height = size.height() if size.height() > 0 else self._default_size.height()
        return QSize(width, height)

    def _fill_rect_with_texture(self, painter: QPainter, rect: QRect, cfg: LayerVisualConfig) -> None:
        texture = self._textures.get(cfg.spin_name)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        if texture is not None and not texture.isNull():
            painter.drawTiledPixmap(rect, texture)
        else:
            painter.fillRect(rect, QColor(cfg.fallback_color))
        painter.restore()

    def _draw_facilities(self, painter: QPainter, rect: QRect | None) -> None:
        if rect is None or not self._facility_labels:
            return
        count = len(self._facility_labels)
        gap = 10
        available_width = rect.width() - gap * (count + 1)
        if available_width <= 0:
            return
        box_width = max(20, int(available_width / count))
        box_height = max(14, rect.height() - 12)
        top = rect.bottom() - box_height - 4
        pen = QPen(QColor("#775b3a"))
        pen.setWidth(2)
        text_pen = QPen(QColor("#333333"))

        for idx, label in enumerate(self._facility_labels):
            left = rect.left() + gap + idx * (box_width + gap)
            box = QRect(left, top, box_width, box_height)
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillRect(box, QColor("#fdfbf5"))
            painter.setPen(pen)
            painter.drawRect(box)
            painter.setPen(text_pen)
            painter.drawText(box.adjusted(2, 2, -2, -2), Qt.AlignmentFlag.AlignCenter, label)
            painter.restore()
