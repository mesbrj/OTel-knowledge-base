from uuid import UUID
from contextlib import asynccontextmanager

from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from pydantic import ValidationError

from adapter.sql.models import User, Team, Project, ProjectUserLink, ProjectRole
from adapter.sql.data_base import DatabaseManager
from ports.repository.data_base import DbAccess


class QueryBuilder:
    def __init__(self, session, table_mapping):
        self._session = session
        self._table = table_mapping
        self._statement = None

    @property
    def table(self):
        return self._table

    def select(self, model):
        self._statement = select(model)
        return self

    def where(self, *conditions):
        if self._statement is None:
            raise ValueError("Must call select() before where()")
        self._statement = self._statement.where(*conditions)
        return self

    async def first(self):
        if self._statement is None:
            raise ValueError("Must call select() before executing query")
        result = await self._session.exec(self._statement)
        return result.first()

    async def all(self):
        if self._statement is None:
            raise ValueError("Must call select() before executing query")
        result = await self._session.exec(self._statement)
        return result.all()


class DbAccessImpl(DbAccess):

    table = {
        "users": User,
        "teams": Team,
        "projects": Project,
        "started_projects": ProjectUserLink,
        "project_roles": ProjectRole,
    }

    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager

    @asynccontextmanager
    async def query_records(self):
        try:
            async with self._db_manager.get_session() as db:
                yield QueryBuilder(db, self.table)

        except SQLAlchemyError as error:
            raise ValueError(f"Error occurred: {error}")

    async def create_record(self, table_id: str, attributes: dict):
        if not table_id or table_id not in self.table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")
        try:
            self.table[table_id].model_validate(attributes)
            async with self._db_manager.get_session() as db:
                rec = self.table[table_id](**attributes)
                db.add(rec)
                await db.commit()
                await db.refresh(rec)
                return rec

        except (SQLAlchemyError, ValidationError) as error:
            raise ValueError(f"Error occurred: {error}")

    async def read_record(
        self,
        table_id: str,
        record_name: str | None = None,
        record_id: UUID | None =  None,
        offset: int | None = None,
        limit: int | None = None,
        order: str | None = None,
        ):
        if not table_id or table_id not in self.table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")
        if record_name and table_id == "started_projects":
            raise ValueError(f"Table '{table_id}' does not support filtering by name")

        is_single_query = record_id is not None or record_name is not None
        try:
            async with self._db_manager.get_session() as db:
                statement = select(self.table[table_id])
                # Eager load sqlalchemy relationships for Team table
                if table_id == "teams":
                    statement = statement.options(
                        selectinload(Team.manager),
                        selectinload(Team.users)
                    )
                if record_id:
                    statement = statement.where(self.table[table_id].id == record_id)
                elif record_name:
                    statement = statement.where(self.table[table_id].name == record_name)
                else:
                    statement = statement.offset(offset or 0).limit(limit or 100)
                    if order in ("asc", "desc"):
                        order_field = self.table[table_id].created_at if table_id == "started_projects" else self.table[table_id].name
                        statement = statement.order_by(
                            order_field.asc() if order == "asc" else order_field.desc()
                        )
                result = await db.exec(statement)
                return result.first() if is_single_query else result.all()

        except (SQLAlchemyError, ValidationError) as error:
            raise ValueError(f"Error occurred: {error}")

    async def update_record(
        self,
        table_id: str,
        record_name: str | None = None,
        record_id: UUID | None = None,
        attributes: dict = {}
        ):
        if not table_id or table_id not in self.table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")

        record_id = attributes.get("id")
        record_name = attributes.get("name")
        if not record_id and not record_name:
            raise ValueError("Either 'id' or 'name' is required for update operation.")
        if record_name and table_id == "started_projects":
            raise ValueError(f"Table '{table_id}' does not support filtering by name")

        try:
            async with self._db_manager.get_session() as db:
                statement = select(self.table[table_id]).where(
                    self.table[table_id].id == record_id if record_id
                    else self.table[table_id].name == record_name
                )
                result = await db.exec(statement)
                existing_record = result.first()

                if not existing_record:
                    identifier = f"id '{record_id}'" if record_id else f"name '{record_name}'"
                    raise ValueError(f"Record with {identifier} not found in table '{table_id}'.")

                for key, value in attributes.items():
                    if key not in ("id", "created_at", "updated_at") and value is not None:
                        if not (key == "name" and record_name and not record_id):
                            setattr(existing_record, key, value)
                db.add(existing_record)
                await db.commit()
                await db.refresh(existing_record)
                return existing_record

        except (SQLAlchemyError, ValidationError) as error:
            raise ValueError(f"Error occurred: {error}")

    async def delete_record(self, table_id: str, record_name: str | None = None, record_id: UUID | None = None):
        if not table_id or table_id not in self.table.keys():
            raise ValueError(f"Table '{table_id}' does not exist.")
        if not record_id and not record_name:
            raise ValueError("Either 'id' or 'name' is required for delete operation.")
        if record_name and table_id == "started_projects":
            raise ValueError(f"Table '{table_id}' does not support filtering by name")
        try:
            async with self._db_manager.get_session() as db:
                statement = select(self.table[table_id]).where(
                    self.table[table_id].id == record_id if record_id else self.table[table_id].name == record_name
                )
                result = await db.exec(statement)
                existing_record = result.first()
                if not existing_record:
                    identifier = f"id '{record_id}'" if record_id else f"name '{record_name}'"
                    raise ValueError(f"Record with {identifier} not found in table '{table_id}'.")
                await db.delete(existing_record)
                await db.commit()
                return {"message": f"Record deleted successfully"}

        except (SQLAlchemyError, ValidationError) as error:
            raise ValueError(f"Error occurred: {error}")
