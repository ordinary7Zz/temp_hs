from __future__ import annotations

from typing import Iterable, List, Optional, Type, Union, cast

from .entities import AirportRunway, AircraftShelter, UndergroundCommandPost
from .exporters import CSVExporter, JSONExporter
from .repository import AbstractRepository

Entity = Union[AirportRunway, AircraftShelter, UndergroundCommandPost]
EntityType = Type[AirportRunway] | Type[AircraftShelter] | Type[UndergroundCommandPost]


class TargetService:
    """面向三类设施（跑道、隐蔽库、地下指挥所）的用例服务：列表、新增、编辑、删除、导出。"""

    def __init__(self, repo: AbstractRepository[Entity]) -> None:
        self.repo = repo

    # ---------- Generic operations ----------

    def list_all(self, entity_cls: EntityType | None = None) -> List[Entity]:
        return self.repo.list_all(entity_cls)

    def get(self, item_id: int, entity_cls: EntityType | None = None) -> Optional[Entity]:
        return self.repo.get(item_id, entity_cls)

    def create(self, entity: Entity) -> Entity:
        return self.repo.add(entity)

    def edit(self, item_id: int, entity_cls: EntityType | None = None, **partial) -> Entity:
        def mutator(e: Entity) -> None:
            for key, value in partial.items():
                if key in ("id", "created_time", "created_at"):
                    continue
                if hasattr(e, key):
                    setattr(e, key, value)

        return self.repo.update(item_id, mutator, entity_cls)

    def remove(self, item_id: int, entity_cls: EntityType | None = None) -> bool:
        return self.repo.delete(item_id, entity_cls)

    # ---------- Convenience wrappers per table ----------

    def list_airport_runways(self) -> List[AirportRunway]:
        return [cast(AirportRunway, e) for e in self.repo.list_all(AirportRunway)]

    def get_airport_runway(self, item_id: int) -> Optional[AirportRunway]:
        entity = self.repo.get(item_id, AirportRunway)
        return cast(Optional[AirportRunway], entity)

    def create_airport_runway(self, runway: AirportRunway) -> AirportRunway:
        return cast(AirportRunway, self.repo.add(runway))

    def edit_airport_runway(self, item_id: int, **partial) -> AirportRunway:
        return cast(
            AirportRunway,
            self.edit(item_id, AirportRunway, **partial),
        )

    def remove_airport_runway(self, item_id: int) -> bool:
        return self.remove(item_id, AirportRunway)

    def list_aircraft_shelters(self) -> List[AircraftShelter]:
        return [cast(AircraftShelter, e) for e in self.repo.list_all(AircraftShelter)]

    def get_aircraft_shelter(self, item_id: int) -> Optional[AircraftShelter]:
        entity = self.repo.get(item_id, AircraftShelter)
        return cast(Optional[AircraftShelter], entity)

    def create_aircraft_shelter(self, shelter: AircraftShelter) -> AircraftShelter:
        return cast(AircraftShelter, self.repo.add(shelter))

    def edit_aircraft_shelter(self, item_id: int, **partial) -> AircraftShelter:
        return cast(
            AircraftShelter,
            self.edit(item_id, AircraftShelter, **partial),
        )

    def remove_aircraft_shelter(self, item_id: int) -> bool:
        return self.remove(item_id, AircraftShelter)

    def list_underground_command_posts(self) -> List[UndergroundCommandPost]:
        return [
            cast(UndergroundCommandPost, e)
            for e in self.repo.list_all(UndergroundCommandPost)
        ]

    def get_underground_command_post(self, item_id: int) -> Optional[UndergroundCommandPost]:
        entity = self.repo.get(item_id, UndergroundCommandPost)
        return cast(Optional[UndergroundCommandPost], entity)

    def create_underground_command_post(
        self, post: UndergroundCommandPost
    ) -> UndergroundCommandPost:
        return cast(UndergroundCommandPost, self.repo.add(post))

    def edit_underground_command_post(self, item_id: int, **partial) -> UndergroundCommandPost:
        return cast(
            UndergroundCommandPost,
            self.edit(item_id, UndergroundCommandPost, **partial),
        )

    def remove_underground_command_post(self, item_id: int) -> bool:
        return self.remove(item_id, UndergroundCommandPost)

    # ---------- Export ----------

    def export_csv(
        self,
        items: Iterable[Entity] | None = None,
        *,
        entity_cls: EntityType | None = None,
    ) -> bytes:
        exporter = CSVExporter()
        data = items if items is not None else self.repo.list_all(entity_cls)
        return exporter.export(data)

    def export_json(
        self,
        items: Iterable[Entity] | None = None,
        *,
        entity_cls: EntityType | None = None,
    ) -> bytes:
        exporter = JSONExporter()
        data = items if items is not None else self.repo.list_all(entity_cls)
        return exporter.export(data)
