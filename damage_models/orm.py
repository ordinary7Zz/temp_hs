"""
毁伤数据ORM映射类
"""
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Text
from .db import Base


class DamageSceneORM(Base):
    """毁伤场景ORM映射"""
    __tablename__ = 'DamageScene_Info'

    DSID = Column(Integer, primary_key=True, autoincrement=True, comment='主键,自增长')
    DSCode = Column(String(60), nullable=False, unique=True, comment='场景编号（唯一）')
    DSName = Column(String(60), nullable=False, unique=True, comment='场景名称（唯一）')
    DSOffensive = Column(String(60), nullable=True, comment='进攻方')
    DSDefensive = Column(String(60), nullable=True, comment='假想敌')
    DSBattle = Column(String(60), nullable=True, comment='所在战场')
    AMID = Column(Integer, nullable=False, comment='弹药ID')
    AMCode = Column(String(60), nullable=False, comment='弹药代码')
    TargetType = Column(Integer, nullable=False, comment='打击目标类型')
    TargetID = Column(Integer, nullable=False, comment='打击目标ID')
    TargetCode = Column(String(60), nullable=False, comment='打击目标代码')
    DSStatus = Column(Integer, nullable=True, comment='场景状态')
    CreatedTime = Column(DateTime, nullable=True, comment='创建时间')
    UpdatedTime = Column(DateTime, nullable=True, comment='更新时间')


class DamageParameterORM(Base):
    """毁伤参数ORM映射"""
    __tablename__ = 'DamageParameter_Info'

    DPID = Column(Integer, primary_key=True, autoincrement=True, comment='主键,自增长')
    DSID = Column(Integer, nullable=False, comment='场景ID')
    DSCode = Column(String(60), nullable=False, comment='场景编号（唯一）')
    Carrier = Column(String(60), nullable=True, comment='投放平台')
    GuidanceMode = Column(String(60), nullable=True, comment='制导方式')
    WarheadType = Column(String(60), nullable=False, comment='战斗部类型')
    ChargeAmount = Column(DECIMAL(10, 2), nullable=True, comment='装药量')
    DropHeight = Column(DECIMAL(10, 2), nullable=True, comment='投弹高度')
    DropSpeed = Column(DECIMAL(10, 2), nullable=True, comment='投弹速度')
    DropMode = Column(String(60), nullable=True, comment='投弹方式')
    FlightRange = Column(DECIMAL(10, 2), nullable=True, comment='射程')
    ElectroInterference = Column(String(60), nullable=True, comment='电磁干扰等级')
    WeatherConditions = Column(String(60), nullable=True, comment='天气状况')
    WindSpeed = Column(DECIMAL(10, 2), nullable=True, comment='环境风速')
    DPStatus = Column(Integer, nullable=True, comment='参数状态')
    CreatedTime = Column(DateTime, nullable=True, comment='创建时间')
    UpdatedTime = Column(DateTime, nullable=True, comment='更新时间')


class AssessmentResultORM(Base):
    """毁伤效能计算评估ORM映射"""
    __tablename__ = 'Assessment_Result'

    DAID = Column(Integer, primary_key=True, autoincrement=True, comment='主键,自增长')
    DSID = Column(Integer, nullable=False, comment='场景ID')
    DPID = Column(Integer, nullable=False, comment='参数ID')
    AMID = Column(Integer, nullable=False, comment='弹药ID')
    TargetType = Column(Integer, nullable=False, comment='打击目标类型')
    TargetID = Column(Integer, nullable=False, comment='打击目标ID')
    DADepth = Column(DECIMAL(10, 2), nullable=True, comment='弹坑深度')
    DADiameter = Column(DECIMAL(10, 2), nullable=True, comment='弹坑直径')
    DAVolume = Column(DECIMAL(10, 2), nullable=True, comment='弹坑容积')
    DAArea = Column(DECIMAL(10, 2), nullable=True, comment='弹坑面积')
    DALength = Column(DECIMAL(10, 2), nullable=True, comment='弹坑长度')
    DAWidth = Column(DECIMAL(10, 2), nullable=True, comment='弹坑宽度')
    Discturction = Column(DECIMAL(10, 2), nullable=True, comment='结构破坏程度')
    DamageDegree = Column(String(60), nullable=True, comment='毁伤等级')
    CreatedTime = Column(DateTime, nullable=True, comment='创建时间')
    UpdatedTime = Column(DateTime, nullable=True, comment='更新时间')


class AssessmentReportORM(Base):
    """毁伤评估报告ORM映射"""
    __tablename__ = 'Assessment_Report'

    ReportID = Column(Integer, primary_key=True, autoincrement=True, comment='主键,自增长')
    ReportCode = Column(String(60), nullable=True, comment='报告编号')
    ReportName = Column(String(60), nullable=False, comment='报告名称')
    DAID = Column(Integer, nullable=False, comment='毁伤评估ID')
    DSID = Column(Integer, nullable=False, comment='毁伤场景ID')
    DPID = Column(Integer, nullable=False, comment='毁伤参数ID')
    AMID = Column(Integer, nullable=False, comment='弹药数据ID')
    TargetType = Column(Integer, nullable=False, comment='打击目标类型')
    TargetID = Column(Integer, nullable=False, comment='打击目标ID')
    DamageDegree = Column(String(60), nullable=False, comment='毁伤等级')
    Comment = Column(Text(), nullable=True, comment='评估结论')
    Creator = Column(Integer, nullable=False, comment='报告操作人员')
    Reviewer = Column(String(60), nullable=True, comment='报告审核人')
    CreatedTime = Column(DateTime, nullable=True, comment='创建时间')
    UpdatedTime = Column(DateTime, nullable=True, comment='更新时间')