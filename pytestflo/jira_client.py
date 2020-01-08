import ast

from requests import Session

TEST_CASE_IDS = "{0}/rest/tms/1.0/testplan/test-case-ids/{1}"
ISSUE = "{0}/rest/api/2/issue/{1}"
TRANSITIONS = "{0}/rest/api/latest/issue/{1}/transitions?expand=transitions.fields"
COMMENT = "{0}/rest/api/2/issue/{1}/comment"

TRANSITION_MAP = {
    "passed": "71",
    "failed": "81"
}


class TestItem(object):
    """
    Jira test item description
    """

    def __init__(self, case_id, template_key):
        self.case_id = case_id
        self.template_key = template_key
        self.__nodeids = []
        self.outcome = None

    @property
    def nodeids(self):
        return self.__nodeids

    def add_nodeid(self, nodeid):
        self.__nodeids.append(nodeid)

    def add_outcome(self, outcome):
        if self.outcome:
            self.outcome.append(outcome)
        else:
            self.outcome = [outcome]


class Jira(object):
    """
    Jira client
    """

    def __init__(self, host, auth_token):
        self.host = host
        self.session = Session()
        self.session.headers = {
            "Authorization": f"Basic {auth_token}"
        }

    def get_test_items(self, test_plan_key):
        """Getting test cases for specified test plan key"""
        case_ids_str = self.session.get(
            TEST_CASE_IDS.format(self.host, test_plan_key)
        ).text

        result = []

        for case_id in ast.literal_eval(case_ids_str):
            issue_dct = self.session.get(
                ISSUE.format(self.host, case_id)
            ).json()

            template_key = issue_dct["fields"]["customfield_11713"]
            result.append(TestItem(case_id, template_key))
        return result

    def set_status(self, case_id, transition):
        """Setting status for specified test case.
        Available value:
            - passed
            - failed
        """
        return self.session.post(
            TRANSITIONS.format(self.host, case_id),
            json={
                "transition": {
                    "id": TRANSITION_MAP.get(transition)
                }
            }
        )

    def add_comment(self, case_id, comment):
        """Adding comment for specified test case"""
        return self.session.post(
            COMMENT.format(self.host, case_id),
            json={
                "body": comment
            }
        )
