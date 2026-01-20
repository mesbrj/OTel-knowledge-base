from uuid import UUID
from abc import ABC, abstractmethod


class DbAccess(ABC):
    @abstractmethod
    async def query_records(self): ...

    @abstractmethod
    async def create_record(
        self,
        table_id: str,
        attributes: dict
        ): ...

    @abstractmethod
    async def read_record(
        self,
        table_id: str,
        record_name: str | None = None,
        record_id: UUID | None = None,
        offset: int | None = None,
        limit: int | None = None,
        order: str | None = None,
        ): ...

    @abstractmethod
    async def update_record(
        self,
        table_id: str,
        record_name: str | None = None,
        record_id: UUID | None = None,
        attributes: dict = {}
        ): ...

    @abstractmethod
    async def delete_record(
        self,
        table_id: str,
        record_name: str | None = None,
        record_id: UUID | None = None
        ): ...