import os

import pytest
from plugins.flocknotifier import api
from plugins.flocknotifier.result_summary import ResultSummary


def pytest_addoption(parser):
    parser.addini('hook-id', """Unique Flock API hook URL identifier for sending messages. 
                Must be set up here: https://dev.flock.com/webhooks""")
    parser.addoption(
        "--flock",
        action="store_true",
        default=False,
        help="Enables Flock notifications"
    )
    parser.addoption(
        "--job-id",
        action="store",
        default=None,
        help="Gitlab job unique ID"
    )
    parser.addoption(
        "--gitlab-user",
        action="store",
        default=None,
        help="Gitlab user email"
    )
    parser.addoption(
        "--pipeline-url",
        action="store",
        default=None,
        help="Gitlab pipeline URL"
    )
    parser.addoption(
        "--report-url",
        action="store",
        default=None,
        help="Allue report URL"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    pytest.summary = ResultSummary()
    pytest.is_hook_enabled = config.getoption("--flock")
    if not pytest.is_hook_enabled:
        return

    job = config.getoption("--job-id") or os.environ.get("CI_JOB_ID")
    owner = config.getoption("--gitlab-user") or os.environ.get("GITLAB_USER_EMAIL")
    pipline = config.getoption("--pipeline-url") or os.environ.get("CI_PIPELINE_URL")

    pytest.flock_client = api.FlockAPIClient(config.getini("hook-id"), job)
    pytest.flock_client.on_start(owner, pipline)


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    yield
    if not pytest.is_hook_enabled:
        return
    pytest.summary.reporter = terminalreporter
    pytest.summary.status = exitstatus
    pytest.summary.report_url = config.getoption("--report-url") or os.environ.get("CI_PAGES_URL") or ""

    r = pytest.flock_client.send_results(pytest.summary)
    if r.ok:
        terminalreporter.line("\nNotification with test results was successfully sent to Flock!")
    else:
        terminalreporter.line(f"\nCan't send notification with hook: {pytest.flock_client.hook}")
