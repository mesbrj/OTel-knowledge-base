from functools import wraps


def validation_helper(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        wrapped = func.__qualname__.split('.')
        if wrapped[0] == 'DataManagerImpl' and wrapped[1] == 'process':
            wrapped.append(kwargs.get("operation"))
            wrapped.append(kwargs.get("entity"))

        match wrapped:

            case ['DataManagerImpl', 'process', 'create', 'users']:
                if kwargs.get("team_name"):
                    record = await self.db.read_record(
                        table_id = "teams",
                        record_name = kwargs.get("team_name")
                    )
                    if not record:
                        raise ValueError(
                            f"Team with name '{kwargs.get('team_name')}' does not exist."
                        )
                    kwargs["team_id"] = record.id

            case ['DataManagerImpl', 'process', 'create', 'teams']:
                if kwargs.get("manager_email"):
                    async with self.db.query_records() as query:
                        user = await (
                            query
                            .select(query.table["users"])
                            .where(query.table["users"].email == kwargs.get("manager_email"))
                            .first()
                        )
                    if not user:
                        raise ValueError(
                            f"User with email '{kwargs.get('manager_email')}' does not exist."
                        )
                    kwargs["manager_id"] = user.id

        return await func(self, *args, **kwargs)

    return wrapper