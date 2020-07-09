import os
import allure
import pytest
import plugins.pytestflo.strategies as run_strategies
from logging import info as ilog
from logging import warning as wlog
from pluggy import HookspecMarker
from plugins.pytestflo import utils

hookspec = HookspecMarker("pytest")

STRATEGY_ENV = "TFLO_RUN_BY"
VALUE_ENV = "TFLO_RUN_VALUE"
AVAILABLE_RUN_STRATEGIES = [
    x.replace('RunStrategy', '')
    for x in run_strategies.__dict__.keys()
    if x.startswith('RunStrategy')
]


def pytest_addoption(parser):
    parser.addoption(
        "--run-by",
        action="store",
        dest="run_by",
        choices=AVAILABLE_RUN_STRATEGIES,
        help="Test execution strategy.",
        default=""
    )

    parser.addoption(
        "--run-value",
        action="store",
        dest="run_value",
        help="Jira query value to execute tests with.",
        default=""
    )

    parser.addini(
        name="gitlab_api_token",
        help="Gitlab API auth token",
        default=""
    )

    parser.addini(
        name="jira_server",
        help="JIRA server URL",
        default=""
    )

    parser.addini(
        name="jira_email",
        help="JIRA user e-mail",
        default=""
    )

    parser.addini(
        name="jira_password",
        help="JIRA password",
        default=""
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    config.addinivalue_line("markers", "testflo(key): mark test to map with existing TestFLO test template")

    run_value = os.environ.get(VALUE_ENV) or config.option.run_value

    strategy_name = os.environ.get(STRATEGY_ENV) or config.option.run_by
    strategy_cls_name = "RunStrategy" + strategy_name
    StrategyClass = getattr(run_strategies, strategy_cls_name, None)

    if not StrategyClass:
        raise ValueError(
            f"Invalid run strategy name \"{strategy_name}\"! Available strategies: {AVAILABLE_RUN_STRATEGIES}")

    pytest.tflo = StrategyClass(
        config.getini("jira_server"),
        config.getini("jira_email"),
        config.getini("jira_password"),
        run_value,
        gitlab_token=config.getini("gitlab_api_token")
    )


@hookspec(firstresult=True)
def pytest_collection_modifyitems(session, config, items):
    items_cp = items.copy()
    items.clear()

    for item in items_cp:
        item.issue = None

        tflo_marks = utils.get_mark_list(item, "testflo")
        if not tflo_marks:
            continue

        tflo_mark = tflo_marks[0]

        if tflo_mark not in pytest.tflo.test_case_templates.keys():
            continue

        item.issue = pytest.tflo.test_case_templates[tflo_mark]
        automation_status = str(item.issue.fields.customfield_11903)

        if automation_status not in ("Automated", "Muted",):
            continue

        if automation_status == "Muted":
            item.add_marker(pytest.mark.skip("Muted in Jira"))

        # Устанаваливаем приятненькое имечко
        params = utils.get_test_parameters(item)
        nice_title = utils.get_allure_title(item, params)

        item.add_marker(allure.title(nice_title))
        item.add_marker(allure.link(f"{pytest.tflo.jira.client_info()}/browse/{tflo_mark}"))

        parent = getattr(item.issue.fields.customfield_11401, "value", None)
        suite = item.issue.fields.customfield_13015 or getattr(item.cls, "__name__", None) or item.module.__name__

        if parent:
            item.add_marker(allure.parent_suite(parent))
        item.add_marker(allure.suite(suite))

        nodes = item._nodeid.split("::")[:-1]
        nodes.append(utils.get_pretty_name(item, params))
        item._nodeid = "::".join(nodes)

        items.append(item)

    if not items:
        wlog("Test not found!")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    report = (yield).get_result()

    if call.when != "call":
        return report

    pytest.tflo.on_pytest_runtest_makereport(item=item, report=report)
    return report


def pytest_sessionfinish(session, exitstatus):
    pytest.tflo.on_pytest_sessionfinish()
