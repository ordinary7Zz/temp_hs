from __future__ import annotations

from typing import Callable, List, Optional, Protocol, TypeVar

T = TypeVar("T")


class AbstractRepository(Protocol[T]):
    def list_all(self, entity_cls: type | None = None) -> List[T]: ...

    def get(self, item_id: int, entity_cls: type | None = None) -> Optional[T]: ...

    def add(self, item: T) -> T: ...

    def update(
        self,
        item_id: int,
        mutator: Callable[[T], None],
        entity_cls: type | None = None,
    ) -> T: ...

    def delete(self, item_id: int, entity_cls: type | None = None) -> bool: ...

    def update_entity(self, entity: T) -> T: ...

    def add_update_method(self, entity: T, meta: object | None = None) -> None: ...
