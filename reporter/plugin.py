import getpass
import os
import pytest
from plugins.reporter import api, utils

ALLURE_RESULTS_ZIP = "allure_results.zip"
ALLURE_ENVIRONMENT_PROPERTIES_FILE = "environment.properties"


def pytest_addoption(parser):
    parser.addini(
        name="allure_results",
        help="Folder for allure results",
        default="allure-results"
    )
    parser.addini(
        name="allure_server_url",
        help="Allure report server URL",
        default=""
    )


def pytest_configure(config):
    if not config.option.allure_report_dir:
        config.option.allure_report_dir = config.getini("allure_results")


def pytest_sessionfinish(session):
    allure_dir = session.config.option.allure_report_dir
    server_url = session.config.getini("allure_server_url")

    assert os.path.isdir(allure_dir), f"{allure_dir} is not exist"

    try:
        utils.compress_to_zip(
            folder=allure_dir,
            zip_name=ALLURE_RESULTS_ZIP
        )

        client = api.AllureServer(server_url)
        path = os.environ.get("JOB_TYPE") or os.environ.get("GITLAB_USER_LOGIN") or getpass.getuser()

        utils.print_(f"\r\n" + "-" * 80)
        utils.print_(f"Генерируется отчет для \"{path}\"...")

        rep_num = client.get_build_num(path)
        path += f"/{rep_num}"
        rep_link = client.generate_report(
            client.send_results(ALLURE_RESULTS_ZIP),
            path
        )
        if rep_link:
            os.environ["ALLURE_REPORT_URL"] = rep_link
            utils.print_(f"Ссылка на отчет: {rep_link}")
        else:
            utils.print_("Не удалось сгенерировать отчет...")
        utils.print_("-" * 80)
    finally:
        utils.cleanup(ALLURE_RESULTS_ZIP, allure_dir)


@pytest.fixture(scope="session", autouse=True)
def add_environment_property(request):
    properties = {}

    def maker(key, value):
        properties.update({key: value})

    yield maker

    allure_dir = request.session.config.option.allure_report_dir
    if not allure_dir or not os.path.isdir(allure_dir) or not properties:
        return

    allure_env_path = os.path.join(allure_dir, ALLURE_ENVIRONMENT_PROPERTIES_FILE)
    with open(allure_env_path, 'w') as f:
        data = '\n'.join([f'{variable}={value}' for variable, value in properties.items()])
        f.write(data)


@pytest.fixture(autouse=True)
def set_properties(request, add_environment_property):
    stage = "Production" if os.environ.get("PROD_CONFIG") else \
        os.environ.get("STAND_NAME") or request.config.getoption('--config')
    add_environment_property("Stage", stage)
