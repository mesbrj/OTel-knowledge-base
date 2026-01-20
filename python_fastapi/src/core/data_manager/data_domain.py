from uuid import UUID
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# Entities

class UserEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    email: EmailStr | None = None
    location: str | None = None
    team_name: str | None = None
    team_id: UUID | None = None
    team: Optional['TeamEntity'] = None
    manages: Optional['TeamEntity'] = None
    projects: Optional[list['ProjectEntity']] = None
    entity: Literal["users"] = "users"


class TeamEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    manager_name: str | None = None
    manager_id: UUID | None = None
    manager: Optional['UserEntity'] = None
    users: Optional[list[UserEntity]] = None
    entity: Literal["teams"] = "teams"


class ProjectEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    users: Optional[list[UserEntity]] = None
    entity: Literal["projects"] = "projects"


class ProjectRoleEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    name: str | None = None
    description: str | None = None
    projects: Optional[list[ProjectEntity]] = None
    entity: Literal["project_roles"] = "project_roles"


class StartedProjectEntity(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID | None = None
    project_name: str | None = None
    project_id: UUID | None = None
    user_name: str | None = None
    user_id: UUID | None = None
    role_name: str | None = None
    role_id: UUID | None = None
    role: ProjectRoleEntity | None = None
    entity: Literal["started_projects"] = "started_projects"