from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Text, DateTime, DECIMAL, LargeBinary
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy.orm import Mapped, mapped_column, deferred

from am_models.db import Base


class AmmunitionORM(Base):
    __tablename__ = "Ammunition_Info"

    am_id: Mapped[int] = mapped_column(
        "AMID",
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )  # 自增主键

    am_name: Mapped[str] = mapped_column(
        "AMName",
        String(100),
        nullable=False,
    )  # 官方名称

    am_image_blob: Mapped[bytes | None] = deferred(
        mapped_column("AMImage", MEDIUMBLOB, nullable=True)
    )

    chinese_name: Mapped[str] = mapped_column(
        "AMNameCN",
        String(100),
        nullable=True,
    )  # 中文名称

    short_name: Mapped[str] = mapped_column(
        "AMAbbreviation",
        String(60),
        nullable=True,
    )  # 简称

    country: Mapped[str] = mapped_column(
        "Country",
        String(60),
        nullable=True,
    )  # 国家/地区

    used_by: Mapped[str] = mapped_column(
        "Base",
        String(60),
        nullable=True,
    )  # 基地/部队

    am_type: Mapped[str] = mapped_column(
        "AMType",
        String(60),
        nullable=False,
    )  # 弹药类型

    model_name: Mapped[str] = mapped_column(
        "AMModel",
        String(60),
        nullable=False,
    )  # 弹药型号

    submodel_name: Mapped[str] = mapped_column(
        "AMSubmodel",
        String(60),
        nullable=True,
    )  # 型号子类

    manufacturer: Mapped[str] = mapped_column(
        "Manufacturer",
        String(60),
        nullable=True,
    )  # 制造商

    attended_time: Mapped[str] = mapped_column(
        "AttendedDate",
        String(60),
        nullable=True,
    )  # 服役时间

    weight_kg: Mapped[Decimal] = mapped_column(
        "AMWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=False,
    )  # 弹体全重

    length_m: Mapped[Decimal] = mapped_column(
        "AMLength",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 弹体长度

    diameter_m: Mapped[Decimal] = mapped_column(
        "AMDiameter",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 弹体直径

    texture: Mapped[str] = mapped_column(
        "AMTexture",
        String(60),
        nullable=True,
    )  # 弹体材质

    wingspan_close_mm: Mapped[Decimal] = mapped_column(
        "WingspanClose",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 翼展(收)

    wingspan_open_mm: Mapped[Decimal] = mapped_column(
        "WingspanOpen",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 翼展(展)

    structure: Mapped[str] = mapped_column(
        "AMStructure",
        String(60),
        nullable=True,
    )  # 结构

    max_speed_ma: Mapped[Decimal] = mapped_column(
        "MaxSpeed",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 最大速度

    radar_cross_section: Mapped[str] = mapped_column(
        "RadarSection",
        String(60),
        nullable=True,
    )  # 雷达截面

    power_plant: Mapped[str] = mapped_column(
        "AMPower",
        String(60),
        nullable=True,
    )  # 动力装置

    launch_mass_kg: Mapped[Decimal] = mapped_column(
        "LaunchWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=False,
    )  # 发射质量

    warhead_type: Mapped[str] = mapped_column(
        "WarheadType",
        String(60),
        nullable=False,
    )  # 战斗部类型

    warhead_name: Mapped[str] = mapped_column(
        "WarheadName",
        String(60),
        nullable=False,
    )  # 战斗部名称

    destroying_elements: Mapped[str] = mapped_column(
        "Penetrator",
        String(60),
        nullable=True,
    )  # 毁伤元

    fuze: Mapped[str] = mapped_column(
        "Fuze",
        String(60),
        nullable=True,
    )  # 引信

    explosion_equivalent_tnt_t: Mapped[Decimal] = mapped_column(
        "TNTEquivalent",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 爆炸当量(TNT)

    precision_m: Mapped[Decimal] = mapped_column(
        "CEP",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 精度(圆概率误差CEP)

    destroying_mechanism: Mapped[str] = mapped_column(
        "DestroyMechanism",
        String(60),
        nullable=True,
    )  # 破坏机制

    target: Mapped[str] = mapped_column(
        "Targets",
        String(60),
        nullable=True,
    )  # 打击目标

    carrier: Mapped[str] = mapped_column(
        "Carrier",
        String(60),
        nullable=True,
    )  # 载机(投放平台)

    guidance_mode: Mapped[str] = mapped_column(
        "GuidanceMode",
        String(60),
        nullable=True,
    )  # 制导方式

    explosive_payload_kg: Mapped[Decimal] = mapped_column(
        "ChargeAmount",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 装药量

    penetrating_power: Mapped[str] = mapped_column(
        "PenetratePower",
        String(60),
        nullable=True,
    )  # 穿透能力

    drop_height_range_m: Mapped[str] = mapped_column(
        "DropHeight",
        String(60),
        nullable=True,
    )  # 投弹高度范围

    drop_speed_kmh: Mapped[Decimal] = mapped_column(
        "DropSpeed",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 投弹速度

    drop_mode: Mapped[str] = mapped_column(
        "DropMode",
        String(60),
        nullable=True,
    )  # 投弹方式

    coverage_area: Mapped[str] = mapped_column(
        "CoverageArea",
        String(60),
        nullable=True,
    )  # 布撒范围

    range_km: Mapped[Decimal] = mapped_column(
        "FlightRange",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 射程

    is_explosive_bomb: Mapped[int] = mapped_column(
        "IsExplosiveBomb",
        Integer,
        nullable=False,
    )  # 爆破战斗部标识

    exb_component: Mapped[str] = mapped_column(
        "EXBComponent",
        String(60),
        nullable=True,
    )  # 炸药成分

    exb_explosion: Mapped[Decimal] = mapped_column(
        "EXBExplosion",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 炸药热爆

    exb_weight: Mapped[Decimal] = mapped_column(
        "EXBWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 装药质量

    exb_more_parameters: Mapped[str] = mapped_column(
        "EXBMoreParameters",
        Text,
        nullable=True,
    )  # 爆破弹其他参数

    is_energy_bomb: Mapped[int] = mapped_column(
        "IsEnergyBomb",
        Integer,
        nullable=False,
    )  # 聚能战斗部标识

    eb_density: Mapped[Decimal] = mapped_column(
        "EBDensity",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 炸药密度

    eb_velocity: Mapped[Decimal] = mapped_column(
        "EBVelocity",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 装药爆速

    eb_pressure: Mapped[Decimal] = mapped_column(
        "EBPressure",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 爆轰压

    eb_cover_material: Mapped[str] = mapped_column(
        "EBCoverMaterial",
        String(60),
        nullable=True,
    )  # 覆盖材料

    eb_cone_angle: Mapped[Decimal] = mapped_column(
        "EBConeAngle",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 锥角

    eb_more_parameters: Mapped[str] = mapped_column(
        "EBMoreParameters",
        Text,
        nullable=True,
    )  # 聚能弹其他参数

    is_fragment_bomb: Mapped[int] = mapped_column(
        "IsFragmentBomb",
        Integer,
        nullable=False,
    )  # 破片战斗部标识

    fb_bomb_explosion: Mapped[Decimal] = mapped_column(
        "FBBombExplosion",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 炸弹热爆

    fb_fragment_shape: Mapped[str] = mapped_column(
        "FBFragmentShape",
        Text,
        nullable=True,
    )  # 破片形状

    fb_surface_area: Mapped[Decimal] = mapped_column(
        "FBSurfaceArea",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 破片表面积

    fb_fragment_weight: Mapped[Decimal] = mapped_column(
        "FBFragmentWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 破片质量

    fb_diameter: Mapped[Decimal] = mapped_column(
        "FBDiameter",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 装药直径

    fb_length: Mapped[Decimal] = mapped_column(
        "FBLength",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 装药长度

    fb_shell_weight: Mapped[Decimal] = mapped_column(
        "FBShellWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 壳体质量

    fb_more_parameters: Mapped[str] = mapped_column(
        "FBMoreParameters",
        Text,
        nullable=True,
    )  # 破片弹其他参数

    is_armor_bomb: Mapped[int] = mapped_column(
        "IsArmorBomb",
        Integer,
        nullable=False,
    )  # 穿甲弹战斗部标识

    ab_bullet_weight: Mapped[Decimal] = mapped_column(
        "ABBulletWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 弹丸质量

    ab_diameter: Mapped[Decimal] = mapped_column(
        "ABDiameter",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 弹丸直径

    ab_head_length: Mapped[Decimal] = mapped_column(
        "ABHeadLength",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 弹丸头部长度

    ab_more_parameters: Mapped[str] = mapped_column(
        "ABMoreParameters",
        Text,
        nullable=True,
    )  # 穿甲弹其他参数

    is_cluster_bomb: Mapped[int] = mapped_column(
        "IsClusterBomb",
        Integer,
        nullable=False,
    )  # 子母弹战斗部标识

    cbm_bullet_weight: Mapped[Decimal] = mapped_column(
        "CBMBulletWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 母弹质量

    cbm_bullet_section: Mapped[Decimal] = mapped_column(
        "CBMBulletSection",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 母弹最大横截面

    cbm_projectile: Mapped[Decimal] = mapped_column(
        "CBMProjectile",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 母弹阻力系数

    cbs_bullet_count: Mapped[Decimal] = mapped_column(
        "CBSBulletCount",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 子弹数量

    cbs_bullet_model: Mapped[str] = mapped_column(
        "CBSBulletModel",
        String(60),
        nullable=True,
    )  # 子弹型号

    cbs_bullet_weight: Mapped[Decimal] = mapped_column(
        "CBSBulletWeight",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 子弹质量

    cb_diameter: Mapped[Decimal] = mapped_column(
        "CBDiameter",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 最大直径

    cbs_bullet_length: Mapped[Decimal] = mapped_column(
        "CBSBulletLength",
        DECIMAL(precision=10, scale=3, asdecimal=True),
        nullable=True,
    )  # 子弹参考长度

    cb_more_parameters: Mapped[str] = mapped_column(
        "CBMoreParameters",
        Text,
        nullable=True,
    )  # 子母弹其他参数

    am_status: Mapped[int] = mapped_column(
        "AMStatus",
        Integer,
        nullable=True,
        default=1,
    )  # 弹药状态

    created_time: Mapped[datetime] = mapped_column(
        "CreatedTime",
        DateTime(timezone=False),
        nullable=True,
    )  # 创建时间(UTC)

    updated_time: Mapped[datetime] = mapped_column(
        "UpdatedTime",
        DateTime(timezone=False),
        nullable=True,
    )  # 更新时间(UTC)
