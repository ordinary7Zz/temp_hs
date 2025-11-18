from __future__ import annotations
from typing import Iterable, Protocol, Any, List, Dict
import csv, json, dataclasses, io


class Exporter(Protocol):
    def export(self, items: Iterable[Any]) -> bytes: ...


class CSVExporter:
    def __init__(self, field_order: List[str] | None = None) -> None:
        self.field_order = field_order

    def export(self, items: Iterable[Any]) -> bytes:
        rows: List[Dict[str, Any]] = []
        for obj in items:
            if dataclasses.is_dataclass(obj):
                row = dataclasses.asdict(obj)
            elif hasattr(obj, "__dict__"):
                row = dict(obj.__dict__)
            else:
                raise TypeError("Unsupported item type for CSV export")
            rows.append(row)
        if not rows:
            return b""
        fieldnames = self.field_order or list(rows[0].keys())
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in fieldnames})
        return buf.getvalue().encode("utf-8-sig")  # 使用 BOM 以便 Excel 正确识别


class JSONExporter:
    def export(self, items: Iterable[Any]) -> bytes:
        def to_obj(o: Any):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            if hasattr(o, "__dict__"):
                return dict(o.__dict__)
            return o

        payload = [to_obj(x) for x in items]
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
