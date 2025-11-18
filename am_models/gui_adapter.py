from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional
import json

from .entities import Ammunition


# -------- Helpers --------
def to_decimal_or_none(x: Any) -> Optional[Decimal]:
    if x is None:
        return None
    if isinstance(x, Decimal):
        return x
    s = str(x).strip()
    if s == "":
        return None
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _to_str_or_none(x: Any) -> Optional[str]:
    if x is None:
        return None
    s = str(x)
    return s if s != "" else None


# ---------- UI JSON -> Ammunition ----------
def ui_json_to_ammunition(data: Dict[str, Any], image: bytes = None) -> Ammunition:
    """
    将 UI 收集的嵌套 JSON（basic/struct/warhead_fcs/warhead_params）
    解析为 Ammunition 实体。对缺失/空串做容错。
    """
    basic = data.get("basic", {}) or {}
    struct = data.get("struct", {}) or {}
    fcs = data.get("warhead_fcs", {}) or {}
    wps = data.get("warhead_params", {}) or {}
    wps_exp = wps.get("blast_warhead", {})
    wps_eb = wps.get("shaped_charge_warhead", {})
    wps_fb = wps.get("fragmentation_warhead", {})
    wps_ab = wps.get("armor_piercing_warhead", {})
    wps_cb = wps.get("cluster_warhead", {})

    # 名称优先级：中文名 > 官方名 > 简称
    am_name = _to_str_or_none(basic.get("official_name"))or ""
     # am_name = (
    #         _to_str_or_none(basic.get("chinese_name"))
    #         or _to_str_or_none(basic.get("official_name"))
    #         or _to_str_or_none(basic.get("short_name"))
    #         or "UNKNOWN"
    # )
    #

    # 必填字段（实体层面必需）
    am_type = _to_str_or_none(basic.get("ammunition_type")) or "UNKNOWN"
    #official_name = _to_str_or_none(basic.get("official_name")) or ""
    weight_kg = to_decimal_or_none(struct.get("weight_kg")) or Decimal("0")
    launch_mass_kg = to_decimal_or_none(struct.get("launch_mass_kg")) or Decimal("0")
    warhead_type = _to_str_or_none(fcs.get("warhead_type")) or "UNKNOWN"
    warhead_name = _to_str_or_none(fcs.get("warhead_name")) or ""

    # 可选字段
    e = Ammunition(
        # 主键插入前为空
        am_id=None,

        # 必填
        am_name=am_name,
        am_image_blob=image,
        am_type=am_type,
        weight_kg=weight_kg,
        launch_mass_kg=launch_mass_kg,
        warhead_type=warhead_type,
        warhead_name=warhead_name,

        # basic
        country=_to_str_or_none(basic.get("country")),
        used_by=_to_str_or_none(basic.get("used_by")),
        chinese_name=_to_str_or_none(basic.get("chinese_name")),
        short_name=_to_str_or_none(basic.get("short_name")),
        model_name=_to_str_or_none(basic.get("model_name")),
        submodel_name=_to_str_or_none(basic.get("submodel_name")),
        manufacturer=_to_str_or_none(basic.get("manufacturer")),
        attended_time=_to_str_or_none(basic.get("attended_time")),

        # struct
        length_m=to_decimal_or_none(struct.get("length_m")),
        diameter_m=to_decimal_or_none(struct.get("diameter_m")),
        texture=_to_str_or_none(struct.get("texture")),
        wingspan_close_mm=to_decimal_or_none(struct.get("wingspan_close_mm")),
        wingspan_open_mm=to_decimal_or_none(struct.get("wingspan_open_mm")),
        structure=_to_str_or_none(struct.get("structure")),
        max_speed_ma=to_decimal_or_none(struct.get("max_speed_ma")),
        radar_cross_section=_to_str_or_none(struct.get("radar_cross_section")),
        power_plant=_to_str_or_none(struct.get("power_plant")),

        # fcs
        destroying_elements=_to_str_or_none(fcs.get("destroying_elements")),
        fuze=_to_str_or_none(fcs.get("fuze")),
        explosion_equivalent_TNT_T=to_decimal_or_none(fcs.get("explosion_equivalent_TNT_T")),
        precision_m=to_decimal_or_none(fcs.get("precision_m")),
        destroying_mechanism=_to_str_or_none(fcs.get("destroying_mechanism")),
        target=_to_str_or_none(fcs.get("target")),
        carrier=_to_str_or_none(fcs.get("carrier")),
        guidance_mode=_to_str_or_none(fcs.get("guidance_mode")),
        explosive_payload_kg=to_decimal_or_none(fcs.get("explosive_payload_kg")),
        penetrating_power=_to_str_or_none(fcs.get("penetrating_power")),
        drop_height_range_m=_to_str_or_none(fcs.get("drop_height_range_m")),
        drop_speed_kmh=_to_str_or_none(fcs.get("drop_speed_kmh")),
        drop_mode=_to_str_or_none(fcs.get("drop_mode")),
        coverage_area=_to_str_or_none(fcs.get("coverage_area")),
        range_km=to_decimal_or_none(fcs.get("range_km")),

        is_explosive_bomb=1 if warhead_type == "爆破战斗部" else 0,
        exb_component=_to_str_or_none(wps_exp.get("explosive_comp")),
        exb_explosion=to_decimal_or_none(wps_exp.get("explosive_thermal_explosion")),
        exb_weight=to_decimal_or_none(wps_exp.get("actual_charge_mass")),
        # exb_more_parameters=_to_str_or_none(wps_exp.get("exb_more_parameters")),

        is_energy_bomb=1 if warhead_type == "聚能战斗部" else 0,
        eb_density=to_decimal_or_none(wps_eb.get("explosive_density")),
        eb_velocity=to_decimal_or_none(wps_eb.get("charge_detonation_velocity")),
        eb_pressure=to_decimal_or_none(wps_eb.get("detonation_pressure")),
        eb_cover_material=_to_str_or_none(wps_eb.get("liner_material")),
        eb_cone_angle=to_decimal_or_none(wps_eb.get("liner_cone_angle")),
        # eb_more_parameters=_to_str_or_none(wps_eb.get("eb_more_parameters")),

        is_fragment_bomb=1 if warhead_type == "破片战斗部" else 0,
        fb_bomb_explosion=to_decimal_or_none(wps_fb.get("explosive_thermal_explosion")),
        fb_fragment_shape=_to_str_or_none(wps_fb.get("fragment_shape")),
        fb_surface_area=to_decimal_or_none(wps_fb.get("fragment_surface_area")),
        fb_fragment_weight=to_decimal_or_none(wps_fb.get("fragment_mass")),
        fb_diameter=to_decimal_or_none(wps_fb.get("charge_diameter")),
        fb_length=to_decimal_or_none(wps_fb.get("charge_length")),
        fb_shell_weight=to_decimal_or_none(wps_fb.get("case_mass_fragment")),
        # fb_more_parameters=_to_str_or_none(wps_fb.get("fb_more_parameters")),

        is_armor_bomb=1 if warhead_type == "穿甲战斗部" else 0,
        ab_bullet_weight=to_decimal_or_none(wps_ab.get("projectile_mass")),
        ab_diameter=to_decimal_or_none(wps_ab.get("projectile_diameter")),
        ab_head_length=to_decimal_or_none(wps_ab.get("projectile_nose_length")),
        # ab_more_parameters=_to_str_or_none(wps_ab.get("ab_more_parameters")),

        is_cluster_bomb=1 if warhead_type == "子母战斗部" else 0,
        cbm_bullet_weight=to_decimal_or_none(wps_cb.get("warhead_mass")),
        cbm_bullet_section=to_decimal_or_none(wps_cb.get("warhead_ref_area")),
        cbm_projectile=to_decimal_or_none(wps_cb.get("warhead_drag_coefficient")),
        cbs_bullet_count=to_decimal_or_none(wps_cb.get("submunition_count")),
        cbs_bullet_model=_to_str_or_none(wps_cb.get("submunition_model")),
        cbs_bullet_weight=to_decimal_or_none(wps_cb.get("submunition_mass")),
        cb_diameter=to_decimal_or_none(wps_cb.get("max_diameter")),
        cbs_bullet_length=to_decimal_or_none(wps_cb.get("submunition_ref_area")),
        # cb_more_parameters=_to_str_or_none(wps_cb.get("cb_more_parameters")),

        am_status=1,

        # 审计（保持现有风格）
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    return e


# ---------- Ammunition -> UI JSON ----------
def ammunition_to_ui_json(a: Ammunition) -> Dict[str, Any]:
    """
    将 Ammunition 导出为 UI 侧 JSON 结构。对 None 输出为空串 ""，以便前端绑定。
    未在实体中出现的 UI 字段（如 vendor）保留键但置空。
    """

    def S(x: Optional[str]) -> str:
        return "" if x is None else x

    def D(x: Optional[Decimal]) -> str:
        return "" if x is None else str(x)

    out = {
        "basic": {
            "country": S(a.country),
            "used_by": S(a.used_by),
            "ammunition_type": S(a.am_type),
            "official_name": S(a.am_name),
            "chinese_name": S(a.chinese_name),
            "short_name": S(a.short_name),
            "model_name": S(a.model_name),
            "submodel_name": S(a.submodel_name),
            "manufacturer": S(a.manufacturer),
            "vendor": "",  # 模型无该字段，保留键
            "attended_time": S(a.attended_time),
        },
        "struct": {
            "weight_kg": D(a.weight_kg),
            "length_m": D(a.length_m),
            "diameter_m": D(a.diameter_m),
            "texture": S(a.texture),
            "wingspan_close_mm": D(a.wingspan_close_mm),
            "wingspan_open_mm": D(a.wingspan_open_mm),
            "structure": S(a.structure),
            "max_speed_ma": D(a.max_speed_ma),
            "radar_cross_section": S(a.radar_cross_section),
            "power_plant": S(a.power_plant),
            "launch_mass_kg": D(a.launch_mass_kg),
        },
        "warhead_fcs": {
            "warhead_type": S(a.warhead_type),
            "warhead_name": S(a.warhead_name),
            "destroying_elements": S(a.destroying_elements),
            "fuze": S(a.fuze),
            "explosion_equivalent_TNT_T": D(a.explosion_equivalent_TNT_T),
            "precision_m": D(a.precision_m),
            "destroying_mechanism": S(a.destroying_mechanism),
            "target": S(a.target),
            "carrier": S(a.carrier),
            "guidance_mode": S(a.guidance_mode),
            "explosive_payload_kg": D(a.explosive_payload_kg),
            "penetrating_power": S(a.penetrating_power),
            "drop_height_range_m": S(a.drop_height_range_m),
            "drop_speed_kmh": D(a.drop_speed_kmh),
            "drop_mode": S(a.drop_mode),
            "coverage_area": S(a.coverage_area),
            "range_km": D(a.range_km),
        },
        "warhead_params": {
            "blast_warhead": {
                "explosive_comp": S(a.exb_component),
                "explosive_thermal_explosion": D(a.exb_explosion),
                "actual_charge_mass": D(a.exb_weight),
            },
            "shaped_charge_warhead": {
                "explosive_density": D(a.eb_density),
                "charge_detonation_velocity": D(a.eb_velocity),
                "detonation_pressure": D(a.eb_pressure),
                "liner_material": S(a.eb_cover_material),
                "liner_cone_angle": D(a.eb_cone_angle),
            },
            "fragmentation_warhead": {
                "explosive_thermal_explosion": D(a.fb_bomb_explosion),
                "case_mass_fragment": D(a.fb_shell_weight),
                "fragment_shape": S(a.fb_fragment_shape),
                "fragment_surface_area": D(a.fb_surface_area),
                "fragment_mass": D(a.fb_fragment_weight),
                "charge_diameter": D(a.fb_diameter),
                "charge_length": D(a.fb_length),
            },
            "armor_piercing_warhead": {
                "projectile_mass": D(a.ab_bullet_weight),
                "projectile_nose_length": D(a.ab_head_length),
                "projectile_diameter": D(a.ab_diameter),
            },
            "cluster_warhead": {
                "warhead_mass": D(a.cbm_bullet_weight),
                "warhead_ref_area": D(a.cbm_bullet_section),
                "warhead_drag_coefficient": D(a.cbm_projectile),
                "submunition_count": D(a.cbs_bullet_count),
                "submunition_model": S(a.cbs_bullet_model),
                "submunition_mass": D(a.cbs_bullet_weight),
                "max_diameter": D(a.cb_diameter),
                "submunition_ref_area": D(a.cbs_bullet_length),
            },
        },

    }

    return out
