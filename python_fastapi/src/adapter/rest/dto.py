from typing import Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr

class CreateUser(BaseModel):
    name: str
    email: EmailStr
    location: str | None = None
    team_name: str | None = None
    team_id: UUID | None = None
    entity: Literal["users"] = "users"


class CreateTeam(BaseModel):
    name: str
    description: str | None = None
    manager_email: EmailStr | None = None
    manager_id: UUID | None = None
    entity: Literal["teams"] = "teams"


class CreateResponse(BaseModel):
    record_id: UUID
    record_name: str | None = None


class ReadEntity(BaseModel):
    record_id: UUID | None = None
    record_name: str | None = None
    entity: Literal["users", "teams"]


class QueryPagination(BaseModel):
    offset: int | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] = "asc"


class ReadUserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    email: EmailStr
    location: str | None = None
    team_id: UUID | None = None
    entity: Literal["users"] = "users"


class ReadTeamResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    description: str | None = None
    manager_id: UUID | None = None
    manager: ReadUserResponse | None = None
    users: list[ReadUserResponse] | None = None
    entity: Literal["teams"] = "teams"
