# pytestflo
Pytest plugin for integration with Jira TestFLO

# how to use
pytest test_module.py --testplan TFLO-123,
where TFLO-123 - test plan ID from Jira

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

    
