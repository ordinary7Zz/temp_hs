import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from loguru import logger


@dataclass
class Ammunition:
    """
    弹药毁伤模型（与《数据表.xlsx》一致）
    """

    # ===== 必填字段（允许空值 = N，除 am_id 外均为必填） =====
    am_name: str  # 名称
    am_image_blob: bytes  # 图片二进制
    am_type: str  # 弹药类型
    weight_kg: Decimal  # 弹体全重 Decimal(10,3)
    launch_mass_kg: Decimal  # 发射质量 Decimal(10,3)
    warhead_type: str  # 战斗部类型
    warhead_name: str  # 战斗部名称

    # ===== 可选字段（允许空值 = Y） =====
    country: Optional[str] = None  # 国家 varchar(64)
    used_by: Optional[str] = None  # 使用方 varchar(128)
    chinese_name: Optional[str] = None  # 中文名称 varchar(128)
    short_name: Optional[str] = None  # 简称 varchar(128)
    model_name: Optional[str] = None  # 型号 varchar(128)
    submodel_name: Optional[str] = None  # 子型号 varchar(128)
    manufacturer: Optional[str] = None  # 生产商 varchar(128)
    attended_time: Optional[str] = None  # 服役/出现时间 varchar(128)

    length_m: Optional[Decimal] = None  # 长度 Decimal(10,3)
    diameter_m: Optional[Decimal] = None  # 弹体直径 Decimal(10,3)
    texture: Optional[str] = None  # 材质 varchar(128)
    wingspan_close_mm: Optional[Decimal] = None  # 闭合翼展 Decimal(10,3)
    wingspan_open_mm: Optional[Decimal] = None  # 展开翼展 Decimal(10,3)
    structure: Optional[str] = None  # 结构 varchar(512)

    max_speed_ma: Optional[Decimal] = None  # 最大速度(马赫) Decimal(10,3)
    radar_cross_section: Optional[str] = None  # RCS varchar(128)
    power_plant: Optional[str] = None  # 动力装置 varchar(128)

    destroying_elements: Optional[str] = None  # 杀伤元件 varchar(128)
    fuze: Optional[str] = None  # 引信 varchar(128)
    explosion_equivalent_TNT_T: Optional[Decimal] = None  # 当量(TNT吨) Decimal(10,3)
    precision_m: Optional[Decimal] = None  # 精度(米) Decimal(10,4)
    destroying_mechanism: Optional[str] = None  # 毁伤机理 varchar(4056)

    target: Optional[str] = None  # 目标 varchar(256)
    carrier: Optional[str] = None  # 载体 varchar(128)
    guidance_mode: Optional[str] = None  # 制导方式 varchar(128)
    explosive_payload_kg: Optional[Decimal] = None  # 装药量(kg) Decimal(10,3)
    penetrating_power: Optional[str] = None  # 穿透力 varchar(128)
    drop_height_range_m: Optional[str] = None  # 投放高度范围 varchar(128)
    drop_speed_kmh: Optional[Decimal] = None  # 投放速度(km/h) varchar(128)
    drop_mode: Optional[str] = None  # 投放方式 varchar(128)
    coverage_area: Optional[str] = None  # 覆盖面积 varchar(128)
    range_km: Optional[Decimal] = None  # 射程(km) Decimal(10,3)

    '''
        战斗部特有参数
    '''
    # 爆破战斗部
    is_explosive_bomb: int = 0
    exb_component: Optional[str] = None
    exb_explosion: Optional[Decimal] = None
    exb_weight: Optional[Decimal] = None
    exb_more_parameters: Optional[str] = None

    # 聚能战斗部
    is_energy_bomb: int = 0
    eb_density: Optional[Decimal] = None
    eb_velocity: Optional[Decimal] = None
    eb_pressure: Optional[Decimal] = None
    eb_cover_material: Optional[str] = None
    eb_cone_angle: Optional[Decimal] = None
    eb_more_parameters: Optional[str] = None

    # 破片战斗部
    is_fragment_bomb: int = 0
    fb_bomb_explosion: Optional[Decimal] = None
    fb_fragment_shape: Optional[str] = None
    fb_surface_area: Optional[Decimal] = None
    fb_fragment_weight: Optional[Decimal] = None
    fb_diameter: Optional[Decimal] = None
    fb_length: Optional[Decimal] = None
    fb_shell_weight: Optional[Decimal] = None
    fb_more_parameters: Optional[str] = None

    # 穿甲弹
    is_armor_bomb: int = 0
    ab_bullet_weight: Optional[Decimal] = None
    ab_diameter: Optional[Decimal] = None
    ab_head_length: Optional[Decimal] = None
    ab_more_parameters: Optional[str] = None

    # 子母弹
    is_cluster_bomb: int = 0
    cbm_bullet_weight: Optional[Decimal] = None
    cbm_bullet_section: Optional[Decimal] = None
    cbm_projectile: Optional[Decimal] = None
    cbs_bullet_count: Optional[Decimal] = None
    cbs_bullet_model: Optional[str] = None
    cbs_bullet_weight: Optional[Decimal] = None
    cb_diameter: Optional[Decimal] = None
    cbs_bullet_length: Optional[Decimal] = None
    cb_more_parameters: Optional[str] = None

    # 弹药状态
    am_status: int = 0

    # ===== 审计字段（表中允许空；保持原有风格提供默认值） =====
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # ===== 主键（MySQL 自增；表中为 NOT NULL&PK，但实体可在插入前为空） =====
    am_id: Optional[int] = None

    def update(self, **kwargs) -> None:
        logger.warning("当前实体并非由数据库获取，未绑定SQL的update方法，请先调用repo.add_update_method(am)")
        for k, v in kwargs.items():
            if k in ("am_id", "created_at"):
                continue
            if hasattr(self, k):
                setattr(self, k, v)
        self.updated_at = datetime.utcnow()
