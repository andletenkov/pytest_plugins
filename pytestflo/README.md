# pytestflo
Pytest plugin for integration with Jira TestFLO

# how to use
1. Mark pytest test functions with `@pytest.mark.testflo("TFLO-1")`, where `TFLO-1` - issue key form Jira, to link them with TestFLO issues

2.
- Run Jira test items by specified testplan key:
```shell script
pytest test_module.py --run-by Testplan --run-value TFLO-123
```
- Or by specified Jira item labels:
```shell script
pytest test_module.py --run-by Labels --run-value "API, Smoke"
```
will select only items with corresponding labels

- Also test execution can be triggered by some project from GitLab
```shell script
pytest test_module.py --run-by Trigger --run-value 123
``` 
where `123` - CI project ID from GitLab ($CI_PROJECT_ID env variable).
This option requires GitLab API token specified in pytest.ini (`gitlab_api_token` field)

# examples
```python
@pytest.mark.testflo("TFLO-1")
def test_something():
    assert True


@pytest.mark.testflo("TFLO-2")
@pytest.mark.parametrize("param", [
    1, 2, 3, 4, 5
])
def test_with_params(param):
    assert param == 2
```

    
