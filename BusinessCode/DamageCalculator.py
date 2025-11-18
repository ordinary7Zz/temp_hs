"""
毁伤结果计算模块
根据场景ID、参数ID、弹药ID和目标ID计算毁伤效果
"""
from __future__ import annotations
from loguru import logger
from DBCode.DBHelper import DBHelper
from damage_models.sql_repository_dbhelper import (
    DamageSceneRepository,
    DamageParameterRepository
)
from am_models.sql_repository import SQLRepository as AmmunitionRepository
from target_model.sql_repository import SQLRepository as TargetModelRepository
from am_models.db import session_scope as AmSessionScope
from target_model.db import session_scope as TargetSessionScope
from target_model.entities import AirportRunway, AircraftShelter, UndergroundCommandPost


from loguru import logger

class DamageCalculator:
    """毁伤结果计算器"""

    def __init__(self):
        """计算结果"""
        # 弹坑深度:
        self.craterDepth = 0.5
        # 弹坑面积:
        self.craterArea = 0.5
        # 弹坑直径:
        self.craterDiameter = 0.5
        # 弹坑容积:
        self.craterVolume = 0.5
        # 弹坑长度:
        self.craterLength = 0.5
        # 弹坑宽度:
        self.craterWidth = 0.5
        # 结构破坏程度
        self.discturction = 1
        # 毁伤程度
        self.damage_degree = '轻度毁伤'

    def calculate_damage_result(self, scene_id: int, parameter_id: int,
                                ammunition_id: int, target_type: int, target_id: int):
        """
        计算毁伤结果

        参数:
            scene_id: 场景ID
            parameter_id: 参数ID
            ammunition_id: 弹药ID
            target_type: 目标类型 (1-机场跑道, 2-单机掩蔽库, 3-地下指挥所)
            target_id: 目标ID

        返回:
            dict: 包含各项毁伤结果的字典
            {
                'da_depth': 弹坑深度(m),
                'da_diameter': 弹坑直径(m),
                'da_volume': 弹坑容积(m³),
                'da_area': 弹坑面积(m²),
                'da_length': 弹坑长度(m),
                'da_width': 弹坑宽度(m),
                'discturction': 结构破坏程度(0-1),
                'damage_degree': 毁伤等级
            }
        """
        try:
            logger.info(f"开始计算毁伤结果: 场景ID={scene_id}, 参数ID={parameter_id}, "
                       f"弹药ID={ammunition_id}, 目标类型={target_type}, 目标ID={target_id}")

            # 获取场景、参数、弹药、目标的详细信息
            scene_info = self._get_scene_info(scene_id)
            parameter_info = self._get_parameter_info(parameter_id)
            ammunition_info = self._get_ammunition_info(ammunition_id)
            target_info = self._get_target_info(target_type, target_id)

            logger.debug(f"场景信息: {scene_info}")
            logger.debug(f"参数信息: {parameter_info}")
            logger.debug(f"弹药信息: {ammunition_info}")
            logger.debug(f"目标信息: {target_info}")

            # TODO: 实现真实的计算逻辑
            # 目前返回固定值用于测试
            # result = self._calculate_fixed_result()
            if parameter_info and ("爆破" in parameter_info.WarheadType or "破片"in parameter_info.WarheadType):
                self.calculate_explosive_warhead(scene_info, parameter_info, target_type, target_info, ammunition_info)

            logger.info(f"毁伤结果计算完成")
            return self._wrap_result()

        except Exception as e:
            logger.exception(f"计算毁伤结果时发生错误: {e}")
            raise

    def _get_scene_info(self, scene_id: int):
        """获取场景信息"""
        try:
            db = DBHelper()
            try:
                repo = DamageSceneRepository(db)
                scene = repo.get_by_id(scene_id)
                if scene:
                    return scene
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取场景信息失败: {e}")
            return None

    def _get_parameter_info(self, parameter_id: int):
        """获取参数信息"""
        try:
            db = DBHelper()
            try:
                repo = DamageParameterRepository(db)
                param = repo.get_by_id(parameter_id)
                if param:
                    return param
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取参数信息失败: {e}")
            return None

    def _get_ammunition_info(self, ammunition_id: int):
        """获取弹药信息"""
        try:
            db = DBHelper()
            try:
                with AmSessionScope() as session:
                    repo = AmmunitionRepository(session)
                ammunition = repo.get(ammunition_id)
                ammunition.am_image_blob = None
                if ammunition:
                    return ammunition
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取弹药信息失败: {e}")
            return None

    def _get_target_info(self, target_type: int, target_id: int):
        """获取目标信息"""
        try:
            db = DBHelper()
            try:
                with TargetSessionScope() as session:
                    repo = TargetModelRepository(session)
                target = None
                if target_type == 1:
                    target = repo.get(target_id, AirportRunway)
                    target.runway_picture = None
                elif target_type == 2:
                    target = repo.get(target_id, AircraftShelter)
                    target.shelter_picture = None
                elif target_type == 3:
                    target = repo.get(target_id, UndergroundCommandPost)
                    target.shelter_picture = None
                if target:
                    return target
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"获取目标信息失败: {e}")
            return None

    def _wrap_result(self):
        return {
            'da_depth': round(self.craterDepth, 2),          # 弹坑深度(m)
            'da_diameter': round(self.craterDiameter, 2),       # 弹坑直径(m)
            'da_volume': round(self.craterVolume, 2),         # 弹坑容积(m³)
            'da_area': round(self.craterArea, 2),           # 弹坑面积(m²)
            'da_length': round(self.craterLength, 2),         # 弹坑长度(m)
            'da_width': round(self.craterWidth, 2),          # 弹坑宽度(m)
            'discturction': self.discturction,      # 结构破坏程度(0-1)
            'damage_degree': self.damage_degree  # 毁伤等级
        }
    # def _calculate_fixed_result(self):
    #     """
    #     返回固定的测试结果
    #     TODO: 实现真实的毁伤计算逻辑
    #     """
    #     return {
    #         'da_depth': 0.5,          # 弹坑深度(m)
    #         'da_diameter': 0.5,       # 弹坑直径(m)
    #         'da_volume': 0.5,         # 弹坑容积(m³)
    #         'da_area': 0.5,           # 弹坑面积(m²)
    #         'da_length': 0.5,         # 弹坑长度(m)
    #         'da_width': 0.5,          # 弹坑宽度(m)
    #         'discturction': 0.5,      # 结构破坏程度(0-1)
    #         'damage_degree': '重度毁伤'  # 毁伤等级
    #     }

    def _calculate_real_result(self, scene_info, parameter_info,
                               ammunition_info, target_info):
        """
        真实的毁伤计算逻辑
        TODO: 根据实际的物理模型和经验公式实现

        参数:
            scene_info: 场景信息
            parameter_info: 参数信息
            ammunition_info: 弹药信息
            target_info: 目标信息

        返回:
            dict: 计算结果
        """
        # TODO: 实现真实的计算逻辑
        # 这里应该包含：
        # 1. 根据弹药类型、装药量等计算爆炸当量
        # 2. 根据投放高度、速度等计算冲击波参数
        # 3. 根据目标类型和结构计算毁伤效果
        # 4. 计算弹坑参数（深度、直径、容积等）
        # 5. 评估结构破坏程度
        # 6. 确定毁伤等级

        pass

    def calculate_explosive_warhead(self, scene, parameter, target_type, target, ammunition):
        # 炸药爆热
        heatExpl = 5000.0
        if ammunition.exb_explosion:
            heatExpl = float(ammunition.exb_explosion)

        # TNT炸药爆热
        heatTNT = 4187.0

        # 装药质量
        chargeMass = 2.5
        if ammunition.explosive_payload_kg:
            chargeMass = float(ammunition.explosive_payload_kg)
        elif ammunition.exb_weight:
            chargeMass = float(ammunition.exb_weight)
        elif parameter.ChargeAmount:
            chargeMass = float(parameter.ChargeAmount)

        # 战斗部质心到孔底部的距离
        distCG2HoleBot = 0.3
        if ammunition.length_m:
            distCG2HoleBot = float(ammunition.length_m) * 0.5

        # 土质性质的抛掷系数
        throwCoeffSoil = 0.0
        if target_type == 1:
            throwCoeffSoil = 1.7
            if chargeMass >= 25:
                chargeMass = max(2.0, chargeMass / 25.0)
        elif target_type == 2:
            throwCoeffSoil = 1
            if chargeMass >= 25:
                chargeMass = max(10.0, chargeMass / 5.0)
        elif target_type == 3:
            throwCoeffSoil = 0.75
            if chargeMass >= 25:
                chargeMass = max(10.0, chargeMass / 5.0)

        if target_type == 1:
            # 弹坑深度:
            self.craterDepth = ((chargeMass * heatExpl / (distCG2HoleBot * heatTNT))**(1/3) + distCG2HoleBot) / 3.0
            # 弹坑直径:
            self.craterDiameter = 5.0 * self.craterDepth
            # 弹坑面积:
            self.craterArea = 0.5 * 3.14 * (self.craterDiameter / 2) ** 2
            # 弹坑容积:
            self.craterVolume = 2 / 3 * 3.14 * (self.craterDiameter / 2) ** 3 / 8.0
            # 弹坑长度:
            self.craterLength = 1.05 * self.craterDiameter
            # 弹坑宽度:
            self.craterWidth = 0.95 * self.craterDiameter
            # 结构破坏程度:
            if self.craterDepth >= 1.3:
                self.discturction = round(1 + 4 * (self.craterDepth - 1.3), 2)
        else:
            # 弹坑深度:
            self.craterDepth = ((chargeMass * heatExpl / (distCG2HoleBot * heatTNT))**(1/3) + distCG2HoleBot) / 1.5
            # 弹坑直径:
            self.craterDiameter = 1.8 * self.craterDepth
            # 弹坑面积:
            self.craterArea = 0.5 * 3.14 * (self.craterDiameter / 2) ** 2
            # 弹坑容积:
            self.craterVolume = 2 / 3 * 3.14 * (self.craterDiameter / 2) ** 3 / 8.0
            # 弹坑长度:
            self.craterLength = 1.05 * self.craterDiameter
            # 弹坑宽度:
            self.craterWidth = 0.95 * self.craterDiameter
            # 结构破坏程度:
            if self.craterDepth >= 1.3:
                self.discturction = round(1 + 4 * (self.craterDepth - 1.3), 2)

        damage_degree_values = ["未达到轻度毁伤", "轻度毁伤", "中度毁伤", "重度毁伤", "完全摧毁"]
        if self.discturction <= 1:
            self.damage_degree = damage_degree_values[0]
        elif self.discturction <= 8:
            self.damage_degree = damage_degree_values[1]
        elif self.discturction <= 15:
            self.damage_degree = damage_degree_values[2]
        elif self.discturction <= 20:
            self.damage_degree = damage_degree_values[3]
        else:
            self.damage_degree = damage_degree_values[4]

# 便捷函数
def calculate_damage(scene_id: int, parameter_id: int, ammunition_id: int,
                     target_type: int, target_id: int):
    """
    计算毁伤结果的便捷函数

    参数:
        scene_id: 场景ID
        parameter_id: 参数ID
        ammunition_id: 弹药ID
        target_type: 目标类型
        target_id: 目标ID

    返回:
        dict: 毁伤结果字典
    """
    calculator = DamageCalculator()
    return calculator.calculate_damage_result(
        scene_id, parameter_id, ammunition_id, target_type, target_id
    )

