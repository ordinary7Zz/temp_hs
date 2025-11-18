"""
毁伤数据SQL仓储类
使用 DBHelper 进行数据库操作（模仿 am_models 的方式）
"""
from typing import List, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .entities import DamageScene, DamageParameter, AssessmentResult, AssessmentReport
from DBCode.DBHelper import DBHelper


class DamageSceneRepository:
    """毁伤场景仓储类 - 使用 DBHelper"""

    def __init__(self, db_helper: DBHelper):
        self.db = db_helper

    def add(self, scene: DamageScene) -> int:
        """添加毁伤场景"""
        now = datetime.now()

        sql = """
        INSERT INTO DamageScene_Info 
        (DSCode, DSName, DSOffensive, DSDefensive, DSBattle, AMID, AMCode, 
         TargetType, TargetID, TargetCode, DSStatus, CreatedTime, UpdatedTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            scene.DSCode, scene.DSName, scene.DSOffensive, scene.DSDefensive,
            scene.DSBattle, scene.AMID, scene.AMCode, scene.TargetType,
            scene.TargetID, scene.TargetCode, scene.DSStatus, now, now
        )

        self.db.execute_query(sql, params)

        # 获取插入的ID
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]['id'] if result else 0

    def update(self, scene: DamageScene) -> bool:
        """更新毁伤场景"""
        now = datetime.now()

        sql = """
        UPDATE DamageScene_Info 
        SET DSCode=%s, DSName=%s, DSOffensive=%s, DSDefensive=%s, DSBattle=%s,
            AMID=%s, AMCode=%s, TargetType=%s, TargetID=%s, TargetCode=%s,
            DSStatus=%s, UpdatedTime=%s
        WHERE DSID=%s
        """

        params = (
            scene.DSCode, scene.DSName, scene.DSOffensive, scene.DSDefensive,
            scene.DSBattle, scene.AMID, scene.AMCode, scene.TargetType,
            scene.TargetID, scene.TargetCode, scene.DSStatus, now, scene.DSID
        )

        affected = self.db.execute_query(sql, params)
        return affected > 0 if affected else False

    def delete(self, dsid: int) -> bool:
        """删除毁伤场景(软删除，将DSStatus设置为0)"""
        now = datetime.now()
        sql = "UPDATE DamageScene_Info SET DSStatus=0, UpdatedTime=%s WHERE DSID=%s"
        affected = self.db.execute_query(sql, (now, dsid))
        return affected > 0 if affected else False

    def get_by_id(self, dsid: int) -> Optional[DamageScene]:
        """根据ID获取毁伤场景"""
        sql = "SELECT * FROM DamageScene_Info WHERE DSID=%s"
        result = self.db.execute_query(sql, (dsid,))

        if result and len(result) > 0:
            return self._row_to_entity(result[0])
        return None

    def get_all(self) -> List[DamageScene]:
        """获取所有毁伤场景(仅未删除的)"""
        sql = "SELECT * FROM DamageScene_Info WHERE DSStatus=1 ORDER BY DSID DESC"
        result = self.db.execute_query(sql)

        return [self._row_to_entity(row) for row in result] if result else []

    def search(self, keyword: str) -> List[DamageScene]:
        """搜索毁伤场景(仅未删除的)"""
        sql = """
        SELECT * FROM DamageScene_Info 
        WHERE DSStatus=0 AND (DSCode LIKE %s OR DSName LIKE %s)
        ORDER BY DSID DESC
        """
        pattern = f'%{keyword}%'
        result = self.db.execute_query(sql, (pattern, pattern))

        return [self._row_to_entity(row) for row in result] if result else []

    @staticmethod
    def _row_to_entity(row: dict) -> DamageScene:
        """数据库行转实体"""
        return DamageScene(
            DSID=row.get('DSID'),
            DSCode=row.get('DSCode', ''),
            DSName=row.get('DSName', ''),
            DSOffensive=row.get('DSOffensive'),
            DSDefensive=row.get('DSDefensive'),
            DSBattle=row.get('DSBattle'),
            AMID=row.get('AMID', 0),
            AMCode=row.get('AMCode', ''),
            TargetType=row.get('TargetType', 0),
            TargetID=row.get('TargetID', 0),
            TargetCode=row.get('TargetCode', ''),
            DSStatus=row.get('DSStatus'),
            CreatedTime=row.get('CreatedTime'),
            UpdatedTime=row.get('UpdatedTime')
        )


class DamageParameterRepository:
    """毁伤参数仓储类 - 使用 DBHelper"""

    def __init__(self, db_helper: DBHelper):
        self.db = db_helper

    def add(self, param: DamageParameter) -> int:
        """添加毁伤参数"""
        now = datetime.now()

        sql = """
        INSERT INTO DamageParameter_Info 
        (DSID, DSCode, Carrier, GuidanceMode, WarheadType, ChargeAmount,
         DropHeight, DropSpeed, DropMode, FlightRange, ElectroInterference,
         WeatherConditions, WindSpeed, DPStatus, CreatedTime, UpdatedTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            param.DSID, param.DSCode, param.Carrier, param.GuidanceMode,
            param.WarheadType, param.ChargeAmount, param.DropHeight,
            param.DropSpeed, param.DropMode, param.FlightRange,
            param.ElectroInterference, param.WeatherConditions,
            param.WindSpeed, param.DPStatus, now, now
        )

        self.db.execute_query(sql, params)

        # 获取插入的ID
        result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return result[0]['id'] if result else 0

    def update(self, param: DamageParameter) -> bool:
        """更新毁伤参数"""
        now = datetime.now()

        sql = """
        UPDATE DamageParameter_Info 
        SET DSID=%s, DSCode=%s, Carrier=%s, GuidanceMode=%s, WarheadType=%s,
            ChargeAmount=%s, DropHeight=%s, DropSpeed=%s, DropMode=%s,
            FlightRange=%s, ElectroInterference=%s, WeatherConditions=%s,
            WindSpeed=%s, DPStatus=%s, UpdatedTime=%s
        WHERE DPID=%s
        """

        params = (
            param.DSID, param.DSCode, param.Carrier, param.GuidanceMode,
            param.WarheadType, param.ChargeAmount, param.DropHeight,
            param.DropSpeed, param.DropMode, param.FlightRange,
            param.ElectroInterference, param.WeatherConditions,
            param.WindSpeed, param.DPStatus, now, param.DPID
        )

        affected = self.db.execute_query(sql, params)
        return affected > 0 if affected else False

    def delete(self, dpid: int) -> bool:
        """删除毁伤参数(软删除，将DPStatus设置为0)"""
        now = datetime.now()
        sql = "UPDATE DamageParameter_Info SET DPStatus=0, UpdatedTime=%s WHERE DPID=%s"
        affected = self.db.execute_query(sql, (now, dpid))
        return affected > 0 if affected else False

    def get_by_id(self, dpid: int) -> Optional[DamageParameter]:
        """根据ID获取毁伤参数"""
        sql = "SELECT * FROM DamageParameter_Info WHERE DPID=%s"
        result = self.db.execute_query(sql, (dpid,))

        if result and len(result) > 0:
            return self._row_to_entity(result[0])
        return None

    def get_by_scene_id(self, dsid: int) -> List[DamageParameter]:
        """根据场景ID获取毁伤参数列表(仅未删除的)"""
        sql = "SELECT * FROM DamageParameter_Info WHERE DSID=%s AND DPStatus=1 ORDER BY DPID DESC"
        result = self.db.execute_query(sql, (dsid,))

        return [self._row_to_entity(row) for row in result] if result else []

    def get_all(self) -> List[DamageParameter]:
        """获取所有毁伤参数(仅未删除的)"""
        sql = "SELECT * FROM DamageParameter_Info WHERE DPStatus=1 ORDER BY DPID DESC"
        result = self.db.execute_query(sql)

        return [self._row_to_entity(row) for row in result] if result else []

    @staticmethod
    def _row_to_entity(row: dict) -> DamageParameter:
        """数据库行转实体"""
        return DamageParameter(
            DPID=row.get('DPID'),
            DSID=row.get('DSID', 0),
            DSCode=row.get('DSCode', ''),
            Carrier=row.get('Carrier'),
            GuidanceMode=row.get('GuidanceMode'),
            WarheadType=row.get('WarheadType', ''),
            ChargeAmount=float(row['ChargeAmount']) if row.get('ChargeAmount') else None,
            DropHeight=float(row['DropHeight']) if row.get('DropHeight') else None,
            DropSpeed=float(row['DropSpeed']) if row.get('DropSpeed') else None,
            DropMode=row.get('DropMode'),
            FlightRange=float(row['FlightRange']) if row.get('FlightRange') else None,
            ElectroInterference=row.get('ElectroInterference'),
            WeatherConditions=row.get('WeatherConditions'),
            WindSpeed=float(row['WindSpeed']) if row.get('WindSpeed') else None,
            DPStatus=row.get('DPStatus'),
            CreatedTime=row.get('CreatedTime'),
            UpdatedTime=row.get('UpdatedTime')
        )


class AssessmentResultRepository:
    """毁伤效能计算评估仓储类 - 使用 DBHelper"""

    def __init__(self, db_helper: DBHelper):
        self.db = db_helper

    def add(self, result: AssessmentResult) -> int:
        """添加毁伤结果"""
        now = datetime.now()

        sql = """
        INSERT INTO Assessment_Result 
        (DSID, DPID, AMID, TargetType, TargetID, DADepth, DADiameter, DAVolume,
         DAArea, DALength, DAWidth, Discturction, DamageDegree, CreatedTime, UpdatedTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            result.DSID, result.DPID, result.AMID, result.TargetType, result.TargetID,
            result.DADepth, result.DADiameter, result.DAVolume, result.DAArea,
            result.DALength, result.DAWidth, result.Discturction, result.DamageDegree,
            now, now
        )

        self.db.execute_query(sql, params)

        # 获取插入的ID
        db_result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return db_result[0]['id'] if db_result else 0

    def update(self, result: AssessmentResult) -> bool:
        """更新毁伤结果"""
        now = datetime.now()

        sql = """
        UPDATE Assessment_Result 
        SET DSID=%s, DPID=%s, AMID=%s, TargetType=%s, TargetID=%s,
            DADepth=%s, DADiameter=%s, DAVolume=%s, DAArea=%s,
            DALength=%s, DAWidth=%s, Discturction=%s, DamageDegree=%s,
            UpdatedTime=%s
        WHERE DAID=%s
        """

        params = (
            result.DSID, result.DPID, result.AMID, result.TargetType, result.TargetID,
            result.DADepth, result.DADiameter, result.DAVolume, result.DAArea,
            result.DALength, result.DAWidth, result.Discturction, result.DamageDegree,
            now, result.DAID
        )

        affected = self.db.execute_query(sql, params)
        return affected > 0 if affected else False

    def delete(self, daid: int) -> bool:
        """删除毁伤结果"""
        sql = "DELETE FROM Assessment_Result WHERE DAID=%s"
        affected = self.db.execute_query(sql, (daid,))
        return affected > 0 if affected else False

    def get_by_id(self, daid: int) -> Optional[AssessmentResult]:
        """根据ID获取毁伤结果"""
        sql = "SELECT * FROM Assessment_Result WHERE DAID=%s"
        db_result = self.db.execute_query(sql, (daid,))

        if db_result and len(db_result) > 0:
            return self._row_to_entity(db_result[0])
        return None

    def get_by_scene_id(self, dsid: int) -> List[AssessmentResult]:
        """根据场景ID获取毁伤结果列表"""
        sql = "SELECT * FROM Assessment_Result WHERE DSID=%s ORDER BY DAID DESC"
        db_result = self.db.execute_query(sql, (dsid,))

        return [self._row_to_entity(row) for row in db_result] if db_result else []

    def get_all(self) -> List[AssessmentResult]:
        """获取所有毁伤结果"""
        sql = "SELECT * FROM Assessment_Result ORDER BY DAID DESC"
        db_result = self.db.execute_query(sql)

        return [self._row_to_entity(row) for row in db_result] if db_result else []

    def search(self, keyword: str) -> List[AssessmentResult]:
        """搜索毁伤结果"""
        sql = """
        SELECT * FROM Assessment_Result 
        WHERE DamageDegree LIKE %s OR DAID LIKE %s
        ORDER BY DAID DESC
        """
        pattern = f'%{keyword}%'
        db_result = self.db.execute_query(sql, (pattern, pattern))

        return [self._row_to_entity(row) for row in db_result] if db_result else []

    @staticmethod
    def _row_to_entity(row: dict) -> AssessmentResult:
        """数据库行转实体"""
        return AssessmentResult(
            DAID=row.get('DAID'),
            DSID=row.get('DSID', 0),
            DPID=row.get('DPID', 0),
            AMID=row.get('AMID', 0),
            TargetType=row.get('TargetType', 0),
            TargetID=row.get('TargetID', 0),
            DADepth=float(row['DADepth']) if row.get('DADepth') else None,
            DADiameter=float(row['DADiameter']) if row.get('DADiameter') else None,
            DAVolume=float(row['DAVolume']) if row.get('DAVolume') else None,
            DAArea=float(row['DAArea']) if row.get('DAArea') else None,
            DALength=float(row['DALength']) if row.get('DALength') else None,
            DAWidth=float(row['DAWidth']) if row.get('DAWidth') else None,
            Discturction=float(row['Discturction']) if row.get('Discturction') else None,
            DamageDegree=row.get('DamageDegree'),
            CreatedTime=row.get('CreatedTime'),
            UpdatedTime=row.get('UpdatedTime')
        )


class AssessmentReportRepository:
    """毁伤评估报告仓储类 - 使用 DBHelper"""

    def __init__(self, db_helper: DBHelper):
        self.db = db_helper

    def add(self, report: AssessmentReport) -> int:
        """添加毁伤评估报告"""
        now = datetime.now()

        sql = """
        INSERT INTO Assessment_Report 
        (ReportCode, ReportName, DAID, DSID, DPID, AMID, TargetType, TargetID,
         DamageDegree, Comment, Creator, Reviewer, CreatedTime, UpdatedTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            report.ReportCode, report.ReportName, report.DAID, report.DSID,
            report.DPID, report.AMID, report.TargetType, report.TargetID,
            report.DamageDegree, report.Comment, report.Creator, report.Reviewer,
            now, now
        )

        self.db.execute_query(sql, params)

        # 获取插入的ID
        db_result = self.db.execute_query("SELECT LAST_INSERT_ID() as id")
        return db_result[0]['id'] if db_result else 0

    def update(self, report: AssessmentReport) -> bool:
        """更新毁伤评估报告"""
        now = datetime.now()

        sql = """
        UPDATE Assessment_Report 
        SET ReportCode=%s, ReportName=%s, DAID=%s, DSID=%s, DPID=%s, AMID=%s,
            TargetType=%s, TargetID=%s, DamageDegree=%s, Comment=%s,
            Creator=%s, Reviewer=%s, UpdatedTime=%s
        WHERE ReportID=%s
        """

        params = (
            report.ReportCode, report.ReportName, report.DAID, report.DSID,
            report.DPID, report.AMID, report.TargetType, report.TargetID,
            report.DamageDegree, report.Comment, report.Creator, report.Reviewer,
            now, report.ReportID
        )

        affected = self.db.execute_query(sql, params)
        return affected > 0 if affected else False

    def delete(self, report_id: int) -> bool:
        """删除毁伤评估报告"""
        sql = "DELETE FROM Assessment_Report WHERE ReportID=%s"
        affected = self.db.execute_query(sql, (report_id,))
        return affected > 0 if affected else False

    def get_by_id(self, report_id: int) -> Optional[AssessmentReport]:
        """根据ID获取毁伤评估报告"""
        sql = "SELECT * FROM Assessment_Report WHERE ReportID=%s"
        db_result = self.db.execute_query(sql, (report_id,))

        if db_result and len(db_result) > 0:
            return self._row_to_entity(db_result[0])
        return None

    def get_all(self) -> List[AssessmentReport]:
        """获取所有毁伤评估报告"""
        sql = "SELECT * FROM Assessment_Report ORDER BY ReportID DESC"
        db_result = self.db.execute_query(sql)

        return [self._row_to_entity(row) for row in db_result] if db_result else []

    def search(self, keyword: str) -> List[AssessmentReport]:
        """搜索毁伤评估报告"""
        sql = """
        SELECT * FROM Assessment_Report 
        WHERE ReportCode LIKE %s OR ReportName LIKE %s
        ORDER BY ReportID DESC
        """
        pattern = f'%{keyword}%'
        db_result = self.db.execute_query(sql, (pattern, pattern))

        return [self._row_to_entity(row) for row in db_result] if db_result else []

    @staticmethod
    def _row_to_entity(row: dict) -> AssessmentReport:
        """数据库行转实体"""
        return AssessmentReport(
            ReportID=row.get('ReportID'),
            ReportCode=row.get('ReportCode', ''),
            ReportName=row.get('ReportName', ''),
            DAID=row.get('DAID', 0),
            DSID=row.get('DSID'),
            DPID=row.get('DPID'),
            AMID=row.get('AMID'),
            TargetType=row.get('TargetType', 0),
            TargetID=row.get('TargetID'),
            DamageDegree=row.get('DamageDegree'),
            Comment=row.get('Comment'),
            Creator=row.get('Creator'),
            Reviewer=row.get('Reviewer'),
            CreatedTime=row.get('CreatedTime'),
            UpdatedTime=row.get('UpdatedTime')
        )
