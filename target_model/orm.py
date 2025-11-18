from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from target_model.db import Base


class AirportRunwayORM(Base):
    __tablename__ = "Runway_Info"

    id: Mapped[int] = mapped_column("RunwayID", Integer, primary_key=True, autoincrement=True)

    runway_code: Mapped[str] = mapped_column("RunwayCode", String(60), nullable=False, unique=True, index=True)
    runway_name: Mapped[str] = mapped_column("RunwayName", String(60), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column("Country", String(60), nullable=True, index=True)
    base: Mapped[str | None] = mapped_column("Base", String(60), nullable=True)
    runway_picture: Mapped[bytes | None] = mapped_column("RunwayPicture", LargeBinary, nullable=True)

    r_length: Mapped[float] = mapped_column("RLength", Float(asdecimal=False), nullable=False)
    r_width: Mapped[float] = mapped_column("RWidth", Float(asdecimal=False), nullable=False)

    pccsc_thick: Mapped[float] = mapped_column("PCCSCThick", Float(asdecimal=False), nullable=False)
    pccsc_strength: Mapped[float] = mapped_column("PCCSCStrength", Float(asdecimal=False), nullable=False)
    pccsc_flexural: Mapped[float | None] = mapped_column("PCCSCFlexural", Float(asdecimal=False), nullable=True)
    pccsc_freeze: Mapped[float | None] = mapped_column("PCCSCFreeze", Float(asdecimal=False), nullable=True)
    pccsc_cement: Mapped[str | None] = mapped_column("PCCSCCement", String(60), nullable=True)
    pccsc_block_size1: Mapped[float | None] = mapped_column("PCCSCBlockSize1", Float(asdecimal=False), nullable=True)
    pccsc_block_size2: Mapped[float | None] = mapped_column("PCCSCBlockSize2", Float(asdecimal=False), nullable=True)

    ctbc_thick: Mapped[float] = mapped_column("CTBCThick", Float(asdecimal=False), nullable=False)
    ctbc_strength: Mapped[float] = mapped_column("CTBCStrength", Float(asdecimal=False), nullable=False)
    ctbc_flexural: Mapped[float | None] = mapped_column("CTBCFlexural", Float(asdecimal=False), nullable=True)
    ctbc_cement: Mapped[float | None] = mapped_column("CTBCCement", Float(asdecimal=False), nullable=True)
    ctbc_compaction: Mapped[float | None] = mapped_column("CTBCCompaction", Float(asdecimal=False), nullable=True)

    gcss_thick: Mapped[float] = mapped_column("GCSSThick", Float(asdecimal=False), nullable=False)
    gcss_strength: Mapped[float | None] = mapped_column("GCSSStrength", Float(asdecimal=False), nullable=True)
    gcss_compaction: Mapped[float | None] = mapped_column("GCSSCompaction", Float(asdecimal=False), nullable=True)

    cs_thick: Mapped[float] = mapped_column("CSThick", Float(asdecimal=False), nullable=False)
    cs_strength: Mapped[float | None] = mapped_column("CSStrength", Float(asdecimal=False), nullable=True)
    cs_compaction: Mapped[float | None] = mapped_column("CSCompaction", Float(asdecimal=False), nullable=True)

    runway_status: Mapped[int | None] = mapped_column("RunwayStatus", Integer, nullable=True, default=1)
    created_time: Mapped[datetime] = mapped_column(
        "CreatedTime", DateTime(timezone=False), default=datetime.utcnow, nullable=True
    )
    updated_time: Mapped[datetime] = mapped_column(
        "UpdatedTime", DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )


class AircraftShelterORM(Base):
    __tablename__ = "Shelter_Info"

    id: Mapped[int] = mapped_column("ShelterID", Integer, primary_key=True, autoincrement=True)

    shelter_code: Mapped[str] = mapped_column("ShelterCode", String(60), nullable=False, unique=True, index=True)
    shelter_name: Mapped[str] = mapped_column("ShelterName", String(60), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column("Country", String(60), nullable=True, index=True)
    base: Mapped[str | None] = mapped_column("Base", String(60), nullable=True)
    shelter_picture: Mapped[bytes | None] = mapped_column("ShelterPicture", LargeBinary, nullable=True)

    shelter_width: Mapped[float] = mapped_column("ShelterWidth", Float(asdecimal=False), nullable=False)
    shelter_height: Mapped[float] = mapped_column("ShelterHeight", Float(asdecimal=False), nullable=False)
    shelter_length: Mapped[float] = mapped_column("ShelterLength", Float(asdecimal=False), nullable=False)
    cave_width: Mapped[float | None] = mapped_column("CaveWidth", Float(asdecimal=False), nullable=True)
    cave_height: Mapped[float | None] = mapped_column("CaveHeight", Float(asdecimal=False), nullable=True)
    structural_form: Mapped[str | None] = mapped_column("StructuralForm", String(60), nullable=True)

    door_material: Mapped[str | None] = mapped_column("DoorMaterial", String(60), nullable=True)
    door_thick: Mapped[float | None] = mapped_column("DoorThick", Float(asdecimal=False), nullable=True)

    mask_layer_material: Mapped[str] = mapped_column("MaskLayerMaterial", String(60), nullable=False)
    mask_layer_thick: Mapped[float] = mapped_column("MaskLayerThick", Float(asdecimal=False), nullable=False)
    soil_layer_material: Mapped[str] = mapped_column("SoilLayerMaterial", String(60), nullable=False)
    soil_layer_thick: Mapped[float] = mapped_column("SoilLayerThick", Float(asdecimal=False), nullable=False)
    disper_layer_material: Mapped[str] = mapped_column("DisperLayerMaterial", String(16), nullable=False)
    disper_layer_thick: Mapped[float] = mapped_column("DisperLayerThick", Float(asdecimal=False), nullable=False)
    disper_layer_reinforcement: Mapped[str | None] = mapped_column("DisperLayerReinforcement", String(60),
                                                                   nullable=True)
    structure_layer_material: Mapped[str] = mapped_column("StructureLayerMaterial", String(16), nullable=False)
    structure_layer_thick: Mapped[float] = mapped_column("StructureLayerThick", Float(asdecimal=False), nullable=False)
    structure_layer_reinforcement: Mapped[str | None] = mapped_column(
        "StructureLayerReinforcement", String(60), nullable=True
    )

    explosion_resistance: Mapped[float | None] = mapped_column(
        "ExplosionResistance", Float(asdecimal=False), nullable=True
    )
    anti_kinetic: Mapped[float | None] = mapped_column("AntiKinetic", Float(asdecimal=False), nullable=True)
    resistance_depth: Mapped[float | None] = mapped_column("ResistanceDepth", Float(asdecimal=False), nullable=True)
    nuclear_blast: Mapped[float | None] = mapped_column("NuclearBlast", Float(asdecimal=False), nullable=True)
    radiation_shielding: Mapped[float | None] = mapped_column("RadiationShielding", Float(asdecimal=False),
                                                              nullable=True)
    fire_resistance: Mapped[float | None] = mapped_column("FireResistance", Float(asdecimal=False), nullable=True)
    shelter_status: Mapped[int | None] = mapped_column("ShelterStatus", Integer, nullable=True, default=1)

    created_time: Mapped[datetime] = mapped_column(
        "CreatedTime", DateTime(timezone=False), default=datetime.utcnow, nullable=True
    )
    updated_time: Mapped[datetime] = mapped_column(
        "UpdatedTime", DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )


class UndergroundCommandPostORM(Base):
    __tablename__ = "UCC_Info"

    id: Mapped[int] = mapped_column("UCCID", Integer, primary_key=True, autoincrement=True)

    ucc_code: Mapped[str] = mapped_column("UCCCode", String(60), nullable=False, unique=True, index=True)
    ucc_name: Mapped[str] = mapped_column("UCCName", String(60), nullable=False, unique=True, index=True)
    country: Mapped[str | None] = mapped_column("Country", String(60), nullable=True, index=True)
    base: Mapped[str | None] = mapped_column("Base", String(60), nullable=True)
    shelter_picture: Mapped[bytes | None] = mapped_column("ShelterPicture", LargeBinary, nullable=True)
    location: Mapped[str | None] = mapped_column("Location", String(60), nullable=True)

    rock_layer_materials: Mapped[str] = mapped_column("RockLayerMaterials", String(60), nullable=False)
    rock_layer_thick: Mapped[float] = mapped_column("RockLayerThick", Float(asdecimal=False), nullable=False)
    rock_layer_strength: Mapped[float | None] = mapped_column("RockLayerStrength", Float(asdecimal=False),
                                                              nullable=True)

    protective_layer_material: Mapped[str] = mapped_column("ProtectiveLayerMaterial", String(60), nullable=False)
    protective_layer_thick: Mapped[float] = mapped_column("ProtectiveLayerThick", Float(asdecimal=False),
                                                          nullable=False)
    protective_layer_strength: Mapped[float] = mapped_column("ProtectiveLayerStrength", Float(asdecimal=False),
                                                             nullable=False)

    lining_layer_material: Mapped[str] = mapped_column("LiningLayerMaterial", String(60), nullable=False)
    lining_layer_thick: Mapped[float] = mapped_column("LiningLayerThick", Float(asdecimal=False), nullable=False)
    lining_layer_strength: Mapped[float] = mapped_column("LiningLayerStrength", Float(asdecimal=False), nullable=False)

    ucc_wall_materials: Mapped[str] = mapped_column("UCCWallMaterials", String(60), nullable=False)
    ucc_wall_thick: Mapped[float] = mapped_column("UCCWallThick", Float(asdecimal=False), nullable=False)
    ucc_wall_strength: Mapped[float] = mapped_column("UCCWallStrength", Float(asdecimal=False), nullable=False)

    ucc_width: Mapped[float | None] = mapped_column("UCCWidth", Float(asdecimal=False), nullable=True)
    ucc_length: Mapped[float | None] = mapped_column("UCCLength", Float(asdecimal=False), nullable=True)
    ucc_height: Mapped[float | None] = mapped_column("UCCHeight", Float(asdecimal=False), nullable=True)
    ucc_status: Mapped[int | None] = mapped_column("UCCStatus", Integer, nullable=True, default=1)

    created_time: Mapped[datetime] = mapped_column(
        "CreatedTime", DateTime(timezone=False), default=datetime.utcnow, nullable=True
    )
    updated_time: Mapped[datetime] = mapped_column(
        "UpdatedTime", DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
