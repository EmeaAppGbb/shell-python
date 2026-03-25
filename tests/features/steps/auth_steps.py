"""Step definitions for authentication scenarios."""

from behave import given, when, then
from steps.shared_context import register_user, login_user


@given('the user store is empty')
def step_user_store_empty(context):
    """Reset the in-memory user store via a test endpoint or direct call."""
    # Attempt to call a test-reset endpoint; if unavailable, the in-memory
    # store resets naturally between server restarts.
    try:
        context.client.delete("/api/test/reset")
    except Exception:
        pass


@given('a user "{username}" with password "{password}" is registered')
def step_register_existing_user(context, username, password):
    """Register a user as a precondition (ignore response)."""
    register_user(context, username, password)
    # Reset response so the scenario's "When" step captures fresh data
    context.response = None
    context.last_json = None


@given('I am logged in as "{username}" with password "{password}"')
def step_logged_in_as(context, username, password):
    """Log in as the given user and store the auth cookies."""
    login_user(context, username, password)
    # Reset response for the scenario's "When" step
    context.response = None
    context.last_json = None


@when('I register with username "{username}" and password "{password}"')
def step_register(context, username, password):
    """Register a new user via the API."""
    register_user(context, username, password)


@when('I login with username "{username}" and password "{password}"')
def step_login(context, username, password):
    """Log in via the API."""
    login_user(context, username, password)


@when('I call the logout endpoint')
def step_logout(context):
    """Call the logout endpoint with current auth cookies."""
    resp = context.client.post("/api/auth/logout", cookies=context.cookies)
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None
    # Update cookies from response
    context.cookies = dict(resp.cookies)


@when('I request my profile')
def step_request_profile(context):
    """Request the authenticated user's profile."""
    resp = context.client.get("/api/auth/me", cookies=context.cookies)
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None


@when('I request my profile without authentication')
def step_request_profile_no_auth(context):
    """Request the profile endpoint without any auth cookies."""
    resp = context.client.get("/api/auth/me")
    context.response = resp
    try:
        context.last_json = resp.json()
    except Exception:
        context.last_json = None


@then('the response status should be {status_code:d}')
def step_check_status(context, status_code):
    """Verify the HTTP response status code."""
    assert context.response is not None, "No response captured"
    assert context.response.status_code == status_code, (
        f"Expected {status_code}, got {context.response.status_code}. "
        f"Body: {context.response.text}"
    )


@then('the response should contain "{text}"')
def step_response_contains(context, text):
    """Check that the response body contains the given text."""
    assert context.response is not None, "No response captured"
    assert text.lower() in context.response.text.lower(), (
        f"Expected '{text}' in response: {context.response.text}"
    )


@then('the response should contain role "{role}"')
def step_response_contains_role(context, role):
    """Verify the role field in the JSON response."""
    assert context.last_json is not None, "No JSON response"
    assert context.last_json.get("role") == role, (
        f"Expected role '{role}', got '{context.last_json.get('role')}'"
    )


@then('the response should contain error "{text}"')
def step_response_error_contains(context, text):
    """Check that the error field in the response contains the given text."""
    assert context.last_json is not None, "No JSON response"
    error_msg = context.last_json.get("error", "") or context.last_json.get("detail", "")
    assert text.lower() in str(error_msg).lower(), (
        f"Expected error containing '{text}', got: {context.last_json}"
    )


@then('the response should set a token cookie')
def step_check_token_cookie_set(context):
    """Verify that a token cookie was set in the response."""
    assert context.response is not None, "No response captured"
    cookies = context.response.cookies
    # The cookie could be in the response or already captured
    has_token = "token" in cookies or "token" in context.cookies
    assert has_token, f"No token cookie found. Cookies: {dict(cookies)}"


@then('the token cookie should be cleared')
def step_check_token_cookie_cleared(context):
    """Verify that the token cookie was cleared (expired or empty)."""
    assert context.response is not None, "No response captured"
    # After logout, the Set-Cookie header should expire/delete the token
    set_cookie = context.response.headers.get("set-cookie", "")
    # Token should be empty or max-age=0 or expires in the past
    cleared = (
        'token=""' in set_cookie
        or "token=;" in set_cookie
        or "max-age=0" in set_cookie.lower()
        or 'expires=thu, 01 jan 1970' in set_cookie.lower()
    )
    assert cleared, f"Token cookie not cleared. Set-Cookie: {set_cookie}"
