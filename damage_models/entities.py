"""
毁伤数据实体类
包含毁伤场景(DamageScene)、毁伤参数(DamageParameter)、毁伤结果(AssessmentResult)和毁伤评估报告(AssessmentReport)四个实体
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class DamageScene:
    """毁伤场景实体"""
    DSID: Optional[int] = None  # 主键,自增长
    DSCode: str = ""  # 场景编号（唯一）
    DSName: str = ""  # 场景名称（唯一）
    DSOffensive: Optional[str] = None  # 进攻方
    DSDefensive: Optional[str] = None  # 假想敌
    DSBattle: Optional[str] = None  # 所在战场
    AMID: int = 0  # 弹药ID
    AMCode: str = ""  # 弹药代码
    TargetType: int = 0  # 打击目标类型
    TargetID: int = 0  # 打击目标ID
    TargetCode: str = ""  # 打击目标代码
    DSStatus: Optional[int] = None  # 场景状态
    CreatedTime: Optional[datetime] = None  # 创建时间
    UpdatedTime: Optional[datetime] = None  # 更新时间


@dataclass
class DamageParameter:
    """毁伤参数实体"""
    DPID: Optional[int] = None  # 主键,自增长
    DSID: int = 0  # 场景ID
    DSCode: str = ""  # 场景编号（唯一）
    Carrier: Optional[str] = None  # 投放平台
    GuidanceMode: Optional[str] = None  # 制导方式
    WarheadType: str = ""  # 战斗部类型
    ChargeAmount: Optional[float] = None  # 装药量
    DropHeight: Optional[float] = None  # 投弹高度
    DropSpeed: Optional[float] = None  # 投弹速度
    DropMode: Optional[str] = None  # 投弹方式
    FlightRange: Optional[float] = None  # 射程
    ElectroInterference: Optional[str] = None  # 电磁干扰等级
    WeatherConditions: Optional[str] = None  # 天气状况
    WindSpeed: Optional[float] = None  # 环境风速
    DPStatus: Optional[int] = None  # 参数状态
    CreatedTime: Optional[datetime] = None  # 创建时间
    UpdatedTime: Optional[datetime] = None  # 更新时间


@dataclass
class AssessmentResult:
    """毁伤效能计算评估实体"""
    DAID: Optional[int] = None  # 主键ID
    DSID: int = 0  # 场景ID
    DPID: int = 0  # 参数ID
    AMID: int = 0  # 弹药ID
    TargetType: int = 0  # 打击目标类型
    TargetID: int = 0  # 打击目标ID
    DADepth: Optional[float] = None  # 弹坑深度
    DADiameter: Optional[float] = None  # 弹坑直径
    DAVolume: Optional[float] = None  # 弹坑容积
    DAArea: Optional[float] = None  # 弹坑面积
    DALength: Optional[float] = None  # 弹坑长度
    DAWidth: Optional[float] = None  # 弹坑宽度
    Discturction: Optional[float] = None  # 结构破坏程度
    DamageDegree: Optional[str] = None  # 毁伤等级
    CreatedTime: Optional[datetime] = None  # 创建时间
    UpdatedTime: Optional[datetime] = None  # 更新时间


@dataclass
class AssessmentReport:
    """毁伤评估报告实体"""
    ReportID: Optional[int] = None  # 主键ID
    ReportCode: str = ""  # 报告编号
    ReportName: str = ""  # 报告名称
    DAID: int = 0  # 毁伤评估ID
    DSID: Optional[int] = None  # 毁伤场景ID
    DPID: Optional[int] = None  # 毁伤参数ID
    AMID: Optional[int] = None  # 弹药数据ID
    TargetType: int = 0  # 打击目标类型
    TargetID: Optional[int] = None  # 打击目标ID
    DamageDegree: Optional[str] = None  # 毁伤等级
    Comment: Optional[str] = None  # 评估结论
    Creator: Optional[int] = None  # 报告操作人员
    Reviewer: Optional[str] = None  # 报告审核人
    CreatedTime: Optional[datetime] = None  # 创建时间
    UpdatedTime: Optional[datetime] = None  # 更新时间

