# pytestflo
Pytest plugin for sending notifications about completed test runs to Flock

# how to use

Unique Flock API hook URL identifier for sending messages must be set up here: https

Add hook ID in pytest.ini:
```ini
[pytest]
...
hook-id = {hook_id}
``` 
Run tests:
```shell script
pytest test_module.py --flock
```
Available options:
```text
--job-id
--gitlab-user
--pipeline-url
--report-url
```
Use -h for more details
