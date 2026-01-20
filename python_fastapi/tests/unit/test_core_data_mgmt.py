from os import path
from uuid import UUID, uuid4

import pytest
from unittest.mock import AsyncMock, Mock

from core.data_manager.use_cases import DataManagerImpl, PublicCrud
from adapter.sql.data_access import DbAccessImpl
from adapter.sql.data_base import DatabaseManager


@pytest.mark.asyncio
async def test_data_manager_with_mock_repository():
    mock_repo = Mock(spec=DbAccessImpl)

    mock_record = Mock()
    mock_record.id = uuid4()
    mock_record.name = "test_team"
    mock_record.description = "Test description"

    mock_repo.create_record = AsyncMock(return_value=mock_record)

    data_manager = DataManagerImpl(repository=mock_repo)

    result = await data_manager.process(
        operation="create",
        entity="teams",
        name="test_team",
        description="Test description"
    )

    mock_repo.create_record.assert_called_once()
    assert result.name == "test_team"
    assert result.description == "Test description"


@pytest.mark.asyncio
async def test_public_crud_filters_entities():
    mock_data_manager = Mock(spec=DataManagerImpl)
    mock_data_manager.process = AsyncMock(return_value=Mock(id=uuid4(), name="user1"))

    public_crud = PublicCrud(data_manager=mock_data_manager)

    result = await public_crud.process(
        operation="create",
        entity="users",
        name="user1",
        email="user1@example.com"
    )
    assert result is not None
    mock_data_manager.process.assert_called_once()

    mock_data_manager.process.reset_mock()
    result = await public_crud.process(
        operation="create",
        entity="project_roles",
        name="role1"
    )
    assert result is None
    mock_data_manager.process.assert_not_called()

@pytest.mark.asyncio
async def test_general_data_manager(
    db_create_tables,
    db_close,
    sample_teams_data,
    ):
    repository = DbAccessImpl(db_manager=DatabaseManager)
    data_manager = DataManagerImpl(repository=repository)

    await db_create_tables()
    for team_attrs in sample_teams_data["valid_values"]:
        await data_manager.process(
            operation="create",
            entity="teams",
            **team_attrs
        )
    teams_1 = await data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][0]["name"]
    )
    teams_2 = await data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][1]["name"]
    )

    assert teams_1.description == sample_teams_data["valid_values"][0]["description"]
    assert teams_2.description == sample_teams_data["valid_values"][1]["description"]

    await db_close()

    assert not path.exists("test.db")

@pytest.mark.asyncio
async def test_pub_data_manager(
    db_create_tables,
    db_close,
    sample_teams_data,
    sample_users_data,
    ):
    repository = DbAccessImpl(db_manager=DatabaseManager)
    data_manager = DataManagerImpl(repository=repository)
    public_data_manager = PublicCrud(data_manager=data_manager)

    await db_create_tables()

    for team_attrs in sample_teams_data["valid_values"]:
        await public_data_manager.process(
            operation="create",
            entity="teams",
            **team_attrs
        )
    teams_1 = await public_data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][0]["name"]
    )
    teams_2 = await public_data_manager.process(
        operation="read",
        entity="teams",
        record_name=sample_teams_data["valid_values"][1]["name"]
    )

    assert teams_1.description == sample_teams_data["valid_values"][0]["description"]
    assert teams_2.description == sample_teams_data["valid_values"][1]["description"]

    for user_attrs in sample_users_data["valid_values"]:
        await public_data_manager.process(
            operation="create",
            entity="users",
            **user_attrs
        )
    users_1 = await public_data_manager.process(
        operation="read",
        entity="users",
        record_name=sample_users_data["valid_values"][0]["name"]
    )
    users_2 = await public_data_manager.process(
        operation="read",
        entity="users",
        record_name=sample_users_data["valid_values"][1]["name"]
    )

    assert users_1.email == sample_users_data["valid_values"][0]["email"]
    assert users_2.email == sample_users_data["valid_values"][1]["email"]
    assert users_1.team_id is None
    assert users_2.team_id == teams_1.id

    await db_close()

    assert not path.exists("test.db")