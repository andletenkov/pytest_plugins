# pytestflo
Pytest plugin for sending notifications about completed test runs to Flock

# how to use
Unique Flock API hook URL identifier for sending messages must be set up here: https://dev.flock.com/webhooks
```shell script
pytest test_module.py --hook {hookId}
```
