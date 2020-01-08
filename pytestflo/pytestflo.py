import sys
import pytest
from pytestflo.jira_client import Jira


def pytest_addoption(parser):
    parser.addoption(
        '--testplan',
        action='store',
        help='TestFLO test plan key'
    )
    parser.addoption(
        '--host',
        action='store',
        help='Jira host'
    )
    parser.addoption(
        '--token',
        action='store',
        help='Base64 encoded username:password string'
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'testflo(key): mark test to map with existing testFLO test template'
    )
    pytest.test_plan_key = None
    pytest.testflo_cases = []
    pytest.pytest_items = {}
    pytest.jira = Jira(
        config.getoption('--host'),
        config.getoption('--token')
    )
    test_plan_key = config.getoption('--testplan')

    if test_plan_key is not None:
        pytest.test_plan_key = test_plan_key
        pytest.testflo_cases.extend(pytest.jira.get_test_items(test_plan_key))


def _get_result(case):
    """Getting test outcome and comment to post to Jira issue
    :returns tuple of outcome and comment
    """
    if len(case.outcome) == 1:
        out = case.outcome[0]
    elif 'failed' in case.outcome:
        out = 'failed'
    else:
        out = 'passed'

    comment_header = "Done automatically\n"
    display_names = [nodeid.split('::')[-1] for nodeid in case.nodeids]
    comment_body = "\n".join(("{}: {}".format(*i) for i in dict(zip(display_names, case.outcome)).items()))
    return out, comment_header + comment_body


def pytest_terminal_summary(terminalreporter):
    if pytest.test_plan_key:
        print("\nUpdating TestFLO issues...", file=sys.stdout)
        updated = int()
        for item in pytest.testflo_cases:
            if item.outcome:
                result, comment = _get_result(item)
                r = pytest.jira.set_status(item.case_id, result)
                if r.status_code not in [200, 204]:
                    print(r.text, file=sys.stdout)
                else:
                    pytest.jira.add_comment(item.case_id, comment)
                    print(".", end="", file=sys.stdout)
                    updated += 1
        print(f"\n{updated} issues updated successfully", file=sys.stdout)


def _get_testflo_mark_value(item):
    """Getting TestFLO mark value for current test"""
    return [mark.args[0] for mark in item.iter_markers(name='testflo')]


def pytest_runtest_setup(item):
    if item.config.getoption('--testplan'):
        keys = _get_testflo_mark_value(item)
        if keys:
            template_keys = [case.template_key for case in pytest.testflo_cases]
            if keys[0] not in template_keys:
                pytest.skip("Not contained in test plan")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()

    if call.when == "call":
        keys = _get_testflo_mark_value(item)
        if keys:
            for case in pytest.testflo_cases:
                if keys[0] == case.template_key:
                    case.add_outcome(report.outcome)
                    case.add_nodeid(item.nodeid)
