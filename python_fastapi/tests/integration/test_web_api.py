from pytest import mark


@mark.anyio
async def test_health_check(fastapi_client):
    response = await fastapi_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@mark.anyio
async def test_create_team(fastapi_client, sample_teams_data):
    team_data = sample_teams_data["valid_values"][0]
    response = await fastapi_client.post("/teams", json=team_data)

    assert response.status_code == 201

    data = response.json()

    assert data["record_name"] == team_data["name"]
    assert "record_id" in data


@mark.anyio
async def test_create_user(fastapi_client, sample_users_data):
    user_data = sample_users_data["valid_values"][0]
    response = await fastapi_client.post("/users", json=user_data)

    assert response.status_code == 201

    data = response.json()

    assert data["record_name"] == user_data["name"]
    assert "record_id" in data


@mark.anyio
async def test_create_user_with_team_name(fastapi_client, sample_teams_data, sample_users_data):
    # First create a team
    team_data = sample_teams_data["valid_values"][0]
    team_response = await fastapi_client.post("/teams", json=team_data)
    assert team_response.status_code == 201
    team_record = team_response.json()
    team_id = team_record["record_id"]

    # Create user with team_name
    user_data = sample_users_data["valid_values"][1]  # Has team_name
    user_response = await fastapi_client.post("/users", json=user_data)
    assert user_response.status_code == 201
    user_record = user_response.json()

    # Read the user to verify team_id FK
    read_response = await fastapi_client.get(f"/users/{user_record['record_id']}")
    assert read_response.status_code == 200
    user_details = read_response.json()
    
    assert user_details["team_id"] == team_id
    assert user_details["name"] == user_data["name"]


@mark.anyio
async def test_read_user_by_id(fastapi_client, sample_users_data):
    # Create a user first
    user_data = sample_users_data["valid_values"][0]
    create_response = await fastapi_client.post("/users", json=user_data)
    assert create_response.status_code == 201
    created_user = create_response.json()
    user_id = created_user["record_id"]

    # Read the user by ID
    response = await fastapi_client.get(f"/users/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["location"] == user_data.get("location")


@mark.anyio
async def test_read_all_users_paginated(fastapi_client, sample_teams_data, sample_users_data):
    # First create teams for FK relationships
    team_data = sample_teams_data["valid_values"][0]  # engineering
    team_response = await fastapi_client.post("/teams", json=team_data)
    assert team_response.status_code == 201
    team_id = team_response.json()["record_id"]

    # Create multiple users with different scenarios
    created_ids = []
    users_to_create = [
        sample_users_data["valid_values"][0],  # alice (no team)
        sample_users_data["valid_values"][1],  # bob (with team_name: engineering)
        sample_users_data["valid_values"][3]   # diana (no team)
    ]
    for user_data in users_to_create:
        response = await fastapi_client.post("/users", json=user_data)
        assert response.status_code == 201
        created_ids.append(response.json()["record_id"])

    # Test default pagination
    response = await fastapi_client.get("/users")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Verify bob has team_id set
    bob = next((u for u in data if u["name"] == "bob"), None)
    assert bob is not None
    assert bob["team_id"] == team_id

    # Verify alice and diana have no team
    alice = next((u for u in data if u["name"] == "alice"), None)
    assert alice is not None
    assert alice["team_id"] is None

    # Test with limit
    response = await fastapi_client.get("/users?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    # Test with offset
    response = await fastapi_client.get("/users?offset=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    # Test with order desc
    response = await fastapi_client.get("/users?order=desc")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@mark.anyio
async def test_read_team_by_id(fastapi_client, sample_teams_data, sample_users_data):
    # Create the manager user first
    manager_data = {
        "name": "alice_manager",
        "email": "alice.manager@example.com",
        "location": "San Francisco"
    }
    manager_response = await fastapi_client.post("/users", json=manager_data)
    assert manager_response.status_code == 201
    manager_id = manager_response.json()["record_id"]

    # Create a team with manager_email
    team_data = {
        "name": "engineering",
        "description": "Engineering team",
        "manager_email": manager_data["email"]
    }
    create_response = await fastapi_client.post("/teams", json=team_data)
    assert create_response.status_code == 201
    created_team = create_response.json()
    team_id = created_team["record_id"]

    # Create multiple users for this team (more than 2)
    team_users = []
    user_names = ["bob", "charlie", "diana_engineer"]
    user_emails = ["bob@example.com", "charlie.eng@example.com", "diana.eng@example.com"]

    for name, email in zip(user_names, user_emails):
        user_data = {
            "name": name,
            "email": email,
            "location": "New York",
            "team_name": team_data["name"]
        }
        user_response = await fastapi_client.post("/users", json=user_data)
        assert user_response.status_code == 201
        team_users.append(user_response.json())

    # Read the team by ID
    response = await fastapi_client.get(f"/teams/{team_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == team_id
    assert data["name"] == team_data["name"]
    assert data["description"] == team_data["description"]

    # Verify manager relationship is properly loaded with actual data
    assert "manager" in data
    assert data["manager"] is not None
    assert data["manager"]["id"] == manager_id
    assert data["manager"]["name"] == manager_data["name"]
    assert data["manager"]["email"] == manager_data["email"]

    # Verify users relationship is properly loaded with multiple users
    assert "users" in data
    assert isinstance(data["users"], list)
    assert len(data["users"]) == 3  # Three team members

    # Verify each user is in the team
    user_ids_in_team = [u["id"] for u in data["users"]]
    for user in team_users:
        assert user["record_id"] in user_ids_in_team

    # Verify user details
    for user_data_item in data["users"]:
        assert "id" in user_data_item
        assert "name" in user_data_item
        assert "email" in user_data_item
        assert user_data_item["team_id"] == team_id


@mark.anyio
async def test_read_all_teams_paginated(fastapi_client, sample_teams_data):
    # Create multiple teams
    created_ids = []
    for team_data in sample_teams_data["valid_values"]:
        response = await fastapi_client.post("/teams", json=team_data)
        assert response.status_code == 201
        created_ids.append(response.json()["record_id"])

    # Test default pagination
    response = await fastapi_client.get("/teams")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

    # Test with limit
    response = await fastapi_client.get("/teams?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Test with offset and order
    response = await fastapi_client.get("/teams?offset=1&limit=1&order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@mark.anyio
async def test_read_team_with_users(fastapi_client, sample_teams_data, sample_users_data):
    # Create the engineering team
    team_data = sample_teams_data["valid_values"][0]  # engineering
    team_response = await fastapi_client.post("/teams", json=team_data)
    assert team_response.status_code == 201
    team_id = team_response.json()["record_id"]

    # Create marketing team (needed for charlie)
    marketing_data = sample_teams_data["valid_values"][1]  # marketing
    marketing_response = await fastapi_client.post("/teams", json=marketing_data)
    assert marketing_response.status_code == 201

    # Create users with team_name references
    for user_data in sample_users_data["valid_values"][1:3]:  # bob (engineering) and charlie (marketing)
        response = await fastapi_client.post("/users", json=user_data)
        assert response.status_code == 201

    # Read the engineering team with relationships
    response = await fastapi_client.get(f"/teams/{team_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == team_id
    assert "users" in data
