"""In-memory user store for MVP.

This module provides a dict-based store matching the TypeScript shell's Map<string, User>.
To switch to Cosmos DB, replace the functions below with async Cosmos SDK calls:

    from azure.cosmos.aio import CosmosClient
    client = CosmosClient(settings.cosmos_endpoint, credential)
    database = client.get_database_client(settings.cosmos_database)
    container = database.get_container_client(settings.cosmos_container)

Each function documents the equivalent Cosmos DB operation.
"""

from app.models import User

# In-memory store — equivalent to `const users = new Map<string, User>()`
_users: dict[str, User] = {}


def get_users() -> dict[str, User]:
    """Return the raw store. Cosmos DB: container.read_all_items()"""
    return _users


def get_user_by_username(username: str) -> User | None:
    """Find user by username. Cosmos DB: container.query_items(query, parameters)"""
    return next((u for u in _users.values() if u.username == username), None)


def get_user_by_id(user_id: str) -> User | None:
    """Find user by ID. Cosmos DB: container.read_item(item=user_id, partition_key=user_id)"""
    return _users.get(user_id)


def add_user(user: User) -> None:
    """Insert a new user. Cosmos DB: container.create_item(body=user.model_dump())"""
    _users[user.id] = user


def get_all_users() -> list[User]:
    """Return all users. Cosmos DB: container.read_all_items()"""
    return list(_users.values())


def clear_users() -> None:
    """Clear all users — test-only. Cosmos DB: delete & recreate container."""
    _users.clear()


def delete_user(user_id: str) -> None:
    """Delete user by ID. Cosmos DB: container.delete_item(item=user_id, partition_key=user_id)"""
    _users.pop(user_id, None)
