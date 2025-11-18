from __future__ import annotations

from dataclasses import fields
from datetime import datetime
from typing import Callable, Iterable, List, Optional, Tuple, Type, Union, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from .entities import AirportRunway, AircraftShelter, UndergroundCommandPost
from .orm import AirportRunwayORM, AircraftShelterORM, UndergroundCommandPostORM

Entity = Union[AirportRunway, AircraftShelter, UndergroundCommandPost]
EntityType = Type[AirportRunway] | Type[AircraftShelter] | Type[UndergroundCommandPost]


class _EntityMeta:
    def __init__(
        self,
        entity_cls: EntityType,
        orm_cls: type,
        primary_key: str = "id",
        audit_fields: Tuple[str, ...] | None = None,
    ) -> None:
        self.entity_cls = entity_cls
        self.orm_cls = orm_cls
        self.primary_key = primary_key
        self.audit_fields: Tuple[str, ...] = audit_fields or ("created_at", "updated_at")
        self.created_field: str | None = self.audit_fields[0] if self.audit_fields else None
        if self.audit_fields and len(self.audit_fields) > 1:
            self.updated_field: str | None = self.audit_fields[1]
        else:
            self.updated_field = self.created_field
        self.field_names: Tuple[str, ...] = tuple(f.name for f in fields(entity_cls))
        self.mutable_fields: Tuple[str, ...] = tuple(
            name for name in self.field_names if name != self.primary_key
        )
        self.mutable_non_audit_fields: Tuple[str, ...] = tuple(
            name for name in self.mutable_fields if name not in self.audit_fields
        )

    def to_entity(self, row: object) -> Entity:
        data = {name: getattr(row, name, None) for name in self.field_names}
        return cast(Entity, self.entity_cls(**data))

    def assign_row_from_entity(self, row: object, entity: Entity, *, for_create: bool) -> None:
        for name in self.mutable_non_audit_fields:
            setattr(row, name, getattr(entity, name))
        if for_create:
            for name in self.audit_fields:
                setattr(row, name, getattr(entity, name))
        elif self.updated_field:
            setattr(row, self.updated_field, getattr(entity, self.updated_field, datetime.utcnow()))


class SQLRepository:
    """
    SQLAlchemy 驱动的通用仓储，支持机场跑道、飞机隐蔽库与地下指挥所三张表的统一 CRUD。
    API 仿照 am_models.sql_repository.SQLRepository，并为实体实例动态绑定 update()。
    """


    _METAS: Tuple[_EntityMeta, ...] = (
        _EntityMeta(AirportRunway, AirportRunwayORM, audit_fields=("created_time", "updated_time")),
        _EntityMeta(AircraftShelter, AircraftShelterORM, audit_fields=("created_time", "updated_time")),
        _EntityMeta(UndergroundCommandPost, UndergroundCommandPostORM, audit_fields=("created_time", "updated_time")),
    )
    _META_BY_ENTITY: dict[type, _EntityMeta] = {meta.entity_cls: meta for meta in _METAS}

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------- Query ----------

    def list_all(self, entity_cls: EntityType | None = None) -> List[Entity]:
        results: List[Entity] = []
        for meta in self._iter_metas(entity_cls):
            rows = self.session.scalars(select(meta.orm_cls)).all()
            entities = [meta.to_entity(r) for r in rows]
            for ent in entities:
                self.add_update_method(ent, meta)
            results.extend(entities)
        return results

    def get(self, item_id: int, entity_cls: EntityType | None = None) -> Optional[Entity]:
        for meta in self._iter_metas(entity_cls):
            row = self.session.get(meta.orm_cls, item_id)
            if row is not None:
                entity = meta.to_entity(row)
                self.add_update_method(entity, meta)
                return entity
        return None

    # ---------- Mutations ----------

    def add(self, item: Entity) -> Entity:
        meta = self._meta_from_entity(item)

        if meta.created_field and getattr(item, meta.created_field, None) is None:
            setattr(item, meta.created_field, datetime.utcnow())
        if meta.updated_field:
            setattr(item, meta.updated_field, datetime.utcnow())

        row = meta.orm_cls()
        meta.assign_row_from_entity(row, item, for_create=True)
        self.session.add(row)
        self.session.flush()

        setattr(item, meta.primary_key, getattr(row, meta.primary_key))
        self.add_update_method(item, meta)
        return item

    def update(self, item_id: int, mutator: Callable[[Entity], None],
               entity_cls: EntityType | None = None) -> Entity:
        entity = self.get(item_id, entity_cls)
        if entity is None:
            raise KeyError(f"Item id={item_id} not found")

        mutator(entity)
        return self.update_entity(entity)

    def update_entity(self, entity: Entity, meta: _EntityMeta | None = None) -> Entity:
        meta = meta or getattr(entity, "_repo_meta", None) or self._meta_from_entity(entity)
        pk_value = getattr(entity, meta.primary_key)
        if pk_value is None:
            raise ValueError(f"{meta.entity_cls.__name__}.{meta.primary_key} is required for update")

        row = self.session.get(meta.orm_cls, pk_value)
        if row is None:
            raise KeyError(f"Item {meta.entity_cls.__name__} id={pk_value} not found")

        if meta.updated_field:
            setattr(entity, meta.updated_field, datetime.utcnow())
        meta.assign_row_from_entity(row, entity, for_create=False)
        self.session.flush()
        self.add_update_method(entity, meta)
        return entity

    def delete(self, item_id: int, entity_cls: EntityType | None = None) -> bool:
        for meta in self._iter_metas(entity_cls):
            row = self.session.get(meta.orm_cls, item_id)
            if row is not None:
                self.session.delete(row)
                return True
        return False

    # ---------- Helpers ----------

    def add_update_method(self, entity: Entity, meta: _EntityMeta | None = None) -> None:
        """
        为实体绑定 instance.update()，保证外部只需修改属性后调用 update() 即可落库。
        """
        meta = meta or self._meta_from_entity(entity)
        setattr(entity, "_repo_meta", meta)

        def _inst_update(**kwargs: object) -> Entity:
            for key, value in kwargs.items():
                if key == "id" or key == meta.created_field:
                    continue
                if hasattr(entity, key):
                    setattr(entity, key, value)
            return self.update_entity(entity, meta)

        setattr(entity, "update", _inst_update)

    def _iter_metas(self, entity_cls: EntityType | None) -> Iterable[_EntityMeta]:
        if entity_cls is None:
            return self._METAS
        return (self._meta_from_cls(entity_cls),)

    def _meta_from_entity(self, entity: Entity) -> _EntityMeta:
        entity_type = type(entity)
        if entity_type not in self._META_BY_ENTITY:
            raise ValueError(f"Unsupported entity type: {entity_type!r}")
        return self._META_BY_ENTITY[entity_type]

    def _meta_from_cls(self, entity_cls: EntityType) -> _EntityMeta:
        if entity_cls not in self._META_BY_ENTITY:
            raise ValueError(f"Unsupported entity class: {entity_cls!r}")
        return self._META_BY_ENTITY[entity_cls]
