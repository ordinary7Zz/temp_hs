from __future__ import annotations

import logging
from typing import List, Optional, Callable, Dict, Sequence, Any
from datetime import datetime

from loguru import logger
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import Session

from .entities import Ammunition
from .orm import AmmunitionORM


class SQLRepository:
    """Ammunition 的 MySQL 仓储：支持 list_all / get / add / update / delete。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------- Query ----------

    def list_all(self) -> List[Ammunition]:
        rows = self.session.scalars(select(AmmunitionORM)).all()
        ents = [self.to_entity(r) for r in rows]
        for e in ents:
            self.add_update_method(e)
        return ents

    def get(self, item_id: int) -> Optional[Ammunition]:
        row = self.session.get(AmmunitionORM, item_id)
        if not row:
            return None
        ent = self.to_entity(row)
        self.add_update_method(ent)
        return ent

    def list_columns(
            self,
            columns: Sequence[str],
            *,
            where: Optional[Callable[[AmmunitionORM], Any]] = None,
            order_by: Optional[Sequence[str]] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        只查询指定列，返回 [{col: value, ...}, ...]
        - columns: 例如 ["am_id", "am_name", "country"]
        - where:   可传函数，接收 AmmunitionORM，返回可用于 .where(...) 的表达式
                   例如 where=lambda T: T.country == "China"
        - order_by: 例如 ["am_id"] 或 ["-created_time", "am_name"]（前缀 '-' 表示倒序）
        - limit/offset: 分页

        用法示例：
            rows = repo.list_columns(["am_id","am_name"], where=lambda T: T.country=="China",
                                     order_by=["-am_id"], limit=50)
        """
        if not columns:
            return []

        # 1) 解析列对象
        orm_cols = []
        for name in columns:
            try:
                col = getattr(AmmunitionORM, name)
            except AttributeError:
                raise ValueError(f"Unknown column: {name!r}")
            orm_cols.append(col.label(name))  # 用 label 保持返回字典键与传入名称一致

        # 2) 组装语句
        stmt = select(*orm_cols)
        if where is not None:
            expr = where(AmmunitionORM) if callable(where) else where
            if expr is not None:
                stmt = stmt.where(expr)

        # 3) 排序解析："-field" 为 desc，其余 asc
        if order_by:
            order_items = []
            for key in order_by:
                if key.startswith("-"):
                    colname = key[1:]
                    col = getattr(AmmunitionORM, colname, None)
                    if col is None:
                        raise ValueError(f"Unknown order_by column: {colname!r}")
                    order_items.append(desc(col))
                else:
                    col = getattr(AmmunitionORM, key, None)
                    if col is None:
                        raise ValueError(f"Unknown order_by column: {key!r}")
                    order_items.append(asc(col))
            if order_items:
                stmt = stmt.order_by(*order_items)

        if limit is not None:
            stmt = stmt.limit(int(limit))
        if offset is not None:
            stmt = stmt.offset(int(offset))

        # 4) 执行并转成字典列表
        result = self.session.execute(stmt).all()
        # result 中的每行是一个元组，顺序与 orm_cols 匹配
        out: List[Dict[str, Any]] = [dict(zip(columns, row)) for row in result]
        return out

    # ---------- Mutations ----------

    def add(self, item: Ammunition) -> Ammunition:
        row = AmmunitionORM()
        # 创建时设置时间戳（若实体没设的话）
        if not item.created_at:
            item.created_at = datetime.utcnow()
        item.updated_at = datetime.utcnow()

        self._assign_row_from_entity(row, item, for_create=True)
        self.session.add(row)
        self.session.flush()  # 获取自增主键
        # 回写主键
        item.am_id = row.am_id

        # 绑定原地更新方法
        self.add_update_method(item)
        return item

    def add_update_method(self, e: Ammunition) -> None:
        """
        给实体实例动态绑定 am.update() 方法，直接落库。
        说明：
        - 这是“实例级”绑定，不影响类定义；若实体类已有 update()，
          此绑定会在实例上覆盖类方法（符合“直接改，不兼容旧版”的要求）。
        - 使用方式：
              am = repo.get(123)
              am.chinese_name = "xxx"
              am.update()              # 立即同步到 DB（需要在外层事务 commit）
        """
        repo = self

        def _inst_update():
            return repo.update_entity(e)

        # 动态绑定实例方法
        setattr(e, "update", _inst_update)

    def update_entity(self, e: Ammunition) -> Ammunition:
        """
        将实体 e 当前字段原地同步到数据库。
        要求 e.am_id 存在；函数会刷新 updated_at。
        """
        logger.debug(f"update_entity: {e}")
        e.updated_at = datetime.utcnow()
        if not e.am_id:
            raise ValueError("Ammunition.am_id is required for update")

        row = self.session.get(AmmunitionORM, e.am_id)
        if not row:
            raise KeyError(f"Item am_id={e.am_id} not found")

        # 更新时间戳
        e.updated_at = datetime.utcnow()

        # 回写所有字段
        self._assign_row_from_entity(row, e, for_create=False)
        self.session.flush()
        return e

    def delete(self, item_id: int) -> bool:
        row = self.session.get(AmmunitionORM, item_id)
        if not row:
            return False
        self.session.delete(row)
        return True

    # ---------- Helpers ----------

    @staticmethod
    def to_entity(r: AmmunitionORM, include_blob: bool = True) -> Ammunition:
        """ORM -> 实体（字段全集映射）"""
        if r is None:
            return None  # type: ignore[return-value]

        return Ammunition(
            # 主键
            am_id=r.am_id,

            # 必填
            am_name=r.am_name,
            am_image_blob=(r.am_image_blob if include_blob else None),
            am_type=r.am_type,
            model_name=r.model_name,
            weight_kg=r.weight_kg,
            launch_mass_kg=r.launch_mass_kg,
            warhead_type=r.warhead_type,
            warhead_name=r.warhead_name,

            # 可选
            country=r.country,
            used_by=r.used_by,
            chinese_name=r.chinese_name,
            short_name=r.short_name,
            submodel_name=r.submodel_name,
            manufacturer=r.manufacturer,
            attended_time=r.attended_time,

            length_m=r.length_m,
            diameter_m=r.diameter_m,
            texture=r.texture,
            wingspan_close_mm=r.wingspan_close_mm,
            wingspan_open_mm=r.wingspan_open_mm,
            structure=r.structure,

            max_speed_ma=r.max_speed_ma,
            radar_cross_section=r.radar_cross_section,
            power_plant=r.power_plant,

            destroying_elements=r.destroying_elements,
            fuze=r.fuze,
            explosion_equivalent_TNT_T=r.explosion_equivalent_tnt_t,
            precision_m=r.precision_m,
            destroying_mechanism=r.destroying_mechanism,

            target=r.target,
            carrier=r.carrier,
            guidance_mode=r.guidance_mode,
            explosive_payload_kg=r.explosive_payload_kg,
            penetrating_power=r.penetrating_power,
            drop_height_range_m=r.drop_height_range_m,
            drop_speed_kmh=r.drop_speed_kmh,
            drop_mode=r.drop_mode,
            coverage_area=r.coverage_area,
            range_km=r.range_km,

            is_explosive_bomb=r.is_explosive_bomb,
            exb_component=r.exb_component,
            exb_explosion=r.exb_explosion,
            exb_weight=r.exb_weight,
            exb_more_parameters=r.exb_more_parameters,

            is_energy_bomb=r.is_energy_bomb,
            eb_density=r.eb_density,
            eb_velocity=r.eb_velocity,
            eb_pressure=r.eb_pressure,
            eb_cover_material=r.eb_cover_material,
            eb_cone_angle=r.eb_cone_angle,
            eb_more_parameters=r.eb_more_parameters,

            is_fragment_bomb=r.is_fragment_bomb,
            fb_bomb_explosion=r.fb_bomb_explosion,
            fb_fragment_shape=r.fb_fragment_shape,
            fb_surface_area=r.fb_surface_area,
            fb_fragment_weight=r.fb_fragment_weight,
            fb_diameter=r.fb_diameter,
            fb_length=r.fb_length,
            fb_shell_weight=r.fb_shell_weight,
            fb_more_parameters=r.fb_more_parameters,

            is_armor_bomb=r.is_armor_bomb,
            ab_bullet_weight=r.ab_bullet_weight,
            ab_diameter=r.ab_diameter,
            ab_head_length=r.ab_head_length,
            ab_more_parameters=r.ab_more_parameters,

            is_cluster_bomb=r.is_cluster_bomb,
            cbm_bullet_weight=r.cbm_bullet_weight,
            cbm_bullet_section=r.cbm_bullet_section,
            cbm_projectile=r.cbm_projectile,
            cbs_bullet_count=r.cbs_bullet_count,
            cbs_bullet_model=r.cbs_bullet_model,
            cbs_bullet_weight=r.cbs_bullet_weight,
            cb_diameter=r.cb_diameter,
            cbs_bullet_length=r.cbs_bullet_length,
            cb_more_parameters=r.cb_more_parameters,

            am_status=r.am_status,

            created_at=r.created_time,
            updated_at=r.updated_time,
        )

    @staticmethod
    def _assign_row_from_entity(row: AmmunitionORM, e: Ammunition, *, for_create: bool) -> None:
        """
        实体 -> ORM；for_create 创建时不回写主键，更新时也不允许改主键/created_at。
        """
        # 主键（仅创建完成后由数据库生成，不在这里设置）
        if not for_create and e.am_id is not None:
            row.am_id = e.am_id  # 一般不改；保持与传入一致

        # 必填字段
        row.am_name = e.am_name
        row.am_image_blob = e.am_image_blob
        row.am_type = e.am_type
        row.launch_mass_kg = e.launch_mass_kg
        row.warhead_type = e.warhead_type
        row.warhead_name = e.warhead_name

        # 可选字段
        row.country = e.country
        row.used_by = e.used_by
        row.chinese_name = e.chinese_name
        row.short_name = e.short_name
        row.model_name = e.model_name
        row.submodel_name = e.submodel_name
        row.manufacturer = e.manufacturer
        row.attended_time = e.attended_time

        row.weight_kg = e.weight_kg
        row.length_m = e.length_m
        row.diameter_m = e.diameter_m
        row.texture = e.texture
        row.wingspan_close_mm = e.wingspan_close_mm
        row.wingspan_open_mm = e.wingspan_open_mm
        row.structure = e.structure

        row.max_speed_ma = e.max_speed_ma
        row.radar_cross_section = e.radar_cross_section
        row.power_plant = e.power_plant

        row.destroying_elements = e.destroying_elements
        row.fuze = e.fuze
        row.explosion_equivalent_tnt_t = e.explosion_equivalent_TNT_T
        row.precision_m = e.precision_m
        row.destroying_mechanism = e.destroying_mechanism

        row.target = e.target
        row.carrier = e.carrier
        row.guidance_mode = e.guidance_mode
        row.explosive_payload_kg = e.explosive_payload_kg
        row.penetrating_power = e.penetrating_power
        row.drop_height_range_m = e.drop_height_range_m
        row.drop_speed_kmh = e.drop_speed_kmh
        row.drop_mode = e.drop_mode
        row.coverage_area = e.coverage_area
        row.range_km = e.range_km

        row.is_explosive_bomb = e.is_explosive_bomb
        row.exb_component = e.exb_component
        row.exb_explosion = e.exb_explosion
        row.exb_weight = e.exb_weight
        row.exb_more_parameters = e.exb_more_parameters

        row.is_energy_bomb = e.is_energy_bomb
        row.eb_density = e.eb_density
        row.eb_velocity = e.eb_velocity
        row.eb_pressure = e.eb_pressure
        row.eb_cover_material = e.eb_cover_material
        row.eb_cone_angle = e.eb_cone_angle
        row.eb_more_parameters = e.eb_more_parameters

        row.is_fragment_bomb = e.is_fragment_bomb
        row.fb_bomb_explosion = e.fb_bomb_explosion
        row.fb_fragment_shape = e.fb_fragment_shape
        row.fb_surface_area = e.fb_surface_area
        row.fb_fragment_weight = e.fb_fragment_weight
        row.fb_diameter = e.fb_diameter
        row.fb_length = e.fb_length
        row.fb_shell_weight = e.fb_shell_weight
        row.fb_more_parameters = e.fb_more_parameters

        row.is_armor_bomb = e.is_armor_bomb
        row.ab_bullet_weight = e.ab_bullet_weight
        row.ab_diameter = e.ab_diameter
        row.ab_head_length = e.ab_head_length
        row.ab_more_parameters = e.ab_more_parameters

        row.is_cluster_bomb = e.is_cluster_bomb
        row.cbm_bullet_weight = e.cbm_bullet_weight
        row.cbm_bullet_section = e.cbm_bullet_section
        row.cbm_projectile = e.cbm_projectile
        row.cbs_bullet_count = e.cbs_bullet_count
        row.cbs_bullet_model = e.cbs_bullet_model
        row.cbs_bullet_weight = e.cbs_bullet_weight
        row.cb_diameter = e.cb_diameter
        row.cbs_bullet_length = e.cbs_bullet_length
        row.cb_more_parameters = e.cb_more_parameters

        row.am_status = 1

        # 审计字段：创建时尽量保留实体默认；更新时不改 created_at，仅改 updated_at
        if for_create:
            row.created_at = e.created_at
            row.updated_at = e.updated_at
        else:
            # created_at 不动
            row.updated_at = e.updated_at or datetime.utcnow()
