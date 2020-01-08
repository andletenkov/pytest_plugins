from setuptools import setup

setup(
    name='pytestflo',
    version='0.1.0',
    description='Pytest plugin for TestFLO and automated tests integration',
    url='https://www.pytestflo.com',
    author='Andrey Letenkov',
    author_email='andletenkov@gmail.com',
    license='proprietary',
    py_modules=['pytestflo', 'jira_client'],
    install_requires=['pytest', 'requests'],
    entry_points={'pytest11': ['pytestflo = pytestflo', ], },
)
