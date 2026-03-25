"""Step definitions for admin and RBAC scenarios."""

from behave import when, then
from steps.shared_context import make_authenticated_request


@when('I request the admin user list')
def step_request_admin_users(context):
    """Request the admin users endpoint with current auth cookies."""
    make_authenticated_request(context, "GET", "/api/admin/users")


@when('I request the admin user list without authentication')
def step_request_admin_users_no_auth(context):
    """Request the admin users endpoint without authentication."""
    resp = context.client.get("/api/admin/users")
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None


@then('the user list should contain "{username}"')
def step_user_list_contains(context, username):
    """Verify the user list includes the given username."""
    assert context.last_json is not None, "No JSON response"
    assert isinstance(context.last_json, list), (
        f"Expected a list, got: {type(context.last_json)}"
    )
    usernames = [u.get("username") for u in context.last_json]
    assert username in usernames, (
        f"User '{username}' not in list: {usernames}"
    )


@then('the profile username should be "{username}"')
def step_profile_username(context, username):
    """Verify the profile response has the expected username."""
    assert context.last_json is not None, "No JSON response"
    assert context.last_json.get("username") == username, (
        f"Expected username '{username}', got '{context.last_json.get('username')}'"
    )


@then('the profile should include a role')
def step_profile_has_role(context):
    """Verify the profile response includes a role field."""
    assert context.last_json is not None, "No JSON response"
    assert "role" in context.last_json, (
        f"No 'role' in profile: {context.last_json}"
    )


@then('the profile should include a createdAt timestamp')
def step_profile_has_created_at(context):
    """Verify the profile response includes a createdAt field."""
    assert context.last_json is not None, "No JSON response"
    assert "createdAt" in context.last_json, (
        f"No 'createdAt' in profile: {context.last_json}"
    )
