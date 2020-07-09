import requests
from plugins.pytestflo import utils
from jira.client import JIRA


class ABCRunStrategy:
    _test_case_templates = {}

    def __init__(self, jira_server, jira_email, jira_pass, value, *args, **kwargs):
        self._jira = JIRA(options={"server": jira_server}, basic_auth=(jira_email, jira_pass))
        self._value = value

    @property
    def jira(self):
        return self._jira

    @property
    def test_case_templates(self):
        raise NotImplementedError

    def on_pytest_runtest_makereport(self, *args, **kwargs):
        raise NotImplementedError

    def on_pytest_sessionfinish(self, *args, **kwargs):
        raise NotImplementedError


class RunStrategyLabels(ABCRunStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = self._value.upper().replace(" ", ", ").replace(",,", ",")

    @property
    def test_case_templates(self):
        if self._test_case_templates:
            return self._test_case_templates

        jql = f"issuetype = \"Test Case Template\" AND labels in ({self._value})"
        self._test_case_templates = {x.key: x for x in self._jira.search_issues(jql)}
        return self._test_case_templates

    def on_pytest_runtest_makereport(self, *args, **kwargs):
        pass

    def on_pytest_sessionfinish(self, *args, **kwargs):
        pass


class RunStrategyTrigger(ABCRunStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._gitlab_token = kwargs.get("gitlab_token")

    @property
    def test_case_templates(self):
        if self._test_case_templates:
            return self._test_case_templates

        resp = requests.get(
            f"https://gitlab.fbs-d.com/api/v4/projects/{self._value}",
            headers={
                "Authorization": f"Bearer {self._gitlab_token}"
            }
        )
        assert resp.status_code == 200, f"Invalid Gitlab API call. Body: {resp.text}"

        gitlab_upstream_project = str(resp.json().get("description", "")).upper()
        jql = f"issuetype = \"Test Case Template\" AND labels in ({gitlab_upstream_project})"
        self._test_case_templates = {x.key: x for x in self._jira.search_issues(jql)}
        return self._test_case_templates

    def on_pytest_runtest_makereport(self, *args, **kwargs):
        pass

    def on_pytest_sessionfinish(self, *args, **kwargs):
        pass


class RunStrategyTestPlan(ABCRunStrategy):
    _results = {}

    @property
    def test_case_templates(self):
        if self._test_case_templates:
            return self._test_case_templates

        jql = f"issue in templatesFromPlan(\"{self._value}\")"
        templates = self._jira.search_issues(jql)

        for template in templates:
            try:
                test_cases = self._jira.search_issues(
                    f"issuetype = \"Test Case\" and \"TC Template\" ~ \"{template.key}\""
                )
                template.test_case_issue = [tc for tc in test_cases if tc.fields.parent.key == self._value][0]
            except Exception:
                template.test_case_issue = None

        self._test_case_templates = {x.key: x for x in templates}
        return self._test_case_templates

    def on_pytest_runtest_makereport(self, *args, **kwargs):
        item = kwargs.get("item")
        report = kwargs.get("report")

        if not hasattr(item, "issue") or not item.issue:
            return

        # Устанавливаем читабельное имя в секции FAILURES
        if not report.passed:
            report.longrepr = f"{utils.get_pretty_name(item, utils.get_test_parameters(item))}: {report.longreprtext}"

        is_passed = True if report.outcome == "passed" else False

        if item.issue.key not in self._results:
            self._results[item.issue.key] = {
                "case_comments": list(),
                "outcome": list(),
            }

        self._results[item.issue.key]["outcome"].append(is_passed)

        comment = utils.COMMENT_TEMPLATE.substitute(
            nodeid=item.nodeid,
            color="green" if is_passed else "red",
            is_passed="PASSED" if is_passed else "FAILED"
        )

        self._results[item.issue.key]["case_comments"].append(comment)

    def on_pytest_sessionfinish(self, *args, **kwargs):
        get_available_transitions = lambda key: dict([(t["name"], t["id"],) for t in self._jira.transitions(key)])

        for tct_key, summary in self._results.items():
            issue = self.test_case_templates.get(tct_key)

            if not issue:
                continue

            if not hasattr(issue, "test_case_issue") or not issue.test_case_issue:
                continue

            is_passed = all(summary["outcome"])
            case_comments_line = '\n'.join(summary["case_comments"])
            comment = f"*Done automatically*\n\n{case_comments_line}"

            # Выставляем статус Open у связанного Test Case
            transitions = get_available_transitions(issue.test_case_issue.key)

            if "Retest" in transitions:
                self._jira.transition_issue(issue.test_case_issue, transitions["Retest"])
                transitions = get_available_transitions(issue.test_case_issue.key)

            if "Pass" not in transitions or "Fail" not in transitions:
                continue

            transition_name = "Pass" if is_passed else "Fail"
            self._jira.transition_issue(issue.test_case_issue, transitions[transition_name])

            # Добавляем комментарий к Test Case Template в JIRA
            self._jira.add_comment(issue.test_case_issue, comment)
