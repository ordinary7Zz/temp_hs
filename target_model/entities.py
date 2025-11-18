from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# 机场跑道
@dataclass
class AirportRunway:
    runway_code: str = ""
    runway_name: str = ""
    country: Optional[str] = None
    base: Optional[str] = None
    runway_picture: Optional[bytes] = None

    r_length: Optional[float] = None
    r_width: Optional[float] = None

    pccsc_thick: Optional[float] = None
    pccsc_strength: Optional[float] = None
    pccsc_flexural: Optional[float] = None
    pccsc_freeze: Optional[float] = None
    pccsc_cement: Optional[str] = None
    pccsc_block_size1: Optional[float] = None
    pccsc_block_size2: Optional[float] = None

    ctbc_thick: Optional[float] = None
    ctbc_strength: Optional[float] = None
    ctbc_flexural: Optional[float] = None
    ctbc_cement: Optional[float] = None
    ctbc_compaction: Optional[float] = None

    gcss_thick: Optional[float] = None
    gcss_strength: Optional[float] = None
    gcss_compaction: Optional[float] = None

    cs_thick: Optional[float] = None
    cs_strength: Optional[float] = None
    cs_compaction: Optional[float] = None

    runway_status: Optional[int] = None
    created_time: datetime = field(default_factory=datetime.utcnow)
    updated_time: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None  # 主键（自增）

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k) and k not in ("id", "createdTime"):
                setattr(self, k, v)
        self.updated_time = datetime.utcnow()


# 机场掩蔽库
@dataclass
class AircraftShelter:
    shelter_code: str = ""
    shelter_name: str = ""
    country: Optional[str] = None
    base: Optional[str] = None
    shelter_picture: Optional[bytes] = None

    shelter_width: Optional[float] = None
    shelter_height: Optional[float] = None
    shelter_length: Optional[float] = None
    cave_width: Optional[float] = None
    cave_height: Optional[float] = None
    structural_form: Optional[str] = None

    door_material: Optional[str] = None
    door_thick: Optional[float] = None

    mask_layer_material: Optional[str] = None
    mask_layer_thick: Optional[float] = None
    soil_layer_material: Optional[str] = None
    soil_layer_thick: Optional[float] = None
    disper_layer_material: Optional[str] = None
    disper_layer_thick: Optional[float] = None
    disper_layer_reinforcement: Optional[str] = None
    structure_layer_material: Optional[str] = None
    structure_layer_thick: Optional[float] = None
    structure_layer_reinforcement: Optional[str] = None

    explosion_resistance: Optional[float] = None
    anti_kinetic: Optional[float] = None
    resistance_depth: Optional[float] = None
    nuclear_blast: Optional[float] = None
    radiation_shielding: Optional[float] = None
    fire_resistance: Optional[float] = None
    shelter_status: Optional[int] = None

    created_time: datetime = field(default_factory=datetime.utcnow)
    updated_time: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k) and k not in ("id", "createdTime"):
                setattr(self, k, v)
        self.updated_time = datetime.utcnow()


# 地下指挥所

@dataclass
class UndergroundCommandPost:
    ucc_code: str = ""
    ucc_name: str = ""
    country: Optional[str] = None
    base: Optional[str] = None
    shelter_picture: Optional[bytes] = None
    location: Optional[str] = None

    rock_layer_materials: str = ""
    rock_layer_thick: Optional[float] = None
    rock_layer_strength: Optional[float] = None

    protective_layer_material: str = ""
    protective_layer_thick: Optional[float] = None
    protective_layer_strength: Optional[float] = None

    lining_layer_material: str = ""
    lining_layer_thick: Optional[float] = None
    lining_layer_strength: Optional[float] = None

    ucc_wall_materials: str = ""
    ucc_wall_thick: Optional[float] = None
    ucc_wall_strength: Optional[float] = None

    ucc_width: Optional[float] = None
    ucc_length: Optional[float] = None
    ucc_height: Optional[float] = None
    ucc_status: Optional[int] = None

    created_time: datetime = field(default_factory=datetime.utcnow)
    updated_time: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None

    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k) and k not in ("id", "createdTime"):
                setattr(self, k, v)
        self.updated_time = datetime.utcnow()
