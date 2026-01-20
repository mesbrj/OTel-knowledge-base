from uuid import UUID
from fastapi import APIRouter, status

from adapter.rest.di import PublicCrudDep, PaginationDep
from adapter.rest.dto import (
    CreateResponse, CreateUser, CreateTeam,
    ReadUserResponse, ReadTeamResponse
)

health_routes = APIRouter()
crud_routes = APIRouter()

@health_routes.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@crud_routes.post(
    "/users",
    response_model=CreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"]
)
async def create_user(
    body: CreateUser,
    data_manager: PublicCrudDep
):
    new_rec = await data_manager.process(
        operation="create",
        entity=body.entity,
        **body.model_dump(exclude={"entity"})
    )
    return CreateResponse(
        record_id=new_rec.id,
        record_name=new_rec.name,
    )


@crud_routes.post(
    "/teams",
    response_model=CreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Teams"]
)
async def create_team(
    body: CreateTeam,
    data_manager: PublicCrudDep
):
    new_rec = await data_manager.process(
        operation="create",
        entity=body.entity,
        **body.model_dump(exclude={"entity"})
    )
    return CreateResponse(
        record_id=new_rec.id,
        record_name=new_rec.name,
    )


@crud_routes.get(
    "/users/{record_id}",
    response_model=ReadUserResponse,
    status_code=status.HTTP_200_OK,
    tags=["Users"]
)
async def read_user_by_id(
    record_id: UUID,
    data_manager: PublicCrudDep
):
    record = await data_manager.process(
        operation="read",
        entity="users",
        record_id=record_id
    )
    return record


@crud_routes.get(
    "/users",
    response_model=list[ReadUserResponse],
    status_code=status.HTTP_200_OK,
    tags=["Users"]
)
async def read_all_users(
    data_manager: PublicCrudDep,
    pagination: PaginationDep
):
    records = await data_manager.process(
        operation="read",
        entity="users",
        offset=pagination.offset,
        limit=pagination.limit,
        order=pagination.order
    )
    return records


@crud_routes.get(
    "/teams/{record_id}",
    response_model=ReadTeamResponse,
    status_code=status.HTTP_200_OK,
    tags=["Teams"]
)
async def read_team_by_id(
    record_id: UUID,
    data_manager: PublicCrudDep
):
    record = await data_manager.process(
        operation="read",
        entity="teams",
        record_id=record_id
    )
    return record


@crud_routes.get(
    "/teams",
    response_model=list[ReadTeamResponse],
    status_code=status.HTTP_200_OK,
    tags=["Teams"]
)
async def read_all_teams(
    data_manager: PublicCrudDep,
    pagination: PaginationDep
):
    records = await data_manager.process(
        operation="read",
        entity="teams",
        offset=pagination.offset,
        limit=pagination.limit,
        order=pagination.order
    )
    return records

