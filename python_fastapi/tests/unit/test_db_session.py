from os import path

from pytest import mark

from sqlmodel import select


@mark.asyncio
async def test_db_session(
    db_tables,
    db_create_tables,
    db_session,
    db_close,
    sample_one_team,
    sample_one_user
    ):

    team_id = None
    team_name = None

    await db_create_tables()

    async with db_session as db:
        rec_team = db_tables["teams"](**sample_one_team)
        rec_user = db_tables["users"](**sample_one_user)
        db.add(rec_team)
        db.add(rec_user)
        await db.commit()
        await db.refresh(rec_team)
        await db.refresh(rec_user)

        assert rec_team.name == sample_one_team["name"]
        assert rec_team.description == sample_one_team["description"]
        assert rec_user.name == sample_one_user["name"]
        assert rec_user.email == sample_one_user["email"]

        team_id = rec_team.id
        team_name = rec_team.name

    async with db_session as db:
        query_result = await db.exec(
            select(db_tables["teams"]).where(
                        db_tables["teams"].name == team_name
                    )
        )
        query_result = query_result.first()

        assert query_result.id == team_id
        result_team_id = query_result.id

        new_user = db_tables["users"](
            name="anotheruser",
            email="anotheruser@example.com",
            team_id=result_team_id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        assert new_user.team_id == result_team_id
        assert new_user.team_id == team_id

    await db_close()

    assert not path.exists("test.db")
