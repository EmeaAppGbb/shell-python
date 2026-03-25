"""
Behave environment hooks for spec2cloud Python shell BDD tests.

Configures the HTTP client, base URL, and resets test state between scenarios.
"""

import httpx


def before_all(context):
    """Set up shared configuration for the test run."""
    context.base_url = "http://localhost:5000"


def before_scenario(context, scenario):
    """Reset per-scenario state before each test."""
    context.response = None
    context.cookies = {}
    context.last_json = None

    # Clear the in-memory user store via health + test-reset
    # The API uses an in-memory store; we call clear_users indirectly
    # by hitting a test-only endpoint or restarting.
    # For BDD tests, we rely on the step "the user store is empty" to
    # call the test-reset mechanism.
    context.client = httpx.Client(base_url=context.base_url, timeout=10.0)


def after_scenario(context, scenario):
    """Clean up HTTP client after each scenario."""
    if hasattr(context, "client") and context.client:
        context.client.close()
