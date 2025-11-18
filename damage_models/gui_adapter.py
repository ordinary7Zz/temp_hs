"""
毁伤数据GUI适配器
处理UI数据与实体的转换
"""
from __future__ import annotations
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, Optional
from .entities import DamageScene, DamageParameter


# -------- Helpers --------
def _to_int_or_none(x: Any) -> Optional[int]:
    """转换为整数或None"""
    if x is None or x == "":
        return None
    try:
        return int(x)
    except (ValueError, TypeError):
        return None


def _to_float_or_none(x: Any) -> Optional[float]:
    """转换为浮点数或None"""
    if x is None or x == "":
        return None
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def _to_str_or_none(x: Any) -> Optional[str]:
    """转换为字符串或None"""
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None


def _to_datetime_or_none(x: Any) -> Optional[datetime]:
    """转换为datetime或None"""
    if x is None or x == "":
        return None
    if isinstance(x, datetime):
        return x
    # 可以添加更多的日期格式解析
    return None


# -------- DamageScene Adapter --------
class DamageSceneGUIAdapter:
    """毁伤场景GUI适配器"""
    
    @staticmethod
    def from_gui(data: Dict[str, Any]) -> DamageScene:
        """从GUI数据创建实体"""
        return DamageScene(
            DSID=_to_int_or_none(data.get('DSID')),
            DSCode=str(data.get('DSCode', '')),
            DSName=str(data.get('DSName', '')),
            DSOffensive=_to_str_or_none(data.get('DSOffensive')),
            DSDefensive=_to_str_or_none(data.get('DSDefensive')),
            DSBattle=_to_str_or_none(data.get('DSBattle')),
            AMID=int(data.get('AMID', 0)),
            AMCode=str(data.get('AMCode', '')),
            TargetType=int(data.get('TargetType', 0)),
            TargetID=int(data.get('TargetID', 0)),
            TargetCode=str(data.get('TargetCode', '')),
            DSStatus=_to_int_or_none(data.get('DSStatus')),
            CreatedTime=_to_datetime_or_none(data.get('CreatedTime')),
            UpdatedTime=_to_datetime_or_none(data.get('UpdatedTime'))
        )
    
    @staticmethod
    def to_gui(scene: DamageScene) -> Dict[str, Any]:
        """转换为GUI数据"""
        data = asdict(scene)
        # 处理datetime对象
        for key in ['CreatedTime', 'UpdatedTime']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].strftime('%Y-%m-%d %H:%M:%S')
        return data
    
    @staticmethod
    def to_table_row(scene: DamageScene) -> list:
        """转换为表格行数据"""
        return [
            scene.DSID,
            scene.DSCode,
            scene.DSName,
            scene.DSOffensive or '',
            scene.DSDefensive or '',
            scene.DSBattle or '',
            scene.AMID,
            scene.AMCode,
            scene.TargetType,
            scene.TargetID,
            scene.TargetCode,
            scene.DSStatus,
            scene.CreatedTime.strftime('%Y-%m-%d %H:%M:%S') if scene.CreatedTime else '',
            scene.UpdatedTime.strftime('%Y-%m-%d %H:%M:%S') if scene.UpdatedTime else ''
        ]


# -------- DamageParameter Adapter --------
class DamageParameterGUIAdapter:
    """毁伤参数GUI适配器"""
    
    @staticmethod
    def from_gui(data: Dict[str, Any]) -> DamageParameter:
        """从GUI数据创建实体"""
        return DamageParameter(
            DPID=_to_int_or_none(data.get('DPID')),
            DSID=int(data.get('DSID', 0)),
            DSCode=str(data.get('DSCode', '')),
            Carrier=_to_str_or_none(data.get('Carrier')),
            GuidanceMode=_to_str_or_none(data.get('GuidanceMode')),
            WarheadType=str(data.get('WarheadType', '')),
            ChargeAmount=_to_float_or_none(data.get('ChargeAmount')),
            DropHeight=_to_float_or_none(data.get('DropHeight')),
            DropSpeed=_to_float_or_none(data.get('DropSpeed')),
            DropMode=_to_str_or_none(data.get('DropMode')),
            FlightRange=_to_float_or_none(data.get('FlightRange')),
            ElectroInterference=_to_str_or_none(data.get('ElectroInterference')),
            WeatherConditions=_to_str_or_none(data.get('WeatherConditions')),
            WindSpeed=_to_float_or_none(data.get('WindSpeed')),
            DPStatus=_to_int_or_none(data.get('DPStatus')),
            CreatedTime=_to_datetime_or_none(data.get('CreatedTime')),
            UpdatedTime=_to_datetime_or_none(data.get('UpdatedTime'))
        )
    
    @staticmethod
    def to_gui(param: DamageParameter) -> Dict[str, Any]:
        """转换为GUI数据"""
        data = asdict(param)
        # 处理datetime对象
        for key in ['CreatedTime', 'UpdatedTime']:
            if data.get(key) and isinstance(data[key], datetime):
                data[key] = data[key].strftime('%Y-%m-%d %H:%M:%S')
        return data
    
    @staticmethod
    def to_table_row(param: DamageParameter) -> list:
        """转换为表格行数据"""
        return [
            param.DPID,
            param.DSID,
            param.DSCode,
            param.Carrier or '',
            param.GuidanceMode or '',
            param.WarheadType,
            param.ChargeAmount or '',
            param.DropHeight or '',
            param.DropSpeed or '',
            param.DropMode or '',
            param.FlightRange or '',
            param.ElectroInterference or '',
            param.WeatherConditions or '',
            param.WindSpeed or '',
            param.DPStatus,
            param.CreatedTime.strftime('%Y-%m-%d %H:%M:%S') if param.CreatedTime else '',
            param.UpdatedTime.strftime('%Y-%m-%d %H:%M:%S') if param.UpdatedTime else ''
        ]
