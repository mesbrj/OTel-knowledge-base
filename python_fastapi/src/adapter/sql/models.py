from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import ConfigDict, EmailStr
from sqlmodel import Field, SQLModel, String, Relationship
from sqlalchemy import Column, DateTime, func


class ProjectUserLink(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, index=True, unique=True)
    project_id: UUID = Field(foreign_key="project.id", primary_key=True, ondelete="CASCADE")
    user_id: UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    role_id: UUID | None = Field(default=None, foreign_key="projectrole.id", ondelete="SET NULL")
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    role: Optional["ProjectRole"] = Relationship(back_populates="projects")


class User(SQLModel, table=True):
    model_config = ConfigDict(extra='ignore')

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    email: EmailStr = Field(sa_type=String, unique=True, index=True)
    location: str | None = Field(default=None)
    team_id: UUID | None = Field(default=None, foreign_key="team.id", ondelete="SET NULL")
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    team: Optional["Team"] = Relationship(back_populates="users", sa_relationship_kwargs={"foreign_keys": "[User.team_id]"})
    manages: Optional["Team"] = Relationship(back_populates="manager", sa_relationship_kwargs={"foreign_keys": "[Team.manager_id]", "uselist": False})
    projects: list["Project"] = Relationship(back_populates="users", link_model=ProjectUserLink)


class Team(SQLModel, table=True):
    model_config = ConfigDict(extra='ignore')

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    manager_id: UUID | None = Field(default=None, foreign_key="user.id", unique=True, ondelete="SET NULL")
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    users: list[User] = Relationship(back_populates="team", sa_relationship_kwargs={"foreign_keys": "[User.team_id]"})
    manager: Optional[User] = Relationship(back_populates="manages", sa_relationship_kwargs={"foreign_keys": "[Team.manager_id]"})


class Project(SQLModel, table=True):
    model_config = ConfigDict(extra='ignore')

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    users: list["User"] = Relationship(back_populates="projects", link_model=ProjectUserLink)


class ProjectRole(SQLModel, table=True):
    model_config = ConfigDict(extra='ignore')

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    created_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    projects: list[ProjectUserLink] = Relationship(back_populates="role")