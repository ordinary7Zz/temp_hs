"""
毁伤数据SQL仓储类
使用 DBHelper 进行数据库操作
"""
from typing import List, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .entities import DamageScene, DamageParameter, AssessmentResult, AssessmentReport
from DBCode.DBHelper import DBHelper
from .orm import DamageSceneORM, DamageParameterORM, AssessmentResultORM, AssessmentReportORM


class DamageSceneRepository:
    """毁伤场景仓储类"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, scene: DamageScene) -> int:
        """添加毁伤场景"""
        scene.CreatedTime = datetime.now()
        scene.UpdatedTime = datetime.now()
        
        orm_obj = DamageSceneORM(
            DSCode=scene.DSCode,
            DSName=scene.DSName,
            DSOffensive=scene.DSOffensive,
            DSDefensive=scene.DSDefensive,
            DSBattle=scene.DSBattle,
            AMID=scene.AMID,
            AMCode=scene.AMCode,
            TargetType=scene.TargetType,
            TargetID=scene.TargetID,
            TargetCode=scene.TargetCode,
            DSStatus=scene.DSStatus,
            CreatedTime=scene.CreatedTime,
            UpdatedTime=scene.UpdatedTime
        )
        self.session.add(orm_obj)
        self.session.commit()
        return orm_obj.DSID
    
    def update(self, scene: DamageScene) -> bool:
        """更新毁伤场景"""
        orm_obj = self.session.query(DamageSceneORM).filter_by(DSID=scene.DSID).first()
        if not orm_obj:
            return False
        
        scene.UpdatedTime = datetime.now()
        
        orm_obj.DSCode = scene.DSCode
        orm_obj.DSName = scene.DSName
        orm_obj.DSOffensive = scene.DSOffensive
        orm_obj.DSDefensive = scene.DSDefensive
        orm_obj.DSBattle = scene.DSBattle
        orm_obj.AMID = scene.AMID
        orm_obj.AMCode = scene.AMCode
        orm_obj.TargetType = scene.TargetType
        orm_obj.TargetID = scene.TargetID
        orm_obj.TargetCode = scene.TargetCode
        orm_obj.DSStatus = scene.DSStatus
        orm_obj.UpdatedTime = scene.UpdatedTime
        
        self.session.commit()
        return True
    
    def delete(self, dsid: int) -> bool:
        """删除毁伤场景"""
        orm_obj = self.session.query(DamageSceneORM).filter_by(DSID=dsid).first()
        if not orm_obj:
            return False
        
        self.session.delete(orm_obj)
        self.session.commit()
        return True
    
    def get_by_id(self, dsid: int) -> Optional[DamageScene]:
        """根据ID获取毁伤场景"""
        orm_obj = self.session.query(DamageSceneORM).filter_by(DSID=dsid).first()
        if not orm_obj:
            return None
        
        return self._orm_to_entity(orm_obj)
    
    def get_all(self) -> List[DamageScene]:
        """获取所有毁伤场景"""
        orm_list = self.session.query(DamageSceneORM).all()
        return [self._orm_to_entity(orm_obj) for orm_obj in orm_list]
    
    def search(self, keyword: str) -> List[DamageScene]:
        """搜索毁伤场景"""
        orm_list = self.session.query(DamageSceneORM).filter(
            (DamageSceneORM.DSCode.like(f'%{keyword}%')) |
            (DamageSceneORM.DSName.like(f'%{keyword}%'))
        ).all()
        return [self._orm_to_entity(orm_obj) for orm_obj in orm_list]
    
    @staticmethod
    def _orm_to_entity(orm_obj: DamageSceneORM) -> DamageScene:
        """ORM对象转实体"""
        return DamageScene(
            DSID=orm_obj.DSID,
            DSCode=orm_obj.DSCode,
            DSName=orm_obj.DSName,
            DSOffensive=orm_obj.DSOffensive,
            DSDefensive=orm_obj.DSDefensive,
            DSBattle=orm_obj.DSBattle,
            AMID=orm_obj.AMID,
            AMCode=orm_obj.AMCode,
            TargetType=orm_obj.TargetType,
            TargetID=orm_obj.TargetID,
            TargetCode=orm_obj.TargetCode,
            DSStatus=orm_obj.DSStatus,
            CreatedTime=orm_obj.CreatedTime,
            UpdatedTime=orm_obj.UpdatedTime
        )


class DamageParameterRepository:
    """毁伤参数仓储类"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, param: DamageParameter) -> int:
        """添加毁伤参数"""
        param.CreatedTime = datetime.now()
        param.UpdatedTime = datetime.now()
        
        orm_obj = DamageParameterORM(
            DSID=param.DSID,
            DSCode=param.DSCode,
            Carrier=param.Carrier,
            GuidanceMode=param.GuidanceMode,
            WarheadType=param.WarheadType,
            ChargeAmount=param.ChargeAmount,
            DropHeight=param.DropHeight,
            DropSpeed=param.DropSpeed,
            DropMode=param.DropMode,
            FlightRange=param.FlightRange,
            ElectroInterference=param.ElectroInterference,
            WeatherConditions=param.WeatherConditions,
            WindSpeed=param.WindSpeed,
            DPStatus=param.DPStatus,
            CreatedTime=param.CreatedTime,
            UpdatedTime=param.UpdatedTime
        )
        self.session.add(orm_obj)
        self.session.commit()
        return orm_obj.DPID
    
    def update(self, param: DamageParameter) -> bool:
        """更新毁伤参数"""
        orm_obj = self.session.query(DamageParameterORM).filter_by(DPID=param.DPID).first()
        if not orm_obj:
            return False
        
        param.UpdatedTime = datetime.now()
        
        orm_obj.DSID = param.DSID
        orm_obj.DSCode = param.DSCode
        orm_obj.Carrier = param.Carrier
        orm_obj.GuidanceMode = param.GuidanceMode
        orm_obj.WarheadType = param.WarheadType
        orm_obj.ChargeAmount = param.ChargeAmount
        orm_obj.DropHeight = param.DropHeight
        orm_obj.DropSpeed = param.DropSpeed
        orm_obj.DropMode = param.DropMode
        orm_obj.FlightRange = param.FlightRange
        orm_obj.ElectroInterference = param.ElectroInterference
        orm_obj.WeatherConditions = param.WeatherConditions
        orm_obj.WindSpeed = param.WindSpeed
        orm_obj.DPStatus = param.DPStatus
        orm_obj.UpdatedTime = param.UpdatedTime
        
        self.session.commit()
        return True
    
    def delete(self, dpid: int) -> bool:
        """删除毁伤参数"""
        orm_obj = self.session.query(DamageParameterORM).filter_by(DPID=dpid).first()
        if not orm_obj:
            return False
        
        self.session.delete(orm_obj)
        self.session.commit()
        return True
    
    def get_by_id(self, dpid: int) -> Optional[DamageParameter]:
        """根据ID获取毁伤参数"""
        orm_obj = self.session.query(DamageParameterORM).filter_by(DPID=dpid).first()
        if not orm_obj:
            return None
        
        return self._orm_to_entity(orm_obj)
    
    def get_by_scene_id(self, dsid: int) -> List[DamageParameter]:
        """根据场景ID获取毁伤参数列表"""
        orm_list = self.session.query(DamageParameterORM).filter_by(DSID=dsid).all()
        return [self._orm_to_entity(orm_obj) for orm_obj in orm_list]
    
    def get_all(self) -> List[DamageParameter]:
        """获取所有毁伤参数"""
        orm_list = self.session.query(DamageParameterORM).all()
        return [self._orm_to_entity(orm_obj) for orm_obj in orm_list]
    
    @staticmethod
    def _orm_to_entity(orm_obj: DamageParameterORM) -> DamageParameter:
        """ORM对象转实体"""
        return DamageParameter(
            DPID=orm_obj.DPID,
            DSID=orm_obj.DSID,
            DSCode=orm_obj.DSCode,
            Carrier=orm_obj.Carrier,
            GuidanceMode=orm_obj.GuidanceMode,
            WarheadType=orm_obj.WarheadType,
            ChargeAmount=float(orm_obj.ChargeAmount) if orm_obj.ChargeAmount else None,
            DropHeight=orm_obj.DropHeight,
            DropSpeed=float(orm_obj.DropSpeed) if orm_obj.DropSpeed else None,
            DropMode=orm_obj.DropMode,
            FlightRange=float(orm_obj.FlightRange) if orm_obj.FlightRange else None,
            ElectroInterference=orm_obj.ElectroInterference,
            WeatherConditions=orm_obj.WeatherConditions,
            WindSpeed=float(orm_obj.WindSpeed) if orm_obj.WindSpeed else None,
            DPStatus=orm_obj.DPStatus,
            CreatedTime=orm_obj.CreatedTime,
            UpdatedTime=orm_obj.UpdatedTime
        )
