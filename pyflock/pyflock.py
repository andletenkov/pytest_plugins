import pytest
from plugins.flocknotifier import api_client
from plugins.flocknotifier.result_summary import ResultSummary


def pytest_addoption(parser):
    parser.addoption(
        "--hook",
        action="store",
        default=None,
        help="""Unique Flock API hook URL identifier for sending messages. 
                Must be set up here: https://dev.flock.com/webhooks"""
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    pytest.summary = ResultSummary()


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    yield
    hook = config.getoption("--hook")
    if not hook:
        return
    pytest.summary.reporter = terminalreporter
    pytest.summary.status = exitstatus
    r = api_client.send_results(hook,  pytest.summary)
    if r.ok:
        terminalreporter.line("\nNotification with test results was successfully sent to Flock!")
