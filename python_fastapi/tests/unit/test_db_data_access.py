from os import path

import pytest

from adapter.sql.data_access import DbAccessImpl
from adapter.sql.data_base import DatabaseManager

@pytest.mark.asyncio
async def test_db_data_access(
    db_create_tables,
    db_close,
    sample_teams_data,
    sample_users_data
    ):

    await db_create_tables()
    db_access = DbAccessImpl(db_manager=DatabaseManager)

    await db_access.create_record(
        table_id="teams",
        attributes=sample_teams_data["valid_values"][0]
    )
    await db_access.create_record(
        table_id="teams",
        attributes=sample_teams_data["valid_values"][1]
    )
    team_record_1 = await db_access.read_record(
        table_id="teams",
        record_name=sample_teams_data["valid_values"][0]["name"]
    )
    team_record_2 = await db_access.read_record(
        table_id="teams",
        record_name=sample_teams_data["valid_values"][1]["name"]
    )

    assert team_record_1.name == sample_teams_data["valid_values"][0]["name"]
    assert team_record_2.name == sample_teams_data["valid_values"][1]["name"]
    assert team_record_1.description == sample_teams_data["valid_values"][0]["description"]
    assert team_record_2.description == sample_teams_data["valid_values"][1]["description"]

    await db_access.create_record(
        table_id="users",
        attributes=sample_users_data["valid_values"][0]
    )
    await db_access.create_record(
        table_id="users",
        attributes=sample_users_data["valid_values"][1]
    )
    user_record_1 = await db_access.read_record(
        table_id="users",
        record_name=sample_users_data["valid_values"][0]["name"]
    )
    user_record_2 = await db_access.read_record(
        table_id="users",
        record_name=sample_users_data["valid_values"][1]["name"]
    )

    assert user_record_1.name == sample_users_data["valid_values"][0]["name"]
    assert user_record_2.name == sample_users_data["valid_values"][1]["name"]
    assert user_record_1.email == sample_users_data["valid_values"][0]["email"]
    assert user_record_2.email == sample_users_data["valid_values"][1]["email"]

    await db_close()

    assert not path.exists("test.db")
