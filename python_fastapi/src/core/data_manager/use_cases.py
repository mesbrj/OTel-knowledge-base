from ports.inbound.data_manager import DataManager
from ports.repository.data_base import DbAccess
from core.data_manager.data_helper import validation_helper
from core.data_manager.data_domain import (
    UserEntity, TeamEntity, ProjectEntity,
    ProjectRoleEntity, StartedProjectEntity
)


class DataManagerImpl(DataManager):
    def __init__(self, repository: DbAccess):
        self.db = repository
        self.entities = {
            "users": UserEntity,
            "teams": TeamEntity,
            "projects": ProjectEntity,
            "project_roles": ProjectRoleEntity,
            "started_projects": StartedProjectEntity,
        }

    @validation_helper
    async def process(self, operation: str, entity: str, **kwargs):
        if (
            not entity 
            or entity not in self.entities.keys()
        ):
            raise ValueError(f"Entity '{entity}' is not supported.")

        if operation == "create":
            attributes = self.entities[entity](**kwargs)
            record = await self.db.create_record(
                table_id = entity,
                attributes = attributes.model_dump(exclude_none=True)
            )
            return record

        elif operation == "read":
            record = await self.db.read_record(
                table_id = entity,
                record_name = kwargs.get("record_name", None),
                record_id = kwargs.get("record_id", None),
                offset = kwargs.get("offset", None),
                limit = kwargs.get("limit", None),
                order = kwargs.get("order", "asc"),
            )
            return record

class PublicCrud():
    def __init__(self, data_manager: DataManager):
        self._proxy_to = data_manager

    def __getattr__(self, name):
        async def filter(*args, **kwargs):
            if kwargs["entity"] not in ["users", "teams", "projects"]:
                return None
            if kwargs["operation"] not in ["create", "read", "update", "delete"]:
                return None
            return await getattr(self._proxy_to, name)(*args, **kwargs)
        return filter
