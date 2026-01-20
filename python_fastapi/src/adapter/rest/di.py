from fastapi import Depends, Query
from typing import Annotated

from ports.inbound.data_manager import DataManager
from config.container import container
from adapter.rest.dto import QueryPagination


def get_pagination(
    offset: int | None = Query(None, ge=0),
    limit: int | None = Query(None, ge=1, le=100),
    order: str = Query("asc", pattern="^(asc|desc)$")
) -> QueryPagination:
    return QueryPagination(offset=offset, limit=limit, order=order)


PublicCrudDep = Annotated[DataManager, Depends(container.public_crud)]
PaginationDep = Annotated[QueryPagination, Depends(get_pagination)]
